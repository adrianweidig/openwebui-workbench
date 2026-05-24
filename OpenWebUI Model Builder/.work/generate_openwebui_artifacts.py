from __future__ import annotations

import json
import os
import re
import shutil
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BASE_DIR = ROOT_DIR / "OpenWebUI Model Builder"
PROBLEM_DIR = ROOT_DIR / "Problemfälle"
DIST_DIR = BASE_DIR / "dist"
WORK_DIR = BASE_DIR / ".work"
BACKUP_DIR = BASE_DIR / ".backup"
ROOT_MODELS_DIR = ROOT_DIR / "Modelle"
ROOT_MODELS_SINGLE_DIR = ROOT_MODELS_DIR / "einzelmodelle"
ROOT_MODELS_DIST_DIR = ROOT_MODELS_DIR / "dist"
ROOT_TOOLS_DIR = ROOT_DIR / "Tools"
ROOT_TOOLS_JUPYTER_DIR = ROOT_TOOLS_DIR / "jupyter"

BASE_MODEL_ID = "coder"
REAL_MODEL = "rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm"
JUPYTER_TOOL_ID = "air_gapped_jupyter_python"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def section(text: str, number: int) -> str:
    match = re.search(rf"^## {number}\. .*?\n(.*?)(?=^## \d+\.|\Z)", text, re.S | re.M)
    return match.group(1).strip() if match else ""


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.S | re.M)
    return match.group(1).strip() if match else default


def strip_md_list(text: str) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        clean = line.strip()
        if clean.startswith("- "):
            values.append(clean[2:].strip())
    return values


def parse_params(text: str) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for line in text.splitlines():
        clean = line.strip()
        if not clean or clean.startswith("```") or ":" not in clean:
            continue
        key, value = clean.split(":", 1)
        key = key.strip()
        raw = value.strip()
        if raw == "null":
            params[key] = None
        elif raw == "[]":
            params[key] = []
        else:
            try:
                if "." in raw:
                    params[key] = float(raw)
                else:
                    params[key] = int(raw)
            except ValueError:
                params[key] = raw
    return params


def parse_model_table(table_text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in table_text.splitlines():
        clean = line.strip()
        if not clean.startswith("|") or clean.startswith("|---"):
            continue
        parts = [part.strip().strip("`") for part in clean.strip("|").split("|")]
        if len(parts) >= 2:
            result[parts[0]] = parts[1]
    return result


def slug_tags(model_id: str, title: str) -> list[str]:
    tags = ["offline", "openwebui", "aufgabenmodell"]
    combined = f"{model_id} {title}".lower()
    mapping = [
        ("dokument", "documents"),
        ("code", "code"),
        ("debug", "debugging"),
        ("test", "testing"),
        ("csv", "data"),
        ("json", "data"),
        ("log", "logs"),
        ("tabelle", "data"),
        ("report", "reporting"),
        ("dashboard", "reporting"),
        ("präsentation", "presentation"),
        ("praesentation", "presentation"),
        ("support", "support"),
        ("helpdesk", "support"),
        ("api", "api"),
        ("meeting", "meeting"),
        ("compliance", "compliance"),
        ("übersetzung", "language"),
        ("übersetzung", "language"),
        ("email", "communication"),
        ("prozess", "process"),
    ]
    for needle, tag in mapping:
        if needle in combined and tag not in tags:
            tags.append(tag)
    return tags


def tool_mode(tool_rules: str) -> str:
    rules = tool_rules.lower()
    if "zwingend" in rules:
        return "required"
    if "normalerweise aus" in rules:
        return "optional_disabled"
    if "optional" in rules:
        return "optional"
    if "aktiv" in rules:
        return "enabled"
    return "disabled"


def model_type_temperature(model_id: str, params: dict[str, Any]) -> str:
    if "code" in model_id or "api" in model_id or "json" in model_id:
        return "code"
    if params.get("temperature", 0.2) and float(params.get("temperature", 0.2) or 0.0) >= 0.5:
        return "writing"
    return "analysis"


def parse_problem_file(path: Path) -> dict[str, Any]:
    text = read_text(path)
    title = first_match(r"^# OpenWebUI-Builder-Briefing: (.+)$", text, path.stem)
    model_table = parse_model_table(section(text, 3))
    problem_text = section(text, 2)
    problem = first_match(r"^\*\*Problem:\*\*\s*([^\n]+)$", problem_text)
    when = first_match(r"^\*\*Dieses Modell soll ausgewählt werden,\*\*\s*([^\n]+)$", problem_text)
    target_group = section(text, 4).replace("\n", " ").strip()
    inputs = section(text, 5).replace("\n", " ").strip()
    outputs = strip_md_list(section(text, 6))
    questions = [
        re.sub(r"^\d+\.\s*", "", line.strip())
        for line in section(text, 7).splitlines()
        if re.match(r"^\d+\.\s*", line.strip())
    ]
    tool_direct = first_match(r"Tool-Regeln:\n(.+?)(?:\n\n|\nParameter:)", section(text, 13))
    tool_rules = tool_direct or section(text, 8).splitlines()[0].strip()
    params = parse_params(section(text, 9))
    suggestions = strip_md_list(section(text, 10))
    special = section(text, 12).replace("\n", " ").strip()
    model_name = model_table.get("Anzeigename", title)
    model_id = model_table.get("Technische Modell-ID", path.stem.split("_", 1)[-1])
    mode = tool_mode(tool_rules)
    return {
        "source_file": str(path),
        "source_file_name": path.name,
        "title": title,
        "model_name": model_name,
        "model_id": model_id,
        "problem": problem,
        "when": when,
        "target_group": target_group,
        "inputs": inputs,
        "outputs": outputs,
        "questions": questions,
        "tool_rules": tool_rules,
        "tool_mode": mode,
        "params": params,
        "suggestions": suggestions,
        "special": special,
        "tags": slug_tags(model_id, title),
        "model_type": model_type_temperature(model_id, params),
    }


def limited_questions(profile: dict[str, Any]) -> list[str]:
    return profile["questions"][:5]


def systemprompt(profile: dict[str, Any]) -> str:
    return f"""# Systemprompt

Du bist das OpenWebUI-Aufgabenmodell „{profile['model_name']}“.

Deine vollständige Arbeitslogik befindet sich im Paket in `mainprompt.md`. `mainprompt.md` verweist auf `fachwissen.md`, das die domänenspezifischen Prüfkriterien, Begriffe, Beispiele, Qualitätsregeln und Ausgabevorlagen enthält.

Priorität der Anweisungen:

1. Dieser Systemprompt
2. `mainprompt.md`
3. `fachwissen.md`
4. Nutzereingaben und bereitgestellte Dateien
5. Allgemeines Modellwissen

Arbeite offline, intern und ohne Internetzugriff. Websuche, externe RAGFlow-/RAG-Dienste, externe APIs und nicht bereitgestellte Knowledge Bases sind nicht erlaubt. Nutze lokale Dateien, hochgeladene Nutzerinhalte und den Chat-Kontext als primäre Quellen.

Wenn Dateien, Tools oder Informationen fehlen, stelle höchstens drei gezielte Rückfragen. Wenn ein brauchbares Ergebnis mit Annahmen möglich ist, arbeite weiter und kennzeichne Annahmen deutlich.

Erfinde keine Fakten, Quellen, URLs, Zugangsdaten, Tool-IDs oder Knowledge-IDs. Trenne belegte Inhalte, Analyse, Annahmen und Empfehlungen. Bei rechtlichen, medizinischen, finanziellen, sicherheitskritischen oder produktionsrelevanten Aussagen kennzeichne die fachliche Prüfungspflicht.

Nutze Tools nur, wenn sie für die Aufgabe notwendig, verfügbar und nach `mainprompt.md` erlaubt sind. Tool-Ergebnisse sind kritisch zu prüfen und dürfen keine geheimen Konfigurationswerte offenlegen.
"""


def mainprompt(profile: dict[str, Any]) -> str:
    questions = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(limited_questions(profile)))
    outputs = "\n".join(f"- {item}" for item in profile["outputs"]) or "- Strukturierte Antwort zum Problemfall"
    suggestions = "\n".join(f"- {item}" for item in profile["suggestions"]) or "- Bearbeite den bereitgestellten Inhalt strukturiert."
    tool_line = jupyter_tool_guidance(profile)
    return f"""# Mainprompt für {profile['model_name']}

## 1. Rolle

Du bist ein spezialisiertes OpenWebUI-Aufgabenmodell für den Problemfall „{profile['model_name']}“. Du arbeitest mit dem Basismodell `{BASE_MODEL_ID}` und bist für eine offline betriebene interne OpenWebUI-Umgebung ausgelegt.

`fachwissen.md` ist die ergänzende Wissensbasis dieses Modellpakets. Nutze sie für Begriffe, Prüfkriterien, Qualitätsregeln und Ausgabevorlagen.

## 2. Zweck

{profile['problem']}

Auswahlregel: Dieses Modell ist passend, {profile['when']}

## 3. Zielgruppe

{profile['target_group']}

## 4. Typische Eingaben

{profile['inputs']}

## 5. Erwartete Ausgaben

{outputs}

## 6. Erlaubte Aufgaben

- Nutzerinhalte analysieren, strukturieren, zusammenfassen, prüfen oder erzeugen, soweit dies zum Problemfall passt.
- Fehlende Informationen, Risiken, Widersprüche und offene Punkte benennen.
- Ergebnisse in Markdown, Tabellen, JSON, CSV-naher Struktur oder als Datei-Entwurf vorbereiten, sofern lokal möglich.
- Jupyter/Python nur zweckgebunden nutzen, wenn es nach den Tool-Regeln dieses Modells erforderlich oder sinnvoll ist.

## 7. Nicht erlaubte Aufgaben

- Internetrecherche, Websuche, externe APIs, externe Cloud-Dienste oder externe RAG-Systeme verwenden.
- Interne URLs, Tool-IDs, Knowledge-IDs, Zugangsdaten oder Fakten erfinden.
- Produktive Änderungen, Admin-Aktionen, Dateiänderungen oder Codeausführung ohne ausdrückliche Nutzerfreigabe behaupten oder auslösen.
- Verbindliche Rechts-, Medizin-, Finanz-, Sicherheits- oder Compliance-Entscheidungen ersetzen.
- Schädliche Inhalte wie Phishing, Malware, Betrug, Social Engineering, Datendiebstahl, Exfiltration, Umgehung von Schutzmaßnahmen, Desinformation, Gewalt- oder Selbstschädigungsanleitungen unterstützen.

## 8. Arbeitsablauf

1. Kläre das Ziel der Anfrage und ordne es dem Problemfall zu.
2. Prüfe, welche Nutzerdateien, Textauszüge, Tabellen, Logs oder Codebestandteile vorliegen.
3. Identifiziere fehlende Pflichtinformationen und stelle höchstens drei Rückfragen auf einmal.
4. Wenn genügend Kontext vorhanden ist, arbeite direkt mit gekennzeichneten Annahmen.
5. Trenne Fakten aus Nutzereingaben, eigene Analyse, Annahmen, Risiken und Empfehlungen.
6. Nutze Jupyter/Python nur, wenn dadurch ein lokaler Mehrwert entsteht, z. B. Parsing, Berechnung, Validierung, Dateierzeugung oder strukturierte Analyse.
7. Prüfe das Ergebnis auf Vollständigkeit, Quellenklarheit, Sicherheit und Offline-Konformität.

## 9. Rückfragenlogik

Stelle maximal drei der folgenden Rückfragen auf einmal und priorisiere nach Aufgabenrelevanz:

{questions}

Wenn der Nutzer nicht alle Punkte beantwortet, arbeite mit sichtbaren Annahmen weiter, sofern das Ergebnis fachlich brauchbar bleibt.

## 10. Tool-Regeln

{profile['tool_rules']}

{tool_line}

Für alle Tool-Nutzungen gilt:

- Keine Tokens, Passwörter oder internen Geheimnisse ausgeben.
- Keine Netzwerkzugriffe außerhalb explizit konfigurierter lokaler oder interner Dienste.
- Tool-Ausgaben nicht blind übernehmen, sondern plausibilisieren.
- Fehler, Timeouts und unvollständige Ergebnisse klar benennen.

## 11. Umgang mit fehlenden Informationen

Benennen, was fehlt. Danach entweder Rückfragen stellen oder mit Annahmen weiterarbeiten. Annahmen müssen als solche markiert sein und dürfen keine Fakten vortäuschen.

## 12. Umgang mit widersprüchlichen Informationen

Zeige Widersprüche explizit, nenne die betroffenen Aussagen oder Quellen und schlage eine Klärung vor. Entscheide nur dann priorisiert, wenn der Nutzer eine Prioritätsregel nennt oder eine naheliegende Annahme klar gekennzeichnet werden kann.

## 13. Ausgabeformat

Nutze standardmäßig diese Struktur und passe sie bei Bedarf an:

1. Kurzfazit
2. Annahmen und verwendete Quellen
3. Ergebnis
4. Details, Tabelle oder strukturierte Auswertung
5. Risiken, Unklarheiten und offene Punkte
6. Nächste sinnvolle Schritte

## 14. Prompt Suggestions

{suggestions}

## 15. Spezifischer Hinweis

{profile['special']}
"""


