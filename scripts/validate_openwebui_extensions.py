from __future__ import annotations

import ast
import importlib.util
import inspect
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
EXT_DIR = ROOT / "Tools" / "openwebui_ext"
TOOLS_DIR = EXT_DIR / "tools"
FILTERS_DIR = EXT_DIR / "filters"
SKILLS_DIR = EXT_DIR / "skills"

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
