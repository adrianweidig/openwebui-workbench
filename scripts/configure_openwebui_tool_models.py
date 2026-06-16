from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dist_zip_manifest import zip_drift_issues


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = Path(__file__).with_name("openwebui_workspace_config.yaml")
CONFIG_EXAMPLE = Path(__file__).with_name("openwebui_workspace_config.example.yaml")

TOOLS_INDEX = ROOT / "Tools" / "index.json"
TOOLS_DIST = ROOT / "Tools" / "dist"
IMPORT_SCRIPT = ROOT / "Tools" / "import_openwebui_workspace.py"
TOOL_REGISTRY = TOOLS_DIST / "openwebui-tool-registry.json"
TOOL_IMPORT = TOOLS_DIST / "openwebui-tools-import.json"
OFFLINE_TOOL_IMPORT = TOOLS_DIST / "openwebui-tools-offline-import.json"
FUNCTION_REGISTRY = TOOLS_DIST / "openwebui-function-registry.json"
FUNCTION_IMPORT = TOOLS_DIST / "openwebui-functions-import.json"
SKILLS_DIR = ROOT / "Tools" / "openwebui_ext" / "skills"
PROMPTS_DIR = ROOT / "Tools" / "openwebui_ext" / "prompts"
PROMPT_REGISTRY = TOOLS_DIST / "openwebui-prompt-registry.json"
PROMPT_IMPORT = TOOLS_DIST / "openwebui-prompts-import.json"
MODEL_DIST = ROOT / "Modelle" / "dist"
REGISTRATION_PLAN = MODEL_DIST / "openwebui-registration-plan.json"
TOOLS_FALLBACK_BUNDLE = MODEL_DIST / "tools_fallback_bundle.json"
FUNCTIONS_FALLBACK_BUNDLE = MODEL_DIST / "functions_fallback_bundle.json"
MODEL_IMPORT = MODEL_DIST / "openwebui-models-import.json"
MODEL_FALLBACK = MODEL_DIST / "models_fallback_bundle.json"
MODEL_PARAMS_SUMMARY = MODEL_DIST / "openwebui-model-params-summary.json"
MODEL_ARTIFACTS = MODEL_DIST / "artifacts" / "models"
MODEL_EXAMPLE_ARTIFACTS = MODEL_DIST / "artifacts" / "examples"
MODEL_I18N_ARTIFACTS = MODEL_DIST / "artifacts" / "i18n"
MODEL_ICONS = ROOT / "Modelle" / "icons"
MODEL_ICON_MANIFEST = MODEL_ICONS / "openwebui-generic-icons.json"
MODEL_ICON_ARTIFACTS = MODEL_DIST / "artifacts" / "icons"
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
TOOLS_ZIP = TOOLS_DIST / "openwebui-tools-skills-offline.zip"
MODELS_ZIP = MODEL_DIST / "openwebui-offline-artifacts.zip"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)

FUNCTION_CALLING_NATIVE = "native"
CHAT_MODEL_TOOL_MODE = "all_validated_custom_tools"
CHAT_MODEL_FILTER_MODE = "all_validated_default_filters"
WORKBENCH_DEFAULT_BASE_MODEL_ID = "coder"
WORKBENCH_BASE_MODEL_ID_ENV = "WORKBENCH_BASE_MODEL_ID"
WORKBENCH_LEGACY_MISTRAL_MODEL_ID_ENV = "WORKBENCH_MISTRAL_MODEL_ID"
WORKBENCH_FUNCTION_CALLING = "native"
WORKBENCH_REASONING_EFFORT = "high"
WORKBENCH_TEMPERATURE = 0.7
WORKBENCH_TOP_P = 0.95
WORKBENCH_PARALLEL_TOOL_CALLS = True
WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA = "workbench-file-context/v1"
WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID = "workbench_required_file_context_filter"
WORKBENCH_REQUIRED_FILE_CONTEXT_MARKER = "## Workbench-Pflichtdateien"
WORKBENCH_REQUIRED_FILE_CONTEXT_MAX_CHARS = 180_000
WORKBENCH_SYSTEMPROMPT_MAX_CHARS = 2_500
SUPPORTED_CHAT_RUNTIME_PARAMS = {
    "system",
    "temperature",
    "top_p",
    "stop",
    "function_calling",
    "reasoning_effort",
    "parallel_tool_calls",
}
OMITTED_RUNTIME_PARAMS = ["max_tokens"]
OMITTED_UNSUPPORTED_RUNTIME_PARAMS = ["num_ctx", "top_k", "seed"]
PUBLIC_READ_GRANT = {"principal_type": "user", "principal_id": "*", "permission": "read"}
OFFLINE_EXCLUDED_TOOL_IDS = {
    "github_repo_inspector",
    "mediawiki_legacy_crawler",
    "openui_generative_ui",
    "safe_http_fetcher",
    "web_search_and_crawl",
}
LEGACY_EXAMPLE_RESULT_FILE = "beispielergebnis.md"
MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES = {
    "api-schnittstellenentwurf": "beispielergebnis.yaml",
    "codegenerierung": "beispielergebnis.py",
    "informationsextraktion": "beispielergebnis.json",
    "json-csv-log-analyse": "beispielergebnis.json",
    "n8n-workflow-architect": "beispielergebnis.json",
    "präsentationserstellung": "beispielergebnis.html",
    "report-dashboard-vorbereitung": "beispielergebnis.html",
    "tabellen-csv-datenanalyse": "beispielergebnis.py",
}
COMPILED_CONTEXT_MARKER = "## Deterministischer Workbench-Pflichtkontext"
COMPILED_SYSTEM_MAX_CHARS = 220_000
COMPILED_EXAMPLES_MAX_FILES = 2
COMPILED_EXAMPLES_MAX_CHARS_TOTAL = 60_000
COMPILED_EXAMPLE_MAX_CHARS = 35_000
COMPILED_CONTEXT_TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".html",
    ".htm",
    ".csv",
    ".xml",
    ".ini",
    ".sh",
    ".ps1",
}
SYSTEM_BOOTLOADER_MAX_CHARS = 2400
MODEL_EXAMPLES_DIR_NAME = "beispiele"
MODEL_I18N_DIR_NAME = "i18n"
PRIMARY_MODEL_I18N_FILES = ("manifest.json", "de.md", "en.md")
REQUIRED_DEFAULT_FILTER_IDS = [
    WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID,
    "context_compressor_filter",
    "auto_tool_selector",
    "markdown_normalizer",
]
EXAMPLE_PRIORITY_TERMS = {
    "default": [
        "perfekt",
        "referenz",
        "gold",
        "goldstandard",
        "gpt",
        "gpt-5",
        "gpt5",
        "5.5",
        "best",
        "final",
    ],
    "codegenerierung": [
        "code",
        "implementation",
        "implementierung",
        "test",
        "pytest",
        "unittest",
        "validierung",
        "production",
    ],
    "api-schnittstellenentwurf": [
        "openapi",
        "schema",
        "endpoint",
        "validation",
    ],
    "präsentationserstellung": [
        "html",
        "report",
        "dashboard",
        "slide",
        "präsentation",
    ],
    "report-dashboard-vorbereitung": [
        "html",
        "dashboard",
        "chart",
        "bericht",
    ],
}
MODEL_BOOTLOADER_EXTRA_RULES = {
    "eggplant-flaui-skriptmigration": "Spezialregel: Migriere nur nach NUnit/FlaUI UIA3 oder UIA2/OpenCvSharp/Verify.NUnit; keine Koordinatenklicks, xUnit, MSTest, ImageSharp, WinAppDriver oder Playwright-Desktop.",
    "flaui-testassistent": "Spezialregel: Nutze NUnit/FlaUI UIA3 oder UIA2/OpenCvSharp/Verify.NUnit; ersetze Koordinatenklicks durch UIA-Suche und liefere Waits, Assertions und Failure-Artefakte.",
    "n8n-workflow-architect": "n8n-Spezialregel: Ohne konkret bereitgestellten API-Endpunkt erzeugst du keine URL-Felder, keine HTTP-Request-Nodes und keine externen Domains; nutze Manual Trigger, Set/Code und Audit-Ausgabe.",
}
CLOUD_CODER_PRODUCTION_MODEL_IDS: set[str] = set()
CODE_OR_TECHNICAL_MODEL_IDS = {
    "api-schnittstellenentwurf",
    "code-dokumentation",
    "code-review",
    "codeanalyse",
    "codegenerierung",
    "debugging-fehleranalyse",
    "eggplant-flaui-skriptmigration",
    "flaui-testassistent",
    "json-csv-log-analyse",
    "refactoring-unterstützung",
    "tabellen-csv-datenanalyse",
    "testfall-generierung",
    "testprogrammierung",
}
SUPPORTED_PRODUCT_LOCALES = ["de", "en", "es", "fr", "pt-BR", "it", "nl", "pl", "tr", "ja", "zh-Hans"]
MARKDOWN_FORMATTING_MARKER = "Formatting re-enabled"
HIGH_REASONING_SYSTEM_MARKER = "## Laufzeit- und Qualitätsprofil"
CUSTOM_GPT_QUALITY_SYSTEM_MARKER = "## CustomGPT-Qualitätsprofil"
VISION_SYSTEM_MARKER = "## Vision- und UI-Bildanalyse"
TOOL_CALL_PLAYBOOK_SYSTEM_MARKER = "## Explizite Tool-Aufrufmuster"
TOOL_FORCE_SYSTEM_MARKER = "## Verbindliche Tool- und Skill-Nutzung"
MANAGED_SYSTEM_SECTION_MARKERS = [
    HIGH_REASONING_SYSTEM_MARKER,
    CUSTOM_GPT_QUALITY_SYSTEM_MARKER,
    VISION_SYSTEM_MARKER,
    TOOL_CALL_PLAYBOOK_SYSTEM_MARKER,
    TOOL_FORCE_SYSTEM_MARKER,
]
def workbench_base_model_id() -> str:
    return (
        os.environ.get(WORKBENCH_BASE_MODEL_ID_ENV, "").strip()
        or os.environ.get(WORKBENCH_LEGACY_MISTRAL_MODEL_ID_ENV, "").strip()
        or WORKBENCH_DEFAULT_BASE_MODEL_ID
    )


def validate_base_model_id(value: str) -> str:
    clean = str(value or "").strip()
    if not clean:
        raise ValueError("base model id must not be empty")
    if len(clean) > 200 or any(ord(char) < 32 for char in clean):
        raise ValueError("base model id contains invalid characters")
    return clean


def legacy_example_result_file_for_model(model_id: str) -> str:
    return MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES.get(model_id, LEGACY_EXAMPLE_RESULT_FILE)


def required_model_knowledge_files(model_id: str) -> List[str]:
    """Legacy compatibility: only the old example result remains Knowledge."""
    return [legacy_example_result_file_for_model(model_id)]


def formatted_required_model_knowledge_files(model_id: str) -> str:
    return ", ".join(f"`{name}`" for name in required_model_knowledge_files(model_id))


def golden_example_file_for_model(model_dir: Path) -> Path:
    candidates = sorted(
        path for path in model_dir.glob("Golden_Example.*")
        if path.is_file()
    )
    if len(candidates) != 1:
        raise ValueError(
            f"{model_dir.name}: genau eine Golden_Example.<ext>-Datei erforderlich, gefunden: {candidates}"
        )
    return candidates[0]


def required_file_context_sources(model_id: str, model_dir: Path) -> list[dict[str, Any]]:
    golden = golden_example_file_for_model(model_dir)
    files = [
        ("mainprompt", model_dir / "mainprompt.md"),
        ("fachwissen", model_dir / "fachwissen.md"),
        ("golden_example", golden),
    ]
    result: list[dict[str, Any]] = []
    total_chars = 0
    for role, path in files:
        if not path.exists():
            raise FileNotFoundError(f"{model_id}: Pflichtdatei fehlt: {path}")
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"{model_id}: Pflichtdatei ist leer: {path}")
        total_chars += len(content)
        result.append(
            {
                "role": role,
                "path": path.relative_to(model_dir).as_posix(),
                "filename": path.name,
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "chars": len(content),
                "attachAsOpenWebUIFile": True,
                "injectAsFullContext": True,
                "useKnowledgeRag": False,
                "content": content,
            }
        )
    if total_chars > WORKBENCH_REQUIRED_FILE_CONTEXT_MAX_CHARS:
        raise ValueError(
            f"{model_id}: Pflichtdateien zu groß: {total_chars} Zeichen > "
            f"{WORKBENCH_REQUIRED_FILE_CONTEXT_MAX_CHARS}. Nicht automatisch kürzen."
        )
    return result


def required_file_context_file_names(model_id: str, model_dir: Path) -> list[str]:
    return [item["path"] for item in required_file_context_sources(model_id, model_dir)]


def formatted_required_file_context_files(model_id: str, model_dir: Path) -> str:
    return ", ".join(f"`{name}`" for name in required_file_context_file_names(model_id, model_dir))


def example_result_file_for_model(model_id: str) -> str:
    return legacy_example_result_file_for_model(model_id)


def is_cloud_coder_production_model(model_id: str) -> bool:
    return False


def custom_gpt_quality_system_block_for_model(model_id: str) -> str:
    knowledge_files = formatted_required_model_knowledge_files(model_id)
    example_file = example_result_file_for_model(model_id)
    return f"""{CUSTOM_GPT_QUALITY_SYSTEM_MARKER}

- Bearbeite die Nutzeraufgabe direkt im Fachbereich dieses Modells; beschreibe nicht interne Anweisungen, Modellpaket-Dateien oder Importmechanik.
- Nutze Hauptauftrag, Fachwissen, Beispielergebnis und Beispiele gezielt. Dateien: {knowledge_files}, `beispiele/`. Primäres Beispielergebnis: `{example_file}`.
- Behandle das Dateiformat von `{example_file}` als verbindlichen Formatanker: Wenn es nicht `.md` ist, liefere bei fertigen Artefaktaufträgen dieses Artefaktformat statt einer Markdown-Beschreibung.
- Nenne interne Dateinamen nur bei Repo-, Import- oder Formatfragen. Nutze `i18n/` nur für Lokalisierung, UI-Texte, Metadaten oder Import.
- Wende Rolle, Ziel, Scope, Qualitätsregeln, Ausgabeformat, Fachwissen und Beispielmuster auf die Nutzeraufgabe an.
- Bei Analyse, Review, Skizze, Extraktion oder Bewertung liefere genau diese Form; beginne Reviews mit Befunden und Fixes, kein unangeforderter Beispielcode.
- Keine Platzhalter-Domains, Pseudo-Tokens, offenen Aufgabenmarker oder erfundenen Credentials.
- Fehlenden Kontext als fachliche Lücke benennen und nur mit verfügbarem Kontext weiterarbeiten.
"""