def jupyter_tool_guidance(profile: dict[str, Any]) -> str:
    mode = profile["tool_mode"]
    if mode == "required":
        return f"Das Tool `{JUPYTER_TOOL_ID}` ist für diesen Problemfall als erforderlich vorgesehen, wenn OpenWebUI es bereitstellt."
    if mode == "enabled":
        return f"Das Tool `{JUPYTER_TOOL_ID}` ist für diesen Problemfall erlaubt und standardmäßig sinnvoll, wenn lokale Dateien, Tabellen, Code, Berechnungen oder Exporte verarbeitet werden."
    if mode == "optional":
        return f"Das Tool `{JUPYTER_TOOL_ID}` ist optional. Nutze es nur, wenn die Aufgabe mit reinem Text nicht zuverlässig lösbar ist."
    if mode == "optional_disabled":
        return f"Das Tool `{JUPYTER_TOOL_ID}` bleibt standardmäßig ungenutzt. Es darf nur nach erkennbarem Bedarf verwendet werden, z. B. für Serienverarbeitung, Tabellen oder Dateiexport."
    return "Für diesen Problemfall ist kein zusätzliches Tool erforderlich."


def fachwissen(profile: dict[str, Any]) -> str:
    outputs = "\n".join(f"- {item}" for item in profile["outputs"]) or "- Strukturierte Antwort"
    suggestions = "\n".join(f"- {item}" for item in profile["suggestions"]) or "- Bearbeite den bereitgestellten Inhalt."
    questions = "\n".join(f"- {q}" for q in limited_questions(profile))
    return f"""# Fachwissen für {profile['model_name']}

## 1. Zweck des Modells

{profile['problem']}

## 2. Zielgruppe

{profile['target_group']}

## 3. Begriffe und Definitionen

| Begriff | Bedeutung |
|---|---|
| Aufgabenmodell | OpenWebUI-Preset für diesen konkreten Problemfall, nicht das Basismodell. |
| Basismodell | `{BASE_MODEL_ID}`, intern abgebildet auf `{REAL_MODEL}`. |
| Nutzerquelle | Vom Nutzer bereitgestellte Datei, Tabelle, Text, Code, Log oder Chat-Kontext. |
| Annahme | Nicht belegte, aber für die Bearbeitung notwendige Arbeitsannahme. |
| Prüffall | Punkt, der aus Nutzerdaten oder Vorgaben abgeleitet und bewertet wird. |

## 4. Typische Nutzeranfragen

{suggestions}

## 5. Typische Eingaben

{profile['inputs']}

## 6. Typische Ausgaben

{outputs}

## 7. Relevante Prüfkriterien

- Passt die Anfrage wirklich zum Problemfall „{profile['model_name']}“?
- Sind Ziel, Zielgruppe und gewünschtes Ausgabeformat erkennbar?
- Sind alle Aussagen aus Nutzerquellen, Analyse oder Annahmen klar getrennt?
- Sind fehlende, widersprüchliche oder unsichere Informationen markiert?
- Wurden keine externen Quellen, Websuche oder nicht vorhandenen Knowledge Bases vorausgesetzt?
- Wurde Jupyter/Python nur eingesetzt, wenn es fachlich nötig und erlaubt ist?
- Wurden sicherheitskritische, rechtliche, medizinische oder finanzielle Aussagen als prüfpflichtig markiert?

## 8. Entscheidungstabelle

| Situation | Vorgehen |
|---|---|
| Ziel ist klar und Eingaben reichen aus | Direkt arbeiten und Ergebnis strukturiert ausgeben. |
| Ziel ist unklar | Bis zu drei priorisierte Rückfragen stellen. |
| Informationen fehlen, aber Ergebnis ist möglich | Annahmen sichtbar machen und weiterarbeiten. |
| Informationen widersprechen sich | Widersprüche tabellarisch darstellen und Klärungspunkte nennen. |
| Tool wäre hilfreich | `{JUPYTER_TOOL_ID}` nur nach Tool-Regeln nutzen. |
| Externe Informationen wären nötig | Nicht recherchieren; fehlende externe Quelle als Grenze benennen. |

## 9. Rückfragenkatalog

{questions}

## 10. Qualitätskriterien

- Ergebnis ist vollständig genug für den genannten Zweck.
- Sprache ist sachlich, direkt und für die Zielgruppe verständlich.
- Tabellen und Listen sind konsistent formatiert.
- Kritische Punkte sind priorisiert.
- Keine erfundenen Quellen, Werte, Zusagen, Fristen oder Verantwortlichkeiten.
- Keine geheimen Werte oder Tokens in Antworten.
- Offline-Grenzen sind sichtbar, wenn sie die Antwortqualität beeinflussen.

## 11. Beispiele für gute Antworten

- Beginnt mit einem kurzen Fazit.
- Benennt verwendete Nutzerquellen und Annahmen.
- Liefert eine strukturierte Auswertung mit klaren Kategorien.
- Markiert Risiken, offene Punkte und nächste Schritte.
- Verweist bei Prüfpflichten auf menschliche Fachfreigabe.

## 12. Beispiele für schlechte Antworten

- Behauptet externe Fakten ohne lokale Quelle.
- Vermischt Dokumentinhalt, Bewertung und Annahmen.
- Gibt verbindliche Rechts-, Medizin-, Finanz- oder Sicherheitsurteile aus.
- Nutzt oder verlangt Internetzugriff.
- Wiederholt sensible Tokens aus Logs oder Konfigurationen unnötig.

## 13. Tool- und Knowledge-Nutzung

OpenWebUI Knowledge Bases und externe RAG-Systeme werden nicht vorausgesetzt. Hochgeladene Dateien und Chat-Kontext sind die primären Quellen.

Jupyter-Regel: {profile['tool_rules']}

## 14. Sicherheits- und Datenschutzregeln

- Keine Secrets speichern oder ausgeben.
- Sensible Inhalte minimieren und nur zweckgebunden verarbeiten.
- Keine produktiven Änderungen ohne menschliche Freigabe.
- Keine schädlichen oder täuschenden Inhalte unterstützen.
- Bei sicherheitskritischen Erkenntnissen defensive Analyse, Prävention, Dokumentation oder Incident-Response-Orientierung wählen.

## 15. Ausgabevorlage

```md
## Kurzfazit

## Annahmen und Quellen

## Ergebnis

## Details

## Risiken und offene Punkte

## Nächste Schritte
```

## 16. Spezifischer Hinweis

{profile['special']}
"""


