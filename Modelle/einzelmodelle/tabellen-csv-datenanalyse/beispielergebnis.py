#!/usr/bin/env python3
"""Offline-Goldstandard für `tabellen-csv-datenanalyse`.

Erstellt ein kleines, reproduzierbares CSV-Profil mit Spaltentypen,
Missing-Value-Zählung und numerischen Kennzahlen. Nur Standardbibliothek.

Nutzung:
    python beispielergebnis.py --demo
    python beispielergebnis.py daten.csv
    python beispielergebnis.py --self-test
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import statistics
from pathlib import Path
from typing import Sequence


def demo_csv() -> str:
    return "\n".join(
        [
            "team,tickets,sla_hours,region",
            "Service Desk,42,6.5,DACH",
            "Field Support,18,14.0,DACH",
            "Network,7,2.0,EMEA",
            "Service Desk,39,7.5,DACH",
        ]
    )


def read_rows(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV enthält keine Kopfzeile.")
    rows = list(reader)
    if not rows:
        raise ValueError("CSV enthält keine Datenzeilen.")
    return rows


def as_float(value: str) -> float | None:
    value = value.strip().replace(",", ".")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def profile(rows: list[dict[str, str]]) -> dict[str, object]:
    columns = list(rows[0].keys())
    result: dict[str, object] = {"row_count": len(rows), "columns": []}
    column_profiles: list[dict[str, object]] = []
    for column in columns:
        values = [(row.get(column) or "").strip() for row in rows]
        missing = sum(1 for value in values if value == "")
        numeric = [number for value in values if (number := as_float(value)) is not None]
        item: dict[str, object] = {
            "name": column,
            "missing": missing,
            "distinct": len(set(values)),
            "inferred_type": "number" if len(numeric) == len(values) - missing else "text",
        }
        if numeric:
            item["min"] = min(numeric)
            item["max"] = max(numeric)
            item["mean"] = round(statistics.fmean(numeric), 2)
        column_profiles.append(item)
    result["columns"] = column_profiles
    return result


def run_self_test() -> None:
    rows = read_rows(demo_csv())
    result = profile(rows)
    assert result["row_count"] == 4
    tickets = next(item for item in result["columns"] if item["name"] == "tickets")
    assert tickets["inferred_type"] == "number"
    assert tickets["max"] == 42.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        run_self_test()
        print("Self-test passed.")
        return 0
    text = demo_csv() if args.demo else Path(args.csv_path).read_text(encoding="utf-8-sig")
    print(json.dumps(profile(read_rows(text)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
