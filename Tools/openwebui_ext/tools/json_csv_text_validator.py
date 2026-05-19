"""
title: JSON CSV Text Validator
description: Validate and summarize JSON, CSV and structured text while redacting likely secrets.
version: 1.0.0
license: MIT
security: Processes supplied text only. It does not store data, access files, call networks or execute commands.
"""

from __future__ import annotations

import csv
import io
import json
import re
from typing import Any, Dict, List

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


SENSITIVE_NAME = re.compile(r"(?i)(password|passwd|pwd|token|secret|api[_-]?key|authorization|cookie|credential)")


class Tools:
    """OpenWebUI toolkit for bounded local data validation."""

    class Valves(BaseModel):
        max_input_chars: int = Field(200000, description="Maximum supplied text length.")
        max_output_chars: int = Field(12000, description="Maximum returned text length.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def validate_json(self, text: str, pretty: bool = True, __event_emitter__: Any = None) -> str:
        """
        Validate JSON text and return structure summary plus optional formatted JSON.
        :param text: JSON text supplied by the user.
        :param pretty: Include formatted JSON when output size allows it.
        """
        if len(text) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Validiere JSON", False)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return f"Fehler: Ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        sensitive = sorted(self._find_sensitive(data))
        summary = self._json_summary(data)
        lines = ["# JSON-Validierung", "- Status: gültig", f"- Struktur: {summary}", f"- Sensible Feldnamen: {', '.join(sensitive) if sensitive else 'keine auffälligen'}"]
        if pretty:
            formatted = self._redact(json.dumps(data, ensure_ascii=False, indent=2))
            lines.extend(["", "## Formatiertes JSON", "```json", formatted[: int(self.valves.max_output_chars)], "```"])
        await self._emit(__event_emitter__, "JSON-Validierung abgeschlossen", True)
        return "\n".join(lines)[: int(self.valves.max_output_chars)]

    async def validate_csv(self, text: str, delimiter: str = "", __event_emitter__: Any = None) -> str:
        """
        Validate CSV text and summarize columns and row counts.
        :param text: CSV text supplied by the user.
        :param delimiter: Optional delimiter override.
        """
        if len(text) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Analysiere CSV", False)
        sample = text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample) if not delimiter else csv.excel()
            if delimiter:
                dialect.delimiter = delimiter
        except csv.Error:
            dialect = csv.excel()
        reader = csv.reader(io.StringIO(text), dialect)
        rows = list(reader)
        if not rows:
            return "Fehler: Keine CSV-Zeilen erkannt."
        widths = {len(row) for row in rows}
        header = rows[0]
        sensitive = [name for name in header if SENSITIVE_NAME.search(name)]
        lines = [
            "# CSV-Validierung",
            f"- Zeilen gesamt: {len(rows)}",
            f"- Datensätze ohne Kopfzeile: {max(0, len(rows) - 1)}",
            f"- Spalten: {len(header)}",
            f"- Delimiter: `{getattr(dialect, 'delimiter', ',')}`",
            f"- Konsistente Spaltenzahl: {len(widths) == 1}",
            f"- Sensible Spaltennamen: {', '.join(sensitive) if sensitive else 'keine auffälligen'}",
            "",
            "## Spalten",
        ]
        lines.extend(f"- {self._redact(col) or '(leer)'}" for col in header[:60])
        if len(widths) > 1:
            lines.extend(["", "## Strukturprobleme", f"- Unterschiedliche Spaltenzahlen erkannt: {sorted(widths)}"])
        await self._emit(__event_emitter__, "CSV-Analyse abgeschlossen", True)
        return "\n".join(lines)[: int(self.valves.max_output_chars)]

    async def inspect_text(self, text: str, __event_emitter__: Any = None) -> str:
        """
        Inspect structured text for length, line counts and likely secret markers.
        :param text: Text supplied by the user.
        """
        if len(text) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Analysiere Text", False)
        lines = text.splitlines()
        findings = [line.strip()[:200] for line in lines if SENSITIVE_NAME.search(line)]
        await self._emit(__event_emitter__, "Textanalyse abgeschlossen", True)
        return "\n".join([
            "# Textanalyse",
            f"- Zeichen: {len(text)}",
            f"- Zeilen: {len(lines)}",
            f"- Nicht-leere Zeilen: {sum(1 for line in lines if line.strip())}",
            f"- Potentiell sensible Zeilen: {len(findings)}",
            "",
            "## Hinweise",
            "- Sensible Treffer werden nur als Anzahl bewertet; Inhalte werden nicht wiederholt." if findings else "- Keine offensichtlichen sensiblen Marker erkannt.",
        ])

    def _json_summary(self, data: Any) -> str:
        if isinstance(data, dict):
            return f"Objekt mit {len(data)} Schlüsseln"
        if isinstance(data, list):
            return f"Array mit {len(data)} Elementen"
        return type(data).__name__

    def _find_sensitive(self, data: Any, prefix: str = "") -> set[str]:
        found: set[str] = set()
        if isinstance(data, dict):
            for key, value in data.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if SENSITIVE_NAME.search(str(key)):
                    found.add(path[:120])
                found.update(self._find_sensitive(value, path))
        elif isinstance(data, list):
            for item in data[:50]:
                found.update(self._find_sensitive(item, prefix + "[]"))
        return found

    def _redact(self, value: str) -> str:
        return re.sub(r"(?i)(token|api[_-]?key|password|secret|authorization)([\"'\s:=]+)([^\"'\s,}]+)", r"\1\2[REDACTED]", value)

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