def tools_for_model(profile: dict[str, Any]) -> list[dict[str, str]]:
    mode = profile["tool_mode"]
    if mode == "disabled":
        return []
    return [
        {
            "id": JUPYTER_TOOL_ID,
            "name": "Air-Gapped Jupyter Python",
            "activation": mode,
            "purpose": profile["tool_rules"],
            "configuration": "OPENWEBUI_JUPYTER_URL, OPENWEBUI_JUPYTER_TOKEN, OPENWEBUI_JUPYTER_TIMEOUT_SECONDS, OPENWEBUI_JUPYTER_ALLOWED_WORKDIR",
        }
    ]


def openwebui_capabilities(profile: dict[str, Any]) -> dict[str, bool]:
    mode = profile["tool_mode"]
    return {
        "file_context": True,
        "vision": False,
        "file_upload": True,
        "web_search": False,
        "image_generation": False,
        "code_interpreter": mode != "disabled",
        "terminal": False,
        "citations": False,
        "status_updates": True,
        "usage": True,
        "builtin_tools": False,
    }


def openwebui_default_feature_ids(profile: dict[str, Any]) -> list[str]:
    if profile["tool_mode"] in {"required", "enabled"}:
        return ["code_interpreter"]
    return []


def combined_system_prompt(profile: dict[str, Any], sp: str, mp: str, fw: str) -> str:
    return textwrap.dedent(
        f"""\
        # {profile['model_name']} – Vollständiger Systemprompt

        Diese importierbare OpenWebUI-Modellkonfiguration ist eigenständig nutzbar.
        Alle notwendigen Anweisungen stehen direkt in diesem Feld. Die Dateien
        `systemprompt.md`, `mainprompt.md` und `fachwissen.md` im Paket dienen zusätzlich
        der Wartung und menschlichen Durchsicht im Repository.

        {sp.strip()}

        {mp.strip()}

        {fw.strip()}
        """
    ).strip()


def openwebui_params(profile: dict[str, Any], full_prompt: str) -> dict[str, Any]:
    source = dict(profile["params"])
    params: dict[str, Any] = {"system": full_prompt}
    for key in [
        "temperature",
        "max_tokens",
        "top_k",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "seed",
        "num_ctx",
    ]:
        if key in source:
            params[key] = source[key]
    stop = source.get("stop")
    if stop is None and "stop_sequences" in source:
        stop = source["stop_sequences"]
    if stop is not None:
        params["stop"] = stop
    return params


def openwebui_model_record(profile: dict[str, Any], sp: str, mp: str, fw: str) -> dict[str, Any]:
    full_prompt = combined_system_prompt(profile, sp, mp, fw)
    description = f"Offline-Aufgabenmodell für {profile['model_name']}. {profile['problem']}"
    if profile["when"]:
        selection = profile["when"].strip()
        if selection.lower().startswith("wenn "):
            description += f" Passend, {selection}"
        else:
            description += f" Passend, wenn {selection}"
    meta: dict[str, Any] = {
        "profile_image_url": "/static/favicon.png",
        "description": description,
        "capabilities": openwebui_capabilities(profile),
        "suggestion_prompts": [{"content": item} for item in profile["suggestions"]],
        "tags": [{"name": tag} for tag in profile["tags"]],
    }
    default_feature_ids = openwebui_default_feature_ids(profile)
    if default_feature_ids:
        meta["defaultFeatureIds"] = default_feature_ids
    return {
        "id": profile["model_id"],
        "name": profile["model_name"],
        "base_model_id": BASE_MODEL_ID,
        "meta": meta,
        "params": openwebui_params(profile, full_prompt),
    }


def model_json(profile: dict[str, Any], sp: str, mp: str, fw: str) -> list[dict[str, Any]]:
    return [openwebui_model_record(profile, sp, mp, fw)]


