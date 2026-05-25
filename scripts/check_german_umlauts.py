#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

PROTECTED_PATTERN = re.compile(r"(`[^`]*`|[\w./\\-]+\.(?:css|html|json|md|py|svg|txt|yaml|yml|zip))")

LITERAL_REPLACEMENTS = {
    "Abhaengig": "Abhängig",
    "abhaengig": "abhängig",
    "Abhaengigkeit": "Abhängigkeit",
    "Abhaengigkeiten": "Abhängigkeiten",
    "abhaengigkeiten": "abhängigkeiten",
    "Aender": "Änder",
    "aender": "änder",
    "Anhaenge": "Anhänge",
    "anhaenge": "anhänge",
    "Auffaellig": "Auffällig",
    "auffaellig": "auffällig",
    "Ausfuehr": "Ausführ",
    "ausfuehr": "ausführ",
    "auswaehl": "auswähl",
    "Beschluesse": "Beschlüsse",
    "beschluesse": "beschlüsse",
    "befuell": "befüll",
    "Befaehig": "Befähig",
    "befaehig": "befähig",
    "Datenfluesse": "Datenflüsse",
    "datenfluesse": "datenflüsse",
    "ermoeglich": "ermöglich",
    "Ergaenz": "Ergänz",
    "ergaenz": "ergänz",
    "erfuell": "erfüll",
    "faehig": "fähig",
    "Faehig": "Fähig",
    "Faehigkeit": "Fähigkeit",
    "faehigkeit": "fähigkeit",
    "faelle": "fälle",
    "Faelle": "Fälle",
    "fuer": "für",
    "Fuer": "Für",
    "fuehr": "führ",
    "Fuehr": "Führ",
    "fueg": "füg",
    "Fueg": "Füg",
    "gehoer": "gehör",
    "Gehoer": "Gehör",
    "geprueft": "geprüft",
    "Geprueft": "Geprüft",
    "grossen": "großen",
    "Grossen": "Großen",
    "gueltig": "gültig",
    "Gueltig": "Gültig",
    "koennen": "können",
    "Koennen": "Können",
    "Klaerung": "Klärung",
    "klaerung": "klärung",
    "Kontrollfluesse": "Kontrollflüsse",
    "kontrollfluesse": "kontrollflüsse",
    "laengen": "längen",
    "Laengen": "Längen",
    "lauffaehig": "lauffähig",
    "Lauffaehig": "Lauffähig",
    "Loesung": "Lösung",
    "loesung": "lösung",
    "Massnahmen": "Maßnahmen",
    "massnahmen": "maßnahmen",
    "muessen": "müssen",
    "Muessen": "Müssen",
    "naechst": "nächst",
    "Naechst": "Nächst",
    "noetig": "nötig",
    "Noetig": "Nötig",
    "oeffnen": "öffnen",
    "Oeffnen": "Öffnen",
    "praezise": "präzise",
    "Praezise": "Präzise",
    "Praesentationssteuerung": "Präsentationssteuerung",
    "Primaere": "Primäre",
    "primaere": "primäre",
    "Prioritaet": "Priorität",
    "prioritaet": "priorität",
    "Pruef": "Prüf",
    "pruef": "prüf",
    "Qualitaet": "Qualität",
    "qualitaet": "qualität",
    "Rueck": "Rück",
    "rueck": "rück",
    "Saetze": "Sätze",
    "saetze": "sätze",
    "Stoert": "Stört",
    "stoert": "stört",
    "Testfaelle": "Testfälle",
    "testfaelle": "testfälle",
    "Testluecken": "Testlücken",
    "testluecken": "testlücken",
    "Tonalitaet": "Tonalität",
    "tonalitaet": "tonalität",
    "ueber": "über",
    "Ueber": "Über",
    "Uebergabe": "Übergabe",
    "Uebersetzung": "Übersetzung",
    "unterstuetz": "unterstütz",
    "Unterstuetz": "Unterstütz",
    "verfuegbar": "verfügbar",
    "Verfuegbar": "Verfügbar",
    "vollstaendig": "vollständig",
    "Vollstaendig": "Vollständig",
    "waehl": "wähl",
    "Waehl": "Wähl",
    "Vertraege": "Verträge",
    "vertraege": "verträge",
    "erklaer": "erklär",
    "Erklaer": "Erklär",
    "zurueck": "zurück",
    "Zurueck": "Zurück",
    "zusaetz": "zusätz",
    "Zusaetz": "Zusätz",
    "Zustaende": "Zustände",
    "zustaende": "zustände",
}

REGEX_REPLACEMENTS = (
    (re.compile(r"\bweiss\b"), "weiß"),
    (re.compile(r"\bWeiss\b"), "Weiß"),
)


def tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    return [ROOT / line for line in completed.stdout.splitlines() if line.strip()]


def iter_text_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.resolve() == SELF:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def transform_unprotected(text: str, transform: Callable[[str], str]) -> str:
    parts: list[str] = []
    last = 0
    for match in PROTECTED_PATTERN.finditer(text):
        parts.append(transform(text[last : match.start()]))
        parts.append(match.group(0))
        last = match.end()
    parts.append(transform(text[last:]))
    return "".join(parts)


def normalized_segment(text: str) -> str:
    result = text
    for source, target in LITERAL_REPLACEMENTS.items():
        result = result.replace(source, target)
    for pattern, target in REGEX_REPLACEMENTS:
        result = pattern.sub(target, result)
    return result


def normalized_text(text: str) -> str:
    return transform_unprotected(text, normalized_segment)


def line_hits(path: Path, text: str) -> list[str]:
    hits: list[str] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        visible_line = transform_unprotected(line, lambda segment: segment)
        protected_spans = list(PROTECTED_PATTERN.finditer(line))
        for match in reversed(protected_spans):
            visible_line = visible_line[: match.start()] + (" " * (match.end() - match.start())) + visible_line[match.end() :]
        found = sorted(source for source in LITERAL_REPLACEMENTS if source in visible_line)
        found.extend(pattern.pattern for pattern, _target in REGEX_REPLACEMENTS if pattern.search(visible_line))
        if found:
            rel = path.relative_to(ROOT).as_posix()
            hits.append(f"{rel}:{line_number}: {', '.join(found)}")
    return hits


def write_utf8(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check German prose for ASCII umlaut spellings and UTF-8 readability.")
    parser.add_argument("--fix", action="store_true", help="replace curated ASCII umlaut spellings in tracked text files")
    args = parser.parse_args(argv)

    all_hits: list[str] = []
    changed: list[str] = []
    utf8_errors: list[str] = []

    for path in iter_text_files(tracked_files()):
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            utf8_errors.append(f"{rel}: {exc}")
            continue
        updated = normalized_text(text)
        if args.fix and updated != text:
            write_utf8(path, updated)
            changed.append(rel)
            text = updated
        all_hits.extend(line_hits(path, text))

    if changed:
        print("# German umlaut normalization")
        for rel in changed:
            print(f"- aktualisiert: {rel}")

    if utf8_errors:
        print("# UTF-8 errors", file=sys.stderr)
        for hit in utf8_errors:
            print(f"- {hit}", file=sys.stderr)

    if all_hits:
        print("# ASCII umlaut spellings", file=sys.stderr)
        for hit in all_hits:
            print(f"- {hit}", file=sys.stderr)

    return 1 if utf8_errors or all_hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