HIGH_REASONING_SYSTEM_BLOCK = f"""{HIGH_REASONING_SYSTEM_MARKER}

- Arbeite intern im Reasoning-Profil `high`: plane, prüfe und validiere Tool-Ausgaben kritisch; gib nur das fachlich notwendige Ergebnis aus.
- Nutze keine erfundenen Runtime-Parameter und setze kein festes `max_tokens`; OpenWebUI und Modellserver bestimmen Kontext- und Antwortlimits.
"""
VISION_SYSTEM_BLOCK = f"""{VISION_SYSTEM_MARKER}

- Nutze Vision bei Bildern, Screenshots, Scans, Folien, Diagrammen, UI-Zuständen und visueller Artefakt-QA; behaupte keine nicht sichtbaren Details.
- Prüfe Layout, Lesbarkeit, Kontrast, Responsiveness, Overlaps, Dark Mode, Hover/Focus/Touch und sichtbare Fehler; nutze lokale Offline-Tools oder `openwebui-offline-addons`, wenn sie verfügbar sind.
"""
MODEL_TEMPERATURES = {}
DEFAULT_CHAT_TEMPERATURE = 0.7
TOOL_FORCE_PROFILES = {
    "allgemein": {
        "tools": ["air_gapped_jupyter_python", "ask_user", "comfyui_workflow_inspector", "docker_compose_triage", "inline_visuals_toolkit_v3", "json_csv_text_validator", "llm_council", "markdown_skill_builder", "offline_artifact_workbench", "openapi_schema_inspector", "parallel_task_planner", "parallel_tools", "repo_tree_analyzer", "sub_agent", "subagent_orchestrator", "tool_skill_overlay_planner", "visuals_toolkit_v4"],
        "skills": ["offline-use-case-router", "redundant-fallback-tooling", "native-tool-calling-rollout", "parallel-tools-subagents", "secure-tool-usage"],
        "focus": "Freie oder gemischte Nutzerprobleme mit dem Basismodell `coder` bearbeiten, passende Spezialmodelle empfehlen und die offlinefähigen Standardtools sowie alle Standardfilter fallbezogen aktiv nutzen.",
    },
    "anforderungsanalyse-lastenheft": {
        "tools": ["ask_user", "offline_artifact_workbench", "tool_skill_overlay_planner", "json_csv_text_validator", "parallel_task_planner", "llm_council"],
        "skills": ["prompt-to-tool-workflow", "model-tool-skill-overlays", "offline-artifact-production"],
        "focus": "Anforderungen, Akzeptanzkriterien, Tool-/Skill-Abdeckung und Handover-Artefakte strukturiert validieren.",
    },
    "api-schnittstellenentwurf": {
        "tools": ["openapi_schema_inspector", "json_csv_text_validator", "offline_artifact_workbench"],
        "skills": ["api-integration-debugging", "safe-mcp-openapi-import", "secure-tool-usage"],
        "focus": "OpenAPI-/JSON-Schemata prüfen, API-Verträge konsistent halten und Schnittstellenartefakte erzeugen.",
    },
    "code-dokumentation": {
        "tools": ["repo_tree_analyzer", "air_gapped_jupyter_python", "offline_artifact_workbench", "visuals_toolkit_v4"],
        "skills": ["repository-maintenance", "offline-artifact-production", "secure-tool-usage"],
        "focus": "Repository-Struktur, Codeauszüge und Dokumentationsartefakte mit lokalen Prüfpfaden absichern.",
    },
    "code-review": {
        "tools": ["repo_tree_analyzer", "json_csv_text_validator", "air_gapped_jupyter_python", "llm_council"],
        "skills": ["code-review-deep", "repository-maintenance", "secure-tool-usage"],
        "focus": "Diffs, Dateibäume, Findings, Tests und strukturierte Review-Ergebnisse toolgestützt prüfen.",
    },
    "codeanalyse": {
        "tools": ["repo_tree_analyzer", "air_gapped_jupyter_python", "json_csv_text_validator", "llm_council"],
        "skills": ["code-review-deep", "repository-maintenance", "secure-tool-usage"],
        "focus": "Code- und Strukturfragen mit Dateibaum-, Parsing- oder Testhilfen belegen.",
    },
    "codegenerierung": {
        "tools": ["repo_tree_analyzer", "air_gapped_jupyter_python", "json_csv_text_validator", "sub_agent"],
        "skills": ["repository-maintenance", "secure-tool-usage", "openwebui-tool-authoring"],
        "focus": "Vorhandene Struktur prüfen, erzeugten Code lokal plausibilisieren und strukturierte Daten validieren.",
    },
    "compliance-richtlinienprüfung": {
        "tools": ["json_csv_text_validator", "repo_tree_analyzer", "offline_artifact_workbench", "llm_council"],
        "skills": ["research-grounding", "secure-tool-usage", "redundant-fallback-tooling"],
        "focus": "Bereitgestellte Richtlinien, Tabellen, Dateibäume und Nachweisartefakte nachvollziehbar prüfen.",
    },
    "debugging-fehleranalyse": {
        "tools": ["ask_user", "docker_compose_triage", "repo_tree_analyzer", "air_gapped_jupyter_python", "json_csv_text_validator", "parallel_tools"],
        "skills": ["docker-openwebui-troubleshooting", "repository-maintenance", "secure-tool-usage"],
        "focus": "Logs, Compose-Auszüge, Codepfade und Reproduktionsdaten toolgestützt eingrenzen.",
    },
    "dokumentenanalyse": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench"],
        "skills": ["research-grounding", "data-cleaning-analysis", "offline-artifact-production"],
        "focus": "Bereitgestellte Dokumentinhalte, Tabellen und Extrakte lokal prüfen und bei Bedarf als Artefakt ausgeben.",
    },
    "dokumentengenerierung": {
        "tools": ["offline_artifact_workbench", "inline_visuals_toolkit_v3", "visuals_toolkit_v4", "json_csv_text_validator"],
        "skills": ["offline-artifact-production", "visual-toolkit-v3-offline", "secure-tool-usage"],
        "focus": "HTML/PDF/ZIP-fähige Ergebnisse mit Artefakt- und Visual-Tools erzeugen.",
    },
    "dokumentenvergleich": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench"],
        "skills": ["data-cleaning-analysis", "research-grounding", "offline-artifact-production"],
        "focus": "Vergleichstabellen, Differenzen und Belegstellen mit lokalen Prüf- oder Tabellenpfaden absichern.",
    },
    "dokumentenzusammenfassung": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench"],
        "skills": ["research-grounding", "offline-artifact-production", "secure-tool-usage"],
        "focus": "Quellenorientierte Zusammenfassungen, strukturierte Extrakte und Übergabeartefakte absichern.",
    },
    "email-kommunikationsassistenz": {
        "tools": ["json_csv_text_validator", "offline_artifact_workbench"],
        "skills": ["secure-tool-usage", "offline-artifact-production", "research-grounding"],
        "focus": "Strukturierte Kontaktdaten, Vorlagen und Anhänge lokal prüfen; sensible Inhalte minimieren.",
    },
    "eggplant-flaui-skriptmigration": {
        "tools": ["repo_tree_analyzer", "json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench", "parallel_task_planner", "llm_council"],
        "skills": ["flaui-eggplant-desktop-ui-testing", "repository-maintenance", "code-review-deep", "secure-tool-usage", "offline-artifact-production"],
        "focus": "Eggplant-/SenseTalk-Skripte inventarisieren, fachlich klassifizieren und zielstack-konform in FlaUI/NUnit/OpenCV-Artefakte inklusive VisualTrack, Akzeptanzkriterien und Azure-DevOps-Server-Hinweisen migrieren.",
    },
    "flaui-testassistent": {
        "tools": ["repo_tree_analyzer", "json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench", "parallel_task_planner", "llm_council"],
        "skills": ["flaui-eggplant-desktop-ui-testing", "repository-maintenance", "code-review-deep", "secure-tool-usage", "offline-artifact-production"],
        "focus": "FlaUI-/NUnit-Desktop-UI-Tests analysieren, generieren, reviewen, diagnostizieren und mit UIA2/UIA3, VisualTrack, Failure-Artefakten und Azure-DevOps-Server-Pipelinepfaden absichern.",
    },
    "informationsextraktion": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench"],
        "skills": ["data-cleaning-analysis", "research-grounding", "secure-tool-usage"],
        "focus": "Extraktionsschema, JSON/CSV-Ausgabe und Datenqualität vor der finalen Antwort validieren.",
    },
    "internetwissen": {
        "tools": ["ask_user", "json_csv_text_validator", "repo_tree_analyzer", "parallel_task_planner", "offline_artifact_workbench", "inline_visuals_toolkit_v3"],
        "skills": ["research-grounding", "offline-use-case-router", "redundant-fallback-tooling", "secure-tool-usage"],
        "focus": "Offline-Wissensfragen, Quellenkritik, Aktualitätsgrenzen, Recherchepläne und Wissensstrukturierung ohne behauptete Live-Webprüfung absichern.",
    },
    "istqb-testfallgenerator": {
        "tools": ["ask_user", "json_csv_text_validator", "offline_artifact_workbench", "llm_council"],
        "skills": ["data-cleaning-analysis", "research-grounding", "secure-tool-usage"],
        "focus": "Anforderungen, User Stories, Akzeptanzkriterien und fachliche Testartefakte strukturiert prüfen; keine Code- oder Automatisierungsimplementierung erzeugen.",
    },
    "it-helpdesk-diagnose": {
        "tools": ["ask_user", "docker_compose_triage", "json_csv_text_validator", "repo_tree_analyzer"],
        "skills": ["docker-openwebui-troubleshooting", "secure-tool-usage", "offline-use-case-router"],
        "focus": "Fehlertexte, Konfigurationsauszüge und Diagnosepfade mit passenden lokalen Tools prüfen.",
    },
    "json-csv-log-analyse": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "docker_compose_triage", "offline_artifact_workbench"],
        "skills": ["data-cleaning-analysis", "docker-openwebui-troubleshooting", "secure-tool-usage"],
        "focus": "JSON, CSV und Logs immer strukturell validieren, bei Berechnung Jupyter nutzen und Ergebnisse exportierbar machen.",
    },
    "meeting-protokoll-auswertung": {
        "tools": ["json_csv_text_validator", "offline_artifact_workbench", "air_gapped_jupyter_python"],
        "skills": ["research-grounding", "offline-artifact-production", "data-cleaning-analysis"],
        "focus": "Beschlüsse, Aufgabenlisten, Tabellen und Übergabedokumente strukturiert prüfen oder erzeugen.",
    },
    "mistral-vision-workbench": {
        "tools": ["ask_user", "offline_artifact_workbench", "inline_visuals_toolkit_v3", "visuals_toolkit_v4", "air_gapped_jupyter_python", "json_csv_text_validator", "repo_tree_analyzer", "docker_compose_triage", "parallel_task_planner", "parallel_tools", "sub_agent", "subagent_orchestrator", "tool_skill_overlay_planner", "llm_council"],
        "skills": ["visual-toolkit-v3-offline", "offline-artifact-production", "data-cleaning-analysis", "parallel-tools-subagents", "secure-tool-usage"],
        "focus": "Das ausgewählte visionfähige Basismodell für Screenshots, UI-Tests, Folien, Diagramme, Scans, Dokumentbilder und visuelle Artefakt-QA nutzen und mit lokalen Offline-Tools absichern.",
    },
    "offline-workbench-agent": {
        "tools": ["ask_user", "json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench", "inline_visuals_toolkit_v3", "visuals_toolkit_v4", "parallel_task_planner", "parallel_tools", "subagent_orchestrator", "sub_agent", "tool_skill_overlay_planner", "repo_tree_analyzer", "docker_compose_triage", "openapi_schema_inspector", "llm_council", "comfyui_workflow_inspector"],
        "skills": ["offline-use-case-router", "redundant-fallback-tooling", "native-tool-calling-rollout", "parallel-tools-subagents", "visual-toolkit-v3-offline"],
        "focus": "Neue Aufgaben routen, passende Tools erzwingen, komplexe Arbeit planen und Artefakte lokal erzeugen.",
    },
    "prozess-workflow-dokumentation": {
        "tools": ["parallel_task_planner", "parallel_tools", "sub_agent", "offline_artifact_workbench", "inline_visuals_toolkit_v3", "visuals_toolkit_v4", "tool_skill_overlay_planner"],
        "skills": ["parallel-tools-subagents", "offline-artifact-production", "visual-toolkit-v3-offline", "model-tool-skill-overlays"],
        "focus": "Prozesse, Workflows, Verantwortlichkeiten und Diagramme toolgestützt planen und dokumentieren.",
    },
    "promptforge": {
        "tools": ["ask_user", "tool_skill_overlay_planner", "json_csv_text_validator", "parallel_task_planner", "llm_council", "markdown_skill_builder"],
        "skills": ["prompt-to-tool-workflow", "secure-tool-usage", "model-tool-skill-overlays", "native-tool-calling-rollout"],
        "focus": "Vollständige direkt kopierbare Markdown-Promptvorlagen nach Prompting-Best-Practices, Tool-first-Regeln, Sicherheitsgrenzen und konkretem Zielsystem erzeugen.",
    },
    "n8n-workflow-architect": {
        "tools": ["ask_user", "json_csv_text_validator", "openapi_schema_inspector", "offline_artifact_workbench", "air_gapped_jupyter_python", "tool_skill_overlay_planner"],
        "skills": ["safe-mcp-openapi-import", "api-integration-debugging", "secure-tool-usage", "offline-use-case-router"],
        "focus": "Importierbare n8n-Workflow-JSONs wie der Custom GPT n8n Workflow Architect planen, prüfen, validieren und mit Test- sowie Sicherheitshinweisen ausgeben.",
    },
    "openwebui-model-builder": {
        "tools": ["ask_user", "tool_skill_overlay_planner", "markdown_skill_builder", "json_csv_text_validator", "offline_artifact_workbench", "repo_tree_analyzer", "openapi_schema_inspector"],
        "skills": ["openwebui-tool-authoring", "prompt-to-tool-workflow", "model-tool-skill-overlays", "secure-tool-usage", "native-tool-calling-rollout"],
        "focus": "Vollständige OpenWebUI-Modellpakete mit JSON, Systemprompt, Mainprompt, Fachwissen, Tool-/Skill-Zuordnung, Knowledge und Import-QA erzeugen.",
    },
    "präsentationserstellung": {
        "tools": ["ask_user", "offline_artifact_workbench", "inline_visuals_toolkit_v3", "visuals_toolkit_v4", "air_gapped_jupyter_python", "json_csv_text_validator"],
        "skills": ["offline-artifact-production", "visual-toolkit-v3-offline", "offline-creative-media-workflows"],
        "focus": "Hochwertige browserbasierte Keynote-Präsentationen wie der Custom GPT Präsentationscreator als einzelne `präsentation.html` erzeugen; PDF/PPTX nur auf expliziten Wunsch oder als Fallback.",
    },
    "refactoring-unterstützung": {
        "tools": ["repo_tree_analyzer", "air_gapped_jupyter_python", "json_csv_text_validator"],
        "skills": ["repository-maintenance", "code-review-deep", "secure-tool-usage"],
        "focus": "Änderungsbereiche, Tests, Risiken und Strukturwirkungen lokal prüfen.",
    },
    "report-dashboard-vorbereitung": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "inline_visuals_toolkit_v3", "visuals_toolkit_v4", "offline_artifact_workbench"],
        "skills": ["data-cleaning-analysis", "visual-toolkit-v3-offline", "offline-artifact-production"],
        "focus": "Daten prüfen, Kennzahlen berechnen, Visuals erzeugen und Dashboard-Artefakte vorbereiten.",
    },
    "support-ticket-vorbereitung": {
        "tools": ["json_csv_text_validator", "docker_compose_triage", "offline_artifact_workbench"],
        "skills": ["docker-openwebui-troubleshooting", "secure-tool-usage", "offline-artifact-production"],
        "focus": "Ticketdaten, Fehlertexte, Priorisierung und Übergabetexte strukturiert prüfen.",
    },
    "tabellen-csv-datenanalyse": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench", "inline_visuals_toolkit_v3"],
        "skills": ["data-cleaning-analysis", "visual-toolkit-v3-offline", "offline-artifact-production"],
        "focus": "Tabellen und CSV immer validieren, Berechnungen mit Jupyter durchführen und Ergebnisse exportierbar machen.",
    },
    "testfall-generierung": {
        "tools": ["repo_tree_analyzer", "json_csv_text_validator", "air_gapped_jupyter_python", "parallel_tools"],
        "skills": ["code-review-deep", "repository-maintenance", "data-cleaning-analysis"],
        "focus": "Anforderungen, Codepfade, Testdaten und erwartete Ergebnisse mit lokalen Prüfpfaden absichern.",
    },
    "testprogrammierung": {
        "tools": ["repo_tree_analyzer", "json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench", "parallel_task_planner", "llm_council"],
        "skills": ["repository-maintenance", "code-review-deep", "secure-tool-usage", "offline-artifact-production"],
        "focus": "Testcode, Framework-Auswahl, lokale Ausführung, CI/CD-Beispiele und Wartbarkeit mit bereitgestellten Projekt- oder Beispielpfaden prüfen.",
    },
    "übersetzung-lokalisierung": {
        "tools": ["json_csv_text_validator", "offline_artifact_workbench"],
        "skills": ["research-grounding", "data-cleaning-analysis", "offline-artifact-production"],
        "focus": "Terminologielisten, Tabellen, Glossare und zielsprachliche Handover-Artefakte prüfen.",
    },
}
EXCLUDED_MODEL_MARKERS = (
    "embedding",
    "embeddings",
    "embed",
    "rerank",
    "reranker",
    "cross-encoder",
    "bge-reranker",
    "nomic-embed",
)