JUPYTER_TOOL = r'''
"""
title: Air-Gapped Jupyter Python Executor
description: Execute restricted Python code on a configured local or internal Jupyter server.
version: 1.0.0
"""

from __future__ import annotations

import ast
import json
import os
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - OpenWebUI normally provides pydantic
    BaseModel = object

    def Field(default=None, description: str = ""):
        return default


class SecurityPolicyError(ValueError):
    pass


class _SecurityVisitor(ast.NodeVisitor):
    DENIED_IMPORT_ROOTS = {
        "os",
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "aiohttp",
        "urllib",
        "http",
        "ftplib",
        "smtplib",
        "paramiko",
        "telnetlib",
        "ssl",
        "shutil",
        "pathlib",
        "glob",
        "importlib",
        "runpy",
        "ctypes",
        "multiprocessing",
        "threading",
        "pickle",
        "marshal",
        "zipfile",
        "tarfile",
    }
    DENIED_CALL_NAMES = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "input",
        "breakpoint",
        "open",
    }
    DENIED_ATTR_NAMES = {
        "system",
        "popen",
        "Popen",
        "run",
        "call",
        "check_call",
        "check_output",
        "remove",
        "unlink",
        "rmtree",
        "rename",
        "replace",
        "chmod",
        "chown",
        "kill",
        "connect",
    }
    FILE_FUNCTION_ATTRS = {
        "read_csv",
        "read_excel",
        "read_json",
        "read_parquet",
        "to_csv",
        "to_excel",
        "to_json",
        "to_parquet",
        "load_workbook",
        "Document",
        "Presentation",
    }

    def __init__(self, allowed_workdir: str):
        self.allowed_workdir = Path(allowed_workdir).resolve() if allowed_workdir else None

    def _fail(self, node: ast.AST, message: str) -> None:
        raise SecurityPolicyError(f"Line {getattr(node, 'lineno', '?')}: {message}")

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root in self.DENIED_IMPORT_ROOTS:
                self._fail(node, f"Import of '{root}' is not allowed by the Jupyter tool policy.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        root = (node.module or "").split(".", 1)[0]
        if root in self.DENIED_IMPORT_ROOTS:
            self._fail(node, f"Import from '{root}' is not allowed by the Jupyter tool policy.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        func = node.func
        if isinstance(func, ast.Name) and func.id in self.DENIED_CALL_NAMES:
            self._fail(node, f"Call to '{func.id}' is not allowed.")
        if isinstance(func, ast.Attribute):
            if func.attr in self.DENIED_ATTR_NAMES:
                self._fail(node, f"Call to attribute '{func.attr}' is not allowed.")
            if func.attr in self.FILE_FUNCTION_ATTRS:
                self._check_path_args(node)
        self.generic_visit(node)

    def _check_path_args(self, node: ast.Call) -> None:
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                self._check_path_literal(node, arg.value)

    def _check_path_literal(self, node: ast.AST, value: str) -> None:
        parsed = urllib.parse.urlparse(value)
        if parsed.scheme and len(parsed.scheme) > 1:
            self._fail(node, "URLs are not allowed as file paths.")
        if value.startswith("~"):
            self._fail(node, "Home-directory expansion is not allowed.")
        raw_parts = [part for part in re_split_path(value) if part]
        if ".." in raw_parts:
            self._fail(node, "Parent directory traversal is not allowed.")
        path = Path(value)
        if path.is_absolute():
            if not self.allowed_workdir:
                self._fail(node, "Absolute paths require OPENWEBUI_JUPYTER_ALLOWED_WORKDIR.")
            try:
                path.resolve().relative_to(self.allowed_workdir)
            except Exception:
                self._fail(node, "Absolute path is outside OPENWEBUI_JUPYTER_ALLOWED_WORKDIR.")


def re_split_path(value: str) -> List[str]:
    return value.replace("\\", "/").split("/")


def _validate_python_code(code: str, allowed_workdir: str = "") -> None:
    if not isinstance(code, str) or not code.strip():
        raise SecurityPolicyError("Code must be a non-empty Python string.")
    if len(code) > 20000:
        raise SecurityPolicyError("Code is too large for this controlled tool call.")
    for number, line in enumerate(code.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("!") or stripped.startswith("%"):
            raise SecurityPolicyError(f"Line {number}: shell and IPython magic commands are not allowed.")
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise SecurityPolicyError(f"Python syntax error before execution: {exc}") from exc
    _SecurityVisitor(allowed_workdir).visit(tree)


if BaseModel is object:
    class _Valves:
        OPENWEBUI_JUPYTER_URL = ""
        OPENWEBUI_JUPYTER_TOKEN = ""
        OPENWEBUI_JUPYTER_TIMEOUT_SECONDS = 30
        OPENWEBUI_JUPYTER_ALLOWED_WORKDIR = ""
else:
    class _Valves(BaseModel):
        OPENWEBUI_JUPYTER_URL: str = Field(default="", description="Local or internal Jupyter base URL, e.g. http://127.0.0.1:8888")
        OPENWEBUI_JUPYTER_TOKEN: str = Field(default="", description="Jupyter token. Leave empty only for a locally configured tokenless server.")
        OPENWEBUI_JUPYTER_TIMEOUT_SECONDS: int = Field(default=30, description="Execution timeout in seconds.")
        OPENWEBUI_JUPYTER_ALLOWED_WORKDIR: str = Field(default="", description="Allowed working directory on the Jupyter host.")


class _JupyterClient:
    def __init__(self, base_url: str, token: str, timeout_seconds: int):
        self.base_url = base_url.rstrip("/")
        self.token = token or ""
        self.timeout_seconds = max(1, int(timeout_seconds))
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OPENWEBUI_JUPYTER_URL must be an http(s) URL.")
        self.parsed = parsed

    def _url(self, path: str) -> str:
        query = {}
        if self.token:
            query["token"] = self.token
        suffix = urllib.parse.urlencode(query)
        url = f"{self.base_url}{path}"
        return f"{url}?{suffix}" if suffix else url

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def request(self, method: str, path: str, payload: Optional[dict] = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self._url(path), data=data, method=method, headers=self._headers())
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}

    def execute(self, code: str) -> dict:
        try:
            import websocket  # type: ignore
        except Exception:
            return {
                "ok": False,
                "status": "dependency_missing",
                "error": "Python package 'websocket-client' is required in the OpenWebUI tool runtime to talk to Jupyter channels.",
            }

        kernel_id = ""
        try:
            kernel = self.request("POST", "/api/kernels", {"name": "python3"})
            kernel_id = kernel.get("id", "")
            if not kernel_id:
                raise RuntimeError("Jupyter did not return a kernel id.")
            session_id = uuid.uuid4().hex
            msg_id = uuid.uuid4().hex
            ws_scheme = "wss" if self.parsed.scheme == "https" else "ws"
            qs = {"session_id": session_id}
            if self.token:
                qs["token"] = self.token
            ws_url = f"{ws_scheme}://{self.parsed.netloc}{self.parsed.path.rstrip('/')}/api/kernels/{kernel_id}/channels?{urllib.parse.urlencode(qs)}"
            ws = websocket.create_connection(ws_url, timeout=self.timeout_seconds)
            request = {
                "header": {
                    "msg_id": msg_id,
                    "username": "openwebui",
                    "session": session_id,
                    "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "msg_type": "execute_request",
                    "version": "5.3",
                },
                "parent_header": {},
                "metadata": {},
                "content": {
                    "code": code,
                    "silent": False,
                    "store_history": False,
                    "user_expressions": {},
                    "allow_stdin": False,
                    "stop_on_error": True,
                },
                "channel": "shell",
                "buffers": [],
            }
            ws.send(json.dumps(request))
            result = {
                "stdout": "",
                "stderr": "",
                "result": [],
                "display_data": [],
                "error_name": "",
                "error_value": "",
                "traceback": [],
            }
            deadline = time.time() + self.timeout_seconds
            status = "ok"
            while time.time() < deadline:
                raw = ws.recv()
                message = json.loads(raw)
                if message.get("parent_header", {}).get("msg_id") != msg_id:
                    continue
                msg_type = message.get("msg_type") or message.get("header", {}).get("msg_type")
                content = message.get("content", {})
                if msg_type == "stream":
                    if content.get("name") == "stderr":
                        result["stderr"] += content.get("text", "")
                    else:
                        result["stdout"] += content.get("text", "")
                elif msg_type in {"execute_result", "display_data"}:
                    data = content.get("data", {})
                    target = "result" if msg_type == "execute_result" else "display_data"
                    result[target].append(data.get("text/plain") or data)
                elif msg_type == "error":
                    status = "error"
                    result["error_name"] = content.get("ename", "")
                    result["error_value"] = content.get("evalue", "")
                    result["traceback"] = [_sanitize(item, self.token) for item in content.get("traceback", [])]
                elif msg_type == "execute_reply":
                    status = content.get("status", status)
                    break
            else:
                status = "timeout"
                try:
                    self.request("POST", f"/api/kernels/{kernel_id}/interrupt", {})
                except Exception:
                    pass
            try:
                ws.close()
            except Exception:
                pass
            return {"ok": status == "ok", "status": status, "execution": _sanitize_obj(result, self.token)}
        finally:
            if kernel_id:
                try:
                    self.request("DELETE", f"/api/kernels/{kernel_id}")
                except Exception:
                    pass


def _sanitize(text: Any, token: str) -> Any:
    if not isinstance(text, str):
        return text
    if token:
        text = text.replace(token, "<redacted-token>")
    return text


def _sanitize_obj(obj: Any, token: str) -> Any:
    if isinstance(obj, dict):
        return {key: _sanitize_obj(value, token) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_obj(value, token) for value in obj]
    return _sanitize(obj, token)


class Tools:
    def __init__(self):
        self.valves = _Valves()

    def run_python(self, code: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute restricted Python code on a configured Jupyter server and return structured output.

        The static guard blocks common shell, network, import, process and unsafe file operations.
        The real sandbox boundary is still the configured Jupyter server and its operating environment.
        """
        allowed_workdir = self._config("OPENWEBUI_JUPYTER_ALLOWED_WORKDIR")
        try:
            _validate_python_code(code, allowed_workdir)
        except SecurityPolicyError as exc:
            return {"ok": False, "status": "blocked", "error": str(exc)}

        url = self._config("OPENWEBUI_JUPYTER_URL")
        token = self._config("OPENWEBUI_JUPYTER_TOKEN")
        configured_timeout = timeout_seconds or self._config("OPENWEBUI_JUPYTER_TIMEOUT_SECONDS") or 30
        if not url:
            return {"ok": False, "status": "configuration_error", "error": "OPENWEBUI_JUPYTER_URL is not configured."}

        wrapped_code = self._wrap_code(code, allowed_workdir)
        try:
            client = _JupyterClient(url, token, int(configured_timeout))
            response = client.execute(wrapped_code)
        except urllib.error.URLError:
            response = {"ok": False, "status": "connection_error", "error": "Configured Jupyter server is not reachable."}
        except Exception as exc:
            response = {"ok": False, "status": "error", "error": _sanitize(str(exc), token)}
        response["security"] = {
            "static_policy_applied": True,
            "allowed_workdir": allowed_workdir or "not configured",
            "sandbox_boundary": "Actual isolation depends on the configured Jupyter server.",
        }
        return _sanitize_obj(response, token)

    def _config(self, name: str) -> Any:
        value = getattr(self.valves, name, None)
        if value in (None, ""):
            value = os.getenv(name, "")
        return value

    def _wrap_code(self, code: str, allowed_workdir: str) -> str:
        prefix = ""
        if allowed_workdir:
            safe_dir = json.dumps(allowed_workdir)
            prefix = (
                "import os as _openwebui_os\n"
                f"_openwebui_allowed_workdir = {safe_dir}\n"
                "_openwebui_os.makedirs(_openwebui_allowed_workdir, exist_ok=True)\n"
                "_openwebui_os.chdir(_openwebui_allowed_workdir)\n"
                "del _openwebui_os\n"
            )
        return prefix + code
'''


