from __future__ import annotations

import ast
import importlib.util
import inspect
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Tuple, get_type_hints

try:
    from pydantic import create_model
except Exception:  # pragma: no cover - OpenWebUI provides pydantic
    create_model = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
EXT_DIR = ROOT / "Tools" / "openwebui_ext"
TOOLS_DIR = EXT_DIR / "tools"
FILTERS_DIR = EXT_DIR / "filters"
SKILLS_DIR = EXT_DIR / "skills"
TOOLS_DIST = ROOT / "Tools" / "dist"
TOOL_IMPORT = TOOLS_DIST / "openwebui-tools-import.json"
OFFLINE_TOOL_IMPORT = TOOLS_DIST / "openwebui-tools-offline-import.json"
FUNCTION_IMPORT = TOOLS_DIST / "openwebui-functions-import.json"

RISK_PATTERNS = {
    "os.system": re.compile(r"\bos\.system\s*\("),
    "subprocess.Popen": re.compile(r"\bsubprocess\.Popen\s*\("),
    "dynamic eval": re.compile(r"\beval\s*\("),
    "dynamic exec": re.compile(r"\bexec\s*\("),
    "pickle.loads": re.compile(r"\bpickle\.loads\s*\("),
    "hardcoded secret marker": re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*=\s*['\"][A-Za-z0-9_./+=-]{16,}['\"]"),
}

ALLOWED_SPECIAL_PARAMS = {"self", "__event_emitter__", "__event_call__", "__user__", "__metadata__", "__messages__", "__files__", "__model__", "__oauth_token__"}


def load_module(path: Path) -> ModuleType:
    module_name = "owui_tool_" + re.sub(r"\W+", "_", path.stem)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("importlib spec konnte nicht erstellt werden")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_tool_methods(tools_cls: type) -> List[Tuple[str, inspect.Signature, bool]]:
    methods: List[Tuple[str, inspect.Signature, bool]] = []
    for name, member in inspect.getmembers(tools_cls, predicate=inspect.isfunction):
        if name.startswith("_") or name in {"__init__"}:
            continue
        methods.append((name, inspect.signature(member), inspect.iscoroutinefunction(member)))
    return methods


def openwebui_schema_for_function(function: Callable[..., Any]) -> None:
    if create_model is None:
        raise RuntimeError("pydantic ist nicht verfügbar; OpenWebUI-GUI-Schemaerzeugung kann nicht geprüft werden")
    type_hints = get_type_hints(function)
    field_defs: Dict[str, Tuple[Any, Any]] = {}
    for name, param in inspect.signature(function).parameters.items():
        type_hint = type_hints.get(name, Any)
        default_value = param.default if param.default is not param.empty else ...
        field_defs[name] = (type_hint, default_value)
    model = create_model(function.__name__, **field_defs)
    model.model_json_schema()


def check_gui_tool_schema(tool_instance: object) -> List[str]:
    issues: List[str] = []
    for name in dir(tool_instance):
        member = getattr(tool_instance, name)
        if name.startswith("_") or inspect.isclass(member) or not callable(member):
            continue
        try:
            openwebui_schema_for_function(member)
        except Exception as exc:
            issues.append(f"OpenWebUI-GUI-Schema für Methode `{name}` fehlgeschlagen: {type(exc).__name__}: {exc}")
    return issues


def check_tool(path: Path) -> List[str]:
    issues: List[str] = []
    text = path.read_text(encoding="utf-8")
    for label, pattern in RISK_PATTERNS.items():
        if pattern.search(text):
            issues.append(f"Riskantes Muster `{label}` gefunden")
    try:
        ast.parse(text)
    except SyntaxError as exc:
        issues.append(f"Syntaxfehler: Zeile {exc.lineno}: {exc.msg}")
        return issues
    try:
        module = load_module(path)
    except Exception as exc:
        issues.append(f"Import fehlgeschlagen: {type(exc).__name__}: {exc}")
        return issues
    tools_cls = getattr(module, "Tools", None)
    if tools_cls is None or not inspect.isclass(tools_cls):
        issues.append("Keine Klasse `Tools` gefunden")
        return issues
    try:
        tool_instance = tools_cls()
    except Exception as exc:
        issues.append(f"`Tools()` Instanziierung fehlgeschlagen: {type(exc).__name__}: {exc}")
        return issues
    issues.extend(check_gui_tool_schema(tool_instance))
    methods = public_tool_methods(tools_cls)
    if not methods:
        issues.append("Keine öffentliche Tool-Methode gefunden")
    for name, signature, is_async in methods:
        if not is_async:
            issues.append(f"Methode `{name}` ist nicht async")
        for param_name, param in signature.parameters.items():
            if param_name in ALLOWED_SPECIAL_PARAMS:
                continue
            if param.annotation is inspect._empty:
                issues.append(f"Methode `{name}` Parameter `{param_name}` ohne Typannotation")
        if signature.return_annotation is inspect._empty:
            issues.append(f"Methode `{name}` ohne Return-Typannotation")
    return issues


