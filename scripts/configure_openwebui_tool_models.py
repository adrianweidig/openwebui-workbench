from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import inspect
import json
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = Path(__file__).with_name("openwebui_workspace_config.yaml")
CONFIG_EXAMPLE = Path(__file__).with_name("openwebui_workspace_config.example.yaml")

# Optional local defaults. Prefer scripts/openwebui_workspace_config.yaml for real
# deployments so secrets never need to be committed.
SCRIPT_OPENWEBUI_BASE_URL = ""
SCRIPT_OPENWEBUI_ADMIN_TOKEN = ""
SCRIPT_JUPYTER_URL = ""
SCRIPT_JUPYTER_TOKEN = ""
SCRIPT_JUPYTER_TIMEOUT_SECONDS = ""
SCRIPT_JUPYTER_ALLOWED_WORKDIR = ""
SCRIPT_ARTIFACT_ROOT = ""

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
MODEL_ICONS = ROOT / "Modelle" / "icons"
MODEL_ICON_MANIFEST = MODEL_ICONS / "openwebui-generic-icons.json"
MODEL_ICON_ARTIFACTS = MODEL_DIST / "artifacts" / "icons"
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
TOOLS_ZIP = TOOLS_DIST / "openwebui-tools-skills-offline.zip"
MODELS_ZIP = MODEL_DIST / "openwebui-offline-artifacts.zip"