@dataclass(frozen=True)
class ToolRecord:
    id: str
    name: str
    path: str
    purpose: str
    offline: bool
    configuration: List[str]
    sha256: str
    importable: bool
    methods: List[str]
    source: str


@dataclass(frozen=True)
class FunctionRecord:
    id: str
    name: str
    path: str
    purpose: str
    function_type: str
    sha256: str
    importable: bool
    hooks: List[str]
    source: str


@dataclass(frozen=True)
class PromptRecord:
    id: str
    command: str
    name: str
    path: str
    description: str
    tags: List[str]
    sha256: str
    importable: bool
    source: str
    content: str


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def stable_text_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    text_suffixes = {
        ".adb",
        ".ads",
        ".cs",
        ".csproj",
        ".csv",
        ".example",
        ".gpr",
        ".htm",
        ".html",
        ".ini",
        ".java",
        ".json",
        ".md",
        ".props",
        ".ps1",
        ".py",
        ".script",
        ".sh",
        ".svg",
        ".targets",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
    text_filenames = {".env", ".env.example"}
    if path.suffix.lower() in text_suffixes or path.name.lower() in text_filenames:
        return data.replace(b"\r\n", b"\n")
    return data


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def archive_sort_key(path: Path) -> str:
    return rel(path).casefold()


def sorted_archive_paths(paths: Iterable[Path]) -> List[Path]:
    return sorted(paths, key=archive_sort_key)


def should_archive(path: Path) -> bool:
    ignored_dirs = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    if any(part in ignored_dirs for part in path.parts):
        return False
    if path.suffix in {".pyc", ".pyo", ".pyd"}:
        return False
    return True


def write_archive_file(archive: zipfile.ZipFile, path: Path) -> None:
    info = zipfile.ZipInfo(rel(path), ZIP_EPOCH)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = ((0o755 if path.suffix == ".sh" else 0o644) & 0xFFFF) << 16
    archive.writestr(info, stable_text_bytes(path))


def tool_zip_sources() -> List[Path]:
    sources: List[Path] = []
    for item in [ROOT / "Tools" / "jupyter", ROOT / "Tools" / "openwebui_ext"]:
        sources.extend(path for path in sorted_archive_paths(item.rglob("*")) if path.is_file() and should_archive(path))
    sources.extend(
        path
        for path in sorted_archive_paths(
            [
                TOOLS_INDEX,
                ROOT / "Tools" / "README.md",
                IMPORT_SCRIPT,
                CONFIG_EXAMPLE,
                TOOL_REGISTRY,
                OFFLINE_TOOL_IMPORT,
                TOOL_IMPORT,
                FUNCTION_REGISTRY,
                FUNCTION_IMPORT,
                PROMPT_REGISTRY,
                PROMPT_IMPORT,
            ]
        )
        if path.exists()
    )
    return sources


def model_zip_sources() -> List[Path]:
    sources = [
        path
        for path in sorted_archive_paths(
            [
                MODEL_DIST / "README.md",
                MODEL_IMPORT,
                MODEL_FALLBACK,
                TOOLS_FALLBACK_BUNDLE,
                FUNCTIONS_FALLBACK_BUNDLE,
                OFFLINE_TOOL_IMPORT,
                TOOL_IMPORT,
                FUNCTION_IMPORT,
                PROMPT_REGISTRY,
                PROMPT_IMPORT,
                REGISTRATION_PLAN,
                MODEL_PARAMS_SUMMARY,
                MODEL_DIST / "manual_import_checklist.md",
                CONFIG_EXAMPLE,
            ]
        )
        if path.exists()
    ]
    artifacts_dir = MODEL_DIST / "artifacts"
    if artifacts_dir.exists():
        sources.extend(path for path in sorted_archive_paths(artifacts_dir.rglob("*")) if path.is_file() and should_archive(path))
    return sources


def stable_tool_id(path: Path, indexed_by_path: Dict[str, Dict[str, Any]]) -> str:
    key = rel(path).lower()
    if key in indexed_by_path:
        return str(indexed_by_path[key]["id"])
    if path.name == "jupyter_tool.py":
        return "air_gapped_jupyter_python"
    return path.stem


def parse_doc_metadata(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r'\s*"""(.*?)"""', text, flags=re.S)
    meta: Dict[str, str] = {}
    if not match:
        return meta
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    return meta


def parse_doc_manifest(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r'\s*"""(.*?)"""', text, flags=re.S)
    manifest: Dict[str, str] = {}
    if not match:
        return manifest
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            manifest[key.strip()] = value.strip()
    return manifest


def parse_bool(value: Any, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "nein", "off"}
    if value is None:
        return default
    return bool(value)


def inspect_tool(path: Path) -> Tuple[bool, List[str]]:
    """Structurally inspect an OpenWebUI Tool without importing its runtime dependencies."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tools_cls = next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Tools"), None)
        if tools_cls is None:
            return False, []
        methods = sorted(
            node.name
            for node in tools_cls.body
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
            and not node.name.startswith("_")
            and node.name != "__init__"
        )
        return bool(methods), methods
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False, []


def inspect_filter(path: Path) -> Tuple[bool, List[str]]:
    """Structurally inspect an OpenWebUI Filter without importing its runtime dependencies."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        filter_cls = next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Filter"), None)
        if filter_cls is None:
            return False, []
        hooks = sorted(
            node.name
            for node in filter_cls.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name in {"inlet", "stream", "outlet"}
        )
        return bool(hooks), hooks
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False, []


