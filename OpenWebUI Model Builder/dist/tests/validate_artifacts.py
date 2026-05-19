
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
