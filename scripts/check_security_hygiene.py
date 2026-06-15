from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".css",
    ".env",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIPPED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIPPED_PREFIXES = {
    "Modelle/dist/",
    "Tools/dist/",
}
PLACEHOLDER_MARKERS = {
    "DUMMY",
    "EXAMPLE",
    "LOCAL-DEV",
    "MASKIERT",
    "PASTE",
    "PLACEHOLDER",
    "REDACTED",
    "REPLACE",
    "REAL-PRODUCTION",
    "VERIFY-ONLY",
    "YOUR_",
    "${",
    "<",
}
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?ix)"
    r"\b(?P<name>[A-Z0-9_.-]*(?:TOKEN|SECRET|PASSWORD|PASSWD|API[_-]?KEY|AUTHORIZATION|COOKIE)[A-Z0-9_.-]*)\b"
    r"\s*[:=]\s*"
    r"[\"']?(?P<value>[A-Z0-9_./:+={}$-]{12,})[\"']?"
)
SECRET_LITERAL_RES = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
]
PUBLIC_INFRA_MARKER_RES = [
    re.compile("".join(("tor", "vs", r"[.-]", "bw")), re.IGNORECASE),
]


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    kind: str


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local security hygiene checks without printing secret values.")
    parser.add_argument(
        "--include-bandit",
        action="store_true",
        help="run Bandit if it is installed; the default check has no third-party dependency",
    )
    return parser.parse_args(argv)


def candidate_paths(root: Path) -> list[Path]:
    try:
        completed = subprocess.run(
            ["git", "-c", "core.quotePath=false", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        names = [name for name in completed.stdout.decode("utf-8", errors="replace").split("\0") if name]
        return [root / name for name in names]
    except (OSError, subprocess.CalledProcessError):
        return [path for path in root.rglob("*") if path.is_file()]


def should_scan(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
        rel_name = path.relative_to(root).as_posix()
    except ValueError:
        return False
    if any(part in SKIPPED_DIRS for part in rel_parts):
        return False
    if any(rel_name.startswith(prefix) for prefix in SKIPPED_PREFIXES):
        return False
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        return path.stat().st_size <= 2_000_000
    except OSError:
        return False


def is_placeholder(value: str, line: str) -> bool:
    haystack = f"{value} {line}".upper()
    if any(marker in haystack for marker in PLACEHOLDER_MARKERS):
        return True
    return value.strip().lower() in {"none", "null", "true", "false", "empty"}


def is_secret_name(name: str) -> bool:
    upper = name.upper()
    if "TIKTOKEN" in upper or upper.endswith("_TOKENS") or upper in {"TOKENS", "TOTAL_TOKENS", "MAX_TOKENS"}:
        return False
    if any(marker in upper for marker in ("PASSWORD", "PASSWD", "SECRET", "API_KEY", "API-KEY", "AUTHORIZATION", "COOKIE")):
        return True
    if "TOKEN" in upper:
        return upper in {"TOKEN"} or any(
            marker in upper
            for marker in ("ACCESS", "ADMIN", "API", "AUTH", "CRAWL4AI", "JUPYTER", "LLM", "LOGIN", "OAUTH", "OPENWEBUI", "SEARXNG")
        )
    return False


def looks_like_secret_value(value: str, line: str) -> bool:
    clean = value.strip().strip("\"'`,")
    if is_placeholder(clean, line):
        return False
    if len(clean) < 16:
        return False
    if clean.startswith("$"):
        return False
    if any(marker in clean for marker in ("(", ")", "[", "]", "{", "}")):
        return False
    if clean.startswith(("Read-", "Test-", "self.", "os.", "Path.", "runtime.", "value.", "state.")):
        return False
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", clean):
        return False
    if "/" in clean and not any(pattern.search(clean) for pattern in SECRET_LITERAL_RES):
        return False
    has_alpha = any(char.isalpha() for char in clean)
    has_digit = any(char.isdigit() for char in clean)
    has_symbol = any(not char.isalnum() for char in clean)
    return has_alpha and (has_digit or has_symbol)


def scan_text(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings
    for line_no, line in enumerate(lines, start=1):
        for match in SECRET_ASSIGNMENT_RE.finditer(line):
            name = match.group("name")
            value = match.group("value")
            if is_secret_name(name) and looks_like_secret_value(value, line):
                findings.append(Finding(path.relative_to(root), line_no, f"secret assignment in {name}"))
        if not is_placeholder("", line):
            for pattern in SECRET_LITERAL_RES:
                if pattern.search(line):
                    findings.append(Finding(path.relative_to(root), line_no, "secret-looking token literal"))
                    break
    return findings


def scan_public_infra_markers(paths: Iterable[Path], root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(paths):
        if not path.exists():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        rel_name = rel.as_posix()
        if any(pattern.search(rel_name) for pattern in PUBLIC_INFRA_MARKER_RES):
            findings.append(Finding(rel, 0, "public infrastructure marker in path"))
            continue
        if not should_scan(path, root):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(lines, start=1):
            if any(pattern.search(line) for pattern in PUBLIC_INFRA_MARKER_RES):
                findings.append(Finding(rel, line_no, "public infrastructure marker in text"))
    return findings


def scan_paths(paths: Iterable[Path], root: Path = ROOT) -> tuple[int, list[Finding]]:
    checked = 0
    findings: list[Finding] = []
    for path in sorted(paths):
        if not should_scan(path, root):
            continue
        checked += 1
        findings.extend(scan_text(path, root))
    return checked, findings


def run_bandit(root: Path) -> int:
    bandit = shutil.which("bandit")
    if not bandit:
        print("- Bandit: übersprungen, nicht installiert")
        return 0
    completed = subprocess.run(
        [
            bandit,
            "-q",
            "-ll",
            "-r",
            "scripts",
            "Tools",
            "Workbench",
            "-x",
            "Tools/openwebui_ext/tests,Workbench/dashboard/tests",
        ],
        cwd=root,
    )
    if completed.returncode == 0:
        print("- Bandit: keine Medium-/High-Befunde")
    else:
        print("- Bandit: Befunde gemeldet; Details stehen in der Bandit-Ausgabe")
    return completed.returncode


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    paths = candidate_paths(ROOT)
    checked, findings = scan_paths(paths, ROOT)
    public_marker_findings = scan_public_infra_markers(paths, ROOT)
    print("# Security hygiene check")
    print(f"- Dateien geprüft: {checked}")
    print(f"- Verdächtige Secret-Werte: {len(findings)}")
    print(f"- Öffentliche Infrastrukturmarker: {len(public_marker_findings)}")
    if findings or public_marker_findings:
        print("\n## Befunde")
        for finding in findings:
            print(f"- {finding.path.as_posix()}:{finding.line}: {finding.kind}")
        for finding in public_marker_findings:
            line = finding.line if finding.line else 1
            print(f"- {finding.path.as_posix()}:{line}: {finding.kind}")
        print("\nHinweis: Werte werden absichtlich nicht ausgegeben.")
        return 1
    if args.include_bandit:
        return run_bandit(ROOT)
    print("- Bandit: übersprungen, optional mit --include-bandit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
