from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


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
MODEL_DIST = ROOT / "Modelle" / "dist"
REGISTRATION_PLAN = MODEL_DIST / "openwebui-registration-plan.json"
TOOLS_FALLBACK_BUNDLE = MODEL_DIST / "tools_fallback_bundle.json"
FUNCTIONS_FALLBACK_BUNDLE = MODEL_DIST / "functions_fallback_bundle.json"
MODEL_IMPORT = MODEL_DIST / "openwebui-models-import.json"
MODEL_FALLBACK = MODEL_DIST / "models_fallback_bundle.json"
MODEL_PARAMS_SUMMARY = MODEL_DIST / "openwebui-model-params-summary.json"
MODEL_ARTIFACTS = MODEL_DIST / "artifacts" / "models"
MODEL_EXAMPLE_ARTIFACTS = MODEL_DIST / "artifacts" / "examples"
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
SUPPORTED_MISTRAL_RUNTIME_PARAMS = {"system", "temperature", "top_p", "stop", "function_calling"}
OMITTED_RUNTIME_PARAMS = ["max_tokens"]
OMITTED_UNSUPPORTED_RUNTIME_PARAMS = ["reasoning_effort", "num_ctx", "top_k", "seed"]
PUBLIC_READ_GRANT = {"principal_type": "user", "principal_id": "*", "permission": "read"}
OFFLINE_EXCLUDED_TOOL_IDS = {"github_repo_inspector", "safe_http_fetcher"}
REQUIRED_MODEL_KNOWLEDGE_FILES = ["mainprompt.md", "fachwissen.md", "beispielergebnis.md"]
MODEL_EXAMPLES_DIR_NAME = "beispiele"
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
HIGH_REASONING_SYSTEM_BLOCK = f"""{HIGH_REASONING_SYSTEM_MARKER}

- Arbeite intern im Reasoning-Profil `high`: plane, prüfe und validiere Tool-Ausgaben kritisch; gib nur das fachlich notwendige Ergebnis aus.
- Nutze keine erfundenen Runtime-Parameter und setze kein festes `max_tokens`; OpenWebUI und Modellserver bestimmen Kontext- und Antwortlimits.
"""
CUSTOM_GPT_QUALITY_SYSTEM_BLOCK = f"""{CUSTOM_GPT_QUALITY_SYSTEM_MARKER}

- Vor jeder Aufgabe MUSST du die modellbezogenen Knowledge-Dateien `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und Dateien unter `beispiele/` laden und analysieren.
- Wende daraus Rolle, Ziel, Scope, Qualitätsregeln, Ausgabeformat, Fachwissen und Beispielmuster aktiv auf die Nutzeraufgabe an.
- Wenn Knowledge in OpenWebUI fehlt oder nicht sichtbar ist, benenne die Lücke knapp und arbeite nur mit dem verfügbaren Kontext weiter.
"""
VISION_SYSTEM_BLOCK = f"""{VISION_SYSTEM_MARKER}

- Nutze Vision bei Bildern, Screenshots, Scans, Folien, Diagrammen, UI-Zuständen und visueller Artefakt-QA; behaupte keine nicht sichtbaren Details.
- Prüfe Layout, Lesbarkeit, Kontrast, Responsiveness, Overlaps, Dark Mode, Hover/Focus/Touch und sichtbare Fehler; nutze lokale Offline-Tools oder `openwebui-offline-addons`, wenn sie verfügbar sind.
"""
MODEL_TEMPERATURES = {
    "allgemein": 0.45,
    "anforderungsanalyse-lastenheft": 0.4,
    "api-schnittstellenentwurf": 0.35,
    "code-dokumentation": 0.35,
    "code-review": 0.2,
    "codeanalyse": 0.2,
    "codegenerierung": 0.35,
    "compliance-richtlinienprüfung": 0.2,
    "debugging-fehleranalyse": 0.2,
    "dokumentenanalyse": 0.2,
    "dokumentengenerierung": 0.7,
    "dokumentenvergleich": 0.15,
    "dokumentenzusammenfassung": 0.25,
    "email-kommunikationsassistenz": 0.7,
    "informationsextraktion": 0.0,
    "it-helpdesk-diagnose": 0.25,
    "json-csv-log-analyse": 0.15,
    "meeting-protokoll-auswertung": 0.35,
    "mistral-vision-workbench": 0.25,
    "n8n-workflow-architect": 0.25,
    "offline-workbench-agent": 0.45,
    "openwebui-model-builder": 0.35,
    "promptforge": 0.35,
    "prozess-workflow-dokumentation": 0.4,
    "präsentationserstellung": 0.7,
    "refactoring-unterstützung": 0.25,
    "report-dashboard-vorbereitung": 0.4,
    "support-ticket-vorbereitung": 0.35,
    "tabellen-csv-datenanalyse": 0.15,
    "testfall-generierung": 0.3,
    "übersetzung-lokalisierung": 0.35,
}
TOOL_FORCE_PROFILES = {
    "allgemein": {
        "tools": ["air_gapped_jupyter_python", "ask_user", "comfyui_workflow_inspector", "docker_compose_triage", "github_repo_inspector", "inline_visuals_toolkit_v3", "json_csv_text_validator", "llm_council", "markdown_skill_builder", "mediawiki_legacy_crawler", "offline_artifact_workbench", "openapi_schema_inspector", "openui_generative_ui", "parallel_task_planner", "parallel_tools", "repo_tree_analyzer", "safe_http_fetcher", "sub_agent", "subagent_orchestrator", "tool_skill_overlay_planner", "visuals_toolkit_v4", "web_search_and_crawl"],
        "skills": ["offline-use-case-router", "redundant-fallback-tooling", "native-tool-calling-rollout", "parallel-tools-subagents", "secure-tool-usage"],
        "focus": "Freie oder gemischte Nutzerprobleme mit dem Basismodell `coder` bearbeiten, passende Spezialmodelle empfehlen und alle importierbaren Tools sowie alle Standardfilter fallbezogen aktiv nutzen.",
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
    "informationsextraktion": {
        "tools": ["json_csv_text_validator", "air_gapped_jupyter_python", "offline_artifact_workbench"],
        "skills": ["data-cleaning-analysis", "research-grounding", "secure-tool-usage"],
        "focus": "Extraktionsschema, JSON/CSV-Ausgabe und Datenqualität vor der finalen Antwort validieren.",
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
        "focus": "Mistral-Medium-Vision für Screenshots, UI-Tests, Folien, Diagramme, Scans, Dokumentbilder und visuelle Artefakt-QA nutzen und mit lokalen Offline-Tools absichern.",
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
    if path.suffix.lower() in {".py", ".md", ".json", ".txt", ".svg", ".yml", ".yaml"}:
        return data.replace(b"\r\n", b"\n")
    return data


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


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
    archive.writestr(info, path.read_bytes())


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


def temperature_for_model(model_id: str) -> float:
    return MODEL_TEMPERATURES.get(model_id, 0.35)


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
        "setzen aber keine nicht unterstützten Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` oder `seed`."
    )
    previous_default_line = "- Die Modellprofile setzen keine festen Laufzeitwerte wie `max_tokens`, `temperature`, `top_p`, `reasoning_effort`, `num_ctx`, `top_k` oder `seed`; die Zielinstanz verwendet ihre eigenen Defaults."
    tuned_line = "- Die Modellprofile setzen use-case-spezifische Werte für `temperature` und `top_p`, aber kein festes `max_tokens`; die Zielinstanz bestimmt Kontext- und Antwortlimits."
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


def ensure_custom_gpt_quality_profile(system_prompt: Any) -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    block = CUSTOM_GPT_QUALITY_SYSTEM_BLOCK.rstrip()
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
        CUSTOM_GPT_QUALITY_SYSTEM_BLOCK.rstrip(),
        VISION_SYSTEM_BLOCK.rstrip(),
        tool_call_playbook_block_for_model(model_id).rstrip(),
        tool_force_block_for_model(model_id).rstrip(),
    ]
    return "\n\n".join(sections)


def systemprompt_source_for_model(model_id: str) -> str:
    return f"""# Systemprompt

Dies ist nur der kurze Bootstrap-Prompt für das Modell `{model_id}`. Mainprompt, Fachwissen und Beispielwissen liegen in `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und `beispiele/`; diese Knowledge muss vor der Antwort geladen und analysiert werden.

{managed_system_profile_for_model(model_id)}"""


def ensure_markdown_formatting_enabled(system_prompt: Any) -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    stripped = system_prompt.lstrip()
    if stripped.startswith(MARKDOWN_FORMATTING_MARKER):
        return system_prompt
    return f"{MARKDOWN_FORMATTING_MARKER}\n\n{system_prompt}"


def normalize_base_prompt_text(system_prompt: str) -> str:
    replacements = {
        "`systemprompt.md`, `mainprompt.md` und `fachwissen.md`": "`systemprompt.md`, `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und Dateien unter `beispiele/`",
        "`mainprompt.md` und `fachwissen.md`": "`mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und Dateien unter `beispiele/`",
        "Systemprompt, Mainprompt und Fachwissen": "Systemprompt, Mainprompt, Fachwissen und Beispielwissen",
        "systemprompt.md, mainprompt.md und fachwissen.md": "systemprompt.md, mainprompt.md, fachwissen.md, beispielergebnis.md und beispiele/",
    }
    normalized = system_prompt
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def configure_runtime_params(model_id: str, params: Dict[str, Any]) -> None:
    system_prompt = systemprompt_source_for_model(model_id)
    system_prompt = ensure_markdown_formatting_enabled(system_prompt)
    temperature = temperature_for_model(model_id)
    params.clear()
    if system_prompt is not None:
        params["system"] = system_prompt
    params["temperature"] = temperature
    params["top_p"] = top_p_for_temperature(temperature)
    params["stop"] = []
    params["function_calling"] = FUNCTION_CALLING_NATIVE


def icon_data_uri_for_model(model_id: str) -> str:
    if not MODEL_ICON_MANIFEST.exists():
        return "/static/favicon.png"
    manifest = read_json(MODEL_ICON_MANIFEST)
    icon_id = manifest.get("suggested_model_icons", {}).get(model_id) if isinstance(manifest, dict) else None
    icons = manifest.get("icons", []) if isinstance(manifest, dict) else []
    for icon in icons:
        if isinstance(icon, dict) and icon.get("id") == icon_id:
            icon_path = ROOT / str(icon.get("path", ""))
            if icon_path.exists() and icon_path.suffix.lower() == ".svg":
                encoded = base64.b64encode(stable_text_bytes(icon_path)).decode("ascii")
                return f"data:image/svg+xml;base64,{encoded}"
    return "/static/favicon.png"


def tool_ids_for_model(model_id: str, offline_tool_ids: List[str], all_tool_ids: List[str]) -> List[str]:
    if model_id == "allgemein":
        return list(all_tool_ids)
    return list(offline_tool_ids)


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
    profile = TOOL_FORCE_PROFILES.get(model_id, TOOL_FORCE_PROFILES["offline-workbench-agent"])
    meta["profile_image_url"] = icon_data_uri_for_model(model_id)
    meta["toolIds"] = tool_ids_for_model(model_id, offline_tool_ids, all_tool_ids)
    meta["filterIds"] = merge_unique(filter_ids, meta.get("filterIds"))
    meta["defaultFilterIds"] = merge_unique(filter_ids, meta.get("defaultFilterIds"))
    meta["primaryToolIds"] = list(profile["tools"])
    meta["recommendedSkillIds"] = list(profile["skills"])
    meta["requiredKnowledgeFiles"] = list(REQUIRED_MODEL_KNOWLEDGE_FILES)
    configure_runtime_params(model_id, params)
    capabilities["builtin_tools"] = True
    capabilities["file_context"] = bool(capabilities.get("file_context", True))
    capabilities["vision"] = True
    capabilities["file_upload"] = bool(capabilities.get("file_upload", True))
    capabilities["code_interpreter"] = bool(capabilities.get("code_interpreter", True))
    capabilities["status_updates"] = bool(capabilities.get("status_updates", True))
    capabilities["usage"] = bool(capabilities.get("usage", True))
    if capabilities["code_interpreter"]:
        features = meta.setdefault("defaultFeatureIds", [])
        if isinstance(features, list) and "code_interpreter" not in features:
            features.append("code_interpreter")
    return model


def skill_ids() -> List[str]:
    if not SKILLS_DIR.exists():
        return []
    return sorted(path.stem for path in SKILLS_DIR.glob("*.md") if path.name.upper() != "README.MD")


def model_knowledge_files(model_id: str) -> List[Path]:
    model_dir = SINGLE_MODELS / model_id
    files = [model_dir / name for name in REQUIRED_MODEL_KNOWLEDGE_FILES]
    files.extend(model_example_files(model_id))
    return files


def model_example_files(model_id: str) -> List[Path]:
    examples_dir = SINGLE_MODELS / model_id / MODEL_EXAMPLES_DIR_NAME
    if not examples_dir.exists():
        return []
    return sorted(path for path in examples_dir.rglob("*") if path.is_file() and should_archive(path))


def model_knowledge_status(model_id: str) -> Dict[str, Dict[str, Any]]:
    status: Dict[str, Dict[str, Any]] = {}
    for path in model_knowledge_files(model_id):
        exists = path.exists()
        size = len(stable_text_bytes(path)) if exists else 0
        status[path.name] = {
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
        "supported_runtime_params": sorted(SUPPORTED_MISTRAL_RUNTIME_PARAMS),
        "omitted_runtime_params": OMITTED_RUNTIME_PARAMS,
        "omitted_unsupported_runtime_params": OMITTED_UNSUPPORTED_RUNTIME_PARAMS,
        "mistral_medium_128b_policy": "High reasoning is prompt-enforced with explicit tool-call playbooks; unsupported runtime parameters stay omitted.",
        "mistral_medium_vision_policy": "All chat model profiles enable OpenWebUI vision capability and include prompt rules for screenshot, UI, chart, scan, presentation and visual artifact analysis when the backing Mistral deployment supports image inputs.",
        "openwebui_builtin_and_addon_policy": "Chat models prefer standard OpenWebUI builtins and the mounted openwebui-offline-addons runtime for local caches, Playwright/Chromium, Tiktoken, NLTK and Python packages when available.",
        "offline_excluded_tool_ids": sorted(OFFLINE_EXCLUDED_TOOL_IDS),
        "models": [
            {
                "id": model.get("id"),
                "name": model.get("name"),
                "temperature": model.get("params", {}).get("temperature") if isinstance(model.get("params"), dict) else None,
                "top_p": model.get("params", {}).get("top_p") if isinstance(model.get("params"), dict) else None,
                "function_calling": model.get("params", {}).get("function_calling") if isinstance(model.get("params"), dict) else None,
                "runtime_param_keys": sorted(model.get("params", {}).keys()) if isinstance(model.get("params"), dict) else [],
                "has_markdown_formatting_enabled": str(model.get("params", {}).get("system", "")).lstrip().startswith(MARKDOWN_FORMATTING_MARKER)
                if isinstance(model.get("params"), dict)
                else False,
                "has_systemprompt_mainprompt_fachwissen": has_prompt_sections(model),
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
                "primary_tool_ids": TOOL_FORCE_PROFILES.get(str(model.get("id")), {}).get("tools", []),
                "recommended_skill_ids": TOOL_FORCE_PROFILES.get(str(model.get("id")), {}).get("skills", []),
                "required_knowledge_files": REQUIRED_MODEL_KNOWLEDGE_FILES,
                "knowledge_files": model_knowledge_status(str(model.get("id"))),
                "vision_enabled": bool(
                    model.get("meta", {}).get("capabilities", {}).get("vision")
                    if isinstance(model.get("meta"), dict) and isinstance(model.get("meta", {}).get("capabilities"), dict)
                    else False
                ),
                "has_embedded_svg_icon": str(model.get("meta", {}).get("profile_image_url", "")).startswith("data:image/svg+xml;base64,")
                if isinstance(model.get("meta"), dict)
                else False,
                "assigned_tool_ids": model.get("meta", {}).get("toolIds", []) if isinstance(model.get("meta"), dict) else [],
                "meta_primary_tool_ids": model.get("meta", {}).get("primaryToolIds", []) if isinstance(model.get("meta"), dict) else [],
                "meta_recommended_skill_ids": model.get("meta", {}).get("recommendedSkillIds", []) if isinstance(model.get("meta"), dict) else [],
            }
            for model in models
        ],
    }
    changed = not MODEL_PARAMS_SUMMARY.exists() or read_json(MODEL_PARAMS_SUMMARY) != summary
    if changed and write:
        write_json(MODEL_PARAMS_SUMMARY, summary)
    return changed


def write_registration_plan(tool_records: List[ToolRecord], function_records: List[FunctionRecord], models: List[Dict[str, Any]], write: bool) -> bool:
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
            "9_upload_model_knowledge",
            "10_publish_model_knowledge_public",
            "11_import_or_update_models",
            "12_publish_models_public",
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
                "import",
            ],
            "auth": "Default is Authorization: Bearer <token>. For OpenWebUI CUSTOM_API_KEY_HEADER setups use openwebui.auth_header and openwebui.auth_scheme in the central YAML.",
            "behavior": "The importer reads the central YAML first and maps endpoint, token, backend-visible paths, tool valves and function/filter valves into OpenWebUI before importing models. Tools, skills, model knowledge and models are published with public read access; functions and filters are enabled and made global.",
        },
        "api_import_token": "openwebui.admin_token in scripts/openwebui_workspace_config.yaml; --token is only an explicit one-off override. The token must be an OpenWebUI API key or JWT for an admin user.",
        "public_access_policy": {
            "tools": "public_read_grant_after_upsert",
            "skills": "public_read_grant_after_upsert",
            "model_knowledge": "public_read_grant_after_upsert",
            "models": "public_read_grant_after_import",
            "functions_and_filters": "active_and_global_after_upsert",
            "grant": PUBLIC_READ_GRANT,
        },
        "vision_policy": {
            "enabled_for_chat_models": True,
            "specialist_model_id": "mistral-vision-workbench",
            "system_marker": VISION_SYSTEM_MARKER,
            "behavior": "Use Mistral-Medium vision when OpenWebUI forwards image inputs. Apply it to screenshots, UI tests, scans, charts, presentations and visual artifact QA; fall back to OCR, files or user descriptions when image input is unavailable.",
        },
        "model_example_policy": {
            "required_knowledge_file": "beispielergebnis.md",
            "example_dir": MODEL_EXAMPLES_DIR_NAME,
            "dist_examples_dir": rel(MODEL_EXAMPLE_ARTIFACTS),
            "behavior": "Each model package contains a use-case-specific reusable example file and optional rich artifacts. The API importer uploads them into the per-model Knowledge collection together with mainprompt.md, fachwissen.md and beispielergebnis.md.",
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
        "model_knowledge_files_required": REQUIRED_MODEL_KNOWLEDGE_FILES,
        "knowledge_before_models": {
            str(model.get("id")): model_knowledge_status(str(model.get("id")))
            for model in models
            if not is_non_chat_model(model)
        },
        "model_import_file": rel(MODEL_IMPORT),
        "model_params_summary_file": rel(MODEL_PARAMS_SUMMARY),
        "generic_icon_manifest": rel(MODEL_ICON_ARTIFACTS / "openwebui-generic-icons.json"),
        "model_icon_policy": "profile_image_url uses embedded SVG data URIs generated from Modelle/icons/openwebui-generic-icons.json so the all-in-one model import can attach icons without a static file mount.",
        "tool_force_policy": {
            "system_marker": TOOL_FORCE_SYSTEM_MARKER,
            "behavior": "Every chat model starts non-trivial work with a compact tool/skill inventory and uses the smallest suitable available tool set early when files, structured data, code, artifacts, APIs, Docker/OpenWebUI diagnostics, visuals or parallel work are involved.",
            "model_profiles": TOOL_FORCE_PROFILES,
        },
        "tool_call_playbook_policy": {
            "system_marker": TOOL_CALL_PLAYBOOK_SYSTEM_MARKER,
            "target_model_runtime": "local Mistral Medium 128B",
            "behavior": "Every chat model receives a short system-level reminder to prefer OpenWebUI builtins, model primary tools, parallelization/subagents and visual/artifact tooling when the use case requires them. Detailed call syntax stays in Knowledge and skills.",
            "required_prompt_phrases": [
                "OpenWebUI-Builtins",
                "primären Modelltools",
                "Parallelisierung oder Subagenten",
                "geeignetes Tool geprüft",
            ],
        },
        "custom_gpt_quality_policy": {
            "formatting_marker": MARKDOWN_FORMATTING_MARKER,
            "system_marker": CUSTOM_GPT_QUALITY_SYSTEM_MARKER,
            "behavior": "Every chat model has a short bootstrap system prompt that requires loading and analyzing mainprompt.md, fachwissen.md, beispielergebnis.md and beispiele/ before applying role, scope, output format, quality rules and examples to the task.",
        },
        "model_params_policy": {
            "max_tokens": "omitted",
            "runtime_defaults": "target OpenWebUI/model-server context and answer limits",
            "reasoning_profile": "high_prompted_in_system",
            "reasoning_effort_runtime_param": "omitted_for_mistral_medium_128b_compatibility",
            "supported_runtime_params": sorted(SUPPORTED_MISTRAL_RUNTIME_PARAMS),
            "omitted_runtime_params": OMITTED_RUNTIME_PARAMS,
            "omitted_unsupported_runtime_params": OMITTED_UNSUPPORTED_RUNTIME_PARAMS,
            "temperature_by_model": MODEL_TEMPERATURES,
        },
        "global_model_params_recommendation": {"function_calling": FUNCTION_CALLING_NATIVE},
        "verified_model_fields_used": [
            "meta.toolIds",
            "meta.filterIds",
            "meta.defaultFilterIds",
            "meta.capabilities.builtin_tools",
            "meta.capabilities.vision",
            "meta.primaryToolIds",
            "meta.recommendedSkillIds",
            "meta.requiredKnowledgeFiles",
            "params.function_calling",
            "params.temperature",
            "params.top_p",
            "params.stop",
            "params.system markdown formatting marker",
            "params.system high-reasoning section",
            "params.system custom-gpt quality section",
            "params.system vision and UI image analysis section",
            "params.system explicit tool-call playbook section",
            "params.system tool-force section",
            "meta.profile_image_url",
        ],
        "builtin_tool_note": "OpenWebUI Built-in Tool categories are version-dependent. This project safely enables meta.capabilities.builtin_tools and params.function_calling=native, and the model prompts explicitly prefer standard OpenWebUI capabilities such as file/knowledge context, citations, status updates, code interpreter and native tool calls when the instance exposes them.",
        "offline_note": "The standard workflow is offline/air-gapped. Public network tools are not part of tools_first and are not assigned to specialized models. The Allgemein fallback model intentionally receives every importable tool so mixed or uncategorized requests can use the full repository toolbox when the target instance permits it.",
        "filter_note": "OpenWebUI filter functions are registered as Functions. The context compressor is assigned through meta.filterIds and enabled by default through meta.defaultFilterIds for every chat model. The API importer applies function/filter valves from scripts/openwebui_workspace_config.yaml after the functions are imported.",
        "knowledge_note": "The API importer uploads mainprompt.md, fachwissen.md, beispielergebnis.md and files under beispiele/ for every model package as a per-model Knowledge collection before importing the model profile, then appends the Knowledge reference to meta.knowledge for that model.",
        "icon_note": "Generic black-on-white SVG profile icons are shipped under Modelle/dist/artifacts/icons and can be assigned manually or referenced through meta.profile_image_url when copied to a static OpenWebUI path.",
        "chat_models_configured": [model["id"] for model in models if not is_non_chat_model(model)],
        "non_chat_models_excluded": [model["id"] for model in models if is_non_chat_model(model)],
        "tool_mode": CHAT_MODEL_TOOL_MODE,
        "filter_mode": CHAT_MODEL_FILTER_MODE,
    }
    changed = not REGISTRATION_PLAN.exists() or read_json(REGISTRATION_PLAN) != plan
    if changed and write:
        write_json(REGISTRATION_PLAN, plan)
    return changed