def check_gui_import_bundle(path: Path, expected_kind: str) -> List[str]:
    issues: List[str] = []
    if not path.exists():
        return [f"GUI-Importdatei fehlt: {path.relative_to(ROOT)}"]
    try:
        data = __import__("json").loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"GUI-Importdatei kann nicht gelesen werden: {type(exc).__name__}: {exc}"]
    if not isinstance(data, list) or not data:
        return ["GUI-Importdatei muss ein nicht-leeres JSON-Array sein"]
    ids: List[str] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            issues.append(f"Eintrag {index} ist kein Objekt")
            continue
        tool_id = item.get("id")
        if not isinstance(tool_id, str) or not tool_id.isidentifier():
            issues.append(f"Eintrag {index} hat keine OpenWebUI-kompatible id")
        elif tool_id.lower() != tool_id:
            issues.append(f"Eintrag {tool_id} ist nicht lowercase; OpenWebUI normalisiert IDs beim Import")
        elif tool_id in ids:
            issues.append(f"ID doppelt im GUI-Importbundle: {tool_id}")
        else:
            ids.append(tool_id)
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            issues.append(f"Eintrag {tool_id or index} hat keinen Namen")
        if not isinstance(item.get("content"), str) or "class " not in item["content"]:
            issues.append(f"Eintrag {tool_id or index} enthält keinen Python-Quelltext")
        meta = item.get("meta")
        if not isinstance(meta, dict):
            issues.append(f"Eintrag {tool_id or index} hat kein meta-Objekt")
        if expected_kind == "function" and item.get("type") not in {"filter", "action", "pipe"}:
            issues.append(f"Function-Eintrag {tool_id or index} hat keinen gültigen type")
    if expected_kind == "tool":
        for item in data:
            if isinstance(item, dict) and isinstance(item.get("content"), str) and "class Tools" not in item["content"]:
                issues.append(f"Tool-Eintrag {item.get('id')} enthält keine Klasse `Tools`")
    if expected_kind == "function":
        for item in data:
            if isinstance(item, dict) and isinstance(item.get("content"), str) and not any(marker in item["content"] for marker in ["class Filter", "class Pipe", "class Action"]):
                issues.append(f"Function-Eintrag {item.get('id')} enthält keine Function-Klasse")
    return issues


def check_filter(path: Path) -> List[str]:
    issues: List[str] = []
    text = path.read_text(encoding="utf-8")
    for label, pattern in RISK_PATTERNS.items():
        if pattern.search(text):
            issues.append(f"Riskantes Muster `{label}` gefunden")
    try:
        ast.parse(text)
    except SyntaxError as exc:
        issues.append(f"Syntaxfehler: Zeile {exc.lineno}: {exc.msg}")
        return issues
    try:
        module = load_module(path)
    except Exception as exc:
        issues.append(f"Import fehlgeschlagen: {type(exc).__name__}: {exc}")
        return issues
    filter_cls = getattr(module, "Filter", None)
    if filter_cls is None or not inspect.isclass(filter_cls):
        issues.append("Keine Klasse `Filter` gefunden")
        return issues
    hooks = [
        name
        for name in ["inlet", "stream", "outlet"]
        if inspect.isfunction(getattr(filter_cls, name, None))
    ]
    if not hooks:
        issues.append("Kein Filter-Hook `inlet`, `stream` oder `outlet` gefunden")
    for name in hooks:
        method = getattr(filter_cls, name)
        if not inspect.iscoroutinefunction(method):
            issues.append(f"Hook `{name}` ist nicht async")
        signature = inspect.signature(method)
        for param_name, param in signature.parameters.items():
            if param_name in ALLOWED_SPECIAL_PARAMS:
                continue
            if param.annotation is inspect._empty:
                issues.append(f"Hook `{name}` Parameter `{param_name}` ohne Typannotation")
        if signature.return_annotation is inspect._empty:
            issues.append(f"Hook `{name}` ohne Return-Typannotation")
    return issues


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip()
    body = text[end + 4 :].strip()
    data: Dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data, body


def check_skill(path: Path) -> List[str]:
    issues: List[str] = []
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    if not meta.get("name"):
        issues.append("Frontmatter `name` fehlt")
    if not meta.get("description"):
        issues.append("Frontmatter `description` fehlt")
    if len(body.strip()) < 80:
        issues.append("Skill-Inhalt ist zu kurz")
    return issues


def main() -> int:
    tool_files = sorted(TOOLS_DIR.glob("*.py"))
    filter_files = sorted(FILTERS_DIR.glob("*.py")) if FILTERS_DIR.exists() else []
    skill_files = sorted(SKILLS_DIR.glob("*.md"))
    all_issues: Dict[str, List[str]] = {}

    for path in tool_files:
        issues = check_tool(path)
        if issues:
            all_issues[str(path.relative_to(ROOT))] = issues

    for path in filter_files:
        issues = check_filter(path)
        if issues:
            all_issues[str(path.relative_to(ROOT))] = issues

    for path in skill_files:
        if path.name.upper() == "README.MD":
            continue
        issues = check_skill(path)
        if issues:
            all_issues[str(path.relative_to(ROOT))] = issues

    for bundle, kind in [(TOOL_IMPORT, "tool"), (OFFLINE_TOOL_IMPORT, "tool"), (FUNCTION_IMPORT, "function")]:
        issues = check_gui_import_bundle(bundle, kind)
        if issues:
            all_issues[str(bundle.relative_to(ROOT))] = issues

    print("# OpenWebUI Extension Validation")
    print()
    print(f"- Tools geprüft: {len(tool_files)}")
    print(f"- Filter geprüft: {len(filter_files)}")
    print(f"- Skills geprüft: {len([p for p in skill_files if p.name.upper() != 'README.MD'])}")
    print(f"- Dateien mit Befunden: {len(all_issues)}")
    print()
    if all_issues:
        print("## Befunde")
        for file_name, issues in all_issues.items():
            print(f"### {file_name}")
            for issue in issues:
                print(f"- {issue}")
        return 1
    print("## Ergebnis")
    print("Alle geprüften OpenWebUI-Tools, Filter und Skills sind syntaktisch und strukturell valide.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