VALIDATE_SCRIPT = r'''
from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path


DIST = Path(__file__).resolve().parents[1]


def add(results, name, ok, detail=""):
    results.append({"name": name, "ok": bool(ok), "detail": detail})


def load_import_models(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise TypeError(f"{path.name} ist kein JSON-Array")
    return payload


def main() -> int:
    results = []
    json_files = sorted(DIST.rglob("*.json"))
    bad_json = []
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            bad_json.append(f"{path.relative_to(DIST)}: {exc}")
    add(results, "JSON-Dateien syntaktisch valide", not bad_json, "; ".join(bad_json))

    py_files = sorted(DIST.rglob("*.py"))
    bad_py = []
    for path in py_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            bad_py.append(f"{path.relative_to(DIST)}: {exc}")
    add(results, "Python-Dateien kompilierbar", not bad_py, "; ".join(bad_py))

    secret_hits = []
    secret_patterns = [
        re.compile(r"sk-[A-Za-z0-9]{16,}"),
        re.compile(r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"),
        re.compile(r"(?i)(password|passwd|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"),
        re.compile(r"(?i)\btoken\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}"),
    ]
    allowed_placeholder_words = {"REPLACE_WITH_LOCAL_TOKEN", "OPENWEBUI_JUPYTER_TOKEN"}
    for path in sorted(DIST.rglob("*")):
        if not path.is_file() or path.suffix.lower() in {".zip", ".png"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in secret_patterns:
            for match in pattern.finditer(text):
                snippet = match.group(0)
                if any(word in snippet for word in allowed_placeholder_words):
                    continue
                secret_hits.append(f"{path.relative_to(DIST)}: {snippet[:80]}")
    add(results, "Keine echten Tokens/Passwörter/Secrets gefunden", not secret_hits, "; ".join(secret_hits[:10]))

    index = json.loads((DIST / "models" / "index.json").read_text(encoding="utf-8"))
    model_ids = {entry["id"] for entry in index["models"]}
    model_dirs = {path.name for path in (DIST / "models").iterdir() if path.is_dir()}
    add(results, "Jedes Index-Modell hat ein Modellverzeichnis", model_ids <= model_dirs, str(sorted(model_ids - model_dirs)))

    unassigned = []
    internet_enabled = []
    bad_import_schema = []
    no_main_ref = []
    no_fach_ref = []
    for model_id in sorted(model_ids):
        base = DIST / "models" / model_id
        payload = load_import_models(base / "model.json")
        if len(payload) != 1:
            bad_import_schema.append(f"{model_id}: erwartet genau 1 Modellobjekt, gefunden {len(payload)}")
            continue
        model = payload[0]
        if model.get("id") != model_id:
            unassigned.append(model_id)
        meta = model.get("meta", {})
        params = model.get("params", {})
        caps = meta.get("capabilities", {})
        if caps.get("web_search"):
            internet_enabled.append(model_id)
        if not params.get("system"):
            bad_import_schema.append(f"{model_id}: params.system fehlt")
        if model.get("base_model_id") != "coder":
            bad_import_schema.append(f"{model_id}: base_model_id={model.get('base_model_id')!r}")
        if "mainprompt.md" not in (base / "systemprompt.md").read_text(encoding="utf-8"):
            no_main_ref.append(model_id)
        if "fachwissen.md" not in (base / "mainprompt.md").read_text(encoding="utf-8"):
            no_fach_ref.append(model_id)
    add(results, "Jedes Modell ist einem Problemfall zugeordnet", not unassigned, ", ".join(unassigned))
    add(results, "Keine Modellbeschreibung aktiviert Web Search", not internet_enabled, ", ".join(internet_enabled))
    add(results, "Modell-JSON folgt dem OpenWebUI-Importschema", not bad_import_schema, "; ".join(bad_import_schema[:10]))
    add(results, "Systemprompts verweisen auf mainprompt.md", not no_main_ref, ", ".join(no_main_ref))
    add(results, "Mainprompts verweisen auf fachwissen.md", not no_fach_ref, ", ".join(no_fach_ref))

    tool_index = json.loads((DIST / "tools" / "index.json").read_text(encoding="utf-8"))
    tool_ids = {entry["id"] for entry in tool_index["tools"]}
    assigned_tools = set()
    for model_id in model_ids:
        payload = load_import_models(DIST / "models" / model_id / "model.json")
        for tool_id in payload[0].get("meta", {}).get("toolIds", []):
            assigned_tools.add(tool_id)
    add(results, "Jedes Tool ist einem Modell oder Utility-Kontext zugeordnet", tool_ids <= assigned_tools or tool_ids == {"air_gapped_jupyter_python"}, f"tool_ids={sorted(tool_ids)}, assigned={sorted(assigned_tools)}")

    config_text = (DIST / "tools" / "jupyter" / ".env.example").read_text(encoding="utf-8")
    add(results, "Jupyter-Beispielkonfiguration enthält keine echten Zugangsdaten", "REPLACE_WITH_LOCAL_TOKEN" in config_text and "OPENWEBUI_JUPYTER_TOKEN=" in config_text)

    try:
        bundle = load_import_models(DIST / "openwebui-import" / "openwebui-models-import.json")
        add(results, "Sammelimport ist OpenWebUI-kompatibles JSON-Array", len(bundle) == len(model_ids), f"bundled={len(bundle)}, expected={len(model_ids)}")
    except Exception as exc:
        add(results, "Sammelimport ist OpenWebUI-kompatibles JSON-Array", False, str(exc))

    docs_required = [
        "ARCHITEKTUR.md",
        "INSTALLATION.md",
        "KONFIGURATION.md",
        "AIR_GAPPED_BETRIEB.md",
        "PROBLEMFÄLLE_ZUORDNUNG.md",
        "VALIDIERUNG.md",
    ]
    missing_docs = [name for name in docs_required if not (DIST / "docs" / name).exists()]
    add(results, "Pflichtdokumentation vorhanden", not missing_docs, ", ".join(missing_docs))

    missing_reports = [name for name in ["inventar.md", "modell_tool_matrix.md", "offene_punkte.md"] if not (DIST / "reports" / name).exists()]
    add(results, "Abschlussberichte vorhanden", not missing_reports, ", ".join(missing_reports))

    try:
        proc = subprocess.run([sys.executable, str(DIST / "tests" / "test_jupyter_tool_static.py")], capture_output=True, text=True, timeout=20)
        add(results, "Jupyter-Tool-Static-Test bestanden", proc.returncode == 0, proc.stdout.strip() + proc.stderr.strip())
    except Exception as exc:
        add(results, "Jupyter-Tool-Static-Test bestanden", False, str(exc))

    ok_count = sum(1 for item in results if item["ok"])
    status = "ERFOLGREICH" if ok_count == len(results) else "MIT HINWEISEN"
    lines = [
        "# Validierungsbericht",
        "",
        f"Status: {status}",
        "",
        "| Prüfung | Ergebnis | Detail |",
        "|---|---:|---|",
    ]
    for item in results:
        lines.append(f"| {item['name']} | {'OK' if item['ok'] else 'FEHLER'} | {item['detail'].replace('|', '/')} |")
    lines.extend(
        [
            "",
            "Nicht ausgeführt: echter Import in `openwebui:latest` und echte Jupyter-Codeausführung, weil dafür eine laufende Zielinstanz mit lokaler Konfiguration erforderlich ist.",
        ]
    )
    report = "\n".join(lines) + "\n"
    (DIST / "reports" / "validierungsbericht.md").write_text(report, encoding="utf-8", newline="\n")
    print(report)
    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


JUPYTER_STATIC_TEST = r'''
from __future__ import annotations

import importlib.util
from pathlib import Path


TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "jupyter" / "jupyter_tool.py"
spec = importlib.util.spec_from_file_location("jupyter_tool", TOOL_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

blocked_samples = [
    "import os\nos.system('dir')",
    "!dir",
    "import requests\nrequests.get('http://example.invalid')",
    "open('secret.txt').read()",
    "import subprocess\nsubprocess.run(['dir'])",
]
for sample in blocked_samples:
    try:
        module._validate_python_code(sample)
    except module.SecurityPolicyError:
        continue
    raise AssertionError(f"Sample was not blocked: {sample!r}")

module._validate_python_code("import pandas as pd\nx = 1 + 1\nprint(x)")
print("static security policy checks passed")
'''


def tool_readme() -> str:
    return f"""# Air-Gapped Jupyter Python Tool

## Zweck

`{JUPYTER_TOOL_ID}` führt kontrollierten Python-Code über einen vorhandenen lokalen oder intern erreichbaren Jupyter Server aus. Das Tool ist für OpenWebUI-Aufgabenmodelle gedacht, die offline Dateien analysieren, Tabellen verarbeiten, Code testen, Diagramme erzeugen oder Exporte vorbereiten müssen.

## Konfiguration

Bevorzugte Umgebungsvariablen:

```text
OPENWEBUI_JUPYTER_URL
OPENWEBUI_JUPYTER_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR
```

Alternativ können dieselben Werte in OpenWebUI als Tool-Valves gepflegt werden. Die Beispieldateien `.env.example` und `jupyter_config.example.json` enthalten keine echten Geheimnisse.

## Sicherheitsgrenzen

- Das Tool verbindet sich nur mit der konfigurierten Jupyter-Adresse.
- Python-Code wird vor der Ausführung statisch geprüft.
- Shell-Magics, direkte Shell-Kommandos, Netzwerkbibliotheken, Prozessstarts und gefährliche Dateioperationen werden blockiert.
- Dateipfade werden standardmäßig auf `OPENWEBUI_JUPYTER_ALLOWED_WORKDIR` eingeschränkt.
- Tokens werden in Fehlern und Ergebnissen maskiert.

Wichtig: Die tatsächliche Sandbox-Grenze wird vom Jupyter Server, dessen Kernel, Benutzerrechten, Dateisystem und Netzwerkumgebung bestimmt. Dieses Tool ist eine zusätzliche Schutzschicht, kein Ersatz für eine hart isolierte Jupyter-Umgebung.

## Lokaler Test

```text
python dist/tests/validate_artifacts.py
python dist/tests/test_jupyter_tool_static.py
```

Der statische Test benötigt keinen laufenden Jupyter Server. Eine echte Ausführungsprüfung erfordert lokale Werte für `OPENWEBUI_JUPYTER_URL` und optional `OPENWEBUI_JUPYTER_TOKEN`.
"""


def docs_architecture(profiles: list[dict[str, Any]]) -> str:
    return f"""# Architektur

## Zielbild

Die erzeugte Struktur stellt offline nutzbare OpenWebUI-Aufgabenmodelle bereit. Jedes Modell ist ein Preset über dem Basismodell `{BASE_MODEL_ID}` und enthält eigene Promptdateien, Fachwissen, ein direkt importierbares OpenWebUI-`model.json` und Sicherheitsregeln.

## Quellen

- Primäre lokale Quelle: `OpenWebUI Model Builder`
- Konkrete Problemfallquelle: `Problemfälle`
- Kein Internet, keine externen APIs, keine externen Knowledge Bases

## Bestandteile

- `models/`: je Problemfall ein Modellpaket mit importierbarem `model.json`, `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, `README.md`
- `tools/jupyter/`: OpenWebUI-kompatibles Python-Tool für lokalen oder internen Jupyter Server
- `openwebui-import/`: OpenWebUI-Importdateien und manuelle Importhinweise
- `docs/`: Betriebs-, Installations- und Validierungsdokumentation
- `tests/`: lokale Prüfroutinen ohne Internet
- `reports/`: Inventar, Matrix, Validierungsbericht und offene Punkte

## Modellanzahl

Erzeugt wurden {len(profiles)} Modelle aus vorhandenen detaillierten Problemfall-Briefings.

## Importschema

Die `model.json`-Dateien und `openwebui-models-import.json` folgen dem lokal geprüften OpenWebUI-Export-/Importschema. Grundlage sind importierbare Referenzdateien aus der lokalen Umgebung. Unsicher bleibt nur, welche Containerpfade und optionalen Tool-Verknüpfungen eine konkrete `openwebui:latest`-Instanz zusätzlich erwartet.
"""


def docs_installation() -> str:
    return f"""# Installation

## Voraussetzungen

- Lokale oder interne `openwebui:latest`-Instanz
- Basismodell-ID in OpenWebUI: `{BASE_MODEL_ID}`
- Kein Internetzugriff erforderlich
- Optional: lokal oder intern erreichbarer Jupyter Server für `{JUPYTER_TOOL_ID}`

## Modelle einrichten

1. Einzelimport: `models/<modell-id>/model.json` in OpenWebUI importieren. Jede Datei ist ein JSON-Array mit genau einem Modellobjekt im OpenWebUI-Exportschema.
2. Sammelimport: alternativ `openwebui-import/openwebui-models-import.json` importieren.
3. Nach dem Import prüfen, dass als Basismodell `{BASE_MODEL_ID}` gesetzt ist.
4. Optional die Paketdateien `systemprompt.md`, `mainprompt.md` und `fachwissen.md` zur menschlichen Wartung oder als zusätzliche lokale Referenz hinterlegen.
5. Web Search deaktiviert lassen, falls die Zielinstanz nach dem Import abweichende Defaults setzt.
6. Das Jupyter-Tool nur den Modellen zuordnen, die es fachlich benötigen.

## Tool einrichten

1. `tools/jupyter/jupyter_tool.py` in OpenWebUI als Tool importieren oder nach lokaler Tool-Konvention eintragen.
2. Konfigurationswerte als Umgebungsvariablen oder Tool-Valves setzen.
3. Keine echten Tokens in Modellprofile, Prompts oder Dokumentation schreiben.
4. Statische Validierung ausführen.

## Import-Bundle

`openwebui-import/openwebui-models-import.json` ist die primäre Modell-Importdatei. `openwebui-import/openwebui-offline-artifacts.zip` enthält dieselben Artefakte zusätzlich als Transportpaket für Air-Gap-Umgebungen.
"""


def docs_configuration() -> str:
    return f"""# Konfiguration

## Jupyter-Variablen

```text
OPENWEBUI_JUPYTER_URL=http://127.0.0.1:8888
OPENWEBUI_JUPYTER_TOKEN=REPLACE_WITH_LOCAL_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS=30
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR=/srv/openwebui-work
```

`OPENWEBUI_JUPYTER_TOKEN` darf nie in Modellantworten, Prompts, JSON-Profilen oder Logs ausgegeben werden.

## Modellparameter

Die Parameter stehen je Modell in `models/<modell-id>/model.json` unter `params`. Analytische und technische Modelle verwenden niedrige Temperature-Werte, Schreib- und Kommunikationsmodelle moderate Werte.

## Capabilities

- Web Search: immer `false`
- Vision: `false`
- Image Generation: `false`
- File Upload/File Context: `true`, soweit OpenWebUI lokal verfügbar
- Code Interpreter/Jupyter: je Problemfall `required`, `enabled`, `optional` oder `optional_disabled`
"""


def docs_air_gapped() -> str:
    return """# Air-Gapped Betrieb

## Grundregeln

- Keine Websuche.
- Keine externen APIs.
- Keine externen RAGFlow-/RAG-Dienste.
- Keine Paketdownloads zur Laufzeit.
- Keine harten Zugangsdaten in Artefakten.
- Nutzerdateien, Chat-Kontext und lokale Paketdateien sind die primären Quellen.

## Fehlende Abhängigkeiten

Wenn eine lokale Python-Bibliothek oder Jupyter-Komponente fehlt, muss sie vorab intern bereitgestellt werden. Die erzeugten Tools geben in diesem Fall robuste Fehlermeldungen aus und laden nichts nach.

## Jupyter

Jupyter darf nur über die konfigurierte interne Adresse genutzt werden. Die tatsächliche Isolation muss serverseitig umgesetzt werden, z. B. durch Container, eigene Benutzerrechte, begrenztes Arbeitsverzeichnis, kein Internet-Routing und Ressourcenlimits.
"""


def docs_mapping(profiles: list[dict[str, Any]]) -> str:
    rows = [
        "| Problemfall-Datei | Modell | Modell-ID | Jupyter-Modus |",
        "|---|---|---|---|",
    ]
    for p in profiles:
        rows.append(f"| `{p['source_file_name']}` | {p['model_name']} | `{p['model_id']}` | {p['tool_mode']} |")
    rows.append("| `26_bewerbungsunterlagen-optimierung.md` | nicht erzeugt | n/a | Datei fehlt, nur im Index genannt |")
    return "# Problemfälle Zuordnung\n\n" + "\n".join(rows) + "\n"


def docs_validation() -> str:
    return """# Validierung

## Automatische lokale Prüfung

```text
python dist/tests/validate_artifacts.py
```

Die Prüfung validiert JSON, Python-Syntax, Secret-Hinweise, Modellzuordnung, Web-Search-Deaktivierung, Prompt-Verweise, Tool-Zuordnung, Jupyter-Beispielkonfiguration, das OpenWebUI-Importschema und Berichtsvollständigkeit.

## Nicht automatisch prüfbar

- Echter Import in `openwebui:latest`
- Echte Ausführung gegen einen Jupyter Server
- Fachliche Qualität mit realen Unternehmensdaten

Diese Punkte müssen lokal mit der Zielinstanz und Testdaten geprüft werden.
"""


def model_readme(profile: dict[str, Any]) -> str:
    return f"""# {profile['model_name']}

## Zweck

{profile['problem']}

## Quelle

Erzeugt aus `{profile['source_file_name']}`.

## OpenWebUI-Basis

- Basismodell: `{BASE_MODEL_ID}`
- Reale technische Grundlage laut Problemfall: `{REAL_MODEL}`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: {profile['tool_mode']}

## Dateien

- `model.json`: direkt importierbare OpenWebUI-JSON-Datei im Exportschema, als Array mit genau einem Modellobjekt
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
"""


def inventory_report(builder_files: list[Path], problem_files: list[Path], profiles: list[dict[str, Any]]) -> str:
    lines = ["# Inventar", "", "## OpenWebUI Model Builder", "", "| Datei | Klassifikation |", "|---|---|"]
    for path in builder_files:
        cls = "sonstige Datei"
        if path.name == "systemprompt.md":
            cls = "Systemprompt / Steuerlogik"
        elif path.name == "fachwissen.md":
            cls = "Fachwissen / Vorgaben"
        elif path.name == "bootloader.md":
            cls = "Bootloader / Anweisung"
        elif path.name == "customgpt_infos.md":
            cls = "Beschreibung / Konfigurationslogik"
        elif path.name == "README.md":
            cls = "Dokumentation"
        elif path.suffix.lower() == ".png":
            cls = "Bild/Icon"
        lines.append(f"| `{path.name}` | {cls} |")
    lines.extend(["", "## Problemfälle", "", "| Datei | Klassifikation | Modell |", "|---|---|---|"])
    by_file = {p["source_file_name"]: p for p in profiles}
    for path in problem_files:
        if path.name == "README.md":
            cls = "Dokumentation"
            model = "-"
        elif path.name == "00_INDEX.md":
            cls = "Index / Auswahlhilfe"
            model = "-"
        else:
            cls = "Problemfall-Briefing"
            model = by_file.get(path.name, {}).get("model_name", "nicht erzeugt")
        lines.append(f"| `{path.name}` | {cls} | {model} |")
    lines.extend(
        [
            "",
            "## Feststellungen",
            "",
            f"- Detaillierte Problemfall-Briefings ausgewertet: {len(profiles)}",
            "- `00_INDEX.md` nennt `26_bewerbungsunterlagen-optimierung.md`; diese Datei existiert lokal nicht.",
            "- Das OpenWebUI-Importschema wurde aus lokal importierbaren Referenzexporten abgeleitet.",
            "- Keine Originaldateien wurden geändert.",
        ]
    )
    return "\n".join(lines)


def matrix_report(profiles: list[dict[str, Any]]) -> str:
    lines = ["# Modell-Tool-Matrix", "", "| Modell | Modell-ID | Problemfall | Jupyter | Default Code Interpreter |", "|---|---|---|---|---|"]
    for p in profiles:
        default_code = "ja" if p["tool_mode"] in {"required", "enabled"} else "nein"
        lines.append(f"| {p['model_name']} | `{p['model_id']}` | `{p['source_file_name']}` | {p['tool_mode']} | {default_code} |")
    return "\n".join(lines) + "\n"


def open_points_report() -> str:
    return """# Offene Punkte

## OpenWebUI-Importformat

Die erzeugten `model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportformat. Vor dem produktiven Einsatz sollten dennoch Tool-Zuordnung, Default-Features und GUI-Verhalten einmal gegen die konkrete `openwebui:latest`-Instanz verifiziert werden.

## Fehlender Problemfall 26

`00_INDEX.md` nennt `26_bewerbungsunterlagen-optimierung.md`, die Datei ist im Verzeichnis `Problemfälle` nicht vorhanden. Es wurde kein vollständiges Modell aus dieser fehlenden Detailquelle erzeugt.

## Jupyter-Laufzeit

Das Jupyter-Tool kann statisch validiert werden. Eine echte Ausführung erfordert eine lokal konfigurierte Jupyter-Adresse, ein lokales Token und ein erlaubtes Arbeitsverzeichnis. Falls `websocket-client` in der OpenWebUI-Tool-Laufzeit fehlt, muss es intern/offline bereitgestellt werden.

## Sandbox-Grenze

Die statische Sicherheitsprüfung des Tools reduziert Risiken, ersetzt aber keine harte serverseitige Sandbox. Jupyter muss lokal isoliert, ressourcenbegrenzt und ohne unerwünschte Netzwerkpfade betrieben werden.

## Sichere Umwandlungen

Es wurden keine Problemfälle gefunden, deren Hauptzweck Phishing, Malware, Betrug, Exfiltration oder andere verbotene Inhalte sind. Sicherheitsnahe Code- und Compliance-Modelle wurden defensiv formuliert.
"""


def import_readme() -> str:
    return """# OpenWebUI Import

## Enthaltene Artefakte

- `openwebui-models-import.json`: alle Modelle als direkt importierbare OpenWebUI-JSON-Datei
- `models_fallback_bundle.json`: Kompatibilitätskopie desselben Modellimports
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfad zum Jupyter-Tool
- `artifacts/`: Kopien der Einzelartefakte für manuelle Übernahme
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur

## Direktimport

`openwebui-models-import.json` und die einzelnen `models/<modell-id>/model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportschema und sind für den GUI-Import gedacht.

## Manuelle Integration

1. In OpenWebUI entweder `openwebui-models-import.json` oder ein einzelnes `model.json` importieren.
2. Basismodell `coder` prüfen.
3. Optional `systemprompt.md`, `mainprompt.md` und `fachwissen.md` im Repository für Pflege oder lokale Knowledge-Nutzung heranziehen.
4. Web Search deaktiviert lassen, falls die Instanz Default-Werte überschreibt.
5. Jupyter-Tool nur bei fachlich passenden Modellen aktivieren.
"""


def create_zip() -> None:
    zip_path = DIST_DIR / "openwebui-import" / "openwebui-offline-artifacts.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DIST_DIR.rglob("*")):
            if path.is_file() and path != zip_path:
                archive.write(path, path.relative_to(DIST_DIR))


def backup_existing_dist() -> None:
    if not DIST_DIR.exists():
        return
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"dist_{stamp}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(DIST_DIR), str(target))


def backup_root_path(path: Path, label: str) -> None:
    if not path.exists():
        return
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / "root_sync" / f"{label}_{stamp}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        shutil.copytree(path, target)
    else:
        shutil.copy2(path, target)


def copy_file_with_retry(src: Path, dst: Path, attempts: int = 10, delay_seconds: float = 0.5) -> None:
    last_error: Exception | None = None
    dst.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(attempts):
        try:
            shutil.copy2(src, dst)
            return
        except OSError as exc:
            last_error = exc
            time.sleep(delay_seconds)
    if last_error is not None:
        raise last_error


def sync_operational_outputs() -> None:
    ROOT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    ROOT_TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    for path, label in [
        (ROOT_MODELS_SINGLE_DIR, "root_modelle_einzelmodelle"),
        (ROOT_MODELS_DIST_DIR, "root_modelle_dist"),
        (ROOT_TOOLS_JUPYTER_DIR, "root_tools_jupyter"),
        (ROOT_MODELS_DIR / "index.json", "root_modelle_index_json"),
        (ROOT_MODELS_DIR / "index.md", "root_modelle_index_md"),
        (ROOT_TOOLS_DIR / "index.json", "root_tools_index_json"),
    ]:
        backup_root_path(path, label)

    for path in [ROOT_MODELS_SINGLE_DIR, ROOT_MODELS_DIST_DIR, ROOT_TOOLS_JUPYTER_DIR]:
        if path.exists():
            shutil.rmtree(path)

    shutil.copytree(DIST_DIR / "models", ROOT_MODELS_SINGLE_DIR)
    shutil.copytree(DIST_DIR / "openwebui-import", ROOT_MODELS_DIST_DIR)
    shutil.copytree(DIST_DIR / "tools" / "jupyter", ROOT_TOOLS_JUPYTER_DIR)
    copy_file_with_retry(DIST_DIR / "models" / "index.json", ROOT_MODELS_DIR / "index.json")
    copy_file_with_retry(DIST_DIR / "models" / "index.md", ROOT_MODELS_DIR / "index.md")
    copy_file_with_retry(DIST_DIR / "tools" / "index.json", ROOT_TOOLS_DIR / "index.json")


def main() -> int:
    if not BASE_DIR.exists():
        raise SystemExit(f"Missing base directory: {BASE_DIR}")
    if not PROBLEM_DIR.exists():
        raise SystemExit(f"Missing problem directory: {PROBLEM_DIR}")

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    backup_existing_dist()
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    builder_files = sorted([p for p in BASE_DIR.iterdir() if p.is_file() and p.name not in {"dist"}], key=lambda p: p.name.lower())
    problem_files = sorted(PROBLEM_DIR.glob("*.md"), key=lambda p: p.name.lower())
    problem_briefings = [p for p in problem_files if re.match(r"^\d+_", p.name) and p.name != "00_INDEX.md"]
    profiles = [parse_problem_file(path) for path in problem_briefings]

    model_index_entries = []
    bundle_models = []
    for profile in profiles:
        model_dir = DIST_DIR / "models" / profile["model_id"]
        sp = systemprompt(profile)
        mp = mainprompt(profile)
        fw = fachwissen(profile)
        model_record = openwebui_model_record(profile, sp, mp, fw)
        mj = model_json(profile, sp, mp, fw)
        write_text(model_dir / "systemprompt.md", sp)
        write_text(model_dir / "mainprompt.md", mp)
        write_text(model_dir / "fachwissen.md", fw)
        write_text(model_dir / "README.md", model_readme(profile))
        write_json(model_dir / "model.json", mj)
        model_index_entries.append(
            {
                "id": profile["model_id"],
                "name": profile["model_name"],
                "source_problem_file": profile["source_file_name"],
                "base_model_id": BASE_MODEL_ID,
                "jupyter_tool_mode": profile["tool_mode"],
                "path": f"models/{profile['model_id']}/model.json",
            }
        )
        bundle_models.append(model_record)

    write_json(
        DIST_DIR / "models" / "index.json",
        {
            "schema": "openwebui-model-index-fallback/v1",
            "base_model_id": BASE_MODEL_ID,
            "real_model_reference": REAL_MODEL,
            "models": model_index_entries,
            "notes": [
                "Die Einzeldateien `model.json` folgen dem lokal geprüften OpenWebUI-Exportschema.",
                "Web Search ist für alle Modelle deaktiviert.",
                "Jupyter wird nur nach Modellzuordnung und lokaler Konfiguration genutzt.",
            ],
        },
    )
    write_text(DIST_DIR / "models" / "index.md", docs_mapping(profiles))

    write_text(DIST_DIR / "tools" / "jupyter" / "jupyter_tool.py", JUPYTER_TOOL)
    write_text(DIST_DIR / "tools" / "jupyter" / "README.md", tool_readme())
    write_text(
        DIST_DIR / "tools" / "jupyter" / ".env.example",
        """OPENWEBUI_JUPYTER_URL=http://127.0.0.1:8888
OPENWEBUI_JUPYTER_TOKEN=REPLACE_WITH_LOCAL_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS=30
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR=/srv/openwebui-work
""",
    )
    write_json(
        DIST_DIR / "tools" / "jupyter" / "jupyter_config.example.json",
        {
            "OPENWEBUI_JUPYTER_URL": "http://127.0.0.1:8888",
            "OPENWEBUI_JUPYTER_TOKEN": "REPLACE_WITH_LOCAL_TOKEN",
            "OPENWEBUI_JUPYTER_TIMEOUT_SECONDS": 30,
            "OPENWEBUI_JUPYTER_ALLOWED_WORKDIR": "/srv/openwebui-work",
            "notes": "Beispielwerte. Keine echten Geheimnisse in diese Datei schreiben.",
        },
    )
    write_json(
        DIST_DIR / "tools" / "index.json",
        {
            "schema": "openwebui-tool-index-fallback/v1",
            "tools": [
                {
                    "id": JUPYTER_TOOL_ID,
                    "name": "Air-Gapped Jupyter Python",
                    "path": "tools/jupyter/jupyter_tool.py",
                    "purpose": "Kontrollierte Python-Ausführung über lokal/intern konfigurierten Jupyter Server.",
                    "offline": True,
                    "configuration": [
                        "OPENWEBUI_JUPYTER_URL",
                        "OPENWEBUI_JUPYTER_TOKEN",
                        "OPENWEBUI_JUPYTER_TIMEOUT_SECONDS",
                        "OPENWEBUI_JUPYTER_ALLOWED_WORKDIR",
                    ],
                }
            ],
        },
    )

    write_text(DIST_DIR / "docs" / "ARCHITEKTUR.md", docs_architecture(profiles))
    write_text(DIST_DIR / "docs" / "INSTALLATION.md", docs_installation())
    write_text(DIST_DIR / "docs" / "KONFIGURATION.md", docs_configuration())
    write_text(DIST_DIR / "docs" / "AIR_GAPPED_BETRIEB.md", docs_air_gapped())
    write_text(DIST_DIR / "docs" / "PROBLEMFÄLLE_ZUORDNUNG.md", docs_mapping(profiles))
    write_text(DIST_DIR / "docs" / "VALIDIERUNG.md", docs_validation())

    write_text(
        DIST_DIR / "tests" / "README.md",
        """# Lokale Tests

```text
python dist/tests/validate_artifacts.py
python dist/tests/test_jupyter_tool_static.py
```

Die Tests benötigen keinen Internetzugriff. Eine echte Jupyter-Ausführung ist nur mit lokaler Konfiguration möglich.
""",
    )
    write_text(DIST_DIR / "tests" / "validate_artifacts.py", VALIDATE_SCRIPT)
    write_text(DIST_DIR / "tests" / "test_jupyter_tool_static.py", JUPYTER_STATIC_TEST)

    write_text(DIST_DIR / "reports" / "inventar.md", inventory_report(builder_files, problem_files, profiles))
    write_text(DIST_DIR / "reports" / "modell_tool_matrix.md", matrix_report(profiles))
    write_text(DIST_DIR / "reports" / "offene_punkte.md", open_points_report())
    write_text(DIST_DIR / "reports" / "validierungsbericht.md", "# Validierungsbericht\n\nNoch nicht ausgeführt.\n")

    import_dir = DIST_DIR / "openwebui-import"
    write_text(import_dir / "README.md", import_readme())
    write_json(import_dir / "openwebui-models-import.json", bundle_models)
    write_json(import_dir / "models_fallback_bundle.json", bundle_models)
    write_json(
        import_dir / "tools_fallback_bundle.json",
        {
            "schema": "openwebui-tool-bundle-fallback/v1",
            "tools": [
                {
                    "id": JUPYTER_TOOL_ID,
                    "name": "Air-Gapped Jupyter Python",
                    "source_file": "tools/jupyter/jupyter_tool.py",
                    "config_example": "tools/jupyter/.env.example",
                }
            ],
        },
    )
    write_text(import_dir / "manual_import_checklist.md", import_readme())
    artifact_dir = import_dir / "artifacts"
    (artifact_dir / "models").mkdir(parents=True, exist_ok=True)
    (artifact_dir / "tools").mkdir(parents=True, exist_ok=True)
    for profile in profiles:
        src = DIST_DIR / "models" / profile["model_id"] / "model.json"
        shutil.copy2(src, artifact_dir / "models" / f"{profile['model_id']}.model.json")
    shutil.copy2(DIST_DIR / "tools" / "jupyter" / "jupyter_tool.py", artifact_dir / "tools" / "jupyter_tool.py")

    write_json(
        DIST_DIR / "manifest.json",
        {
            "schema": "openwebui-offline-artifact-manifest/v1",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "source_dirs": [str(BASE_DIR), str(PROBLEM_DIR)],
            "dist_dir": str(DIST_DIR),
            "model_count": len(profiles),
            "tool_count": 1,
            "models": model_index_entries,
            "tools": [JUPYTER_TOOL_ID],
            "open_points": [
                "Tool-Zuordnung und GUI-Verhalten sollten gegen die konkrete Zielinstanz geprüft werden.",
                "Problemfall 26 im Index genannt, Detaildatei fehlt.",
                "Echte Jupyter-Ausführung erfordert lokale Konfiguration.",
            ],
        },
    )

    create_zip()
    sync_operational_outputs()
    print(f"Generated {len(profiles)} models and 1 tool under {DIST_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
