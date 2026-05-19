"""
title: Inline Visuals Toolkit V3 Offline
description: Build self-contained SVG charts, dashboards and Mermaid blocks without external network dependencies.
version: 1.0.0
license: MIT
security: Processes supplied JSON/text only. Does not read files, call networks, execute commands or load remote scripts.
"""

from __future__ import annotations

import html
import json
import math
import re
from typing import Any, Dict, List, Tuple

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Tools:
    """OpenWebUI toolkit for safe, offline inline visuals."""

    class Valves(BaseModel):
        max_input_chars: int = Field(180000, description="Maximum JSON/text input size.")
        max_items: int = Field(80, description="Maximum visual data points or dashboard cards.")
        default_width: int = Field(900, description="Default SVG width.")
        default_height: int = Field(520, description="Default SVG height.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def create_svg_chart(self, title: str, data_json: str, chart_type: str = "bar", __event_emitter__: Any = None) -> str:
        """
        Create a self-contained SVG chart from JSON data.
        :param title: Chart title.
        :param data_json: JSON array of objects with label and value fields, or an object mapping labels to numbers.
        :param chart_type: One of bar, line or donut.
        """
        if len(data_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge Offline-SVG-Chart", False)
        try:
            data = self._parse_series(data_json)
        except ValueError as exc:
            return f"Fehler: {exc}"
        if not data:
            return "Fehler: Keine numerischen Datenpunkte erkannt."
        chart = chart_type.lower().strip()
        if chart == "line":
            svg = self._line_chart(title, data)
        elif chart == "donut":
            svg = self._donut_chart(title, data)
        else:
            svg = self._bar_chart(title, data)
        await self._emit(__event_emitter__, "Offline-SVG-Chart erzeugt", True)
        return "\n".join(["# Visual erzeugt", "", svg, "", self._caption(data, chart)])

    async def create_status_dashboard(self, title: str, cards_json: str, __event_emitter__: Any = None) -> str:
        """
        Create a compact offline HTML dashboard from JSON cards.
        :param title: Dashboard title.
        :param cards_json: JSON array of cards with title, value, status and detail fields.
        """
        if len(cards_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge Offline-Dashboard", False)
        try:
            raw_cards = json.loads(cards_json)
        except json.JSONDecodeError as exc:
            return f"Fehler: Ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(raw_cards, list):
            return "Fehler: cards_json muss ein JSON-Array sein."
        cards = [self._normalize_card(item, idx + 1) for idx, item in enumerate(raw_cards[: int(self.valves.max_items)])]
        palette = {"ok": "#0f766e", "warn": "#b45309", "risk": "#b91c1c", "info": "#2563eb"}
        parts = [
            "<div style=\"font-family:Arial,Helvetica,sans-serif;border:1px solid #d1d5db;border-radius:8px;padding:18px;background:#ffffff;color:#111827\">",
            f"<h2 style=\"margin:0 0 14px;font-size:22px\">{html.escape(title)}</h2>",
            "<div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px\">",
        ]
        for card in cards:
            color = palette.get(card["status"], palette["info"])
            parts.extend([
                f"<section style=\"border-left:5px solid {color};background:#f9fafb;padding:12px;border-radius:6px;min-height:112px\">",
                f"<div style=\"font-size:12px;text-transform:uppercase;color:#4b5563\">{html.escape(card['title'])}</div>",
                f"<div style=\"font-size:28px;font-weight:700;margin:6px 0;color:{color}\">{html.escape(card['value'])}</div>",
                f"<p style=\"font-size:13px;line-height:1.35;margin:0;color:#374151\">{html.escape(card['detail'])}</p>",
                "</section>",
            ])
        parts.extend(["</div>", "</div>"])
        await self._emit(__event_emitter__, "Offline-Dashboard erzeugt", True)
        return "\n".join(["# Dashboard erzeugt", "", "".join(parts)])

    async def create_mermaid_block(self, title: str, mermaid_code: str, __event_emitter__: Any = None) -> str:
        """
        Wrap Mermaid code for OpenWebUI rendering and add a short validation summary.
        :param title: Diagram title.
        :param mermaid_code: Mermaid diagram source supplied by the user or model.
        """
        if len(mermaid_code) > int(self.valves.max_input_chars):
            return "Fehler: Mermaid-Code ist zu groß."
        await self._emit(__event_emitter__, "Prüfe Mermaid-Block", False)
        cleaned = mermaid_code.strip().replace("```mermaid", "").replace("```", "").strip()
        first = cleaned.splitlines()[0].strip() if cleaned.splitlines() else ""
        allowed = ("flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram", "journey", "gantt", "pie", "mindmap", "timeline")
        status = "bekannter Diagrammtyp" if first.startswith(allowed) else "Diagrammtyp manuell prüfen"
        await self._emit(__event_emitter__, "Mermaid-Block bereit", True)
        return "\n".join([
            f"# {title}",
            f"- Status: {status}",
            "",
            "```mermaid",
            cleaned,
            "```",
        ])

    async def create_visual_brief(self, request: str, output_format: str = "dashboard", __event_emitter__: Any = None) -> str:
        """
        Create an implementation brief for a visual artifact without fetching external assets.
        :param request: User goal for the visual.
        :param output_format: Target format such as dashboard, chart, mermaid, html-report, slide.
        """
        if len(request) > int(self.valves.max_input_chars):
            return "Fehler: Anfrage ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge Visual-Brief", False)
        fmt = self._clean(output_format, 40).lower()
        await self._emit(__event_emitter__, "Visual-Brief erzeugt", True)
        return "\n".join([
            "# Offline Visual Brief",
            f"- Ziel: {self._clean(request, 500)}",
            f"- Format: {fmt}",
            "- Primärer Pfad: Inline-SVG/HTML ohne CDN, externe Bilder oder Skripte.",
            "- Fallback 1: Mermaid-Diagramm, wenn Struktur wichtiger als visuelle Ausgestaltung ist.",
            "- Fallback 2: Texttabelle mit Kennzahlen, falls Rendering blockiert ist.",
            "- Prüfpunkte: Datenquelle nennen, Achsen/Legende beschriften, Farbkontrast prüfen, keine Secrets anzeigen.",
        ])

    def _parse_series(self, text: str) -> List[Tuple[str, float]]:
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}") from exc
        items: List[Tuple[str, float]] = []
        if isinstance(raw, dict):
            iterable = [{"label": key, "value": value} for key, value in raw.items()]
        elif isinstance(raw, list):
            iterable = raw
        else:
            raise ValueError("Erwartet wird ein JSON-Array oder Objekt.")
        for index, item in enumerate(iterable[: int(self.valves.max_items)]):
            if isinstance(item, dict):
                label = item.get("label", item.get("name", item.get("category", f"Wert {index + 1}")))
                value = item.get("value", item.get("count", item.get("amount", item.get("score"))))
            else:
                label, value = f"Wert {index + 1}", item
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(number):
                items.append((self._clean(str(label), 50), number))
        return items

    def _bar_chart(self, title: str, data: List[Tuple[str, float]]) -> str:
        width, height = int(self.valves.default_width), int(self.valves.default_height)
        left, right, top, bottom = 72, 28, 64, 92
        chart_w, chart_h = width - left - right, height - top - bottom
        max_value = max(max(value for _, value in data), 1.0)
        bar_gap = 10
        bar_w = max(12, (chart_w - bar_gap * (len(data) - 1)) / max(len(data), 1))
        parts = self._svg_base(title, width, height)
        parts.append(f"<line x1='{left}' y1='{top + chart_h}' x2='{left + chart_w}' y2='{top + chart_h}' stroke='#9ca3af'/>")
        for idx, (label, value) in enumerate(data):
            x = left + idx * (bar_w + bar_gap)
            h = max(1, (value / max_value) * chart_h)
            y = top + chart_h - h
            parts.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bar_w:.1f}' height='{h:.1f}' rx='4' fill='{self._color(idx)}'/>")
            parts.append(f"<text x='{x + bar_w / 2:.1f}' y='{y - 7:.1f}' text-anchor='middle' font-size='12' fill='#111827'>{value:g}</text>")
            parts.append(f"<text x='{x + bar_w / 2:.1f}' y='{top + chart_h + 22}' text-anchor='end' font-size='11' fill='#374151' transform='rotate(-35 {x + bar_w / 2:.1f},{top + chart_h + 22})'>{html.escape(label)}</text>")
        parts.append("</svg>")
        return "".join(parts)

    def _line_chart(self, title: str, data: List[Tuple[str, float]]) -> str:
        width, height = int(self.valves.default_width), int(self.valves.default_height)
        left, right, top, bottom = 72, 28, 64, 92
        chart_w, chart_h = width - left - right, height - top - bottom
        values = [value for _, value in data]
        min_value, max_value = min(values), max(values)
        span = max(max_value - min_value, 1.0)
        points: List[Tuple[float, float]] = []
        for idx, (_, value) in enumerate(data):
            x = left + (chart_w * idx / max(1, len(data) - 1))
            y = top + chart_h - ((value - min_value) / span) * chart_h
            points.append((x, y))
        parts = self._svg_base(title, width, height)
        parts.append(f"<polyline fill='none' stroke='#2563eb' stroke-width='3' points='{' '.join(f'{x:.1f},{y:.1f}' for x, y in points)}'/>")
        for idx, ((label, value), (x, y)) in enumerate(zip(data, points)):
            parts.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5' fill='{self._color(idx)}'/>")
            parts.append(f"<text x='{x:.1f}' y='{y - 10:.1f}' text-anchor='middle' font-size='12'>{value:g}</text>")
            parts.append(f"<text x='{x:.1f}' y='{top + chart_h + 22}' text-anchor='end' font-size='11' fill='#374151' transform='rotate(-35 {x:.1f},{top + chart_h + 22})'>{html.escape(label)}</text>")
        parts.append("</svg>")
        return "".join(parts)

    def _donut_chart(self, title: str, data: List[Tuple[str, float]]) -> str:
        width, height = int(self.valves.default_width), int(self.valves.default_height)
        cx, cy, radius = 270, 285, 145
        total = sum(max(0, value) for _, value in data) or 1.0
        start = -90.0
        parts = self._svg_base(title, width, height)
        for idx, (label, value) in enumerate(data):
            amount = max(0.0, value)
            end = start + (amount / total) * 360.0
            parts.append(self._arc(cx, cy, radius, start, end, self._color(idx)))
            y = 112 + idx * 24
            parts.append(f"<rect x='540' y='{y - 12}' width='14' height='14' fill='{self._color(idx)}' rx='2'/>")
            parts.append(f"<text x='564' y='{y}' font-size='14' fill='#111827'>{html.escape(label)} ({amount:g})</text>")
            start = end
        parts.append(f"<circle cx='{cx}' cy='{cy}' r='{radius * 0.55:.1f}' fill='#ffffff'/>")
        parts.append(f"<text x='{cx}' y='{cy}' text-anchor='middle' font-size='22' font-weight='700'>{total:g}</text>")
        parts.append("</svg>")
        return "".join(parts)

    def _arc(self, cx: int, cy: int, radius: int, start: float, end: float, color: str) -> str:
        start_rad, end_rad = math.radians(start), math.radians(end)
        x1, y1 = cx + radius * math.cos(start_rad), cy + radius * math.sin(start_rad)
        x2, y2 = cx + radius * math.cos(end_rad), cy + radius * math.sin(end_rad)
        large = 1 if end - start > 180 else 0
        return f"<path d='M {cx} {cy} L {x1:.2f} {y1:.2f} A {radius} {radius} 0 {large} 1 {x2:.2f} {y2:.2f} Z' fill='{color}'/>"

    def _svg_base(self, title: str, width: int, height: int) -> List[str]:
        return [
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}' role='img' aria-label='{html.escape(title)}'>",
            "<rect width='100%' height='100%' fill='#ffffff'/>",
            f"<text x='28' y='38' font-size='24' font-weight='700' fill='#111827'>{html.escape(self._clean(title, 120))}</text>",
        ]

    def _caption(self, data: List[Tuple[str, float]], chart_type: str) -> str:
        return f"- Typ: `{chart_type}`\n- Datenpunkte: {len(data)}\n- Offline: ja, keine externen Skripte oder Assets"

    def _normalize_card(self, item: Any, index: int) -> Dict[str, str]:
        if not isinstance(item, dict):
            return {"title": f"Karte {index}", "value": self._clean(str(item), 40), "status": "info", "detail": ""}
        return {
            "title": self._clean(str(item.get("title") or item.get("label") or f"Karte {index}"), 80),
            "value": self._clean(str(item.get("value") or item.get("metric") or "-"), 60),
            "status": self._clean(str(item.get("status") or "info"), 12).lower(),
            "detail": self._clean(str(item.get("detail") or item.get("description") or ""), 220),
        }

    def _color(self, index: int) -> str:
        palette = ["#2563eb", "#0f766e", "#b45309", "#7c3aed", "#be123c", "#0891b2", "#4d7c0f", "#c2410c", "#4338ca"]
        return palette[index % len(palette)]

    def _clean(self, value: str, limit: int) -> str:
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", value).strip()[:limit]

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
