from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import inspect
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
TOOLS_INDEX = ROOT / "Tools" / "index.json"
TOOLS_DIST = ROOT / "Tools" / "dist"
TOOL_REGISTRY = TOOLS_DIST / "openwebui-tool-registry.json"
FUNCTION_REGISTRY = TOOLS_DIST / "openwebui-function-registry.json"
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
MAX_MODEL_TOKENS = 262144
SUPPORTED_MISTRAL_RUNTIME_PARAMS = {"system", "temperature", "top_p", "max_tokens", "stop", "function_calling"}
OMITTED_UNSUPPORTED_RUNTIME_PARAMS = ["reasoning_effort", "num_ctx", "top_k", "seed"]
OFFLINE_EXCLUDED_TOOL_IDS = {"github_repo_inspector", "safe_http_fetcher"}
HIGH_REASONING_SYSTEM_MARKER = "## Laufzeit- und Qualitätsprofil"
HIGH_REASONING_SYSTEM_BLOCK = f"""{HIGH_REASONING_SYSTEM_MARKER}

- Arbeite im Reasoning-Profil `high`: Plane schwierige Aufgaben intern gründlich, prüfe Zwischenergebnisse und validiere Tool-Ausgaben kritisch.
- Nutze verfügbare Offline-Tools und agentische Arbeitsschritte aktiv, wenn sie die Qualität, Reproduzierbarkeit oder Artefakterzeugung verbessern.
- Halte Antworten trotzdem aufgabengerecht kompakt; sehr lange Ausgaben oder vollständige Artefakte nur erzeugen, wenn die Nutzeraufgabe das verlangt.
- Die Modellprofile erlauben bis zu 256k Tokens über `max_tokens`, setzen aber keine nicht unterstützten Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` oder `seed`.
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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                importable=importable,
                methods=methods,
            )
        )
    return records


def offline_default_tool_records(records: List[ToolRecord]) -> List[ToolRecord]:
    return [record for record in records if record.importable and record.id not in OFFLINE_EXCLUDED_TOOL_IDS]


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
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                importable=importable,
                hooks=hooks,
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
    optional_records = [record for record in records if record.importable and record.id in OFFLINE_EXCLUDED_TOOL_IDS]
    registry = {
        "schema": "openwebui-tool-registry/v1",
        "order": ["tools", "skills", "models"],
        "tool_import_order": [record.id for record in offline_records],
        "offline_default_tool_import_order": [record.id for record in offline_records],
        "optional_network_tools_not_in_offline_default": [record.id for record in optional_records],
        "tools": [record.__dict__ for record in records],
    }
    fallback = {
        "schema": "openwebui-tool-bundle-fallback/v1",
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
    changed = (not TOOL_REGISTRY.exists() or read_json(TOOL_REGISTRY) != registry) or read_json(TOOLS_FALLBACK_BUNDLE) != fallback
    if changed and write:
        write_json(TOOL_REGISTRY, registry)
        write_json(TOOLS_FALLBACK_BUNDLE, fallback)
    return changed


def write_function_artifacts(records: List[FunctionRecord], write: bool) -> bool:
    registry = {
        "schema": "openwebui-function-registry/v1",
        "order": ["filters", "tools", "models"],
        "filter_import_order": [record.id for record in records if record.importable and record.function_type == "filter"],
        "functions": [record.__dict__ for record in records],
    }
    fallback = {
        "schema": "openwebui-function-bundle-fallback/v1",
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
    changed = (
        not FUNCTION_REGISTRY.exists()
        or read_json(FUNCTION_REGISTRY) != registry
        or not FUNCTIONS_FALLBACK_BUNDLE.exists()
        or read_json(FUNCTIONS_FALLBACK_BUNDLE) != fallback
    )
    if changed and write:
        write_json(FUNCTION_REGISTRY, registry)
        write_json(FUNCTIONS_FALLBACK_BUNDLE, fallback)
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


def ensure_high_reasoning_profile(system_prompt: Any) -> Any:
    if not isinstance(system_prompt, str) or HIGH_REASONING_SYSTEM_MARKER in system_prompt:
        return system_prompt
    insert_before = "\n\n        # Systemprompt"
    if insert_before in system_prompt:
        return system_prompt.replace(insert_before, f"\n\n        {HIGH_REASONING_SYSTEM_BLOCK.replace(chr(10), chr(10) + '        ')}{insert_before}", 1)
    return f"{HIGH_REASONING_SYSTEM_BLOCK}\n\n{system_prompt}"


def configure_runtime_params(model_id: str, params: Dict[str, Any]) -> None:
    system_prompt = ensure_high_reasoning_profile(params.get("system"))
    temperature = temperature_for_model(model_id)
    params.clear()
    if system_prompt is not None:
        params["system"] = system_prompt
    params["temperature"] = temperature
    params["top_p"] = top_p_for_temperature(temperature)
    params["max_tokens"] = MAX_MODEL_TOKENS
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
                encoded = base64.b64encode(icon_path.read_bytes()).decode("ascii")
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
    meta["profile_image_url"] = icon_data_uri_for_model(model_id)
    meta["toolIds"] = list(tool_ids)
    meta["filterIds"] = merge_unique(meta.get("filterIds"), filter_ids)
    meta["defaultFilterIds"] = merge_unique(meta.get("defaultFilterIds"), filter_ids)
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
        "expected_max_tokens": MAX_MODEL_TOKENS,
        "supported_runtime_params": sorted(SUPPORTED_MISTRAL_RUNTIME_PARAMS),
        "omitted_unsupported_runtime_params": OMITTED_UNSUPPORTED_RUNTIME_PARAMS,
        "offline_excluded_tool_ids": sorted(OFFLINE_EXCLUDED_TOOL_IDS),
        "models": [
            {
                "id": model.get("id"),
                "name": model.get("name"),
                "max_tokens": model.get("params", {}).get("max_tokens") if isinstance(model.get("params"), dict) else None,
                "temperature": model.get("params", {}).get("temperature") if isinstance(model.get("params"), dict) else None,
                "top_p": model.get("params", {}).get("top_p") if isinstance(model.get("params"), dict) else None,
                "function_calling": model.get("params", {}).get("function_calling") if isinstance(model.get("params"), dict) else None,
                "runtime_param_keys": sorted(model.get("params", {}).keys()) if isinstance(model.get("params"), dict) else [],
                "has_systemprompt_mainprompt_fachwissen": has_prompt_sections(model),
                "has_embedded_svg_icon": str(model.get("meta", {}).get("profile_image_url", "")).startswith("data:image/svg+xml;base64,")
                if isinstance(model.get("meta"), dict)
                else False,
                "assigned_tool_ids": model.get("meta", {}).get("toolIds", []) if isinstance(model.get("meta"), dict) else [],
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
    optional_network_tool_ids = [record.id for record in tool_records if record.importable and record.id in OFFLINE_EXCLUDED_TOOL_IDS]
    plan = {
        "schema": "openwebui-registration-plan/v1",
        "order": [
            "1_import_workspace_tools",
            "2_import_workspace_filters",
            "3_import_workspace_skills",
            "4_import_or_update_models",
            "5_enable_user_or_group_access",
        ],
        "tools_first": offline_tool_ids,
        "offline_default_tools": offline_tool_ids,
        "optional_network_tools_not_in_offline_default": optional_network_tool_ids,
        "filters_before_models": filter_ids,
        "model_import_file": rel(MODEL_IMPORT),
        "model_params_summary_file": rel(MODEL_PARAMS_SUMMARY),
        "generic_icon_manifest": rel(MODEL_ICON_ARTIFACTS / "openwebui-generic-icons.json"),
        "model_icon_policy": "profile_image_url uses embedded SVG data URIs generated from Modelle/icons/openwebui-generic-icons.json so the all-in-one model import can attach icons without a static file mount.",
        "model_params_policy": {
            "target_context_tokens": MAX_MODEL_TOKENS,
            "max_tokens": MAX_MODEL_TOKENS,
            "reasoning_profile": "high_prompted_in_system",
            "reasoning_effort_runtime_param": "omitted_for_mistral_medium_3_5_128b_compatibility",
            "supported_runtime_params": sorted(SUPPORTED_MISTRAL_RUNTIME_PARAMS),
            "omitted_unsupported_runtime_params": OMITTED_UNSUPPORTED_RUNTIME_PARAMS,
            "temperature_by_model": MODEL_TEMPERATURES,
        },
        "global_model_params_recommendation": {"function_calling": FUNCTION_CALLING_NATIVE, "max_tokens": MAX_MODEL_TOKENS},
        "verified_model_fields_used": [
            "meta.toolIds",
            "meta.filterIds",
            "meta.defaultFilterIds",
            "meta.capabilities.builtin_tools",
            "params.function_calling",
            "params.max_tokens",
            "params.temperature",
            "params.top_p",
            "meta.profile_image_url",
        ],
        "builtin_tool_note": "OpenWebUI Built-in Tool categories are version-dependent. This project safely enables meta.capabilities.builtin_tools and params.function_calling=native; category availability remains controlled by the OpenWebUI instance.",
        "offline_note": "The standard workflow is offline/air-gapped. Public network tools are not assigned to models and are not part of tools_first.",
        "filter_note": "OpenWebUI filter functions are registered as Functions. The context compressor is assigned through meta.filterIds and enabled by default through meta.defaultFilterIds for every chat model.",
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
    for record in tool_records:
        if not record.importable:
            issues.append(f"Tool nicht importierbar: {record.id} ({record.path})")
    for record in function_records:
        if not record.importable:
            issues.append(f"Function nicht importierbar: {record.id} ({record.path})")
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
        if params.get("max_tokens") != MAX_MODEL_TOKENS:
            issues.append(f"Chat-Modell {model_id} nutzt max_tokens nicht auf {MAX_MODEL_TOKENS}")
        expected_temperature = temperature_for_model(model_id)
        if params.get("temperature") != expected_temperature:
            issues.append(f"Chat-Modell {model_id} nutzt temperature nicht use-case-gerecht auf {expected_temperature}")
        if params.get("top_p") != top_p_for_temperature(expected_temperature):
            issues.append(f"Chat-Modell {model_id} nutzt top_p nicht passend zur Temperatur")
        if caps.get("builtin_tools") is not True:
            issues.append(f"Chat-Modell {model_id} hat builtin_tools nicht aktiv")
        if not isinstance(tool_ids, list) or not tool_ids:
            issues.append(f"Chat-Modell {model_id} hat keine toolIds")
        else:
            forbidden = sorted(set(tool_ids).intersection(OFFLINE_EXCLUDED_TOOL_IDS))
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
        for path in [TOOLS_INDEX, ROOT / "Tools" / "README.md", TOOL_REGISTRY, FUNCTION_REGISTRY]:
            if path.exists():
                archive.write(path, rel(path))
    with zipfile.ZipFile(MODELS_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in [
            MODEL_DIST / "README.md",
            MODEL_IMPORT,
            MODEL_FALLBACK,
            TOOLS_FALLBACK_BUNDLE,
            FUNCTIONS_FALLBACK_BUNDLE,
            REGISTRATION_PLAN,
            MODEL_PARAMS_SUMMARY,
            MODEL_DIST / "manual_import_checklist.md",
        ]:
            if path.exists():
                archive.write(path, rel(path))
        for path in (MODEL_DIST / "artifacts").rglob("*"):
            if path.is_file() and should_archive(path):
                archive.write(path, rel(path))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Configure OpenWebUI tools before model tool bindings.")
    parser.add_argument("--write", action="store_true", help="Write generated registry and model JSON changes.")
    parser.add_argument("--check", action="store_true", help="Validate current/generated state and fail on issues.")
    parser.add_argument("--rebuild-zips", action="store_true", help="Rebuild portable offline ZIP artifacts after writing.")
    args = parser.parse_args(list(argv) if argv is not None else None)

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
        return 1 if args.check else 0
    print("\n## Ergebnis")
    print("Tool-/Filter-Registry, Importplan und Modell-Konfiguration sind konsistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