FUNCTION_CALLING_NATIVE = "native"
CHAT_MODEL_TOOL_MODE = "all_validated_custom_tools"
CHAT_MODEL_FILTER_MODE = "all_validated_default_filters"
SUPPORTED_MISTRAL_RUNTIME_PARAMS = {"system", "temperature", "top_p", "stop", "function_calling"}
OMITTED_RUNTIME_PARAMS = ["max_tokens"]
OMITTED_UNSUPPORTED_RUNTIME_PARAMS = ["reasoning_effort", "num_ctx", "top_k", "seed"]
OFFLINE_EXCLUDED_TOOL_IDS = {"github_repo_inspector", "safe_http_fetcher"}
REQUIRED_MODEL_KNOWLEDGE_FILES = ["mainprompt.md", "fachwissen.md"]
HIGH_REASONING_SYSTEM_MARKER = "## Laufzeit- und Qualitätsprofil"
TOOL_FORCE_SYSTEM_MARKER = "## Verbindliche Tool- und Skill-Nutzung"
HIGH_REASONING_SYSTEM_BLOCK = f"""{HIGH_REASONING_SYSTEM_MARKER}

- Arbeite im Reasoning-Profil `high`: Plane schwierige Aufgaben intern gründlich, prüfe Zwischenergebnisse und validiere Tool-Ausgaben kritisch.
- Nutze verfügbare Offline-Tools und agentische Arbeitsschritte aktiv, wenn sie die Qualität, Reproduzierbarkeit oder Artefakterzeugung verbessern.
- Halte Antworten trotzdem aufgabengerecht kompakt; sehr lange Ausgaben oder vollständige Artefakte nur erzeugen, wenn die Nutzeraufgabe das verlangt.
- Die Modellprofile setzen use-case-spezifische Werte für `temperature` und `top_p`, aber kein festes `max_tokens`; die Zielinstanz bestimmt Kontext- und Antwortlimits.
"""
MODEL_TEMPERATURES = {
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
    "offline-workbench-agent": 0.45,
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
    "präsentationserstellung": {
        "tools": ["offline_artifact_workbench", "inline_visuals_toolkit_v3", "visuals_toolkit_v4", "air_gapped_jupyter_python"],
        "skills": ["offline-artifact-production", "visual-toolkit-v3-offline", "offline-creative-media-workflows"],
        "focus": "Folien, Visuals, Diagrammdaten und exportierbare Präsentationsartefakte mit Tools erzeugen.",
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


def load_module(path: Path) -> ModuleType:
    module_name = "owui_config_tool_" + re.sub(r"\W+", "_", path.stem)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("importlib spec konnte nicht erstellt werden")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inspect_tool(path: Path) -> Tuple[bool, List[str]]:
    try:
        module = load_module(path)
        tools_cls = getattr(module, "Tools", None)
        if not inspect.isclass(tools_cls):
            return False, []
        methods = [
            name
            for name, member in inspect.getmembers(tools_cls, predicate=inspect.isfunction)
            if not name.startswith("_") and name != "__init__"
        ]
        return bool(methods), sorted(methods)
    except Exception:
        return False, []


def inspect_filter(path: Path) -> Tuple[bool, List[str]]:
    try:
        module = load_module(path)
        filter_cls = getattr(module, "Filter", None)
        if not inspect.isclass(filter_cls):
            return False, []
        hooks = []
        for name in ["inlet", "stream", "outlet"]:
            member = getattr(filter_cls, name, None)
            if inspect.isfunction(member):
                hooks.append(name)
                if not inspect.iscoroutinefunction(member):
                    return False, hooks
        return "inlet" in hooks or "outlet" in hooks or "stream" in hooks, sorted(hooks)
    except Exception:
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


def merge_unique(existing: Any, required: List[str]) -> List[str]:
    values = existing if isinstance(existing, list) else []
    merged: List[str] = []
    for value in [*values, *required]:
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
    tools = ", ".join(f"`{tool}`" for tool in profile["tools"])
    skills = ", ".join(f"`{skill}`" for skill in profile["skills"])
    focus = profile["focus"]
    return f"""{TOOL_FORCE_SYSTEM_MARKER}

Zu Beginn jeder nicht-trivialen Aufgabe MUSST du eine kurze Tool-/Skill-Inventur durchführen: Prüfe anhand der tatsächlich verfügbaren Tool-IDs, importierten Skills, Nutzerdateien und des gewünschten Ergebnisses, welche Tools oder Skills für diesen Use Case passen. Nutze nur wirklich verfügbare Tools; wenn ein empfohlenes Tool oder ein Skill in der Zielinstanz fehlt, erfinde ihn nicht, sondern arbeite mit dem besten verfügbaren Fallback und benenne die Grenze knapp.

Wenn ein passendes Tool verfügbar ist, nutze es früh im Arbeitsablauf und nicht erst nach einer fertigen Antwort. Bei mehreren unabhängigen Teilprüfungen prüfe, ob `parallel_task_planner`, `parallel_tools`, `subagent_orchestrator` oder `sub_agent` die Arbeit robuster machen. Wenn `auto_tool_selector` als Filter aktiv ist, prüfe dessen Tool-Vorauswahl trotzdem bewusst gegen den aktuellen Use Case.

Vor jeder finalen Antwort prüfst du aktiv, ob ein freigegebenes Tool oder ein importierter Skill die Aufgabe belastbarer, reproduzierbarer oder artefaktfähig macht. Wenn einer der folgenden Auslöser zutrifft, MUSST du vor der finalen Antwort mindestens ein passendes Tool nutzen; nur bei reiner Begriffserklärung, fehlenden Eingaben, explizitem Nutzerverbot oder Sicherheits-/Berechtigungsgründen darfst du darauf verzichten und musst den Verzicht kurz begründen.

- Dateien, Tabellen, JSON, CSV, Logs oder strukturierte Texte: `json_csv_text_validator`; bei Berechnung, Transformation oder Stichproben zusätzlich `air_gapped_jupyter_python`.
- Code, Repository-Strukturen, Diffs, Tests oder Refactoring: `repo_tree_analyzer`; für ausführbare Prüfungen oder Datenaufbereitung `air_gapped_jupyter_python`.
- HTML, PDF, Präsentationen, ZIPs oder andere Übergabeartefakte: `offline_artifact_workbench`; für Diagramme, Mermaid, SVG-Charts oder Dashboards zusätzlich `inline_visuals_toolkit_v3`.
- Docker-, Compose-, OpenWebUI- oder Betriebsfehler: `docker_compose_triage`.
- OpenAPI-, MCP-, Schnittstellen- oder Toolserver-Schemata: `openapi_schema_inspector`.
- Unklare Eingaben, fehlende Dateien oder notwendige Rückfragen vor Toolausführung: `ask_user`, sofern verfügbar.
- Komplexe mehrstufige Aufgaben, parallele Arbeit oder Subagent-Planung: `parallel_task_planner`; für parallele bereits aktivierte Toolaufrufe `parallel_tools`; bei Rollen-/Subagent-Aufteilung zusätzlich `subagent_orchestrator` oder `sub_agent`.
- Modell-, Tool-, Skill- oder Fallback-Zuordnung: `tool_skill_overlay_planner`.
- Unsichere fachliche Abwägungen, zweite Modellmeinung oder robuste Entscheidungsvorbereitung: `llm_council`, sofern lokale Modell- und OpenWebUI-API-Konfiguration vorhanden sind.
- ComfyUI-, Bild-, Audio- oder Video-Workflow-JSON: `comfyui_workflow_inspector`.
- Skill-Entwurf oder Skill-Markdown: `markdown_skill_builder`.
- Rich-Visuals, Dashboards, Wireframes, ASCII-/SVG-Visualisierung oder textbasierte UI-Entwürfe: `visuals_toolkit_v4`; bei klassischen Offline-SVG-/Mermaid-Artefakten zusätzlich oder alternativ `inline_visuals_toolkit_v3`.
- Interne MediaWiki-Arbeit: `mediawiki_legacy_crawler` nur bei explizitem Auftrag und vorhandener Konfiguration.
- Public-Web-, GitHub- oder Rich-UI-Tools wie `web_search_and_crawl`, `safe_http_fetcher`, `github_repo_inspector` und `openui_generative_ui` nur nutzen, wenn sie in der Zielinstanz bewusst importiert, konfiguriert und für den aktuellen Offline-/Netzbereich freigegeben sind.

Für dieses Modell sind primär diese Tools vorgesehen: {tools}.
Wenn Skills importiert oder an das Modell gebunden sind, berücksichtige besonders: {skills}.
Optimierungsfokus: {focus}

Nutze immer den kleinsten ausreichenden Tool-Satz. Validiere Tool-Ausgaben kritisch, verschweige Fehler nicht und gib keine Secrets, Tokens oder unnötigen Rohdaten aus.
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
    if HIGH_REASONING_SYSTEM_MARKER in system_prompt:
        return system_prompt.replace(legacy_line, tuned_line).replace(previous_default_line, tuned_line)
    insert_before = "\n\n        # Systemprompt"
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {HIGH_REASONING_SYSTEM_BLOCK.replace(chr(10), chr(10) + '        ')}{insert_before}", 1)
    return f"{HIGH_REASONING_SYSTEM_BLOCK}\n\n{system_prompt}"


def ensure_tool_force_profile(system_prompt: Any, model_id: str) -> Any:
    if not isinstance(system_prompt, str):
        return system_prompt
    block = tool_force_block_for_model(model_id).rstrip()
    start = system_prompt.find(TOOL_FORCE_SYSTEM_MARKER)
    if start != -1:
        next_heading = re.search(r"\n\n\s+# ", system_prompt[start + len(TOOL_FORCE_SYSTEM_MARKER) :])
        if next_heading:
            cut = start + len(TOOL_FORCE_SYSTEM_MARKER) + next_heading.start()
            return f"{system_prompt[:start]}{block}{system_prompt[cut:]}"
        return f"{system_prompt[:start]}{block}"
    insert_before = "\n\n        # Systemprompt"
    indented_block = block.replace(chr(10), chr(10) + "        ")
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {indented_block}{insert_before}", 1)
    return f"{block}\n\n{system_prompt}"


def configure_runtime_params(model_id: str, params: Dict[str, Any]) -> None:
    system_prompt = ensure_tool_force_profile(ensure_high_reasoning_profile(params.get("system")), model_id)
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


def configure_model(model: Dict[str, Any], tool_ids: List[str], filter_ids: List[str]) -> Dict[str, Any]:
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
    meta["toolIds"] = list(tool_ids)
    meta["filterIds"] = merge_unique(filter_ids, meta.get("filterIds"))
    meta["defaultFilterIds"] = merge_unique(filter_ids, meta.get("defaultFilterIds"))
    meta["primaryToolIds"] = list(profile["tools"])
    meta["recommendedSkillIds"] = list(profile["skills"])
    meta["requiredKnowledgeFiles"] = list(REQUIRED_MODEL_KNOWLEDGE_FILES)
    configure_runtime_params(model_id, params)
    capabilities["builtin_tools"] = True
    capabilities["file_context"] = bool(capabilities.get("file_context", True))
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
    return [model_dir / name for name in REQUIRED_MODEL_KNOWLEDGE_FILES]


def model_knowledge_status(model_id: str) -> Dict[str, Dict[str, Any]]:
    status: Dict[str, Dict[str, Any]] = {}
    for path in model_knowledge_files(model_id):
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        status[path.name] = {
            "path": rel(path),
            "exists": exists,
            "non_empty": size > 0,
            "bytes": size,
        }
    return status


def apply_model_config(tool_records: List[ToolRecord], function_records: List[FunctionRecord], write: bool) -> Tuple[bool, List[Dict[str, Any]]]:
    tool_ids = [record.id for record in offline_default_tool_records(tool_records)]
    filter_ids = [record.id for record in function_records if record.importable and record.function_type == "filter"]
    changed = False
    configured_models: List[Dict[str, Any]] = []
    for path in model_files():
        data, original = load_model(path)
        configured = configure_model(original, tool_ids, filter_ids)
        configured_models.append(configured)
        new_data = [configured]
        if new_data != data:
            changed = True
            if write:
                write_json(path, new_data)
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
        "offline_excluded_tool_ids": sorted(OFFLINE_EXCLUDED_TOOL_IDS),
        "models": [
            {
                "id": model.get("id"),
                "name": model.get("name"),
                "temperature": model.get("params", {}).get("temperature") if isinstance(model.get("params"), dict) else None,
                "top_p": model.get("params", {}).get("top_p") if isinstance(model.get("params"), dict) else None,
                "function_calling": model.get("params", {}).get("function_calling") if isinstance(model.get("params"), dict) else None,
                "runtime_param_keys": sorted(model.get("params", {}).keys()) if isinstance(model.get("params"), dict) else [],
                "has_systemprompt_mainprompt_fachwissen": has_prompt_sections(model),
                "has_tool_force_profile": TOOL_FORCE_SYSTEM_MARKER in str(model.get("params", {}).get("system", ""))
                if isinstance(model.get("params"), dict)
                else False,
                "primary_tool_ids": TOOL_FORCE_PROFILES.get(str(model.get("id")), {}).get("tools", []),
                "recommended_skill_ids": TOOL_FORCE_PROFILES.get(str(model.get("id")), {}).get("skills", []),
                "required_knowledge_files": REQUIRED_MODEL_KNOWLEDGE_FILES,
                "knowledge_files": model_knowledge_status(str(model.get("id"))),
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
            "2_import_workspace_filters",
            "3_import_workspace_skills",
            "4_upload_model_knowledge",
            "5_import_or_update_models",
            "6_enable_user_or_group_access",
        ],
        "api_import_script": rel(IMPORT_SCRIPT),
        "api_import_config_file": rel(CONFIG_FILE),
        "api_import_config_example": rel(CONFIG_EXAMPLE),
        "api_import_command": "python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml",
        "api_import_token": "openwebui.admin_token in config YAML, OPENWEBUI_ADMIN_TOKEN environment variable, or --token CLI argument",
        "tools_first": offline_tool_ids,
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
            "behavior": "Every chat model must use at least one suitable assigned tool before the final answer when a task involves files, structured data, code, artifacts, APIs, Docker/OpenWebUI diagnostics, visuals, parallel planning, model/tool/skill overlays, ComfyUI workflows or skill authoring.",
            "model_profiles": TOOL_FORCE_PROFILES,
        },
        "model_params_policy": {
            "max_tokens": "omitted",
            "runtime_defaults": "target OpenWebUI/model-server context and answer limits",
            "reasoning_profile": "high_prompted_in_system",
            "reasoning_effort_runtime_param": "omitted_for_mistral_medium_3_5_128b_compatibility",
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
            "meta.primaryToolIds",
            "meta.recommendedSkillIds",
            "meta.requiredKnowledgeFiles",
            "params.function_calling",
            "params.temperature",
            "params.top_p",
            "params.stop",
            "params.system tool-force section",
            "meta.profile_image_url",
        ],
        "builtin_tool_note": "OpenWebUI Built-in Tool categories are version-dependent. This project safely enables meta.capabilities.builtin_tools and params.function_calling=native; category availability remains controlled by the OpenWebUI instance.",
        "offline_note": "The standard workflow is offline/air-gapped. Public network tools are not assigned to models and are not part of tools_first.",
        "filter_note": "OpenWebUI filter functions are registered as Functions. The context compressor is assigned through meta.filterIds and enabled by default through meta.defaultFilterIds for every chat model.",
        "knowledge_note": "The API importer uploads mainprompt.md and fachwissen.md for every model package as a per-model Knowledge collection before importing the model profile, then appends the Knowledge reference to meta.knowledge for that model.",
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
        if caps.get("builtin_tools") is not True:
            issues.append(f"Chat-Modell {model_id} hat builtin_tools nicht aktiv")
        if not isinstance(tool_ids, list) or not tool_ids:
            issues.append(f"Chat-Modell {model_id} hat keine toolIds")
        else:
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
            for path in item.rglob("*"):
                if path.is_file() and should_archive(path):
                    archive.write(path, rel(path))
        for path in [
            TOOLS_INDEX,
            ROOT / "Tools" / "README.md",
            IMPORT_SCRIPT,
            CONFIG_EXAMPLE,
            TOOL_REGISTRY,
            OFFLINE_TOOL_IMPORT,
            TOOL_IMPORT,
            FUNCTION_REGISTRY,
            FUNCTION_IMPORT,
        ]:
            if path.exists():
                archive.write(path, rel(path))
    with zipfile.ZipFile(MODELS_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in [
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
        ]:
            if path.exists():
                archive.write(path, rel(path))
        for path in (MODEL_DIST / "artifacts").rglob("*"):
            if path.is_file() and should_archive(path):
                archive.write(path, rel(path))


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
    base_url = args.base_url or SCRIPT_OPENWEBUI_BASE_URL
    token = args.token or SCRIPT_OPENWEBUI_ADMIN_TOKEN
    jupyter_url = args.jupyter_url or SCRIPT_JUPYTER_URL
    jupyter_token = args.jupyter_token or SCRIPT_JUPYTER_TOKEN
    jupyter_timeout = args.jupyter_timeout_seconds or SCRIPT_JUPYTER_TIMEOUT_SECONDS
    jupyter_allowed_workdir = args.jupyter_allowed_workdir or SCRIPT_JUPYTER_ALLOWED_WORKDIR
    artifact_root = args.artifact_root or SCRIPT_ARTIFACT_ROOT
    if base_url:
        import_args.extend(["--base-url", str(base_url)])
    if token:
        import_args.extend(["--token", str(token)])
    if jupyter_url:
        import_args.extend(["--jupyter-url", str(jupyter_url)])
    if jupyter_token:
        import_args.extend(["--jupyter-token", str(jupyter_token)])
    if jupyter_timeout:
        import_args.extend(["--jupyter-timeout-seconds", str(jupyter_timeout)])
    if jupyter_allowed_workdir:
        import_args.extend(["--jupyter-allowed-workdir", str(jupyter_allowed_workdir)])
    if artifact_root:
        import_args.extend(["--artifact-root", str(artifact_root)])
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
    parser.add_argument("--config", default=None, help="YAML config for OpenWebUI/Jupyter endpoints and tokens. Defaults to scripts/openwebui_workspace_config.yaml when present.")
    parser.add_argument("--base-url", default=None, help="OpenWebUI base URL for --import-openwebui, for example http://localhost:3000.")
    parser.add_argument("--token", default=None, help="OpenWebUI admin API token for --import-openwebui. Prefer OPENWEBUI_ADMIN_TOKEN.")
    parser.add_argument("--jupyter-url", default=None, help="Jupyter URL as seen from the OpenWebUI backend/container.")
    parser.add_argument("--jupyter-token", default=None, help="Jupyter token for the air_gapped_jupyter_python tool valve.")
    parser.add_argument("--jupyter-timeout-seconds", default=None, help="Jupyter execution timeout tool valve.")
    parser.add_argument("--jupyter-allowed-workdir", default=None, help="Allowed workdir as seen by the Jupyter host/container.")
    parser.add_argument("--artifact-root", default=None, help="Artifact root as seen by the OpenWebUI backend/container.")
    parser.add_argument("--public-read", action="store_true", help="Grant read access during --import-openwebui where OpenWebUI permits it.")
    parser.add_argument("--skip-knowledge", action="store_true", help="Import model profiles without uploading mainprompt.md and fachwissen.md as Knowledge.")
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
