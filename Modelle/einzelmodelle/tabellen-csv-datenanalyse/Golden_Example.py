#!/usr/bin/env python3
"""Golden Example für `tabellen-csv-datenanalyse`.

Lokales, reproduzierbares CSV-Profiling ohne externe Abhängigkeiten.
Das Skript liest CSV-Daten, erstellt ein Datenprofil, prüft Datenqualität,
berechnet einfache Kennzahlen und gibt einen JSON-Bericht aus.

Nutzung:
    python Golden_Example.py --demo
    python Golden_Example.py daten.csv
    python Golden_Example.py daten.csv --delimiter ";"
    python Golden_Example.py --self-test

Grundsätze:
- Originaldateien werden nur gelesen, nie überschrieben.
- Kennzahlen werden ausschließlich aus geladenen Daten berechnet.
- Fehlende Werte, Typannahmen und Duplikate werden separat ausgewiesen.
- Personenbezogene Daten werden nicht ausgegeben; Beispielwerte bleiben anonymisiert.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


MISSING_MARKERS = {"", "na", "n/a", "null", "none", "-", "--"}


def demo_csv() -> str:
    """Gibt einen kleinen anonymisierten Demonstrationsdatensatz zurück."""
    return "\n".join(
        [
            "ticket_id,team,region,created_date,tickets,sla_hours,status",
            "TCK-1001,Service Desk,DACH,2026-06-01,42,6.5,closed",
            "TCK-1002,Field Support,DACH,2026-06-02,18,14.0,open",
            "TCK-1003,Network,EMEA,2026-06-02,7,2.0,closed",
            "TCK-1004,Service Desk,DACH,2026-06-03,39,7.5,waiting",
            "TCK-1005,Security,EMEA,2026-06-04,,9.0,open",
            "TCK-1005,Security,EMEA,2026-06-04,,9.0,open",
        ]
    )


def normalize_missing(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def is_missing(value: str | None) -> bool:
    return normalize_missing(value).lower() in MISSING_MARKERS


def parse_number(value: str | None) -> float | None:
    """Parst einfache Zahlen mit Punkt oder Komma als Dezimaltrennzeichen."""
    if is_missing(value):
        return None
    normalized = normalize_missing(value).replace(" ", "").replace(",", ".")
    try:
        number = float(normalized)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def parse_iso_date(value: str | None) -> datetime | None:
    """Erkennt stabile ISO-Datumswerte ohne Format-Raten über mehrere Locale-Regeln."""
    if is_missing(value):
        return None
    text = normalize_missing(value)
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def read_csv_text(path: str | None, use_demo: bool) -> str:
    if use_demo:
        return demo_csv()
    if not path:
        raise ValueError("Keine CSV-Datei angegeben. Nutze --demo oder übergib einen Dateipfad.")
    return Path(path).read_text(encoding="utf-8-sig")


def read_rows(text: str, delimiter: str | None = None) -> tuple[list[dict[str, str]], list[str], str]:
    sample = text[:4096]
    if delimiter is None:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            detected_delimiter = dialect.delimiter
        except csv.Error:
            detected_delimiter = ","
    else:
        detected_delimiter = delimiter

    reader = csv.DictReader(io.StringIO(text), delimiter=detected_delimiter)
    if not reader.fieldnames:
        raise ValueError("CSV enthält keine Kopfzeile.")
    fieldnames = [field.strip() if field else "" for field in reader.fieldnames]
    if any(not field for field in fieldnames):
        raise ValueError("CSV enthält mindestens eine leere Spaltenüberschrift.")

    rows: list[dict[str, str]] = []
    for row in reader:
        normalized = {column: normalize_missing(row.get(column)) for column in reader.fieldnames}
        rows.append(normalized)

    if not rows:
        raise ValueError("CSV enthält keine Datenzeilen.")
    return rows, list(reader.fieldnames), detected_delimiter


def stable_row_hash(row: dict[str, str], columns: Sequence[str]) -> str:
    joined = "\u241f".join(normalize_missing(row.get(column)) for column in columns)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def infer_column_type(values: Sequence[str]) -> str:
    non_missing = [value for value in values if not is_missing(value)]
    if not non_missing:
        return "empty"
    numeric_count = sum(1 for value in non_missing if parse_number(value) is not None)
    date_count = sum(1 for value in non_missing if parse_iso_date(value) is not None)
    if numeric_count == len(non_missing):
        return "number"
    if date_count == len(non_missing):
        return "date"
    return "text"


def quantile(sorted_values: Sequence[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("Quantil benötigt mindestens einen Wert.")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[int(position)]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def numeric_summary(numbers: Sequence[float]) -> dict[str, float | int]:
    ordered = sorted(numbers)
    result: dict[str, float | int] = {
        "count": len(ordered),
        "min": round(min(ordered), 4),
        "q1": round(quantile(ordered, 0.25), 4),
        "median": round(statistics.median(ordered), 4),
        "q3": round(quantile(ordered, 0.75), 4),
        "max": round(max(ordered), 4),
        "mean": round(statistics.fmean(ordered), 4),
    }
    if len(ordered) > 1:
        result["stdev"] = round(statistics.stdev(ordered), 4)
    else:
        result["stdev"] = 0.0
    return result


def top_values(values: Iterable[str], limit: int = 5) -> list[dict[str, Any]]:
    clean_values = [value for value in values if not is_missing(value)]
    counter = Counter(clean_values)
    return [{"value": value, "count": count} for value, count in counter.most_common(limit)]


def profile_columns(rows: list[dict[str, str]], columns: Sequence[str]) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    row_count = len(rows)

    for column in columns:
        values = [normalize_missing(row.get(column)) for row in rows]
        missing_count = sum(1 for value in values if is_missing(value))
        non_missing_values = [value for value in values if not is_missing(value)]
        inferred_type = infer_column_type(values)

        item: dict[str, Any] = {
            "name": column,
            "inferred_type": inferred_type,
            "row_count": row_count,
            "missing_count": missing_count,
            "missing_ratio": round(missing_count / row_count, 4),
            "distinct_count": len(set(non_missing_values)),
            "top_values": top_values(non_missing_values),
        }

        if inferred_type == "number":
            numbers = [number for value in values if (number := parse_number(value)) is not None]
            item["numeric"] = numeric_summary(numbers)
        elif inferred_type == "date":
            dates = [date for value in values if (date := parse_iso_date(value)) is not None]
            item["date"] = {
                "count": len(dates),
                "min": min(dates).date().isoformat(),
                "max": max(dates).date().isoformat(),
            }

        profiles.append(item)

    return profiles


def duplicate_summary(rows: list[dict[str, str]], columns: Sequence[str]) -> dict[str, Any]:
    hashes = [stable_row_hash(row, columns) for row in rows]
    counts = Counter(hashes)
    duplicate_rows = sum(count - 1 for count in counts.values() if count > 1)
    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_ratio": round(duplicate_rows / len(rows), 4),
    }


def quality_findings(column_profiles: Sequence[dict[str, Any]], duplicate_info: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    if duplicate_info["duplicate_rows"] > 0:
        findings.append(
            {
                "severity": "medium",
                "area": "duplicates",
                "finding": f"{duplicate_info['duplicate_rows']} vollständige Duplikatzeile(n) erkannt.",
                "recommendation": "Duplikate vor Aggregationen fachlich prüfen und Bereinigung reversibel dokumentieren.",
            }
        )

    for column in column_profiles:
        missing_ratio = float(column["missing_ratio"])
        if missing_ratio > 0:
            severity = "high" if missing_ratio >= 0.2 else "medium"
            findings.append(
                {
                    "severity": severity,
                    "area": "missing_values",
                    "finding": f"Spalte `{column['name']}` enthält {column['missing_count']} fehlende Werte.",
                    "recommendation": "Fehlende Werte nicht still imputieren; Ursache prüfen und Bereinigungsregel dokumentieren.",
                }
            )
        if column["inferred_type"] == "empty":
            findings.append(
                {
                    "severity": "high",
                    "area": "schema",
                    "finding": f"Spalte `{column['name']}` enthält keine auswertbaren Werte.",
                    "recommendation": "Spalte entfernen oder Datenlieferung korrigieren.",
                }
            )

    if not findings:
        findings.append(
            {
                "severity": "info",
                "area": "quality",
                "finding": "Keine offensichtlichen Missing-Value- oder Duplikatprobleme im geladenen Datensatz erkannt.",
                "recommendation": "Fachliche Wertebereiche, Einheiten und Schlüsselspalten zusätzlich gegen Datenwörterbuch prüfen.",
            }
        )

    return findings


def build_report(rows: list[dict[str, str]], columns: Sequence[str], delimiter: str, source_label: str) -> dict[str, Any]:
    column_profiles = profile_columns(rows, columns)
    duplicates = duplicate_summary(rows, columns)
    return {
        "data_profile": {
            "source": source_label,
            "row_count": len(rows),
            "column_count": len(columns),
            "delimiter": delimiter,
            "columns": list(columns),
        },
        "data_quality": {
            "duplicates": duplicates,
            "findings": quality_findings(column_profiles, duplicates),
        },
        "column_profiles": column_profiles,
        "reproducibility": {
            "runtime": "Python Standardbibliothek",
            "original_data_overwritten": False,
            "external_services_used": False,
            "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        },
        "limits": [
            "Datentypen werden aus den sichtbaren CSV-Werten abgeleitet.",
            "Datumswerte werden nur als ISO-nahe Formate erkannt.",
            "Fachliche Wertebereiche und Einheiten benötigen ein Datenwörterbuch.",
        ],
    }


def run_self_test() -> None:
    rows, columns, delimiter = read_rows(demo_csv())
    report = build_report(rows, columns, delimiter, "demo")
    assert report["data_profile"]["row_count"] == 6
    assert report["data_profile"]["column_count"] == 7
    assert report["data_quality"]["duplicates"]["duplicate_rows"] == 1
    tickets_profile = next(item for item in report["column_profiles"] if item["name"] == "tickets")
    assert tickets_profile["inferred_type"] == "number"
    assert tickets_profile["missing_count"] == 2
    sla_profile = next(item for item in report["column_profiles"] if item["name"] == "sla_hours")
    assert sla_profile["numeric"]["max"] == 14.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lokales CSV-Profiling ohne externe Abhängigkeiten.")
    parser.add_argument("csv_path", nargs="?", help="Pfad zur CSV-Datei. Nicht nötig bei --demo.")
    parser.add_argument("--demo", action="store_true", help="Anonymisierte Demonstrationsdaten analysieren.")
    parser.add_argument("--delimiter", help="CSV-Trennzeichen explizit setzen, z. B. ';' oder '\\t'.")
    parser.add_argument("--self-test", action="store_true", help="Eingebaute Plausibilitätstests ausführen.")
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        print("Self-test passed.")
        return 0

    text = read_csv_text(args.csv_path, args.demo)
    rows, columns, delimiter = read_rows(text, args.delimiter)
    source_label = "demo" if args.demo else str(Path(args.csv_path).name)
    report = build_report(rows, columns, delimiter, source_label)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