def parse_markdown_frontmatter(path: Path) -> Tuple[Dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, normalized
    meta: Dict[str, str] = {}
    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip().strip("\"'")
    if end_index is None:
        return {}, normalized
    return meta, "\n".join(lines[end_index + 1 :]).lstrip("\n")


def parse_csv_tags(value: str) -> List[str]:
    tags: List[str] = []
    for item in str(value or "").strip("[]").split(","):
        tag = item.strip().strip("\"'")
        if tag and tag not in tags:
            tags.append(tag)
    return tags or ["workbench"]


def normalize_prompt_command(value: str, fallback: str) -> str:
    command = str(value or fallback).strip().lstrip("/")
    command = re.sub(r"[^a-z0-9_-]+", "-", command.lower()).strip("-")
    return command or fallback


def discover_tools() -> List[ToolRecord]:
    index = read_json(TOOLS_INDEX)
    indexed_entries = index.get("tools", [])
    indexed_by_path = {
        str(entry.get("path", "")).replace("\\", "/").lower(): entry
        for entry in indexed_entries
        if entry.get("path")
    }
    tool_paths = sorted({ROOT / "Tools" / "jupyter" / "jupyter_tool.py", *list((ROOT / "Tools" / "openwebui_ext" / "tools").glob("*.py"))})
    records: List[ToolRecord] = []
    for path in tool_paths:
        meta = parse_doc_metadata(path)
        path_key = rel(path).lower()
        indexed = indexed_by_path.get(path_key, {})
        tool_id = stable_tool_id(path, indexed_by_path)
        importable, methods = inspect_tool(path)
        records.append(
            ToolRecord(
                id=tool_id,
                name=str(indexed.get("name") or meta.get("title") or tool_id.replace("_", " ").title()),
                path=rel(path),
                purpose=str(indexed.get("purpose") or meta.get("description") or "OpenWebUI Workspace Tool."),
                offline=parse_bool(meta.get("offline", indexed.get("offline")), True),
                configuration=list(indexed.get("configuration", [])),
                sha256=hashlib.sha256(stable_text_bytes(path)).hexdigest(),
                importable=importable,
                methods=methods,
                source=path.read_text(encoding="utf-8"),
            )
        )
    return records


def offline_default_tool_records(records: List[ToolRecord]) -> List[ToolRecord]:
    return [record for record in records if record.importable and record.offline and record.id not in OFFLINE_EXCLUDED_TOOL_IDS]


def tool_record_metadata(record: ToolRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "name": record.name,
        "path": record.path,
        "purpose": record.purpose,
        "offline": record.offline,
        "configuration": record.configuration,
        "sha256": record.sha256,
        "importable": record.importable,
        "methods": record.methods,
    }


def function_record_metadata(record: FunctionRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "name": record.name,
        "path": record.path,
        "purpose": record.purpose,
        "function_type": record.function_type,
        "sha256": record.sha256,
        "importable": record.importable,
        "hooks": record.hooks,
    }


def prompt_record_metadata(record: PromptRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "command": record.command,
        "name": record.name,
        "path": record.path,
        "description": record.description,
        "tags": record.tags,
        "sha256": record.sha256,
        "importable": record.importable,
    }


def tool_import_payload(record: ToolRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "name": record.name,
        "meta": {
            "description": record.purpose,
            "manifest": parse_doc_manifest(ROOT / record.path),
        },
        "content": record.source,
    }


def function_import_payload(record: FunctionRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "name": record.name,
        "type": record.function_type,
        "meta": {
            "description": record.purpose,
            "manifest": parse_doc_manifest(ROOT / record.path),
        },
        "content": record.source,
    }


def prompt_import_payload(record: PromptRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "command": record.command,
        "name": record.name,
        "content": record.content,
        "data": {
            "source_file": record.path,
            "source_sha256": record.sha256,
        },
        "meta": {
            "description": record.description,
            "source": record.path,
            "schema": "openwebui-workbench-prompt/v1",
        },
        "tags": record.tags,
        "access_grants": [PUBLIC_READ_GRANT],
    }


def discover_functions() -> List[FunctionRecord]:
    filter_dir = ROOT / "Tools" / "openwebui_ext" / "filters"
    records: List[FunctionRecord] = []
    for path in sorted(filter_dir.glob("*.py")):
        meta = parse_doc_metadata(path)
        importable, hooks = inspect_filter(path)
        function_id = path.stem
        records.append(
            FunctionRecord(
                id=function_id,
                name=str(meta.get("title") or function_id.replace("_", " ").title()),
                path=rel(path),
                purpose=str(meta.get("description") or "OpenWebUI Workspace Filter."),
                function_type=str(meta.get("type") or "filter"),
                sha256=hashlib.sha256(stable_text_bytes(path)).hexdigest(),
                importable=importable,
                hooks=hooks,
                source=path.read_text(encoding="utf-8"),
            )
        )
    return records


def discover_prompts() -> List[PromptRecord]:
    records: List[PromptRecord] = []
    if not PROMPTS_DIR.exists():
        return records
    for path in sorted(PROMPTS_DIR.glob("*.md")):
        if path.name.upper() == "README.MD":
            continue
        meta, body = parse_markdown_frontmatter(path)
        prompt_id = path.stem
        command = normalize_prompt_command(meta.get("command", prompt_id), prompt_id)
        content = body.strip() + "\n" if body.strip() else path.read_text(encoding="utf-8")
        records.append(
            PromptRecord(
                id=prompt_id,
                command=command,
                name=str(meta.get("name") or prompt_id.replace("_", " ").replace("-", " ").title()),
                path=rel(path),
                description=str(meta.get("description") or "OpenWebUI Workspace Prompt."),
                tags=parse_csv_tags(meta.get("tags", "workbench")),
                sha256=hashlib.sha256(stable_text_bytes(path)).hexdigest(),
                importable=bool(content.strip()),
                source=path.read_text(encoding="utf-8"),
                content=content,
            )
        )
    return records


def sync_tools_index(records: List[ToolRecord], write: bool) -> bool:
    data = {
        "schema": "openwebui-tool-index-fallback/v1",
        "tools": [
            {
                "id": record.id,
                "name": record.name,
                "path": record.path,
                "purpose": record.purpose,
                "offline": record.offline,
                "configuration": record.configuration,
            }
            for record in records
            if record.importable
        ],
    }
    changed = data != read_json(TOOLS_INDEX)
    if changed and write:
        write_json(TOOLS_INDEX, data)
    return changed


def write_tool_artifacts(records: List[ToolRecord], write: bool) -> bool:
    offline_records = offline_default_tool_records(records)
    optional_records = [record for record in records if record.importable and record not in offline_records]
    importable_records = [record for record in records if record.importable]
    registry = {
        "schema": "openwebui-tool-registry/v1",
        "order": ["tools", "skills", "models"],
        "gui_import_file": rel(TOOL_IMPORT),
        "gui_offline_import_file": rel(OFFLINE_TOOL_IMPORT),
        "tool_import_order": [record.id for record in offline_records],
        "offline_default_tool_import_order": [record.id for record in offline_records],
        "optional_network_tools_not_in_offline_default": [record.id for record in optional_records],
        "tools": [tool_record_metadata(record) for record in records],
    }
    fallback = {
        "schema": "openwebui-tool-bundle-fallback/v1",
        "gui_import_file": rel(TOOL_IMPORT),
        "gui_offline_import_file": rel(OFFLINE_TOOL_IMPORT),
        "offline_default_tool_import_order": [record.id for record in offline_records],
        "optional_network_tools_not_in_offline_default": [record.id for record in optional_records],
        "tools": [
            {
                "id": record.id,
                "name": record.name,
                "source_file": record.path,
                "config_example": "Tools/jupyter/jupyter_config.example.json" if record.id == "air_gapped_jupyter_python" else None,
            }
            for record in offline_records
        ],
    }
    import_payload = [tool_import_payload(record) for record in importable_records]
    offline_import_payload = [tool_import_payload(record) for record in offline_records]
    changed = (
        (not TOOL_REGISTRY.exists() or read_json(TOOL_REGISTRY) != registry)
        or not TOOLS_FALLBACK_BUNDLE.exists()
        or read_json(TOOLS_FALLBACK_BUNDLE) != fallback
        or not TOOL_IMPORT.exists()
        or read_json(TOOL_IMPORT) != import_payload
        or not OFFLINE_TOOL_IMPORT.exists()
        or read_json(OFFLINE_TOOL_IMPORT) != offline_import_payload
    )
    if changed and write:
        write_json(TOOL_REGISTRY, registry)
        write_json(TOOLS_FALLBACK_BUNDLE, fallback)
        write_json(TOOL_IMPORT, import_payload)
        write_json(OFFLINE_TOOL_IMPORT, offline_import_payload)
    return changed


def write_function_artifacts(records: List[FunctionRecord], write: bool) -> bool:
    importable_records = [record for record in records if record.importable]
    registry = {
        "schema": "openwebui-function-registry/v1",
        "order": ["filters", "tools", "models"],
        "gui_import_file": rel(FUNCTION_IMPORT),
        "filter_import_order": [record.id for record in records if record.importable and record.function_type == "filter"],
        "functions": [function_record_metadata(record) for record in records],
    }
    fallback = {
        "schema": "openwebui-function-bundle-fallback/v1",
        "gui_import_file": rel(FUNCTION_IMPORT),
        "functions": [
            {
                "id": record.id,
                "name": record.name,
                "type": record.function_type,
                "source_file": record.path,
                "default_enabled_for_chat_models": record.function_type == "filter",
            }
            for record in records
            if record.importable
        ],
    }
    import_payload = [function_import_payload(record) for record in importable_records]
    changed = (
        not FUNCTION_REGISTRY.exists()
        or read_json(FUNCTION_REGISTRY) != registry
        or not FUNCTIONS_FALLBACK_BUNDLE.exists()
        or read_json(FUNCTIONS_FALLBACK_BUNDLE) != fallback
        or not FUNCTION_IMPORT.exists()
        or read_json(FUNCTION_IMPORT) != import_payload
    )
    if changed and write:
        write_json(FUNCTION_REGISTRY, registry)
        write_json(FUNCTIONS_FALLBACK_BUNDLE, fallback)
        write_json(FUNCTION_IMPORT, import_payload)
    return changed


def write_prompt_artifacts(records: List[PromptRecord], write: bool) -> bool:
    importable_records = [record for record in records if record.importable]
    registry = {
        "schema": "openwebui-prompt-registry/v1",
        "order": ["tools", "filters", "skills", "prompts", "models"],
        "gui_import_file": rel(PROMPT_IMPORT),
        "prompt_source_dir": rel(PROMPTS_DIR),
        "prompt_import_order": [record.command for record in importable_records],
        "prompts": [prompt_record_metadata(record) for record in records],
    }
    import_payload = [prompt_import_payload(record) for record in importable_records]
    changed = (
        not PROMPT_REGISTRY.exists()
        or read_json(PROMPT_REGISTRY) != registry
        or not PROMPT_IMPORT.exists()
        or read_json(PROMPT_IMPORT) != import_payload
    )
    if changed and write:
        write_json(PROMPT_REGISTRY, registry)
        write_json(PROMPT_IMPORT, import_payload)
    return changed


def sync_icon_artifacts(write: bool) -> bool:
    if not MODEL_ICONS.exists():
        return False
    source_files = sorted(path for path in MODEL_ICONS.rglob("*") if path.is_file() and should_archive(path))
    changed = False
    for source in source_files:
        target = MODEL_ICON_ARTIFACTS / source.relative_to(MODEL_ICONS)
        if not target.exists() or target.read_bytes() != source.read_bytes():
            changed = True
            break
    existing_targets = sorted(path for path in MODEL_ICON_ARTIFACTS.rglob("*") if path.is_file()) if MODEL_ICON_ARTIFACTS.exists() else []
    expected_targets = {MODEL_ICON_ARTIFACTS / source.relative_to(MODEL_ICONS) for source in source_files}
    if any(path not in expected_targets for path in existing_targets):
        changed = True
    if changed and write:
        if MODEL_ICON_ARTIFACTS.exists():
            shutil.rmtree(MODEL_ICON_ARTIFACTS)
        for source in source_files:
            target = MODEL_ICON_ARTIFACTS / source.relative_to(MODEL_ICONS)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return changed


def sync_model_example_artifacts(write: bool) -> bool:
    source_files: List[Tuple[str, Path, Path]] = []
    for model_dir in sorted(path for path in SINGLE_MODELS.iterdir() if path.is_dir()):
        examples_dir = model_dir / MODEL_EXAMPLES_DIR_NAME
        if examples_dir.exists():
            source_files.extend(
                (model_dir.name, path, path.relative_to(examples_dir))
                for path in sorted(examples_dir.rglob("*"))
                if path.is_file() and should_archive(path)
            )

    expected_targets = {
        MODEL_EXAMPLE_ARTIFACTS / model_id / relative_path
        for model_id, _, relative_path in source_files
    }
    existing_targets = sorted(path for path in MODEL_EXAMPLE_ARTIFACTS.rglob("*") if path.is_file()) if MODEL_EXAMPLE_ARTIFACTS.exists() else []
    changed = any(path not in expected_targets for path in existing_targets)
    if not changed:
        for model_id, source, relative_path in source_files:
            target = MODEL_EXAMPLE_ARTIFACTS / model_id / relative_path
            if not target.exists() or target.read_bytes() != source.read_bytes():
                changed = True
                break
    if changed and write:
        if MODEL_EXAMPLE_ARTIFACTS.exists():
            shutil.rmtree(MODEL_EXAMPLE_ARTIFACTS)
        for model_id, source, relative_path in source_files:
            target = MODEL_EXAMPLE_ARTIFACTS / model_id / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return changed


def sync_model_i18n_artifacts(write: bool) -> bool:
    source_files: List[Tuple[str, Path, Path]] = []
    for model_dir in sorted(path for path in SINGLE_MODELS.iterdir() if path.is_dir()):
        i18n_dir = model_dir / MODEL_I18N_DIR_NAME
        if i18n_dir.exists():
            source_files.extend(
                (model_dir.name, path, path.relative_to(i18n_dir))
                for path in sorted(i18n_dir.rglob("*"))
                if path.is_file() and should_archive(path)
            )

    expected_targets = {
        MODEL_I18N_ARTIFACTS / model_id / relative_path
        for model_id, _, relative_path in source_files
    }
    existing_targets = sorted(path for path in MODEL_I18N_ARTIFACTS.rglob("*") if path.is_file()) if MODEL_I18N_ARTIFACTS.exists() else []
    changed = any(path not in expected_targets for path in existing_targets)
    if not changed:
        for model_id, source, relative_path in source_files:
            target = MODEL_I18N_ARTIFACTS / model_id / relative_path
            if not target.exists() or target.read_bytes() != source.read_bytes():
                changed = True
                break
    if changed and write:
        if MODEL_I18N_ARTIFACTS.exists():
            shutil.rmtree(MODEL_I18N_ARTIFACTS)
        for model_id, source, relative_path in source_files:
            target = MODEL_I18N_ARTIFACTS / model_id / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return changed


def model_files() -> List[Path]:
    return sorted(SINGLE_MODELS.glob("*/model.json"))


def load_model(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    data = read_json(path)
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ValueError(f"{rel(path)} ist kein OpenWebUI-Modellarray")
    return data, data[0]


def is_non_chat_model(model: Dict[str, Any]) -> bool:
    meta = model.get("meta", {}) if isinstance(model.get("meta"), dict) else {}
    haystack = " ".join(
        [
            str(model.get("id", "")),
            str(model.get("name", "")),
            str(model.get("base_model_id", "")),
            str(meta.get("description", "")),
            " ".join(str(tag.get("name", "")) for tag in meta.get("tags", []) if isinstance(tag, dict)),
        ]
    ).lower()
    if any(marker in haystack for marker in EXCLUDED_MODEL_MARKERS):
        return True
    caps = meta.get("capabilities", {}) if isinstance(meta.get("capabilities"), dict) else {}
    return bool(caps.get("embedding") or caps.get("reranking") or caps.get("reranker"))


def merge_unique(existing: Any, required: Any) -> List[str]:
    values = existing if isinstance(existing, list) else []
    required_values = required if isinstance(required, list) else []
    merged: List[str] = []
    for value in [*values, *required_values]:
        if isinstance(value, str) and value not in merged:
            merged.append(value)
    return merged


def profile_for_model(model_id: str) -> dict[str, Any]:
    return TOOL_FORCE_PROFILES.get(
        model_id,
        TOOL_FORCE_PROFILES["offline-workbench-agent"],
    )


def selected_tool_ids_for_model(model_id: str, valid_tool_ids: set[str]) -> list[str]:
    profile = profile_for_model(model_id)
    requested = list(dict.fromkeys(profile.get("tools", [])))
    unknown = sorted(set(requested) - set(valid_tool_ids))
    if unknown:
        raise ValueError(
            f"{model_id}: TOOL_FORCE_PROFILES enthält unbekannte oder nicht importierbare Tools: {unknown}"
        )
    return requested


def selected_skill_ids_for_model(model_id: str, valid_skill_ids: set[str]) -> list[str]:
    profile = profile_for_model(model_id)
    requested = list(dict.fromkeys(profile.get("skills", [])))
    unknown = sorted(set(requested) - set(valid_skill_ids))
    if unknown:
        raise ValueError(
            f"{model_id}: TOOL_FORCE_PROFILES enthält unbekannte oder nicht importierbare Skills: {unknown}"
        )
    return requested


def read_utf8_required(path: Path, model_id: str, logical_name: str) -> str:
    if not path.exists():
        raise ValueError(f"{model_id}: Pflichtdatei fehlt: {path}")
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    if not text:
        raise ValueError(f"{model_id}: Pflichtdatei ist leer: {path}")
    return text


def read_utf8_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()


def truncate_example_for_system_context(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    head_budget = int(max_chars * 0.70)
    tail_budget = max_chars - head_budget
    return (
        text[:head_budget].rstrip()
        + "\n\n[... Beispiel für Systemkontext gekürzt; vollständiges Beispiel bleibt über Knowledge/RAG verfügbar ...]\n\n"
        + text[-tail_budget:].lstrip()
    )


def score_example_file(model_id: str, path: Path, profile_focus: str = "") -> tuple[int, str]:
    rel_path = path.as_posix().lower()
    score = 0
    for term in EXAMPLE_PRIORITY_TERMS.get("default", []):
        if term in rel_path:
            score += 10
    for term in EXAMPLE_PRIORITY_TERMS.get(model_id, []):
        if term in rel_path:
            score += 15
    for term in re.findall(r"[a-zA-ZäöüÄÖÜß0-9_-]{4,}", profile_focus.lower()):
        if term in rel_path:
            score += 3
    return (-score, rel_path)


def select_best_example_files_for_model(model_dir: Path, model_id: str, profile_focus: str) -> List[Path]:
    examples_dir = model_dir / MODEL_EXAMPLES_DIR_NAME
    if not examples_dir.exists():
        return []
    example_files = sorted(path for path in examples_dir.rglob("*") if path.is_file() and should_archive(path))
    if not example_files:
        return []
    prioritized = sorted(example_files, key=lambda p: score_example_file(model_id, p, profile_focus))
    return prioritized[:COMPILED_EXAMPLES_MAX_FILES]


def compile_mandatory_context_for_model(model_id: str, model_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    profile = profile_for_model(model_id)
    profile_focus = str(profile.get("focus", ""))
    parts: list[str] = []
    manifest: list[dict[str, Any]] = []

    def append_text(logical_name: str, rel_path: str, content: str) -> None:
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        parts.append("")
        parts.append(f"# Datei: {rel_path}")
        parts.append("")
        parts.append(content)
        manifest.append(
            {
                "path": rel_path,
                "logicalName": logical_name,
                "sha256": sha256,
                "chars": len(content),
            }
        )

    parts.append(COMPILED_CONTEXT_MARKER)
    parts.append("")
    parts.append(
        "Die folgenden Inhalte sind verbindlicher, bereits geladener Systemkontext. "
        "Sie sind nicht optionales RAG-Wissen. Rolle, Hauptauftrag, Fachwissen, "
        "Ausgabeformat und Beispielmuster müssen ab dem ersten Nutzerprompt angewendet werden. "
        "Knowledge/RAG soll zusätzlich gezielt genutzt werden, wenn dadurch ein passenderes Ergebnis entsteht."
    )

    systemprompt_file = model_dir / "systemprompt.md"
    if systemprompt_file.exists():
        append_text("systemprompt", "systemprompt.md", read_utf8_required(systemprompt_file, model_id, "systemprompt"))
    for filename in required_model_knowledge_files(model_id):
        append_text(filename, filename, read_utf8_required(model_dir / filename, model_id, filename))

    selected_examples = select_best_example_files_for_model(model_dir, model_id, profile_focus)
    remaining_budget = COMPILED_EXAMPLES_MAX_CHARS_TOTAL
    for path in selected_examples:
        if remaining_budget <= 0:
            break
        raw = read_utf8_optional(path)
        if not raw:
            continue
        max_for_file = min(COMPILED_EXAMPLE_MAX_CHARS, remaining_budget)
        truncated = truncate_example_for_system_context(raw, max_for_file)
        remaining_budget -= len(truncated)
        append_text(
            "beispielanker",
            path.relative_to(model_dir).as_posix(),
            truncated,
        )

    compiled = "\n".join(parts).strip() + "\n"
    if len(compiled) > COMPILED_SYSTEM_MAX_CHARS:
        raise ValueError(
            f"{model_id}: kompilierter Pflichtkontext ist zu groß: "
            f"{len(compiled)} Zeichen > {COMPILED_SYSTEM_MAX_CHARS}. "
            "Nicht automatisch auf RAG verschieben. Beispielanker reduzieren oder Limit bewusst anpassen."
        )
    return compiled, manifest


def temperature_for_model(model_id: str) -> float:
    # Konsistente moderate Temperatur für Chat-Profile.
    return MODEL_TEMPERATURES.get(model_id, DEFAULT_CHAT_TEMPERATURE)


def top_p_for_temperature(temperature: float) -> float:
    if temperature <= 0.2:
        return 0.8
    if temperature <= 0.45:
        return 0.9
    return 0.95


def tool_force_block_for_model(model_id: str) -> str:
    profile = TOOL_FORCE_PROFILES.get(model_id, TOOL_FORCE_PROFILES["offline-workbench-agent"])
    if model_id == "allgemein":
        tools = "alle in `meta.toolIds` tatsächlich verfügbaren Tools der Instanz"
    else:
        tools = ", ".join(f"`{tool}`" for tool in profile["tools"])
    skills = ", ".join(f"`{skill}`" for skill in profile["skills"])
    focus = profile["focus"]
    return f"""{TOOL_FORCE_SYSTEM_MARKER}

- Beginne jede nicht-triviale Aufgabe mit einer kurzen Tool-/Skill-Inventur anhand verfügbarer Tools, Skills, Dateien, Knowledge und Zielartefakte.
- Nutze passende Tools früh und mit dem kleinsten ausreichenden Tool-Satz; verschweige fehlende Tools, Fehler oder Grenzen nicht.
- Primäre Tools: {tools}. Relevante Skills: {skills}. Fokus: {focus}
"""


def tool_call_playbook_block_for_model(model_id: str) -> str:
    return f"""{TOOL_CALL_PLAYBOOK_SYSTEM_MARKER}

- Prüfe OpenWebUI-Builtins wie Datei-/Knowledge-Kontext, Citations, Statusmeldungen, Code Interpreter, native Tool-Calls und `openwebui-offline-addons` vor Spezialtools.
- Wenn passend, nutze zuerst eines der primären Modelltools aus dem Tool-Profil unten.
- Bei unabhängigen Teilaufgaben sind Parallelisierung oder Subagenten zu bevorzugen; bei Dateien, Code, Tabellen, HTML/PDF/Präsentationen, APIs, Docker/OpenWebUI-Fehlern oder visuellen Artefakten muss ein geeignetes Tool geprüft werden.
"""


def ensure_high_reasoning_profile(system_prompt: Any) -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    legacy_line = (
        "- Die Modellprofile erlauben bis zu " + "256" + "k Tokens über `max_tokens`, "
        "setzen aber keine nicht unterstützten Runtime-Parameter wie `num_ctx`, `top_k` oder `seed`."
    )
    previous_default_line = "- Die Modellprofile setzen keine festen Laufzeitwerte wie `max_tokens`, `temperature`, `top_p`, `reasoning_effort`, `num_ctx`, `top_k` oder `seed`; die Zielinstanz verwendet ihre eigenen Defaults."
    tuned_line = "- Die Modellprofile setzen `reasoning_effort=high`, `temperature=0.7`, `top_p=0.95`, native Tool-Calls und parallele Tool-Calls, aber kein festes `max_tokens`; die Zielinstanz bestimmt Kontext- und Antwortlimits."
    current_line = "- Arbeite im Reasoning-Profil `high`: Plane schwierige Aufgaben intern gründlich, prüfe Zwischenergebnisse und validiere Tool-Ausgaben kritisch."
    upgraded_line = "- Arbeite grundsätzlich im Reasoning-Profil `high`: Plane schwierige Aufgaben intern gründlich, prüfe Zwischenergebnisse und validiere Tool-Ausgaben kritisch. Gib keine verborgene Herleitung aus; liefere nur das fachlich notwendige Ergebnis."
    if HIGH_REASONING_SYSTEM_MARKER in system_prompt:
        return (
            system_prompt.replace(legacy_line, tuned_line)
            .replace(previous_default_line, tuned_line)
            .replace(current_line, upgraded_line)
        )
    for marker in [CUSTOM_GPT_QUALITY_SYSTEM_MARKER, TOOL_CALL_PLAYBOOK_SYSTEM_MARKER, TOOL_FORCE_SYSTEM_MARKER]:
        marker_index = system_prompt.find(marker)
        if marker_index != -1:
            insert_index = system_prompt.rfind("\n\n", 0, marker_index)
            if insert_index == -1:
                insert_index = marker_index
                separator = "\n\n"
            else:
                separator = ""
            return f"{system_prompt[:insert_index]}{separator}{HIGH_REASONING_SYSTEM_BLOCK}{system_prompt[insert_index:]}"
    insert_before = "\n\n        # Systemprompt"
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {HIGH_REASONING_SYSTEM_BLOCK.replace(chr(10), chr(10) + '        ')}{insert_before}", 1)
    return f"{HIGH_REASONING_SYSTEM_BLOCK}\n\n{system_prompt}"


def ensure_custom_gpt_quality_profile(system_prompt: Any, model_id: str = "") -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    block = custom_gpt_quality_system_block_for_model(model_id).rstrip()
    start = system_prompt.find(CUSTOM_GPT_QUALITY_SYSTEM_MARKER)
    if start != -1:
        next_heading = re.search(r"\n\n[ \t]*## ", system_prompt[start + len(CUSTOM_GPT_QUALITY_SYSTEM_MARKER) :])
        if next_heading:
            cut = start + len(CUSTOM_GPT_QUALITY_SYSTEM_MARKER) + next_heading.start()
            return f"{system_prompt[:start]}{block}{system_prompt[cut:]}"
        return f"{system_prompt[:start]}{block}"
    insert_before = f"\n\n        {TOOL_CALL_PLAYBOOK_SYSTEM_MARKER}"
    indented_block = block.replace(chr(10), chr(10) + "        ")
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {indented_block}{insert_before}", 1)
    insert_before = f"\n\n        {TOOL_FORCE_SYSTEM_MARKER}"
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {indented_block}{insert_before}", 1)
    insert_before = "\n\n        # Systemprompt"
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {indented_block}{insert_before}", 1)
    return f"{block}\n\n{system_prompt}"


def ensure_tool_call_playbook(system_prompt: Any, model_id: str) -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    block = tool_call_playbook_block_for_model(model_id).rstrip()
    start = system_prompt.find(TOOL_CALL_PLAYBOOK_SYSTEM_MARKER)
    if start != -1:
        next_heading = re.search(r"\n\n[ \t]*#", system_prompt[start + len(TOOL_CALL_PLAYBOOK_SYSTEM_MARKER) :])
        if next_heading:
            cut = start + len(TOOL_CALL_PLAYBOOK_SYSTEM_MARKER) + next_heading.start()
            return f"{system_prompt[:start]}{block}{system_prompt[cut:]}"
        return f"{system_prompt[:start]}{block}"
    insert_before = f"\n\n        {TOOL_FORCE_SYSTEM_MARKER}"
    indented_block = block.replace(chr(10), chr(10) + "        ")
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {indented_block}{insert_before}", 1)
    insert_before = "\n\n        # Systemprompt"
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {indented_block}{insert_before}", 1)
    return f"{block}\n\n{system_prompt}"


def ensure_tool_force_profile(system_prompt: Any, model_id: str) -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    block = tool_force_block_for_model(model_id).rstrip()
    start = system_prompt.find(TOOL_FORCE_SYSTEM_MARKER)
    if start != -1:
        next_heading = re.search(r"\n\n[ \t]*#", system_prompt[start + len(TOOL_FORCE_SYSTEM_MARKER) :])
        if next_heading:
            cut = start + len(TOOL_FORCE_SYSTEM_MARKER) + next_heading.start()
            return f"{system_prompt[:start]}{block}{system_prompt[cut:]}"
        return f"{system_prompt[:start]}{block}"
    insert_before = "\n\n        # Systemprompt"
    indented_block = block.replace(chr(10), chr(10) + "        ")
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {indented_block}{insert_before}", 1)
    return f"{block}\n\n{system_prompt}"


def strip_markdown_formatting_marker(system_prompt: str) -> str:
    stripped = system_prompt.lstrip()
    if not stripped.startswith(MARKDOWN_FORMATTING_MARKER):
        return system_prompt
    return stripped[len(MARKDOWN_FORMATTING_MARKER) :].lstrip()


def strip_managed_system_sections(system_prompt: str) -> str:
    lines = system_prompt.splitlines()
    cleaned: List[str] = []
    skip_managed_section = False
    for line in lines:
        is_heading = bool(re.match(r"^\s*#", line))
        is_managed_heading = any(marker in line for marker in MANAGED_SYSTEM_SECTION_MARKERS)
        if is_managed_heading:
            skip_managed_section = True
            while cleaned and not cleaned[-1].strip():
                cleaned.pop()
            continue
        if skip_managed_section and is_heading:
            skip_managed_section = False
        if skip_managed_section:
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def managed_system_profile_for_model(model_id: str) -> str:
    sections = [
        HIGH_REASONING_SYSTEM_BLOCK.rstrip(),
        custom_gpt_quality_system_block_for_model(model_id).rstrip(),
        VISION_SYSTEM_BLOCK.rstrip(),
        tool_call_playbook_block_for_model(model_id).rstrip(),
        tool_force_block_for_model(model_id).rstrip(),
    ]
    return "\n\n".join(sections)


def systemprompt_source_for_model(model_id: str) -> str:
    model_dir = SINGLE_MODELS / model_id
    golden_file = golden_example_file_for_model(model_dir).name
    extra_rule = MODEL_BOOTLOADER_EXTRA_RULES.get(model_id, "")
    extra_rule_block = f"\n\n{extra_rule}" if extra_rule else ""
    code_rule = (
        "\n\nBei Codeaufgaben orientiere Implementierung, Tests, Fehlerbehandlung, Struktur und Robustheit an "
        f"`{golden_file}`."
        if model_id in CODE_OR_TECHNICAL_MODEL_IDS
        else ""
    )
    return f"""# Rolle

Du bist das Workbench-Modell `{model_id}` für den in `mainprompt.md` definierten Auftrag.

# Pflichtkontext

Vor jeder Antwort werden `mainprompt.md`, `fachwissen.md` und `{golden_file}` als vollständige Workbench-Pflichtdateien bereitgestellt. Werte alle drei aus, bevor du antwortest.

`mainprompt.md` definiert Auftrag, Scope und Ausgabeziel. `fachwissen.md` definiert verbindliche Fachregeln. `{golden_file}` ist der verbindliche Qualitäts-, Struktur-, Stil- und Formatanker. Übernimm dessen Muster und Qualitätsniveau, ohne irrelevante Inhalte blind zu kopieren.

# Beispiele und RAG

Weitere Beispiele liegen in der Knowledgebase unter `beispiele/`. Nutze sie nur bei Bedarf und höchstens 1-2 passende Beispiele pro Antwort. Die Pflichtdateien sind kein optionales RAG-Wissen.

# Ausführung

Nutze Tools und Skills, wenn sie das Ergebnis verbessern. Erfinde keine Fakten, APIs, Quellen, Dateiinhalte oder Ergebnisse. Benenne fehlenden Kontext knapp.{code_rule}{extra_rule_block}"""


def has_short_bootloader_systemprompt(system_text: str, model_id: str) -> bool:
    model_dir = SINGLE_MODELS / model_id
    try:
        golden_name = golden_example_file_for_model(model_dir).name
    except ValueError:
        golden_name = "Golden_Example."
    return (
        "Workbench-Modell" in system_text
        and "Werte alle drei aus" in system_text
        and "mainprompt.md" in system_text
        and "fachwissen.md" in system_text
        and golden_name in system_text
        and "Golden_Example" in system_text
        and "höchstens 1-2 passende Beispiele" in system_text
        and "Erfinde keine Fakten" in system_text
        and WORKBENCH_REQUIRED_FILE_CONTEXT_MARKER not in system_text
        and len(system_text) <= WORKBENCH_SYSTEMPROMPT_MAX_CHARS
    )


def ensure_markdown_formatting_enabled(system_prompt: Any) -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    stripped = system_prompt.lstrip()
    if stripped.startswith(MARKDOWN_FORMATTING_MARKER):
        return system_prompt
    return f"{MARKDOWN_FORMATTING_MARKER}\n\n{system_prompt}"


def normalize_base_prompt_text(system_prompt: str) -> str:
    replacements = {
        "`systemprompt.md`, `mainprompt.md` und `fachwissen.md`": "`systemprompt.md`, `mainprompt.md`, `fachwissen.md`, die modellseitig definierte Beispielergebnis-Datei sowie Dateien unter `beispiele/` und `i18n/`",
        "`mainprompt.md` und `fachwissen.md`": "`mainprompt.md`, `fachwissen.md`, die modellseitig definierte Beispielergebnis-Datei sowie Dateien unter `beispiele/` und `i18n/`",
        "Systemprompt, Mainprompt und Fachwissen": "Systemprompt, Mainprompt, Fachwissen, Beispielwissen und Produktsprachen",
        "systemprompt.md, mainprompt.md und fachwissen.md": "systemprompt.md, mainprompt.md, fachwissen.md, modellseitig definierte Beispielergebnis-Datei, beispiele/ und i18n/",
    }
    normalized = system_prompt
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def configure_runtime_params(model_id: str, params: Dict[str, Any]) -> None:
    system_prompt = systemprompt_source_for_model(model_id)
    params.clear()
    params["system"] = system_prompt.strip()
    params["temperature"] = WORKBENCH_TEMPERATURE
    params["top_p"] = WORKBENCH_TOP_P
    params["stop"] = []
    params["function_calling"] = WORKBENCH_FUNCTION_CALLING
    params["reasoning_effort"] = WORKBENCH_REASONING_EFFORT
    params["parallel_tool_calls"] = WORKBENCH_PARALLEL_TOOL_CALLS


def icon_data_uri_for_model(model_id: str) -> str:
    if not MODEL_ICON_MANIFEST.exists():
        return "/static/favicon.png"
    manifest = read_json(MODEL_ICON_MANIFEST)
    icon_id = manifest.get("suggested_model_icons", {}).get(model_id) if isinstance(manifest, dict) else None
    icons = manifest.get("icons", []) if isinstance(manifest, dict) else []
    for icon in icons:
        if isinstance(icon, dict) and icon.get("id") == icon_id:
            icon_path = ROOT / str(icon.get("png_path") or icon.get("path", ""))
            if icon_path.exists() and icon_path.suffix.lower() == ".png":
                encoded = base64.b64encode(icon_path.read_bytes()).decode("ascii")
                return f"data:image/png;base64,{encoded}"
    return "/static/favicon.png"


def tool_ids_for_model(model_id: str, offline_tool_ids: List[str], all_tool_ids: List[str]) -> List[str]:
    return list(selected_tool_ids_for_model(model_id, set(all_tool_ids)))


def configure_model(model: Dict[str, Any], offline_tool_ids: List[str], filter_ids: List[str], all_tool_ids: List[str]) -> Dict[str, Any]:
    model = json.loads(json.dumps(model, ensure_ascii=False))
    meta = model.setdefault("meta", {})
    params = model.setdefault("params", {})
    if not isinstance(meta, dict) or not isinstance(params, dict):
        raise ValueError(f"Modell {model.get('id')} hat unerwartete meta/params-Struktur")
    capabilities = meta.setdefault("capabilities", {})
    if not isinstance(capabilities, dict):
        raise ValueError(f"Modell {model.get('id')} hat unerwartete capabilities-Struktur")

    if is_non_chat_model(model):
        meta.pop("toolIds", None)
        meta.pop("filterIds", None)
        meta.pop("defaultFilterIds", None)
        params.pop("function_calling", None)
        capabilities["builtin_tools"] = False
        capabilities["code_interpreter"] = False
        return model

    model_id = str(model.get("id", ""))
    profile = profile_for_model(model_id)
    model_dir = SINGLE_MODELS / model_id
    required_sources = required_file_context_sources(model_id, model_dir)
    example_knowledge = [path.relative_to(model_dir).as_posix() for path in model_knowledge_files(model_id)]
    model["base_model_id"] = workbench_base_model_id()
    meta["profile_image_url"] = icon_data_uri_for_model(model_id)
    meta.pop("localCoderProfile", None)
    meta["toolIds"] = tool_ids_for_model(model_id, offline_tool_ids, all_tool_ids)
    meta["filterIds"] = merge_unique(REQUIRED_DEFAULT_FILTER_IDS, merge_unique(filter_ids, meta.get("filterIds")))
    meta["defaultFilterIds"] = merge_unique(
        REQUIRED_DEFAULT_FILTER_IDS,
        merge_unique(filter_ids, meta.get("defaultFilterIds")),
    )
    meta["primaryToolIds"] = selected_tool_ids_for_model(model_id, set(all_tool_ids))
    meta["skillIds"] = selected_skill_ids_for_model(model_id, set(skill_ids()))
    meta["recommendedSkillIds"] = list(meta["skillIds"])
    meta.pop("coderRuntimeProfile", None)
    meta.pop("requiredKnowledgeFiles", None)
    meta.pop("deterministicContext", None)
    meta["requiredFileContextFiles"] = [item["path"] for item in required_sources]
    meta["exampleKnowledgeFiles"] = example_knowledge
    legacy_example = legacy_example_result_file_for_model(model_id)
    meta["legacyExampleResult"] = legacy_example if (model_dir / legacy_example).exists() else None
    meta["workbenchFileContext"] = {
        "schema": WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA,
        "mode": "required_full_context_files_plus_examples_rag",
        "injectionFilterId": WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID,
        "requiredFiles": required_sources,
        "exampleKnowledgePolicy": {
            "sourceDir": f"{MODEL_EXAMPLES_DIR_NAME}/",
            "mode": "focused_retrieval_on_demand",
            "maxExamplesPerAnswer": 2,
        },
        "knowledgeRetrievalRequiredForCoreBehavior": False,
    }
    meta["defaultLocale"] = "de"
    meta["fallbackLocale"] = "en"
    meta["supportedLocales"] = list(SUPPORTED_PRODUCT_LOCALES)
    meta["productLocaleFiles"] = [f"{MODEL_I18N_DIR_NAME}/{locale}.md" for locale in SUPPORTED_PRODUCT_LOCALES]
    configure_runtime_params(model_id, params)
    capabilities["builtin_tools"] = True
    capabilities["file_context"] = bool(capabilities.get("file_context", True))
    capabilities["vision"] = True
    capabilities["file_upload"] = bool(capabilities.get("file_upload", True))
    capabilities["code_interpreter"] = True if is_cloud_coder_production_model(model_id) else bool(capabilities.get("code_interpreter", True))
    capabilities["status_updates"] = True if is_cloud_coder_production_model(model_id) else bool(capabilities.get("status_updates", True))
    capabilities["usage"] = bool(capabilities.get("usage", True))
    if capabilities["code_interpreter"]:
        features = meta.setdefault("defaultFeatureIds", [])
        if isinstance(features, list) and "code_interpreter" not in features:
            features.append("code_interpreter")
    else:
        features = meta.get("defaultFeatureIds")
        if isinstance(features, list) and not features:
            meta.pop("defaultFeatureIds", None)
    return model


def skill_ids() -> List[str]:
    if not SKILLS_DIR.exists():
        return []
    return sorted(path.stem for path in SKILLS_DIR.glob("*.md") if path.name.upper() != "README.MD")


def model_knowledge_files(model_id: str) -> List[Path]:
    model_dir = SINGLE_MODELS / model_id
    files: List[Path] = []
    legacy_example = model_dir / legacy_example_result_file_for_model(model_id)
    if legacy_example.is_file() and should_archive(legacy_example):
        files.append(legacy_example)
    files.extend(model_example_files(model_id))
    files.extend(model_i18n_files(model_id))
    return files


def model_example_files(model_id: str) -> List[Path]:
    examples_dir = SINGLE_MODELS / model_id / MODEL_EXAMPLES_DIR_NAME
    if not examples_dir.exists():
        return []
    return sorted(path for path in examples_dir.rglob("*") if path.is_file() and should_archive(path))


def model_i18n_files(model_id: str) -> List[Path]:
    i18n_dir = SINGLE_MODELS / model_id / MODEL_I18N_DIR_NAME
    if not i18n_dir.exists():
        return []
    return [path for name in PRIMARY_MODEL_I18N_FILES if (path := i18n_dir / name).is_file() and should_archive(path)]


def model_knowledge_status(model_id: str) -> Dict[str, Dict[str, Any]]:
    status: Dict[str, Dict[str, Any]] = {}
    model_dir = SINGLE_MODELS / model_id
    for path in model_knowledge_files(model_id):
        exists = path.exists()
        size = len(stable_text_bytes(path)) if exists else 0
        try:
            key = path.relative_to(model_dir).as_posix()
        except ValueError:
            key = path.name
        status[key] = {
            "path": rel(path),
            "exists": exists,
            "non_empty": size > 0,
            "bytes": size,
        }
    return status


def apply_model_config(tool_records: List[ToolRecord], function_records: List[FunctionRecord], write: bool) -> Tuple[bool, List[Dict[str, Any]]]:
    offline_tool_ids = [record.id for record in offline_default_tool_records(tool_records)]
    all_tool_ids = [record.id for record in tool_records if record.importable]
    filter_ids = [record.id for record in function_records if record.importable and record.function_type == "filter"]
    changed = False
    configured_models: List[Dict[str, Any]] = []
    for path in model_files():
        data, original = load_model(path)
        configured = configure_model(original, offline_tool_ids, filter_ids, all_tool_ids)
        configured_models.append(configured)
        new_data = [configured]
        model_id = str(configured.get("id", ""))
        systemprompt_path = path.parent / "systemprompt.md"
        systemprompt_source = systemprompt_source_for_model(model_id)
        if new_data != data:
            changed = True
            if write:
                write_json(path, new_data)
        if not systemprompt_path.exists() or systemprompt_path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() != systemprompt_source.rstrip():
            changed = True
            if write:
                write_text(systemprompt_path, systemprompt_source)
    if write:
        write_json(MODEL_IMPORT, configured_models)
        write_json(MODEL_FALLBACK, configured_models)
        MODEL_ARTIFACTS.mkdir(parents=True, exist_ok=True)
        for model in configured_models:
            write_json(MODEL_ARTIFACTS / f"{model['id']}.model.json", [model])
    return changed, configured_models


def write_model_params_summary(models: List[Dict[str, Any]], write: bool) -> bool:
    def has_prompt_sections(model: Dict[str, Any]) -> bool:
        params = model.get("params", {})
        if not isinstance(params, dict):
            return False
        system_text = str(params.get("system", ""))
        return all(marker in system_text for marker in ["Systemprompt", "Mainprompt", "Fachwissen"])

    summary = {
        "schema": "openwebui-model-params-summary/v1",
        "max_tokens_policy": "omitted; target OpenWebUI/model-server limits are used.",
        "supported_runtime_params": sorted(SUPPORTED_CHAT_RUNTIME_PARAMS),
        "omitted_runtime_params": OMITTED_RUNTIME_PARAMS,
        "omitted_unsupported_runtime_params": OMITTED_UNSUPPORTED_RUNTIME_PARAMS,
        "base_model_policy": "All chat models target the selected OpenWebUI base model, defaulting to `coder`, with `reasoning_effort=high`, `parallel_tool_calls=true`, `temperature=0.7`, `top_p=0.95` and native tool calling.",
        "vision_policy": "All chat model profiles enable OpenWebUI vision capability and include prompt rules for screenshot, UI, chart, scan, presentation and visual artifact analysis when the selected backing model supports image inputs.",
        "openwebui_builtin_and_addon_policy": "Chat models prefer standard OpenWebUI builtins and the mounted openwebui-offline-addons runtime for local caches, Playwright/Chromium, Tiktoken, NLTK and Python packages when available.",
        "offline_excluded_tool_ids": sorted(OFFLINE_EXCLUDED_TOOL_IDS),
        "product_i18n_policy": {
            "default_locale": "de",
            "fallback_locale": "en",
            "supported_locales": SUPPORTED_PRODUCT_LOCALES,
            "locale_dir": MODEL_I18N_DIR_NAME,
            "dist_i18n_dir": rel(MODEL_I18N_ARTIFACTS),
            "behavior": "Every chat model ships localized product metadata and product profiles. German remains the default; unsupported or uncertain locales fall back to German.",
        },
        "models": [
            {
                "id": model.get("id"),
                "name": model.get("name"),
                "product_i18n_locales": sorted(
                    (model.get("meta", {}).get("productI18n", {}) if isinstance(model.get("meta"), dict) else {}).keys()
                ),
                "params": model.get("params", {}) if isinstance(model.get("params"), dict) else {},
                "product_locale_files": model.get("meta", {}).get("productLocaleFiles", []) if isinstance(model.get("meta"), dict) else [],
                "temperature": model.get("params", {}).get("temperature") if isinstance(model.get("params"), dict) else None,
                "top_p": model.get("params", {}).get("top_p") if isinstance(model.get("params"), dict) else None,
                "function_calling": model.get("params", {}).get("function_calling") if isinstance(model.get("params"), dict) else None,
                "runtime_param_keys": sorted(model.get("params", {}).keys()) if isinstance(model.get("params"), dict) else [],
                "has_markdown_formatting_enabled": str(model.get("params", {}).get("system", "")).lstrip().startswith(MARKDOWN_FORMATTING_MARKER)
                if isinstance(model.get("params"), dict)
                else False,
                "has_systemprompt_mainprompt_fachwissen": has_prompt_sections(model),
                "has_short_bootloader_systemprompt": has_short_bootloader_systemprompt(
                    str(model.get("params", {}).get("system", "")),
                    str(model.get("id")),
                )
                if isinstance(model.get("params"), dict)
                else False,
                "has_high_reasoning_profile": HIGH_REASONING_SYSTEM_MARKER in str(model.get("params", {}).get("system", ""))
                and "Reasoning-Profil `high`" in str(model.get("params", {}).get("system", ""))
                if isinstance(model.get("params"), dict)
                else False,
                "has_custom_gpt_quality_profile": CUSTOM_GPT_QUALITY_SYSTEM_MARKER in str(model.get("params", {}).get("system", ""))
                if isinstance(model.get("params"), dict)
                else False,
                "has_vision_profile": VISION_SYSTEM_MARKER in str(model.get("params", {}).get("system", ""))
                if isinstance(model.get("params"), dict)
                else False,
                "has_explicit_tool_call_playbook": TOOL_CALL_PLAYBOOK_SYSTEM_MARKER in str(model.get("params", {}).get("system", ""))
                if isinstance(model.get("params"), dict)
                else False,
                "has_openwebui_builtin_and_addon_policy": "OpenWebUI-Builtins" in str(model.get("params", {}).get("system", ""))
                and "openwebui-offline-addons" in str(model.get("params", {}).get("system", ""))
                if isinstance(model.get("params"), dict)
                else False,
                "system_prompt_chars": len(str(model.get("params", {}).get("system", ""))) if isinstance(model.get("params"), dict) else 0,
                "has_tool_force_profile": TOOL_FORCE_SYSTEM_MARKER in str(model.get("params", {}).get("system", ""))
                if isinstance(model.get("params"), dict)
                else False,
                "is_cloud_coder_production_profile": is_cloud_coder_production_model(str(model.get("id"))),
                "coder_runtime_profile": model.get("meta", {}).get("coderRuntimeProfile", {}) if isinstance(model.get("meta"), dict) else {},
                "primary_tool_ids": TOOL_FORCE_PROFILES.get(str(model.get("id")), {}).get("tools", []),
                "recommended_skill_ids": TOOL_FORCE_PROFILES.get(str(model.get("id")), {}).get("skills", []),
                "assigned_tool_ids": model.get("meta", {}).get("toolIds", []) if isinstance(model.get("meta"), dict) else [],
                "attached_skill_ids": model.get("meta", {}).get("skillIds", []) if isinstance(model.get("meta"), dict) else [],
                "required_file_context_files": model.get("meta", {}).get("requiredFileContextFiles", []) if isinstance(model.get("meta"), dict) else [],
                "example_knowledge_files": model.get("meta", {}).get("exampleKnowledgeFiles", []) if isinstance(model.get("meta"), dict) else [],
                "knowledge_files": model_knowledge_status(str(model.get("id"))),
                "vision_enabled": bool(
                    model.get("meta", {}).get("capabilities", {}).get("vision")
                    if isinstance(model.get("meta"), dict) and isinstance(model.get("meta", {}).get("capabilities"), dict)
                    else False
                ),
                "has_embedded_png_icon": str(model.get("meta", {}).get("profile_image_url", "")).startswith("data:image/png;base64,")
                if isinstance(model.get("meta"), dict)
                else False,
                "meta_primary_tool_ids": model.get("meta", {}).get("primaryToolIds", []) if isinstance(model.get("meta"), dict) else [],
                "meta_skill_ids": model.get("meta", {}).get("skillIds", []) if isinstance(model.get("meta"), dict) else [],
                "meta_recommended_skill_ids": model.get("meta", {}).get("recommendedSkillIds", []) if isinstance(model.get("meta"), dict) else [],
            }
            for model in models
        ],
    }
    changed = not MODEL_PARAMS_SUMMARY.exists() or read_json(MODEL_PARAMS_SUMMARY) != summary
    if changed and write:
        write_json(MODEL_PARAMS_SUMMARY, summary)
    return changed


def write_registration_plan(
    tool_records: List[ToolRecord],
    function_records: List[FunctionRecord],
    prompt_records: List[PromptRecord],
    models: List[Dict[str, Any]],
    write: bool,
) -> bool:
    filter_ids = [record.id for record in function_records if record.importable and record.function_type == "filter"]
    offline_tool_ids = [record.id for record in offline_default_tool_records(tool_records)]
    offline_tool_id_set = set(offline_tool_ids)
    optional_network_tool_ids = [record.id for record in tool_records if record.importable and record.id not in offline_tool_id_set]
    workspace_skill_ids = skill_ids()
    plan = {
        "schema": "openwebui-registration-plan/v1",
        "order": [
            "1_import_workspace_tools",
            "2_publish_tools_public",
            "3_apply_tool_valves",
            "4_import_workspace_filters",
            "5_enable_functions_global",
            "6_apply_function_filter_valves",
            "7_import_workspace_skills",
            "8_publish_skills_public",
            "9_import_workspace_prompts",
            "10_publish_prompts_public",
            "11_upload_model_required_file_context",
            "12_upload_model_example_knowledge",
            "13_publish_model_knowledge_public",
            "14_import_or_update_models",
            "15_publish_models_public",
        ],
        "api_import_script": rel(IMPORT_SCRIPT),
        "api_import_config_file": rel(CONFIG_FILE),
        "api_import_config_example": rel(CONFIG_EXAMPLE),
        "api_import_command": "python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml",
        "api_import_config_policy": {
            "source_of_truth": "scripts/openwebui_workspace_config.yaml",
            "example": rel(CONFIG_EXAMPLE),
            "sections": [
                "openwebui",
                "jupyter",
                "artifacts",
                "addons",
                "environment",
                "tool_valves",
                "function_valves",
                "model_file_context",
                "import",
            ],
            "auth": "Default is Authorization: Bearer <token>. For OpenWebUI CUSTOM_API_KEY_HEADER setups use openwebui.auth_header and openwebui.auth_scheme in the central YAML.",
            "behavior": "The importer reads the central YAML first and maps endpoint, token, backend-visible paths, tool valves, function/filter valves and required model-file-context settings into OpenWebUI before importing models. Tools, skills, prompt templates, example Knowledge and models are published with public read access; functions and filters are enabled and made global.",
        },
        "api_import_token": "openwebui.admin_token in scripts/openwebui_workspace_config.yaml; --token is only an explicit one-off override. The token must be an OpenWebUI API key or JWT for an admin user.",
        "public_access_policy": {
            "tools": "public_read_grant_after_upsert",
            "skills": "public_read_grant_after_upsert",
            "prompts": "public_read_grant_after_upsert",
            "model_knowledge": "public_read_grant_after_upsert",
            "models": "public_read_grant_after_import",
            "functions_and_filters": "active_and_global_after_upsert",
            "grant": PUBLIC_READ_GRANT,
        },
        "vision_policy": {
            "enabled_for_chat_models": True,
            "specialist_model_id": "mistral-vision-workbench",
            "behavior": "Vision remains enabled in model metadata. Detailed image, screenshot and artifact-QA rules live in Knowledge so the OpenWebUI system prompt can stay a short bootloader.",
        },
        "model_file_context_policy": {
            "schema": WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA,
            "required_files": ["mainprompt.md", "fachwissen.md", "Golden_Example.<ext>"],
            "injection_filter": WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID,
            "max_required_context_chars": WORKBENCH_REQUIRED_FILE_CONTEXT_MAX_CHARS,
            "behavior": "The importer uploads mainprompt.md, fachwissen.md and Golden_Example.<ext> as real OpenWebUI Files. The required-file-context filter attaches their file IDs and injects their stored content as protected full-context system block on every request.",
        },
        "model_example_policy": {
            "default_legacy_example_file": LEGACY_EXAMPLE_RESULT_FILE,
            "model_legacy_example_file_overrides": MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES,
            "example_dir": MODEL_EXAMPLES_DIR_NAME,
            "source_dir": f"{MODEL_EXAMPLES_DIR_NAME}/",
            "dist_examples_dir": rel(MODEL_EXAMPLE_ARTIFACTS),
            "behavior": "Files under beispiele/ and optional legacy beispielergebnis.* files are imported into per-model Knowledge for focused on-demand retrieval. The three required files are not the Knowledge/RAG core-behavior path.",
        },
        "model_product_i18n_policy": {
            "default_locale": "de",
            "fallback_locale": "en",
            "supported_locales": SUPPORTED_PRODUCT_LOCALES,
            "locale_dir": MODEL_I18N_DIR_NAME,
            "dist_i18n_dir": rel(MODEL_I18N_ARTIFACTS),
            "central_manifest": rel(ROOT / "Modelle" / "i18n" / "product-locales.json"),
            "behavior": "Each model package contains localized product names, descriptions, suggestions and Markdown profiles for all supported product locales. The API importer uploads these profiles into the per-model Knowledge collection.",
        },
        "offline_addons_runtime": {
            "host_reference": "F:\\offline-ai-stack\\openwebui-offline-addons",
            "container_data_root": "/app/backend/data",
            "container_cache_path": "/app/backend/data/cache",
            "container_python_path": "/app/backend/data/python",
            "container_nltk_data_path": "/app/backend/data/nltk_data",
            "container_playwright_browsers_path": "/app/backend/data/cache/ms-playwright",
            "config_keys": [
                "addons.root",
                "addons.python_path",
                "addons.playwright_browsers_path",
                "addons.nltk_data",
                "addons.prefer_playwright_pdf",
                "environment.OPENWEBUI_ARTIFACT_ROOT",
                "environment.OPENWEBUI_OFFLINE_ADDONS_ROOT",
                "environment.OPENWEBUI_OFFLINE_ADDONS_PYTHON_PATH",
                "environment.PLAYWRIGHT_BROWSERS_PATH",
                "environment.NLTK_DATA",
                "environment.TIKTOKEN_CACHE_DIR",
                "tool_valves.offline_artifact_workbench.artifact_root",
                "tool_valves.offline_artifact_workbench.offline_addons_root",
                "tool_valves.offline_artifact_workbench.offline_addons_python_path",
                "tool_valves.offline_artifact_workbench.playwright_browsers_path",
                "tool_valves.offline_artifact_workbench.nltk_data_path",
                "tool_valves.offline_artifact_workbench.prefer_playwright_pdf",
                "function_valves.auto_tool_selector.enable_local_tool_selection",
                "function_valves.auto_tool_selector.enable_mcp_tool_selection",
                "function_valves.auto_tool_selector.strict_available_tools_only",
                "function_valves.context_compressor_filter.default_context_window_tokens",
                "function_valves.context_compressor_filter.reserved_output_tokens",
                "function_valves.context_compressor_filter.safety_margin_tokens",
                "function_valves.context_compressor_filter.hard_guard_enabled",
                "function_valves.markdown_normalizer.enable_code_block_fix",
                "function_valves.markdown_normalizer.enable_latex_fix",
                "function_valves.markdown_normalizer.enable_mermaid_fix",
            ],
            "preferred_uses": [
                "OpenWebUI built-in caches and offline model assets",
                "local Playwright/Chromium rendering for HTML/PDF artifacts",
                "local Python packages for imported tools",
                "NLTK and Tiktoken resources for document and token tooling",
            ],
        },
        "tools_first": offline_tool_ids,
        "allgemein_model_tools": sorted(tool_ids_for_model("allgemein", offline_tool_ids, [record.id for record in tool_records if record.importable])),
        "tool_gui_import_file": rel(TOOL_IMPORT),
        "tool_gui_offline_import_file": rel(OFFLINE_TOOL_IMPORT),
        "offline_default_tools": offline_tool_ids,
        "optional_network_tools_not_in_offline_default": optional_network_tool_ids,
        "function_gui_import_file": rel(FUNCTION_IMPORT),
        "filters_before_models": filter_ids,
        "skills_before_models": workspace_skill_ids,
        "skill_source_dir": rel(SKILLS_DIR),
        "prompt_gui_import_file": rel(PROMPT_IMPORT),
        "prompts_before_models": [record.command for record in prompt_records if record.importable],
        "prompt_source_dir": rel(PROMPTS_DIR),
        "model_required_file_context_schema": WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA,
        "model_legacy_example_file": LEGACY_EXAMPLE_RESULT_FILE,
        "model_legacy_example_file_overrides": MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES,
        "model_product_locales_supported": SUPPORTED_PRODUCT_LOCALES,
        "knowledge_before_models": {
            str(model.get("id")): model_knowledge_status(str(model.get("id")))
            for model in models
            if not is_non_chat_model(model)
        },
        "model_import_file": rel(MODEL_IMPORT),
        "model_params_summary_file": rel(MODEL_PARAMS_SUMMARY),
        "generic_icon_manifest": rel(MODEL_ICON_ARTIFACTS / "openwebui-generic-icons.json"),
        "model_icon_policy": "profile_image_url uses embedded PNG data URIs generated from Modelle/icons/openwebui-generic-icons.json so OpenWebUI can serve profile images offline via /model/profile/image without external URLs or static mounts.",
        "tool_force_policy": {
            "behavior": "Standard chat models keep primaryToolIds, skillIds and recommendedSkillIds in metadata. OpenWebUI uses meta.skillIds for real model-attached Skills; recommendedSkillIds stays as an audit-friendly mirror.",
            "model_profiles": TOOL_FORCE_PROFILES,
            "code_capable_model_ids": sorted(CODE_OR_TECHNICAL_MODEL_IDS),
            "behavior_note": "All chat models, including code-oriented Workbench models, target the selected OpenWebUI base model while keeping model-attached tools, filters, skills and native function calling enabled.",
        },
        "tool_call_playbook_policy": {
            "target_model_runtime": "selected OpenWebUI base model",
            "behavior": "Tool-call guidance remains available through model metadata, tools and optional example Knowledge. The short system prompt tells the model to use tools and skills when they improve the result.",
            "required_prompt_phrases": [
                "Tools und Skills",
                "Golden_Example",
                "beispiele/",
            ],
        },
        "custom_gpt_quality_policy": {
            "formatting_marker": MARKDOWN_FORMATTING_MARKER,
            "system_prompt_max_chars": WORKBENCH_SYSTEMPROMPT_MAX_CHARS,
            "behavior": "Every chat model uses a short deterministic system prompt. It references mainprompt.md, fachwissen.md and Golden_Example.<ext> as required files; beispiele/ stays focused Knowledge/RAG material.",
        },
        "model_params_policy": {
            "max_tokens": "omitted",
            "runtime_defaults": "target OpenWebUI/model-server context and answer limits",
            "reasoning_profile": "runtime_param_high",
            "reasoning_effort_runtime_param": "reasoning_effort=high",
            "supported_runtime_params": sorted(SUPPORTED_CHAT_RUNTIME_PARAMS),
            "omitted_runtime_params": OMITTED_RUNTIME_PARAMS,
            "omitted_unsupported_runtime_params": OMITTED_UNSUPPORTED_RUNTIME_PARAMS,
            "temperature": WORKBENCH_TEMPERATURE,
            "top_p": WORKBENCH_TOP_P,
            "parallel_tool_calls": WORKBENCH_PARALLEL_TOOL_CALLS,
            "base_model_id": workbench_base_model_id(),
        },
        "global_model_params_recommendation": {
            "base_model_id": workbench_base_model_id(),
            "function_calling": WORKBENCH_FUNCTION_CALLING,
            "reasoning_effort": WORKBENCH_REASONING_EFFORT,
            "temperature": WORKBENCH_TEMPERATURE,
            "top_p": WORKBENCH_TOP_P,
            "parallel_tool_calls": WORKBENCH_PARALLEL_TOOL_CALLS,
        },
        "verified_model_fields_used": [
            "meta.toolIds",
            "meta.filterIds",
            "meta.defaultFilterIds",
            "meta.capabilities.builtin_tools",
            "meta.capabilities.vision",
            "meta.primaryToolIds",
            "meta.skillIds",
            "meta.recommendedSkillIds",
            "meta.requiredFileContextFiles",
            "meta.exampleKnowledgeFiles",
            "meta.workbenchFileContext",
            "meta.defaultLocale",
            "meta.fallbackLocale",
            "meta.supportedLocales",
            "meta.productLocaleFiles",
            "meta.productI18n",
            "params.function_calling",
            "params.temperature",
            "params.top_p",
            "params.stop",
            "params.system short bootloader",
            "params.system model-specific Knowledge references",
            "meta.profile_image_url",
        ],
        "builtin_tool_note": "OpenWebUI Built-in Tool categories are version-dependent. This project safely enables meta.capabilities.builtin_tools and params.function_calling=native, and the model prompts explicitly prefer standard OpenWebUI capabilities such as file/knowledge context, citations, status updates, code interpreter and native tool calls when the instance exposes them.",
        "skill_note": "OpenWebUI binds model-attached Skills through meta.skillIds. Skills are imported and published before models, then each chat model receives the profile-specific skillIds list so OpenWebUI can inject the lightweight Skill manifest and expose the view_skill builtin for lazy loading.",
        "offline_note": "The standard workflow is offline/air-gapped. Public network tools are not part of tools_first and are not assigned to any model by default. Optional network tools can still be imported explicitly for connected target instances.",
        "filter_note": "OpenWebUI filter functions are registered as Functions. The context compressor is assigned through meta.filterIds and enabled by default through meta.defaultFilterIds for every chat model. The API importer applies function/filter valves from scripts/openwebui_workspace_config.yaml after the functions are imported.",
        "knowledge_note": "The API importer uploads only example/RAG material such as beispiele/**, legacy beispielergebnis.* and primary product-i18n files into the per-model Knowledge collection. mainprompt.md, fachwissen.md and Golden_Example.<ext> are uploaded as OpenWebUI Files and injected by the required-file-context filter.",
        "icon_note": "Generic black-on-white PNG/SVG profile icons are shipped under Modelle/dist/artifacts/icons. Model profiles embed PNG data URIs in meta.profile_image_url because current OpenWebUI rejects SVG data URIs for profile images.",
        "chat_models_configured": [model["id"] for model in models if not is_non_chat_model(model)],
        "non_chat_models_excluded": [model["id"] for model in models if is_non_chat_model(model)],
        "tool_mode": CHAT_MODEL_TOOL_MODE,
        "filter_mode": CHAT_MODEL_FILTER_MODE,
    }
    changed = not REGISTRATION_PLAN.exists() or read_json(REGISTRATION_PLAN) != plan
    if changed and write:
        write_json(REGISTRATION_PLAN, plan)
    return changed


def validate(
    tool_records: List[ToolRecord],
    function_records: List[FunctionRecord],
    prompt_records: List[PromptRecord],
    models: List[Dict[str, Any]],
) -> List[str]:
    issues: List[str] = []
    valid_tool_ids = {record.id for record in tool_records if record.importable}
    valid_filter_ids = {record.id for record in function_records if record.importable and record.function_type == "filter"}
    valid_skill_ids = set(skill_ids())
    for record in tool_records:
        if not record.importable:
            issues.append(f"Tool nicht importierbar: {record.id} ({record.path})")
    for record in function_records:
        if not record.importable:
            issues.append(f"Function nicht importierbar: {record.id} ({record.path})")
        elif record.function_type != "filter":
            issues.append(f"Aktivierte Function ist kein Filter: {record.id} ({record.path}) type={record.function_type}")
    prompt_commands: dict[str, str] = {}
    for record in prompt_records:
        if not record.importable:
            issues.append(f"Promptvorlage nicht importierbar: {record.id} ({record.path})")
            continue
        previous = prompt_commands.get(record.command)
        if previous:
            issues.append(f"Promptvorlagen nutzen denselben Command `{record.command}`: {previous}, {record.id}")
        prompt_commands[record.command] = record.id
    for model in models:
        model_id = str(model.get("id"))
        meta = model.get("meta", {}) if isinstance(model.get("meta"), dict) else {}
        params = model.get("params", {}) if isinstance(model.get("params"), dict) else {}
        caps = meta.get("capabilities", {}) if isinstance(meta.get("capabilities"), dict) else {}
        tool_ids = meta.get("toolIds", [])
        filter_ids = meta.get("filterIds", [])
        default_filter_ids = meta.get("defaultFilterIds", [])
        if is_non_chat_model(model):
            if tool_ids or filter_ids or default_filter_ids or params.get("function_calling"):
                issues.append(f"Non-Chat-Modell {model_id} hat Tool-/Filter-/Function-Calling-Konfiguration")
            continue
        if model.get("base_model_id") != workbench_base_model_id():
            issues.append(f"Chat-Modell {model_id} nutzt nicht das konfigurierte Mistral-Basismodell {workbench_base_model_id()}")
        if params.get("function_calling") != WORKBENCH_FUNCTION_CALLING:
            issues.append(f"Chat-Modell {model_id} hat function_calling nicht auf native")
        if params.get("reasoning_effort") != WORKBENCH_REASONING_EFFORT:
            issues.append(f"Chat-Modell {model_id} hat reasoning_effort nicht auf 'high' gesetzt")
        if params.get("parallel_tool_calls") is not WORKBENCH_PARALLEL_TOOL_CALLS:
            issues.append(f"Chat-Modell {model_id} hat parallel_tool_calls nicht auf true gesetzt")
        profile_image_url = str(meta.get("profile_image_url", ""))
        if not profile_image_url.startswith("data:image/png;base64,"):
            issues.append(f"Chat-Modell {model_id} hat kein eingebettetes PNG-Icon in meta.profile_image_url")
        unsupported_params = sorted(set(params) - SUPPORTED_CHAT_RUNTIME_PARAMS)
        if unsupported_params:
            issues.append(f"Chat-Modell {model_id} setzt nicht freigegebene Runtime-Parameter: {', '.join(unsupported_params)}")
        if params.get("temperature") != WORKBENCH_TEMPERATURE:
            issues.append(f"Chat-Modell {model_id} nutzt temperature nicht auf {WORKBENCH_TEMPERATURE}")
        if params.get("top_p") != WORKBENCH_TOP_P:
            issues.append(f"Chat-Modell {model_id} nutzt top_p nicht auf {WORKBENCH_TOP_P}")
        if params.get("stop") != []:
            issues.append(f"Chat-Modell {model_id} nutzt stop nicht als leere Liste")
        system_text = str(params.get("system", ""))
        if not has_short_bootloader_systemprompt(system_text, model_id):
            issues.append(f"Chat-Modell {model_id} hat keinen vollständigen Bootloader-Systemprompt")
        if len(system_text) > WORKBENCH_SYSTEMPROMPT_MAX_CHARS:
            issues.append(f"Chat-Modell {model_id} hat params.system über {WORKBENCH_SYSTEMPROMPT_MAX_CHARS} Zeichen")
        for required_phrase in [
            "mainprompt.md",
            "fachwissen.md",
            "Golden_Example",
            "Werte alle drei aus",
            "Qualitäts-, Struktur-, Stil- und Formatanker",
            "beispiele/",
            "höchstens 1-2 passende Beispiele",
            "Erfinde keine Fakten",
        ]:
            if required_phrase not in system_text:
                issues.append(f"Chat-Modell {model_id} fehlt Bootloader-Kriterium: {required_phrase}")
        missing_profile_tools = sorted(set(TOOL_FORCE_PROFILES.get(model_id, {}).get("tools", [])) - set(tool_ids))
        profile_skills = set(TOOL_FORCE_PROFILES.get(model_id, {}).get("skills", []))
        missing_skill_files = sorted(profile_skills - valid_skill_ids)
        if missing_skill_files:
            issues.append(f"Chat-Modell {model_id} nennt Skill-Profil ohne lokale Skill-Datei: {', '.join(missing_skill_files)}")
        meta_primary_tools = meta.get("primaryToolIds", [])
        meta_skills = meta.get("recommendedSkillIds", [])
        bound_skills = meta.get("skillIds", [])
        if missing_profile_tools:
            issues.append(f"Chat-Modell {model_id} nennt Tool-Pflichtprofil mit nicht zugewiesenen Tools: {', '.join(missing_profile_tools)}")
        if not isinstance(meta_primary_tools, list) or set(TOOL_FORCE_PROFILES.get(model_id, {}).get("tools", [])) - set(meta_primary_tools):
            issues.append(f"Chat-Modell {model_id} hat meta.primaryToolIds nicht passend zum Tool-Profil")
        if not isinstance(meta_skills, list) or profile_skills - set(meta_skills):
            issues.append(f"Chat-Modell {model_id} hat meta.recommendedSkillIds nicht passend zum Skill-Profil")
        if not isinstance(bound_skills, list) or profile_skills - set(bound_skills):
            issues.append(f"Chat-Modell {model_id} hat meta.skillIds nicht passend zum Skill-Profil")
        workbench_file_context = meta.get("workbenchFileContext", {})
        if not isinstance(workbench_file_context, dict) or workbench_file_context.get("schema") != WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA:
            issues.append(f"Chat-Modell {model_id} hat kein gültiges meta.workbenchFileContext")
            workbench_file_context = {}
        required_files = workbench_file_context.get("requiredFiles", [])
        if not isinstance(required_files, list) or len(required_files) != 3:
            issues.append(f"Chat-Modell {model_id} hat nicht genau drei requiredFiles im File-Context")
            required_files = []
        required_paths = [item.get("path") for item in required_files if isinstance(item, dict)]
        if required_paths[:2] != ["mainprompt.md", "fachwissen.md"] or not any(str(path).startswith("Golden_Example.") for path in required_paths):
            issues.append(f"Chat-Modell {model_id} hat falsche Pflichtdateien im File-Context")
        if meta.get("requiredFileContextFiles") != required_paths:
            issues.append(f"Chat-Modell {model_id} hat meta.requiredFileContextFiles nicht passend zum File-Context")
        if "requiredKnowledgeFiles" in meta:
            issues.append(f"Chat-Modell {model_id} nutzt noch meta.requiredKnowledgeFiles als Pflichtpfad")
        for item in required_files:
            if not isinstance(item, dict):
                continue
            if item.get("useKnowledgeRag") is not False or item.get("injectAsFullContext") is not True or item.get("attachAsOpenWebUIFile") is not True:
                issues.append(f"Chat-Modell {model_id} hat falsche Flags für Pflichtdatei {item.get('path')}")
            if not isinstance(item.get("content"), str) or not item.get("content", "").strip():
                issues.append(f"Chat-Modell {model_id} hat keinen eingebetteten Pflichtdateiinhalt für {item.get('path')}")
        example_knowledge_files = meta.get("exampleKnowledgeFiles", [])
        if not isinstance(example_knowledge_files, list):
            issues.append(f"Chat-Modell {model_id} hat keine gültigen meta.exampleKnowledgeFiles")
            example_knowledge_files = []
        if any(path in {"mainprompt.md", "fachwissen.md"} or str(path).startswith("Golden_Example.") for path in example_knowledge_files):
            issues.append(f"Chat-Modell {model_id} enthält Pflichtdateien in exampleKnowledgeFiles")
        if meta.get("defaultLocale") != "de":
            issues.append(f"Chat-Modell {model_id} hat Deutsch nicht als meta.defaultLocale")
        if meta.get("fallbackLocale") != "en":
            issues.append(f"Chat-Modell {model_id} hat Englisch nicht als meta.fallbackLocale")
        if meta.get("supportedLocales") != SUPPORTED_PRODUCT_LOCALES:
            issues.append(f"Chat-Modell {model_id} hat keine vollständige Produktsprachenliste")
        expected_locale_files = [f"{MODEL_I18N_DIR_NAME}/{locale}.md" for locale in SUPPORTED_PRODUCT_LOCALES]
        if meta.get("productLocaleFiles") != expected_locale_files:
            issues.append(f"Chat-Modell {model_id} hat keine vollständige Produktsprachen-Dateiliste")
        product_i18n = meta.get("productI18n", {})
        if not isinstance(product_i18n, dict):
            issues.append(f"Chat-Modell {model_id} hat kein gültiges meta.productI18n")
            product_i18n = {}
        for locale in SUPPORTED_PRODUCT_LOCALES:
            locale_entry = product_i18n.get(locale)
            if not isinstance(locale_entry, dict):
                issues.append(f"Chat-Modell {model_id} fehlt meta.productI18n.{locale}")
                continue
            for field in ["name", "description", "suggestion", "profile"]:
                if not isinstance(locale_entry.get(field), str) or not locale_entry.get(field, "").strip():
                    issues.append(f"Chat-Modell {model_id} hat leeres meta.productI18n.{locale}.{field}")
            expected_profile = f"{MODEL_I18N_DIR_NAME}/{locale}.md"
            if locale_entry.get("profile") != expected_profile:
                issues.append(f"Chat-Modell {model_id} verweist für {locale} nicht auf {expected_profile}")
        manifest_path = SINGLE_MODELS / model_id / MODEL_I18N_DIR_NAME / "manifest.json"
        if not manifest_path.exists():
            issues.append(f"Chat-Modell {model_id} fehlt Produktsprachen-Manifest {rel(manifest_path)}")
        i18n_dir = SINGLE_MODELS / model_id / MODEL_I18N_DIR_NAME
        product_locale_profiles = [
            i18n_dir / f"{locale}.md"
            for locale in SUPPORTED_PRODUCT_LOCALES
            if (i18n_dir / f"{locale}.md").exists()
        ]
        if len(product_locale_profiles) < len(SUPPORTED_PRODUCT_LOCALES):
            issues.append(f"Chat-Modell {model_id} hat weniger als {len(SUPPORTED_PRODUCT_LOCALES)} Produktsprachenprofile")
        for path in model_knowledge_files(model_id):
            if not path.exists():
                issues.append(f"Chat-Modell {model_id} fehlt Knowledge-Datei {rel(path)}")
            elif path.stat().st_size == 0:
                issues.append(f"Chat-Modell {model_id} hat leere Knowledge-Datei {rel(path)}")
        if not model_example_files(model_id):
            issues.append(f"Chat-Modell {model_id} hat kein nutzbares Beispielartefakt unter {rel(SINGLE_MODELS / model_id / MODEL_EXAMPLES_DIR_NAME)}")
        if caps.get("builtin_tools") is not True:
            issues.append(f"Chat-Modell {model_id} hat builtin_tools nicht aktiv")
        if caps.get("vision") is not True:
            issues.append(f"Chat-Modell {model_id} hat Vision nicht aktiv")
        if not isinstance(tool_ids, list) or not tool_ids:
            issues.append(f"Chat-Modell {model_id} hat keine toolIds")
        else:
            if model_id != "allgemein":
                non_offline_tool_ids = {record.id for record in tool_records if record.importable and not record.offline}
                forbidden = sorted(set(tool_ids).intersection(OFFLINE_EXCLUDED_TOOL_IDS | non_offline_tool_ids))
                if forbidden:
                    issues.append(f"Chat-Modell {model_id} referenziert im Offline-Standard ausgeschlossene Tools: {', '.join(forbidden)}")
            missing = sorted(set(tool_ids) - valid_tool_ids)
            if missing:
                issues.append(f"Chat-Modell {model_id} referenziert unbekannte Tools: {', '.join(missing)}")
        if valid_filter_ids:
            if not isinstance(filter_ids, list) or not valid_filter_ids.issubset(set(filter_ids)):
                issues.append(f"Chat-Modell {model_id} hat nicht alle Pflichtfilter in filterIds")
            if not isinstance(default_filter_ids, list) or not valid_filter_ids.issubset(set(default_filter_ids)):
                issues.append(f"Chat-Modell {model_id} hat nicht alle Pflichtfilter in defaultFilterIds")
            required_prefix = REQUIRED_DEFAULT_FILTER_IDS
            if isinstance(default_filter_ids, list) and default_filter_ids[: len(required_prefix)] != required_prefix:
                issues.append(
                    f"Chat-Modell {model_id} hat Pflichtfilter nicht in der geforderten Reihenfolge: "
                    + ", ".join(required_prefix)
                )
            missing_filters = sorted(set(filter_ids) - valid_filter_ids) if isinstance(filter_ids, list) else []
            if missing_filters:
                issues.append(f"Chat-Modell {model_id} referenziert unbekannte Filter: {', '.join(missing_filters)}")
    return issues


def rebuild_zips() -> None:
    for target in [TOOLS_ZIP, MODELS_ZIP]:
        if target.exists():
            target.unlink()
    with zipfile.ZipFile(TOOLS_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in tool_zip_sources():
            write_archive_file(archive, path)
    with zipfile.ZipFile(MODELS_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in model_zip_sources():
            write_archive_file(archive, path)


def run_workspace_import(args: argparse.Namespace) -> int:
    spec = importlib.util.spec_from_file_location("openwebui_workspace_import", IMPORT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Importer konnte nicht geladen werden: {rel(IMPORT_SCRIPT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    import_args: List[str] = []
    if args.config:
        import_args.extend(["--config", args.config])
    if args.base_url:
        import_args.extend(["--base-url", str(args.base_url)])
    if args.token:
        import_args.extend(["--token", str(args.token)])
    if args.auth_header:
        import_args.extend(["--auth-header", str(args.auth_header)])
    if args.auth_scheme is not None:
        import_args.extend(["--auth-scheme", str(args.auth_scheme)])
    if args.tls_verify is not None:
        import_args.extend(["--tls-verify", str(args.tls_verify)])
    if args.ca_file:
        import_args.extend(["--ca-file", str(args.ca_file)])
    if args.ca_path:
        import_args.extend(["--ca-path", str(args.ca_path)])
    if args.jupyter_url:
        import_args.extend(["--jupyter-url", str(args.jupyter_url)])
    if args.jupyter_token:
        import_args.extend(["--jupyter-token", str(args.jupyter_token)])
    if args.jupyter_timeout_seconds:
        import_args.extend(["--jupyter-timeout-seconds", str(args.jupyter_timeout_seconds)])
    if args.jupyter_allowed_workdir:
        import_args.extend(["--jupyter-allowed-workdir", str(args.jupyter_allowed_workdir)])
    if args.artifact_root:
        import_args.extend(["--artifact-root", str(args.artifact_root)])
    if args.offline_addons_root:
        import_args.extend(["--offline-addons-root", str(args.offline_addons_root)])
    if args.offline_addons_python_path:
        import_args.extend(["--offline-addons-python-path", str(args.offline_addons_python_path)])
    if args.playwright_browsers_path:
        import_args.extend(["--playwright-browsers-path", str(args.playwright_browsers_path)])
    if args.nltk_data_path:
        import_args.extend(["--nltk-data-path", str(args.nltk_data_path)])
    if args.prefer_playwright_pdf:
        import_args.append("--prefer-playwright-pdf")
    if args.public_read:
        import_args.append("--public-read")
    if args.skip_knowledge:
        import_args.append("--skip-knowledge")
    if args.include_optional_network_tools:
        import_args.append("--include-optional-network-tools")
    if args.import_dry_run:
        import_args.append("--dry-run")
    if args.timeout is not None:
        import_args.extend(["--timeout", str(args.timeout)])
    return int(module.main(import_args))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Configure OpenWebUI tools before model tool bindings.")
    parser.add_argument("--write", action="store_true", help="Write generated registry and model JSON changes.")
    parser.add_argument("--check", action="store_true", help="Validate current/generated state and fail on issues.")
    parser.add_argument("--rebuild-zips", action="store_true", help="Rebuild portable offline ZIP artifacts after writing.")
    parser.add_argument("--base-model-id", default=None, help="OpenWebUI model ID used as base_model_id for all generated Workbench models. Defaults to WORKBENCH_BASE_MODEL_ID, legacy WORKBENCH_MISTRAL_MODEL_ID, or coder.")
    parser.add_argument("--import-openwebui", action="store_true", help="After a successful write/check pass, import tools, functions, skills, knowledge and models into an OpenWebUI instance.")
    parser.add_argument("--import-dry-run", action="store_true", help="Run the importer's local payload validation through this script without calling OpenWebUI.")
    parser.add_argument("--config", default=None, help="Central YAML config for OpenWebUI endpoint, tokens, backend paths and valves. Defaults to scripts/openwebui_workspace_config.yaml when present.")
    parser.add_argument("--base-url", default=None, help="One-off override for openwebui.base_url from the central config.")
    parser.add_argument("--token", default=None, help="One-off override for openwebui.admin_token from the central config.")
    parser.add_argument("--auth-header", default=None, help="One-off override for OpenWebUI API key header. Use x-api-key or CUSTOM_API_KEY_HEADER if Authorization is unavailable.")
    parser.add_argument("--auth-scheme", default=None, help="One-off override for auth scheme. Defaults to Bearer for Authorization and empty for custom API-key headers.")
    parser.add_argument("--tls-verify", choices=("true", "false"), default=None, help="Verify OpenWebUI HTTPS certificates. Set false only for trusted local self-signed endpoints.")
    parser.add_argument("--ca-file", default=None, help="CA bundle file for a private OpenWebUI HTTPS endpoint.")
    parser.add_argument("--ca-path", default=None, help="Directory with trusted CA certificates for a private OpenWebUI HTTPS endpoint.")
    parser.add_argument("--jupyter-url", default=None, help="One-off override for the Jupyter tool valve. Prefer tool_valves.air_gapped_jupyter_python in the config.")
    parser.add_argument("--jupyter-token", default=None, help="One-off override for the Jupyter token tool valve.")
    parser.add_argument("--jupyter-timeout-seconds", default=None, help="One-off override for the Jupyter timeout tool valve.")
    parser.add_argument("--jupyter-allowed-workdir", default=None, help="One-off override for the Jupyter allowed-workdir tool valve.")
    parser.add_argument("--artifact-root", default=None, help="One-off override for the artifact root tool valve.")
    parser.add_argument("--offline-addons-root", default=None, help="One-off override for the offline add-ons root tool valve.")
    parser.add_argument("--offline-addons-python-path", default=None, help="One-off override for the offline add-ons Python path tool valve.")
    parser.add_argument("--playwright-browsers-path", default=None, help="One-off override for the Playwright browser cache tool valve.")
    parser.add_argument("--nltk-data-path", default=None, help="One-off override for the NLTK data path tool valve.")
    parser.add_argument("--prefer-playwright-pdf", action="store_true", default=False, help="One-off override to prefer local Playwright/Chromium for artifact PDF conversion.")
    parser.add_argument("--public-read", action="store_true", help="Compatibility flag; public read is enforced by the importer.")
    parser.add_argument("--skip-knowledge", action="store_true", help="Import model profiles without uploading mainprompt.md, fachwissen.md, model-specific example result files, beispiele/ and primary i18n files as Knowledge.")
    parser.add_argument("--include-optional-network-tools", action="store_true", help="Also import optional network-capable tools during --import-openwebui.")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout in seconds for --import-openwebui.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.base_model_id:
        try:
            os.environ[WORKBENCH_BASE_MODEL_ID_ENV] = validate_base_model_id(args.base_model_id)
        except ValueError as exc:
            parser.error(str(exc))
    if args.import_openwebui and args.import_dry_run:
        parser.error("--import-openwebui and --import-dry-run are mutually exclusive.")
    if (args.import_openwebui or args.import_dry_run) and not args.write:
        parser.error("--import-openwebui/--import-dry-run require --write so generated artifacts cannot be stale.")

    records = discover_tools()
    function_records = discover_functions()
    prompt_records = discover_prompts()
    changed_tools_index = sync_tools_index(records, args.write)
    changed_tool_artifacts = write_tool_artifacts(records, args.write)
    changed_function_artifacts = write_function_artifacts(function_records, args.write)
    changed_prompt_artifacts = write_prompt_artifacts(prompt_records, args.write)
    changed_icon_artifacts = sync_icon_artifacts(args.write)
    changed_example_artifacts = sync_model_example_artifacts(args.write)
    changed_model_i18n_artifacts = sync_model_i18n_artifacts(args.write)
    changed_models, models = apply_model_config(records, function_records, args.write)
    changed_model_params_summary = write_model_params_summary(models, args.write)
    changed_plan = write_registration_plan(records, function_records, prompt_records, models, args.write)
    issues = validate(records, function_records, prompt_records, models)
    changed_generated_artifacts = (
        changed_tools_index
        or changed_tool_artifacts
        or changed_function_artifacts
        or changed_prompt_artifacts
        or changed_icon_artifacts
        or changed_example_artifacts
        or changed_model_i18n_artifacts
        or changed_models
        or changed_model_params_summary
        or changed_plan
    )

    print("# OpenWebUI Tool/Model Configuration")
    print(f"- Tools entdeckt: {len(records)}")
    print(f"- Tools importierbar: {sum(1 for record in records if record.importable)}")
    print(f"- Functions entdeckt: {len(function_records)}")
    print(f"- Filter importierbar: {sum(1 for record in function_records if record.importable and record.function_type == 'filter')}")
    print(f"- Promptvorlagen entdeckt: {len(prompt_records)}")
    print(f"- Promptvorlagen importierbar: {sum(1 for record in prompt_records if record.importable)}")
    print(f"- Modelle geprüft: {len(models)}")
    print(f"- Chat-Modelle: {sum(1 for model in models if not is_non_chat_model(model))}")
    print(f"- Non-Chat-Modelle ausgeschlossen: {sum(1 for model in models if is_non_chat_model(model))}")
    print(f"- Icon-Artefakte geändert: {changed_icon_artifacts}")
    print(f"- Beispielartefakte geändert: {changed_example_artifacts}")
    print(f"- Produkt-i18n-Artefakte geändert: {changed_model_i18n_artifacts}")
    print(f"- Prompt-Artefakte geändert: {changed_prompt_artifacts}")
    print(f"- Modellparameter-Zusammenfassung geändert: {changed_model_params_summary}")
    print(f"- Änderungen erkannt: {changed_generated_artifacts}")
    if args.write and args.rebuild_zips:
        rebuild_zips()
        print("- ZIP-Artefakte: neu gebaut")
    if args.check:
        if changed_generated_artifacts and not args.write:
            issues.append("Generierte Dist-Artefakte sind nicht aktuell; `python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips` ausführen.")
        issues.extend(zip_drift_issues(ROOT, TOOLS_ZIP, tool_zip_sources()))
        issues.extend(zip_drift_issues(ROOT, MODELS_ZIP, model_zip_sources()))
    if issues:
        print("\n## Befunde")
        for issue in issues:
            print(f"- {issue}")
        return 1 if args.check or args.import_openwebui or args.import_dry_run else 0
    print("\n## Ergebnis")
    print("Tool-/Filter-Registry, Importplan und Modell-Konfiguration sind konsistent.")
    if args.import_openwebui or args.import_dry_run:
        print("\n## API-Import")
        return run_workspace_import(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