def validate(tool_records: List[ToolRecord], function_records: List[FunctionRecord], models: List[Dict[str, Any]]) -> List[str]:
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
        if params.get("function_calling") != FUNCTION_CALLING_NATIVE:
            issues.append(f"Chat-Modell {model_id} hat function_calling nicht auf native")
        profile_image_url = str(meta.get("profile_image_url", ""))
        if not profile_image_url.startswith("data:image/svg+xml;base64,"):
            issues.append(f"Chat-Modell {model_id} hat kein eingebettetes SVG-Icon in meta.profile_image_url")
        unsupported_params = sorted(set(params) - SUPPORTED_MISTRAL_RUNTIME_PARAMS)
        if unsupported_params:
            issues.append(f"Chat-Modell {model_id} setzt nicht freigegebene Runtime-Parameter: {', '.join(unsupported_params)}")
        expected_temperature = temperature_for_model(model_id)
        if params.get("temperature") != expected_temperature:
            issues.append(f"Chat-Modell {model_id} nutzt temperature nicht use-case-gerecht auf {expected_temperature}")
        if params.get("top_p") != top_p_for_temperature(expected_temperature):
            issues.append(f"Chat-Modell {model_id} nutzt top_p nicht passend zur Temperatur")
        if params.get("stop") != []:
            issues.append(f"Chat-Modell {model_id} nutzt stop nicht als leere Liste")
        system_text = str(params.get("system", ""))
        if not system_text.lstrip().startswith(MARKDOWN_FORMATTING_MARKER):
            issues.append(f"Chat-Modell {model_id} aktiviert Markdown-Formatierung nicht am Promptanfang")
        if len(system_text) > 3500:
            issues.append(f"Chat-Modell {model_id} hat einen zu langen Systemprompt ({len(system_text)} Zeichen)")
        if HIGH_REASONING_SYSTEM_MARKER not in system_text or "Reasoning-Profil `high`" not in system_text:
            issues.append(f"Chat-Modell {model_id} hat kein durchgängiges High-Reasoning-Systemprofil")
        for required_phrase in ["OpenWebUI-Builtins", "openwebui-offline-addons"]:
            if required_phrase not in system_text:
                issues.append(f"Chat-Modell {model_id} fehlt Builtin-/Addon-Laufzeitvorgabe: {required_phrase}")
        if CUSTOM_GPT_QUALITY_SYSTEM_MARKER not in system_text:
            issues.append(f"Chat-Modell {model_id} hat kein CustomGPT-Qualitätsprofil")
        for required_phrase in [
            "mainprompt.md",
            "fachwissen.md",
            "beispielergebnis.md",
            "beispiele/",
            "laden und analysieren",
            "Rolle, Ziel, Scope",
        ]:
            if required_phrase not in system_text:
                issues.append(f"Chat-Modell {model_id} fehlt CustomGPT-Qualitätskriterium: {required_phrase}")
        if VISION_SYSTEM_MARKER not in system_text:
            issues.append(f"Chat-Modell {model_id} hat keine Vision-/UI-Bildanalyse-Sektion")
        if TOOL_CALL_PLAYBOOK_SYSTEM_MARKER not in system_text:
            issues.append(f"Chat-Modell {model_id} hat keine expliziten Tool-Aufrufmuster")
        for required_phrase in [
            "OpenWebUI-Builtins",
            "primären Modelltools",
            "Parallelisierung oder Subagenten",
            "geeignetes Tool geprüft",
        ]:
            if required_phrase not in system_text:
                issues.append(f"Chat-Modell {model_id} fehlt explizites Tool-Aufrufmuster: {required_phrase}")
        if TOOL_FORCE_SYSTEM_MARKER not in system_text:
            issues.append(f"Chat-Modell {model_id} hat keine verbindliche Tool-Nutzungssektion")
        if "Tool-/Skill-Inventur" not in system_text:
            issues.append(f"Chat-Modell {model_id} erzwingt keine Tool-/Skill-Inventur am Aufgabenanfang")
        missing_profile_tools = sorted(set(TOOL_FORCE_PROFILES.get(model_id, {}).get("tools", [])) - set(tool_ids))
        if missing_profile_tools:
            issues.append(f"Chat-Modell {model_id} nennt Tool-Pflichtprofil mit nicht zugewiesenen Tools: {', '.join(missing_profile_tools)}")
        profile_skills = set(TOOL_FORCE_PROFILES.get(model_id, {}).get("skills", []))
        missing_skill_files = sorted(profile_skills - valid_skill_ids)
        if missing_skill_files:
            issues.append(f"Chat-Modell {model_id} nennt Skill-Profil ohne lokale Skill-Datei: {', '.join(missing_skill_files)}")
        meta_primary_tools = meta.get("primaryToolIds", [])
        if not isinstance(meta_primary_tools, list) or set(TOOL_FORCE_PROFILES.get(model_id, {}).get("tools", [])) - set(meta_primary_tools):
            issues.append(f"Chat-Modell {model_id} hat meta.primaryToolIds nicht passend zum Tool-Profil")
        meta_skills = meta.get("recommendedSkillIds", [])
        if not isinstance(meta_skills, list) or profile_skills - set(meta_skills):
            issues.append(f"Chat-Modell {model_id} hat meta.recommendedSkillIds nicht passend zum Skill-Profil")
        required_knowledge = meta.get("requiredKnowledgeFiles", [])
        if required_knowledge != REQUIRED_MODEL_KNOWLEDGE_FILES:
            issues.append(f"Chat-Modell {model_id} hat meta.requiredKnowledgeFiles nicht vollständig")
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
            missing_filters = sorted(set(filter_ids) - valid_filter_ids) if isinstance(filter_ids, list) else []
            if missing_filters:
                issues.append(f"Chat-Modell {model_id} referenziert unbekannte Filter: {', '.join(missing_filters)}")
    return issues


