from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import re
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
MODEL_ARTIFACTS = MODEL_DIST / "artifacts" / "models"
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
TOOLS_ZIP = TOOLS_DIST / "openwebui-tools-skills-offline.zip"
MODELS_ZIP = MODEL_DIST / "openwebui-offline-artifacts.zip"

FUNCTION_CALLING_NATIVE = "native"
CHAT_MODEL_TOOL_MODE = "all_validated_custom_tools"
CHAT_MODEL_FILTER_MODE = "all_validated_default_filters"
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
                offline=bool(indexed.get("offline", True)),
                configuration=list(indexed.get("configuration", [])),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                importable=importable,
                methods=methods,
            )
        )
    return records


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
    registry = {
        "schema": "openwebui-tool-registry/v1",
        "order": ["tools", "skills", "models"],
        "tool_import_order": [record.id for record in records if record.importable],
        "tools": [record.__dict__ for record in records],
    }
    fallback = {
        "schema": "openwebui-tool-bundle-fallback/v1",
        "tools": [
            {
                "id": record.id,
                "name": record.name,
                "source_file": record.path,
                "config_example": "Tools/jupyter/jupyter_config.example.json" if record.id == "air_gapped_jupyter_python" else None,
            }
            for record in records
            if record.importable
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

    meta["toolIds"] = list(tool_ids)
    meta["filterIds"] = merge_unique(meta.get("filterIds"), filter_ids)
    meta["defaultFilterIds"] = merge_unique(meta.get("defaultFilterIds"), filter_ids)
    params["function_calling"] = FUNCTION_CALLING_NATIVE
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
    tool_ids = [record.id for record in tool_records if record.importable]
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


def write_registration_plan(tool_records: List[ToolRecord], function_records: List[FunctionRecord], models: List[Dict[str, Any]], write: bool) -> bool:
    filter_ids = [record.id for record in function_records if record.importable and record.function_type == "filter"]
    plan = {
        "schema": "openwebui-registration-plan/v1",
        "order": [
            "1_import_workspace_tools",
            "2_import_workspace_filters",
            "3_import_workspace_skills",
            "4_import_or_update_models",
            "5_enable_user_or_group_access",
        ],
        "tools_first": [record.id for record in tool_records if record.importable],
        "filters_before_models": filter_ids,
        "model_import_file": rel(MODEL_IMPORT),
        "global_model_params_recommendation": {"function_calling": FUNCTION_CALLING_NATIVE},
        "verified_model_fields_used": [
            "meta.toolIds",
            "meta.filterIds",
            "meta.defaultFilterIds",
            "meta.capabilities.builtin_tools",
            "params.function_calling",
        ],
        "builtin_tool_note": "OpenWebUI Built-in Tool categories are version-dependent. This project safely enables meta.capabilities.builtin_tools and params.function_calling=native; category availability remains controlled by the OpenWebUI instance.",
        "filter_note": "OpenWebUI filter functions are registered as Functions. The context compressor is assigned through meta.filterIds and enabled by default through meta.defaultFilterIds for every chat model.",
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
        if caps.get("builtin_tools") is not True:
            issues.append(f"Chat-Modell {model_id} hat builtin_tools nicht aktiv")
        if not isinstance(tool_ids, list) or not tool_ids:
            issues.append(f"Chat-Modell {model_id} hat keine toolIds")
        else:
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
                if path.is_file():
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
            MODEL_DIST / "manual_import_checklist.md",
        ]:
            if path.exists():
                archive.write(path, rel(path))
        for path in (MODEL_DIST / "artifacts").rglob("*"):
            if path.is_file():
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
    changed_models, models = apply_model_config(records, function_records, args.write)
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
    print(f"- Änderungen erkannt: {changed_tools_index or changed_tool_artifacts or changed_function_artifacts or changed_models or changed_plan}")
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
