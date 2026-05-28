#!/usr/bin/env python3
"""Offline-Goldstandard für das Modell `codegenerierung`.

Aufgabe: Aus einer CSV mit Support-Tickets einen validierten Markdown-
Kurzreport erzeugen. Das Beispiel nutzt nur die Python-Standardbibliothek,
lädt keine externen Daten und enthält einen eingebauten Selbsttest.

Nutzung:
    python beispielergebnis.py --demo
    python beispielergebnis.py tickets.csv --review-date 2026-05-28
    python beispielergebnis.py --self-test
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
    "ticket_id",
    "category",
    "priority",
    "status",
    "opened_at",
    "sla_due_at",
}
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    category: str
    priority: str
    status: str
    opened_at: date
    sla_due_at: date

    @property
    def is_open(self) -> bool:
        return self.status in {"new", "open", "in_progress", "waiting"}


def parse_iso_date(value: str, field_name: str, row_number: int) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValueError(
            f"Zeile {row_number}: `{field_name}` muss YYYY-MM-DD sein."
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


def parse_tickets(csv_text: str) -> list[Ticket]:
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames is None:
        raise ValueError("CSV enthält keine Kopfzeile.")

    missing = sorted(REQUIRED_COLUMNS.difference(reader.fieldnames))
    if missing:
        raise ValueError(f"CSV-Spalten fehlen: {', '.join(missing)}")

    tickets: list[Ticket] = []
    for row_number, row in enumerate(reader, start=2):
        ticket_id = (row.get("ticket_id") or "").strip()
        if not ticket_id:
            raise ValueError(f"Zeile {row_number}: `ticket_id` fehlt.")

        tickets.append(
            Ticket(
                ticket_id=ticket_id,
                category=(row.get("category") or "").strip() or "Unbekannt",
                priority=normalize_priority(row.get("priority", ""), row_number),
                status=(row.get("status") or "").strip().lower() or "open",
                opened_at=parse_iso_date(row.get("opened_at", ""), "opened_at", row_number),
                sla_due_at=parse_iso_date(row.get("sla_due_at", ""), "sla_due_at", row_number),
            )
        )

    if not tickets:
        raise ValueError("CSV enthält keine Ticketzeilen.")
    return tickets


def overdue_tickets(tickets: Iterable[Ticket], review_date: date) -> list[Ticket]:
    return sorted(
        (ticket for ticket in tickets if ticket.is_open and ticket.sla_due_at < review_date),
        key=lambda ticket: (PRIORITY_ORDER[ticket.priority], ticket.sla_due_at),
    )


def build_markdown_report(tickets: Sequence[Ticket], review_date: date) -> str:
    by_priority = Counter(ticket.priority for ticket in tickets)
    by_category = Counter(ticket.category for ticket in tickets)
    overdue = overdue_tickets(tickets, review_date)

    lines = [
        "# Ticket-SLA-Kurzreport",
        "",
        f"Prüfdatum: {review_date.isoformat()}",
        f"Tickets gesamt: {len(tickets)}",
        f"Offene Tickets mit überschrittener SLA: {len(overdue)}",
        "",
        "## Prioritäten",
        "",
    ]

    for priority in PRIORITY_ORDER:
        lines.append(f"- {priority}: {by_priority.get(priority, 0)}")

    lines.extend(["", "## Kategorien", ""])
    for category, count in sorted(by_category.items()):
        lines.append(f"- {category}: {count}")

    lines.extend(["", "## Kritische nächste Prüfung", ""])
    if overdue:
        for ticket in overdue[:5]:
            lines.append(
                f"- {ticket.ticket_id}: {ticket.priority}, "
                f"{ticket.category}, SLA {ticket.sla_due_at.isoformat()}"
            )
    else:
        lines.append("- Keine offenen SLA-Überschreitungen im Datensatz.")

    lines.extend(
        [
            "",
            "## Grenzen",
            "",
            "- Der Report nutzt nur die übergebene CSV.",
            "- Ursachen, Zuständigkeiten und Kundendaten werden nicht erfunden.",
            "- Produktive Eskalationen brauchen menschliche Freigabe.",
        ]
    )
    return "\n".join(lines) + "\n"


def demo_csv() -> str:
    return "\n".join(
        [
            "ticket_id,category,priority,status,opened_at,sla_due_at",
            "TCK-1001,Login,high,open,2026-05-23,2026-05-27",
            "TCK-1002,Hardware,medium,waiting,2026-05-25,2026-05-31",
            "TCK-1003,Billing,critical,in_progress,2026-05-20,2026-05-24",
            "TCK-1004,Access,low,closed,2026-05-12,2026-05-18",
        ]
    )


def run_self_test() -> None:
    tickets = parse_tickets(demo_csv())
    report = build_markdown_report(tickets, date(2026, 5, 28))
    assert "Tickets gesamt: 4" in report
    assert "Offene Tickets mit überschrittener SLA: 2" in report
    assert "TCK-1003" in report


def read_input(path: str | None, use_demo: bool) -> str:
    if use_demo:
        return demo_csv()
    if path is None:
        raise ValueError("Bitte CSV-Dateipfad angeben oder `--demo` nutzen.")
    return Path(path).read_text(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", help="Pfad zur Ticket-CSV")
    parser.add_argument("--demo", action="store_true", help="eingebaute Beispieldaten nutzen")
    parser.add_argument("--self-test", action="store_true", help="eingebauten Selbsttest ausführen")
    parser.add_argument("--review-date", default="2026-05-28", help="Prüfdatum im Format YYYY-MM-DD")
    args = parser.parse_args(argv)

    try:
        if args.self_test:
            run_self_test()
            print("Self-test passed.")
            return 0
        review_date = date.fromisoformat(args.review_date)
        tickets = parse_tickets(read_input(args.csv_path, args.demo))
        print(build_markdown_report(tickets, review_date), end="")
        return 0
    except Exception as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
