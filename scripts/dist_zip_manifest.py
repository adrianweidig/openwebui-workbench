from __future__ import annotations

import zipfile
from pathlib import Path

TEXT_SUFFIXES = {".py", ".md", ".json", ".txt", ".svg", ".yml", ".yaml", ".html", ".htm"}


def relative_name(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def stable_source_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data


def read_zip_entries(target: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(target) as archive:
        return {
            info.filename: archive.read(info.filename)
            for info in archive.infolist()
            if not info.is_dir()
        }


def zip_drift_issues(root: Path, target: Path, sources: list[Path]) -> list[str]:
    expected = {relative_name(root, path): path for path in sources}
    if not target.exists():
        return [f"{relative_name(root, target)} fehlt; Dist-ZIP mit --rebuild-zips neu erzeugen."]
    try:
        entries = read_zip_entries(target)
    except (OSError, zipfile.BadZipFile) as exc:
        return [f"{relative_name(root, target)} ist nicht lesbar ({type(exc).__name__}); Dist-ZIP neu erzeugen."]

    issues: list[str] = []
    missing = sorted(set(expected) - set(entries))
    extra = sorted(set(entries) - set(expected))
    if missing:
        issues.append(f"{relative_name(root, target)} fehlt Eintrag: {missing[0]}" + (f" (+{len(missing) - 1} weitere)" if len(missing) > 1 else ""))
    if extra:
        issues.append(f"{relative_name(root, target)} enthält veralteten Eintrag: {extra[0]}" + (f" (+{len(extra) - 1} weitere)" if len(extra) > 1 else ""))
    for name in sorted(set(expected).intersection(entries)):
        if entries[name] != stable_source_bytes(expected[name]):
            issues.append(f"{relative_name(root, target)} enthält veralteten Inhalt für {name}")
            break
    return issues