def rebuild_zips() -> None:
    for target in [TOOLS_ZIP, MODELS_ZIP]:
        if target.exists():
            target.unlink()
    with zipfile.ZipFile(TOOLS_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in [ROOT / "Tools" / "jupyter", ROOT / "Tools" / "openwebui_ext"]:
            for path in sorted(item.rglob("*")):
                if path.is_file() and should_archive(path):
                    write_archive_file(archive, path)
        for path in sorted([
            TOOLS_INDEX,
            ROOT / "Tools" / "README.md",
            IMPORT_SCRIPT,
            CONFIG_EXAMPLE,
            TOOL_REGISTRY,
            OFFLINE_TOOL_IMPORT,
            TOOL_IMPORT,
            FUNCTION_REGISTRY,
            FUNCTION_IMPORT,
        ]):
            if path.exists():
                write_archive_file(archive, path)
    with zipfile.ZipFile(MODELS_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted([
            MODEL_DIST / "README.md",
            MODEL_IMPORT,
            MODEL_FALLBACK,
            TOOLS_FALLBACK_BUNDLE,
            FUNCTIONS_FALLBACK_BUNDLE,
            OFFLINE_TOOL_IMPORT,
            TOOL_IMPORT,
            FUNCTION_IMPORT,
            REGISTRATION_PLAN,
            MODEL_PARAMS_SUMMARY,
            MODEL_DIST / "manual_import_checklist.md",
            CONFIG_EXAMPLE,
        ]):
            if path.exists():
                write_archive_file(archive, path)
        for path in sorted((MODEL_DIST / "artifacts").rglob("*")):
            if path.is_file() and should_archive(path):
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
    parser.add_argument("--skip-knowledge", action="store_true", help="Import model profiles without uploading mainprompt.md, fachwissen.md, beispielergebnis.md and beispiele/ as Knowledge.")
    parser.add_argument("--include-optional-network-tools", action="store_true", help="Also import optional network-capable tools during --import-openwebui.")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout in seconds for --import-openwebui.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.import_openwebui and args.import_dry_run:
        parser.error("--import-openwebui and --import-dry-run are mutually exclusive.")
    if (args.import_openwebui or args.import_dry_run) and not args.write:
        parser.error("--import-openwebui/--import-dry-run require --write so generated artifacts cannot be stale.")

    records = discover_tools()
    function_records = discover_functions()
    changed_tools_index = sync_tools_index(records, args.write)
    changed_tool_artifacts = write_tool_artifacts(records, args.write)
    changed_function_artifacts = write_function_artifacts(function_records, args.write)
    changed_icon_artifacts = sync_icon_artifacts(args.write)
    changed_example_artifacts = sync_model_example_artifacts(args.write)
    changed_models, models = apply_model_config(records, function_records, args.write)
    changed_model_params_summary = write_model_params_summary(models, args.write)
    changed_plan = write_registration_plan(records, function_records, models, args.write)
    issues = validate(records, function_records, models)

    print("# OpenWebUI Tool/Model Configuration")
    print(f"- Tools entdeckt: {len(records)}")
    print(f"- Tools importierbar: {sum(1 for record in records if record.importable)}")
    print(f"- Functions entdeckt: {len(function_records)}")
    print(f"- Filter importierbar: {sum(1 for record in function_records if record.importable and record.function_type == 'filter')}")
    print(f"- Modelle geprüft: {len(models)}")
    print(f"- Chat-Modelle: {sum(1 for model in models if not is_non_chat_model(model))}")
    print(f"- Non-Chat-Modelle ausgeschlossen: {sum(1 for model in models if is_non_chat_model(model))}")
    print(f"- Icon-Artefakte geändert: {changed_icon_artifacts}")
    print(f"- Beispielartefakte geändert: {changed_example_artifacts}")
    print(f"- Modellparameter-Zusammenfassung geändert: {changed_model_params_summary}")
    print(f"- Änderungen erkannt: {changed_tools_index or changed_tool_artifacts or changed_function_artifacts or changed_icon_artifacts or changed_models or changed_model_params_summary or changed_plan}")
    if args.write and args.rebuild_zips:
        rebuild_zips()
        print("- ZIP-Artefakte: neu gebaut")
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
