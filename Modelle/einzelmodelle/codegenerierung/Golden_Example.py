#!/usr/bin/env python3
"""Golden Example für das OpenWebUI-Modell `codegenerierung`.

Aufgabe:
    Erzeuge ein kleines, offline nutzbares Python-CLI, das eine CSV-Datei mit
    Aufgaben validiert, Kennzahlen berechnet und einen Markdown-Report ausgibt.

Eigenschaften:
    - nur Python-Standardbibliothek
    - vollständige Eingabevalidierung
    - verständliche Fehlermeldungen
    - deterministische Ausgabe
    - eingebauter Demo-Datensatz
    - eingebauter Selbsttest

Nutzung:
    python Golden_Example.py --demo
    python Golden_Example.py aufgaben.csv --review-date 2026-06-14
    python Golden_Example.py --self-test
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence


REQUIRED_COLUMNS = {
    "task_id",
    "title",
    "owner",
    "priority",
    "status",
    "created_at",
    "due_at",
}

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

OPEN_STATUSES = {
    "new",
    "open",
    "in_progress",
    "blocked",
    "waiting",
}


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str
    owner: str
    priority: str
    status: str
    created_at: date
    due_at: date

    @property
    def is_open(self) -> bool:
        return self.status in OPEN_STATUSES

    @property
    def sort_key(self) -> tuple[int, date, str]:
        return (PRIORITY_ORDER[self.priority], self.due_at, self.task_id)


def parse_iso_date(value: str, field_name: str, row_number: int) -> date:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"Zeile {row_number}: `{field_name}` fehlt.")

    try:
        return date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError(
            f"Zeile {row_number}: `{field_name}` muss im Format YYYY-MM-DD vorliegen."
        ) from exc


def normalize_priority(value: str, row_number: int) -> str:
    priority = value.strip().lower()
    if priority not in PRIORITY_ORDER:
        allowed = ", ".join(PRIORITY_ORDER)
        raise ValueError(
            f"Zeile {row_number}: unbekannte Priorität `{value}`. "
            f"Erlaubt: {allowed}."
        )
    return priority


def normalize_status(value: str) -> str:
    return value.strip().lower() or "open"


def require_text(row: dict[str, str], field_name: str, row_number: int) -> str:
    value = (row.get(field_name) or "").strip()
    if not value:
        raise ValueError(f"Zeile {row_number}: `{field_name}` fehlt.")
    return value


def parse_tasks(csv_text: str) -> list[Task]:
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames is None:
        raise ValueError("CSV enthält keine Kopfzeile.")

    missing = sorted(REQUIRED_COLUMNS.difference(reader.fieldnames))
    if missing:
        raise ValueError(f"CSV-Spalten fehlen: {', '.join(missing)}")

    tasks: list[Task] = []
    seen_ids: set[str] = set()

    for row_number, row in enumerate(reader, start=2):
        task_id = require_text(row, "task_id", row_number)
        if task_id in seen_ids:
            raise ValueError(f"Zeile {row_number}: doppelte `task_id` `{task_id}`.")
        seen_ids.add(task_id)

        created_at = parse_iso_date(row.get("created_at", ""), "created_at", row_number)
        due_at = parse_iso_date(row.get("due_at", ""), "due_at", row_number)

        if due_at < created_at:
            raise ValueError(
                f"Zeile {row_number}: `due_at` liegt vor `created_at` für `{task_id}`."
            )

        tasks.append(
            Task(
                task_id=task_id,
                title=require_text(row, "title", row_number),
                owner=require_text(row, "owner", row_number),
                priority=normalize_priority(row.get("priority", ""), row_number),
                status=normalize_status(row.get("status", "")),
                created_at=created_at,
                due_at=due_at,
            )
        )

    if not tasks:
        raise ValueError("CSV enthält keine Aufgabenzeilen.")

    return tasks


def overdue_tasks(tasks: Iterable[Task], review_date: date) -> list[Task]:
    return sorted(
        (task for task in tasks if task.is_open and task.due_at < review_date),
        key=lambda task: task.sort_key,
    )


def upcoming_tasks(tasks: Iterable[Task], review_date: date) -> list[Task]:
    return sorted(
        (task for task in tasks if task.is_open and task.due_at >= review_date),
        key=lambda task: task.sort_key,
    )


def format_task_line(task: Task) -> str:
    return (
        f"- {task.task_id}: {task.priority}, {task.owner}, "
        f"fällig am {task.due_at.isoformat()} — {task.title}"
    )


def build_markdown_report(tasks: Sequence[Task], review_date: date) -> str:
    by_priority = Counter(task.priority for task in tasks)
    by_status = Counter(task.status for task in tasks)
    by_owner = Counter(task.owner for task in tasks)
    overdue = overdue_tasks(tasks, review_date)
    upcoming = upcoming_tasks(tasks, review_date)

    lines = [
        "# Aufgaben-Kurzreport",
        "",
        f"Prüfdatum: {review_date.isoformat()}",
        f"Aufgaben gesamt: {len(tasks)}",
        f"Offene Aufgaben: {sum(1 for task in tasks if task.is_open)}",
        f"Überfällige offene Aufgaben: {len(overdue)}",
        "",
        "## Prioritäten",
        "",
    ]

    for priority in PRIORITY_ORDER:
        lines.append(f"- {priority}: {by_priority.get(priority, 0)}")

    lines.extend(["", "## Status", ""])
    for status, count in sorted(by_status.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Verantwortliche", ""])
    for owner, count in sorted(by_owner.items()):
        lines.append(f"- {owner}: {count}")

    lines.extend(["", "## Kritische nächste Prüfung", ""])
    if overdue:
        for task in overdue[:5]:
            lines.append(format_task_line(task))
    else:
        lines.append("- Keine offenen überfälligen Aufgaben im Datensatz.")

    lines.extend(["", "## Nächste offene Fälligkeiten", ""])
    if upcoming:
        for task in upcoming[:5]:
            lines.append(format_task_line(task))
    else:
        lines.append("- Keine offenen zukünftigen Fälligkeiten im Datensatz.")

    lines.extend(
        [
            "",
            "## Grenzen",
            "",
            "- Der Report nutzt ausschließlich die übergebene CSV.",
            "- Zuständigkeiten, Ursachen und geschäftliche Prioritäten werden nicht erfunden.",
            "- Produktive Entscheidungen benötigen fachliche Prüfung.",
        ]
    )

    return "\n".join(lines) + "\n"


def demo_csv() -> str:
    return "\n".join(
        [
            "task_id,title,owner,priority,status,created_at,due_at",
            "TASK-1001,Login-Fehler analysieren,Aylin,high,open,2026-06-01,2026-06-10",
            "TASK-1002,Export-Validierung ergänzen,Jonas,medium,in_progress,2026-06-03,2026-06-18",
            "TASK-1003,Produktionsblocker prüfen,Mira,critical,blocked,2026-06-04,2026-06-12",
            "TASK-1004,Archivseite bereinigen,Noah,low,closed,2026-05-20,2026-06-01",
            "TASK-1005,Fehlertexte vereinheitlichen,Aylin,medium,waiting,2026-06-08,2026-06-20",
        ]
    )


def read_input(path: str | None, use_demo: bool) -> str:
    if use_demo:
        return demo_csv()
    if path is None:
        raise ValueError("Bitte CSV-Dateipfad angeben oder `--demo` nutzen.")
    return Path(path).read_text(encoding="utf-8")


def run_self_test() -> None:
    tasks = parse_tasks(demo_csv())
    report = build_markdown_report(tasks, date(2026, 6, 14))

    assert len(tasks) == 5
    assert "Aufgaben gesamt: 5" in report
    assert "Offene Aufgaben: 4" in report
    assert "Überfällige offene Aufgaben: 2" in report
    assert "TASK-1003" in report
    assert "TASK-1002" in report

    try:
        parse_tasks(
            "\n".join(
                [
                    "task_id,title,owner,priority,status,created_at,due_at",
                    "TASK-1,Fehlerhafte Aufgabe,Aylin,urgent,open,2026-06-01,2026-06-02",
                ]
            )
        )
    except ValueError as exc:
        assert "unbekannte Priorität" in str(exc)
    else:
        raise AssertionError("Ungültige Priorität wurde nicht erkannt.")

    try:
        parse_tasks(
            "\n".join(
                [
                    "task_id,title,owner,priority,status,created_at,due_at",
                    "TASK-1,Fehlerhafte Aufgabe,Aylin,high,open,2026-06-03,2026-06-02",
                ]
            )
        )
    except ValueError as exc:
        assert "liegt vor" in str(exc)
    else:
        raise AssertionError("Ungültige Datumsreihenfolge wurde nicht erkannt.")


def parse_review_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("`--review-date` muss im Format YYYY-MM-DD vorliegen.") from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Erzeugt einen Markdown-Report aus einer Aufgaben-CSV.")
    parser.add_argument("csv_path", nargs="?", help="Pfad zur Aufgaben-CSV")
    parser.add_argument("--demo", action="store_true", help="eingebaute Beispieldaten nutzen")
    parser.add_argument("--self-test", action="store_true", help="eingebauten Selbsttest ausführen")
    parser.add_argument(
        "--review-date",
        default="2026-06-14",
        help="Prüfdatum im Format YYYY-MM-DD",
    )

    args = parser.parse_args(argv)

    try:
        if args.self_test:
            run_self_test()
            print("Self-test passed.")
            return 0

        review_date = parse_review_date(args.review_date)
        tasks = parse_tasks(read_input(args.csv_path, args.demo))
        print(build_markdown_report(tasks, review_date), end="")
        return 0
    except Exception as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
