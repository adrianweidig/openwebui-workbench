from __future__ import annotations

from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_PAIRS = [
    ("README.md", "README.en.md"),
    ("CONTRIBUTING.md", "CONTRIBUTING.en.md"),
    ("SECURITY.md", "SECURITY.en.md"),
    ("SUPPORT.md", "SUPPORT.en.md"),
    ("CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.en.md"),
    ("CHANGELOG.md", "CHANGELOG.en.md"),
    ("docs/ARCHITECTURE.md", "docs/en/ARCHITECTURE.md"),
    ("docs/WORKBENCH_DASHBOARD.md", "docs/en/WORKBENCH_DASHBOARD.md"),
    ("docs/de/index.md", "docs/en/index.md"),
    ("docs/de/I18N.md", "docs/en/I18N.md"),
]


def pair_issues(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    for german, english in LANGUAGE_PAIRS:
        german_path = root / german
        english_path = root / english
        if not german_path.is_file():
            issues.append(f"{german} fehlt")
        if not english_path.is_file():
            issues.append(f"{english} fehlt")
        german_header = "\n".join(german_path.read_text(encoding="utf-8").splitlines()[:5]) if german_path.is_file() else ""
        english_header = "\n".join(english_path.read_text(encoding="utf-8").splitlines()[:5]) if english_path.is_file() else ""
        if german_path.is_file() and "English" not in german_header:
            issues.append(f"{german} enthält keinen sichtbaren English-Sprachlink in der Kopfzeile")
        if english_path.is_file() and "Deutsch" not in english_header:
            issues.append(f"{english} enthält keinen sichtbaren Deutsch-Sprachlink in der Kopfzeile")
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    issues = pair_issues(ROOT)
    print("# Documentation language pair check")
    print(f"- Sprachpaare geprüft: {len(LANGUAGE_PAIRS)}")
    if issues:
        print("\n## Befunde")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("- Ergebnis: alle erwarteten Sprachpaare vorhanden")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
