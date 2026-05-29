from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_BYTES = 10 * 1024 * 1024 * 1024
DEFAULT_ROOTS = [ROOT / "KnowledgePacks", ROOT / "Deployment" / "images"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the offline KnowledgePack/image data budget.")
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        help="maximum allowed total size in bytes; defaults to 10 GiB",
    )
    parser.add_argument(
        "--root",
        action="append",
        default=None,
        help="additional or replacement data root relative to the repository root; may be repeated",
    )
    return parser.parse_args(argv)


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for root in paths:
        if not root.exists():
            continue
        if root.is_file():
            yield root
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and ".git" not in path.parts:
                yield path


def format_bytes(value: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}" if unit != "B" else f"{value} B"
        amount /= 1024
    return f"{value} B"


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    roots = [ROOT / item for item in args.root] if args.root else DEFAULT_ROOTS
    files = [(path, path.stat().st_size) for path in iter_files(roots)]
    total = sum(size for _, size in files)
    largest = sorted(files, key=lambda item: item[1], reverse=True)[:10]

    print(f"Offline-Datenbudget: {format_bytes(total)} / {format_bytes(args.max_bytes)}")
    if largest:
        print("Größte Dateien:")
        for path, size in largest:
            rel = path.relative_to(ROOT).as_posix()
            print(f"- {rel}: {format_bytes(size)}")

    if total > args.max_bytes:
        print("Fehler: Offline-Datenbudget überschritten.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
