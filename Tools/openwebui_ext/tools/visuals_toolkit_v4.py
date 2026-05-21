"""
title: Visuals Toolkit V4
author: Cole
version: 4.0.0
license: MIT
description: Tables, charts, heatmaps, timelines, flowcharts, trees, dashboards, metric grids, pie/donut charts, gauges, Gantt charts, Sankey diagrams, radar charts, waterfall charts, funnels, and candlestick charts. Dark-mode-safe HTML with Plotly, auto-resizing iframes, and fullscreen support. Pure ASCII/Markdown fallback when HTML is unavailable.
required_open_webui_version: 0.4.0

tool_instructions: |
  Arguments MUST be valid JSON objects.

  Rules:
  - Do NOT wrap arguments in XML.
  - Do NOT HTML-escape quotes (no &quot;).
  - Arrays and objects must be native JSON, not strings.
  - rows must be a JSON array of objects.
  - Numbers must be numbers, not strings.
  - ALWAYS use mode "auto" (or omit it). NEVER pass mode "text" unless the user explicitly asks for ASCII/plain-text output.

  Compatibility:
  - If Markdown Normalizer filter is active, it may convert HTML output.
    Disable it for models using this tool, or turn off enable_xml_tag_cleanup in its Valves.

  Example (chart):
  {
    "x": ["Mon","Tue","Wed"],
    "y": [120, 180, 160],
    "title": "Sessions",
    "chart_type": "line",
    "mode": "auto"
  }

  Example (pie_chart):
  {
    "labels": ["Chrome","Firefox","Safari"],
    "values": [60, 25, 15],
    "title": "Browser Share",
    "donut": true,
    "mode": "auto"
  }

  Example (gauge):
  {
    "value": 73,
    "title": "CPU Usage",
    "min_val": 0,
    "max_val": 100,
    "unit": "%",
    "mode": "auto"
  }

  Example (funnel):
  {
    "stages": ["Visitors","Signups","Trials","Paid"],
    "values": [10000, 3000, 800, 200],
    "title": "Conversion Funnel",
    "mode": "auto"
  }

  Example (sankey):
  {
    "nodes": ["Budget","Engineering","Marketing","Revenue"],
    "links": [
      {"source": 0, "target": 1, "value": 50},
      {"source": 0, "target": 2, "value": 30},
      {"source": 1, "target": 3, "value": 45},
      {"source": 2, "target": 3, "value": 25}
    ],
    "title": "Budget Flow",
    "mode": "auto"
  }

  Example (candlestick):
  {
    "dates": ["2024-01-01","2024-01-02","2024-01-03"],
    "open": [100, 105, 102],
    "high": [110, 108, 107],
    "low": [98, 101, 100],
    "close": [105, 102, 106],
    "title": "AAPL",
    "mode": "auto"
  }
offline: true
"""
# Air-gap integration note:
# Imported from the public OpenWebUI tool export stored under
# Tools/openwebui_ext/third_party/public_openwebui_tools/.
# Defaults were adjusted for offline operation: no public API fallback, no
# external CDN by default, and no public web crawling/search unless an admin
# explicitly configures local/self-hosted endpoints and allowlists.
from __future__ import annotations

import html
import json
from typing import Any, Dict, List, Literal, Set, Union

from pydantic import BaseModel, Field

try:
    from fastapi.responses import HTMLResponse
except Exception:  # pragma: no cover
    HTMLResponse = None  # type: ignore

ChartType = Literal["bar", "line", "scatter"]
OutputMode = Literal["embed", "text", "auto"]


class Tools:
    """
    Visuals Toolkit V4 — OpenWebUI Tool

    Features:
      - render_table, render_comparison_table
      - render_chart, render_multi_chart (Plotly + ASCII)
      - render_heatmap (Plotly + ASCII)
      - render_metrics_grid (KPI cards)
      - render_timeline (styled HTML + ASCII)
      - render_flowchart (box-drawing + edge-based)
      - render_tree (nested dict + edge list)
      - render_dashboard (composite layout)
      - render_pie_chart (pie/donut)
      - render_gauge (indicator dial)
      - render_gantt (horizontal timeline bars)
      - render_sankey (flow diagram)
      - render_radar (spider/polar chart)
      - render_waterfall (incremental bar chart)
      - render_funnel (conversion funnel)
      - render_candlestick (OHLC financial chart)

    Design:
      - Dark-mode-safe HTML with CSS variables
      - Defensive JSON coercion for LLM tool calls
      - Auto-resizing iframes via frameElement + postMessage
      - Fullscreen toggle button on all embeds
      - Plotly CDN pinned; graceful ASCII fallback
    """

    # ── Dark-mode palette ──
    _BG = "#0b0f14"
    _PANEL = "#0b0f14"
    _HEADER = "#111827"
    _TEXT = "#e5e7eb"
    _MUTED = "#94a3b8"
    _BORDER = "#374151"
    _OUTER = "#1f2937"
    _RADIUS = "12px"
    _BEST_BG = "#14532d"
    _BEST_FG = "#dcfce7"
    _PLOTLY_CDN = "2.27.0"

    def __init__(self) -> None:
        self.valves = self.Valves()

    class Valves(BaseModel):
        allow_external_cdn: bool = Field(
            False,
            description="Air-gap default: do not load Plotly from a public CDN. False uses text/ASCII fallbacks.",
        )
        max_rows: int = Field(250, description="Safety cap for rendered table rows.")
        max_cols: int = Field(60, description="Safety cap for rendered table columns.")
        ascii_chart_height: int = Field(12, description="ASCII chart height in lines.")
        embed_chart_height: int = Field(420, description="Plotly chart height in pixels.")

    # ================================================================
    # Defensive JSON coercion
    # ================================================================

    def _coerce_json(self, value: Any, expect: Literal["list", "dict", "any"]) -> Any:
        if value is None:
            return value
        if expect == "list" and isinstance(value, list):
            return value
        if expect == "dict" and isinstance(value, dict):
            return value
        if expect == "any" and isinstance(value, (list, dict)):
            return value
        if isinstance(value, str):
            s = html.unescape(value.strip())
            if (s.startswith('"') and s.endswith('"')) or (
                s.startswith("'") and s.endswith("'")
            ):
                s = s[1:-1].strip()
            if (s.startswith("{") and s.endswith("}")) or (
                s.startswith("[") and s.endswith("]")
            ):
                try:
                    return json.loads(s)
                except Exception:
                    pass
        return value

    def _coerce_str_list(self, value: Any) -> List[str]:
        v = self._coerce_json(value, "list")
        if isinstance(v, list):
            return [str(x) for x in v]
        if isinstance(v, str):
            return [v]
        return []

    def _coerce_float_list(self, value: Any) -> List[float]:
        v = self._coerce_json(value, "list")
        if not isinstance(v, list):
            return []
        out: List[float] = []
        for x in v:
            if isinstance(x, (int, float)) and not isinstance(x, bool):
                out.append(float(x))
            else:
                try:
                    out.append(float(str(x).strip()))
                except Exception:
                    pass
        return out

    def _resolve_mode(self, mode: OutputMode) -> Literal["embed", "text"]:
        if mode == "auto":
            return (
                "embed"
                if (self.valves.allow_external_cdn and HTMLResponse is not None)
                else "text"
            )
        return mode  # type: ignore

    # ================================================================
    # HTML infrastructure
    # ================================================================

    def _wrap_html(self, title: str, body: str) -> str:
        return f"""<!doctype html>
<html><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
:root{{
  --bg:{self._BG};--panel:{self._PANEL};--header:{self._HEADER};
  --text:{self._TEXT};--muted:{self._MUTED};--border:{self._BORDER};
  --outer:{self._OUTER};--radius:{self._RADIUS};
}}
*,*::before,*::after{{box-sizing:border-box}}
body{{
  margin:0;padding:14px;
  background:var(--bg);color:var(--text);
  font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  font-size:14px;line-height:1.4;
  min-height:200px;overflow:visible;
}}
.card{{
  background:var(--panel);border:1px solid var(--outer);
  border-radius:var(--radius);padding:14px;margin-bottom:14px;
}}
.title{{font-size:16px;font-weight:700;margin:0 0 10px 0}}
table{{width:100%;border-collapse:collapse}}
th{{
  text-align:left;padding:8px;background:var(--header);
  color:var(--text);border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:1;
}}
td{{
  padding:8px;border-bottom:1px solid var(--border);
  color:var(--text);background:var(--panel);vertical-align:top;
}}
pre.vis{{
  background:rgba(255,255,255,0.02);border:1px solid var(--outer);
  border-radius:var(--radius);padding:12px;overflow:auto;
  white-space:pre;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
  color:var(--text);font-size:13px;line-height:1.5;
}}
#fs-btn{{
  position:fixed;top:8px;right:8px;z-index:9999;
  background:rgba(31,41,55,0.85);color:#e5e7eb;
  border:1px solid #374151;border-radius:6px;
  padding:3px 10px;cursor:pointer;font-size:11px;
  opacity:0.5;transition:opacity 0.2s;
}}
#fs-btn:hover{{opacity:1}}
</style>
</head><body>
<button id="fs-btn" onclick="toggleFS()" title="Toggle fullscreen">Fullscreen</button>
{body}
<script>
(function(){{
  function toggleFS(){{
    if(!document.fullscreenElement){{
      var el=document.documentElement;
      (el.requestFullscreen||el.webkitRequestFullscreen||function(){{}}).call(el);
    }}else{{
      (document.exitFullscreen||document.webkitExitFullscreen||function(){{}}).call(document);
    }}
  }}
  window.toggleFS=toggleFS;
  document.addEventListener("fullscreenchange",function(){{
    document.getElementById("fs-btn").textContent=document.fullscreenElement?"Exit Fullscreen":"Fullscreen";
  }});
  function resize(){{
    var h=document.documentElement.scrollHeight;
    try{{if(window.frameElement)window.frameElement.style.height=h+"px";}}catch(e){{}}
    try{{window.parent.postMessage({{type:"iframe-resize",height:h}},"*");}}catch(e){{}}
  }}
  window.addEventListener("load",resize);
  window.addEventListener("resize",resize);
  if(typeof ResizeObserver!=="undefined")new ResizeObserver(resize).observe(document.body);
  setTimeout(resize,300);setTimeout(resize,1000);setTimeout(resize,2500);
}})();
</script>
</body></html>"""

    # ================================================================
    # Markdown table
    # ================================================================

    def _markdown_table(
        self, title: str, cols: List[str], rows: List[Dict[str, Any]]
    ) -> str:
        def cell(v: Any) -> str:
            s = "" if v is None else str(v)
            return s.replace("\n", " ").strip()

        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        body = "\n".join(
            "| " + " | ".join(cell(r.get(c, "")) for c in cols) + " |"
            for r in rows
        )
        out = f"{header}\n{sep}\n{body}"
        return f"### {title}\n\n{out}" if title else out

    # ================================================================
    # HTML tables (dark-mode)
    # ================================================================

    def _detect_numeric(
        self, cols: List[str], rows: List[Dict[str, Any]], skip: str = ""
    ) -> Set[str]:
        numeric: Set[str] = set()
        for c in cols:
            if c == skip:
                continue
            is_num = True
            for r in rows:
                v = r.get(c)
                if v is None:
                    continue
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    continue
                is_num = False
                break
            if is_num:
                numeric.add(c)
        return numeric

    def _html_table(
        self, title: str, cols: List[str], rows: List[Dict[str, Any]]
    ) -> str:
        esc = lambda v: html.escape("" if v is None else str(v))
        numeric = self._detect_numeric(cols, rows)
        ths = "".join(
            f"<th style='text-align:{'right' if c in numeric else 'left'}'>"
            f"{esc(c)}</th>"
            for c in cols
        )
        trs = "".join(
            "<tr>"
            + "".join(
                f"<td style='text-align:{'right' if c in numeric else 'left'}'>"
                f"{esc(r.get(c, ''))}</td>"
                for c in cols
            )
            + "</tr>"
            for r in rows
        )
        return f"""<div class="card">
<div class="title">{html.escape(title)}</div>
<div style="overflow:auto;border:1px solid var(--outer);border-radius:var(--radius)">
<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>
</div></div>"""

    def _html_table_simple(
        self, cols: List[str], rows: List[Dict[str, Any]]
    ) -> str:
        esc = lambda v: html.escape("" if v is None else str(v))
        ths = "".join(f"<th>{esc(c)}</th>" for c in cols)
        trs = "".join(
            "<tr>"
            + "".join(f"<td>{esc(r.get(c, ''))}</td>" for c in cols)
            + "</tr>"
            for r in rows
        )
        return f"""<div style="overflow:auto;border:1px solid var(--outer);border-radius:var(--radius)">
<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>
</div>"""

    # ================================================================
    # Comparison helpers
    # ================================================================

    def _find_best_values(
        self,
        criteria: List[str],
        scores: Dict[str, Dict[str, Any]],
        items: List[str],
    ) -> Dict[str, Set[float]]:
        best: Dict[str, Set[float]] = {}
        if not isinstance(scores, dict):
            return best
        for c in criteria:
            vals: List[float] = []
            for item in items:
                s = scores.get(item, {})
                if not isinstance(s, dict):
                    continue
                v = s.get(c)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    vals.append(float(v))
                else:
                    try:
                        vals.append(float(str(v).strip()))
                    except Exception:
                        pass
            if vals:
                best[c] = {max(vals)}
        return best

    def _is_best(
        self, criterion: str, val: Any, best_vals: Dict[str, Set[float]]
    ) -> bool:
        if criterion not in best_vals:
            return False
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val) in best_vals[criterion]
        try:
            return (
                float(str(val).replace("\u2605", "").strip())
                in best_vals[criterion]
            )
        except Exception:
            return False

    def _html_comparison_table(
        self,
        title: str,
        cols: List[str],
        rows: List[Dict[str, Any]],
        best_vals: Dict[str, Set[float]],
    ) -> str:
        esc = lambda v: html.escape("" if v is None else str(v))
        numeric = self._detect_numeric(cols, rows, skip="Item")
        ths = "".join(
            f"<th style='text-align:{'right' if c in numeric else 'left'}'>"
            f"{esc(c)}</th>"
            for c in cols
        )
        trs_parts: List[str] = []
        for r in rows:
            tds: List[str] = []
            for c in cols:
                raw = r.get(c, "")
                disp = str(raw).replace(" \u2605", "")
                is_b = self._is_best(c, raw, best_vals)
                bg = self._BEST_BG if is_b else "var(--panel)"
                fg = self._BEST_FG if is_b else "var(--text)"
                align = "right" if c in numeric else "left"
                tds.append(
                    f"<td style='text-align:{align};background:{bg};"
                    f"color:{fg}'>{esc(disp)}</td>"
                )
            trs_parts.append(f"<tr>{''.join(tds)}</tr>")
        return f"""<div class="card">
<div class="title">{html.escape(title)}</div>
<div style="overflow:auto;border:1px solid var(--outer);border-radius:var(--radius)">
<table><thead><tr>{ths}</tr></thead><tbody>{''.join(trs_parts)}</tbody></table>
</div></div>"""

    # ================================================================
    # ASCII charts
    # ================================================================

    def _ascii_chart(
        self,
        x: List[Any],
        y: List[float],
        title: str,
        chart_type: str,
        x_label: str = "",
        y_label: str = "",
    ) -> str:
        if not y:
            return f"### {title}\n\nNo data."
        h = max(5, min(self.valves.ascii_chart_height, 40))
        ct = (chart_type or "line").lower().strip()
        if ct == "bar":
            return self._ascii_bar(x, y, title, h)
        if ct == "scatter":
            return self._ascii_scatter(x, y, title, h)
        return self._ascii_line(x, y, title, h)

    def _col_width(self, x: List[Any]) -> int:
        """Dynamic column width based on longest label (min 3, max 10)."""
        if not x:
            return 3
        longest = max(len(str(l)) for l in x)
        return max(3, min(longest + 1, 10))

    def _x_labels(self, x: List[Any], cw: int = 0) -> str:
        w = cw or self._col_width(x)
        return "".join(f"{str(l)[:w]:^{w}}" for l in x)

    def _ascii_bar(
        self, x: List[Any], y: List[float], title: str, height: int
    ) -> str:
        max_y, min_y = max(y), min(y)
        rng = max_y - min_y if max_y != min_y else 1.0
        fills = "\u2588\u2587\u2586\u2585\u2584\u2583\u2582 "
        cw = self._col_width(x)
        bw = max(1, cw - 1)  # bar character width
        lines = [f"### {title}", "", "```text"]
        for i in range(height, 0, -1):
            thr = min_y + (rng * i / height)
            row = ""
            for v in y:
                if v >= thr:
                    row += "\u2588" * bw
                elif v >= thr - (rng / height):
                    frac = (v - (thr - rng / height)) / (rng / height)
                    ch = fills[min(int(frac * len(fills)), len(fills) - 1)]
                    row += ch * bw
                else:
                    row += " " * bw
                row += " "
            lines.append(f"{thr:6.1f} \u2502{row}")
        lines.append(" " * 8 + "\u2534" * (len(y) * cw))
        lines.append(" " * 8 + self._x_labels(x, cw))
        lines.append("```")
        return "\n".join(lines)

    def _ascii_line(
        self, x: List[Any], y: List[float], title: str, height: int
    ) -> str:
        max_y, min_y = max(y), min(y)
        rng = max_y - min_y if max_y != min_y else 1.0
        cw = self._col_width(x)
        gw = len(y) * cw
        grid = [[" "] * gw for _ in range(height)]
        for i, v in enumerate(y):
            r = (
                int((max_y - v) / rng * (height - 1))
                if rng > 0
                else height // 2
            )
            r = max(0, min(height - 1, r))
            col = i * cw + cw // 2
            if col < gw:
                grid[r][col] = "\u25cf"
            if i > 0:
                pv = y[i - 1]
                pr = (
                    int((max_y - pv) / rng * (height - 1))
                    if rng > 0
                    else height // 2
                )
                pr = max(0, min(height - 1, pr))
                mid = col - cw // 2
                lo, hi = sorted([pr, r])
                for rr in range(lo, hi + 1):
                    if rr != pr and rr != r and 0 <= mid < gw:
                        grid[rr][mid] = "\u2502"
                if pr == r and 0 <= mid < gw:
                    grid[r][mid] = "\u2500"
        lines = [f"### {title}", "", "```text"]
        for i, row in enumerate(grid):
            thr = (
                max_y - (rng * i / (height - 1)) if height > 1 else max_y
            )
            lines.append(f"{thr:6.1f} \u2502" + "".join(row))
        lines.append(" " * 8 + "\u2534" * gw)
        lines.append(" " * 8 + self._x_labels(x, cw))
        lines.append("```")
        return "\n".join(lines)

    def _ascii_scatter(
        self, x: List[Any], y: List[float], title: str, height: int
    ) -> str:
        max_y, min_y = max(y), min(y)
        rng = max_y - min_y if max_y != min_y else 1.0
        cw = self._col_width(x)
        gw = len(y) * cw
        grid = [[" "] * gw for _ in range(height)]
        for i, v in enumerate(y):
            r = (
                int((max_y - v) / rng * (height - 1))
                if rng > 0
                else height // 2
            )
            r = max(0, min(height - 1, r))
            col = i * cw + cw // 2
            if col < gw:
                grid[r][col] = "\u25cf"
        lines = [f"### {title}", "", "```text"]
        for i, row in enumerate(grid):
            thr = (
                max_y - (rng * i / (height - 1)) if height > 1 else max_y
            )
            lines.append(f"{thr:6.1f} \u2502" + "".join(row))
        lines.append(" " * 8 + "\u2534" * gw)
        lines.append(" " * 8 + self._x_labels(x, cw))
        lines.append("```")
        return "\n".join(lines)

    def _ascii_heatmap(
        self,
        data: List[List[float]],
        row_labels: List[str],
        col_labels: List[str],
        title: str,
    ) -> str:
        if not data:
            return f"### {title}\n\nNo data."
        all_v = [v for row in data for v in row]
        mn, mx = (min(all_v), max(all_v)) if all_v else (0.0, 1.0)
        rng = mx - mn if mx != mn else 1.0
        blocks = " \u2591\u2592\u2593\u2588"
        lines = [f"### {title}", "", "```text"]
        lines.append(
            " " * 12
            + " ".join(f"{str(c)[:8]:^8}" for c in col_labels)
        )
        lines.append("")
        for i, rl in enumerate(row_labels):
            if i >= len(data):
                break
            s = f"{str(rl)[:10]:10} \u2502"
            for j in range(len(col_labels)):
                v = data[i][j] if j < len(data[i]) else 0.0
                norm = (v - mn) / rng if rng > 0 else 0.5
                idx = min(int(norm * (len(blocks) - 1)), len(blocks) - 1)
                s += f" {blocks[idx] * 2}  "
            lines.append(s)
        lines.extend(["", f"Range: {mn:.2f} to {mx:.2f}", "```"])
        return "\n".join(lines)

    # ================================================================
    # Plotly layout builder
    # ================================================================

    def _plotly_layout(
        self, title: str, x_label: str = "", y_label: str = ""
    ) -> Dict[str, Any]:
        cfg: Dict[str, Any] = {
            "title": {
                "text": title,
                "font": {"size": 16, "color": self._TEXT},
            },
            "paper_bgcolor": self._PANEL,
            "plot_bgcolor": self._PANEL,
            "font": {"color": self._TEXT},
            "margin": {"l": 50, "r": 20, "t": 45, "b": 45},
            "xaxis": {"gridcolor": self._OUTER},
            "yaxis": {"gridcolor": self._OUTER},
        }
        if x_label:
            cfg["xaxis"]["title"] = {"text": x_label}
        if y_label:
            cfg["yaxis"]["title"] = {"text": y_label}
        return cfg

    def _plotly_trace(
        self,
        x: List[Any],
        y: List[float],
        chart_type: str,
        name: str = "",
    ) -> Dict[str, Any]:
        t: Dict[str, Any] = {
            "x": x,
            "y": y,
            "type": "bar" if chart_type == "bar" else "scatter",
        }
        if name:
            t["name"] = name
        if chart_type == "line":
            t["mode"] = "lines+markers"
        elif chart_type == "scatter":
            t["mode"] = "markers"
        return t

    def _plotly_body(
        self, chart_id: str, traces: List[Dict[str, Any]], layout: Dict[str, Any]
    ) -> str:
        return f"""<div class="card">
<div id="{chart_id}" style="width:100%;height:{self.valves.embed_chart_height}px"></div>
</div>
<script src="https://cdn.plot.ly/plotly-{self._PLOTLY_CDN}.min.js"></script>
<script>
(function(){{Plotly.newPlot("{chart_id}",{json.dumps(traces)},{json.dumps(layout)},{{responsive:true,displayModeBar:false}});}})();
</script>"""

    # ================================================================
    # PUBLIC: render_table
    # ================================================================

    async def render_table(
        self,
        rows: Any,
        *,
        title: str = "Table",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a table from a list of row objects.

        :param rows: List of dict rows (keys become columns)
        :param title: Title shown above the table
        :param mode: "embed", "text", or "auto"
        """
        rows = self._coerce_json(rows, "list")
        if not isinstance(rows, list):
            return "Invalid rows: expected a list of objects."
        fixed: List[Dict[str, Any]] = []
        for i, r in enumerate(rows):
            if isinstance(r, dict):
                fixed.append(r)
            else:
                return f"Invalid row at index {i}: expected dict."
        if not fixed:
            return "No rows provided."
        fixed = fixed[: self.valves.max_rows]

        cols: List[str] = []
        seen: Set[str] = set()
        for r in fixed:
            for k in r:
                ks = str(k)
                if ks not in seen:
                    seen.add(ks)
                    cols.append(ks)
        cols = cols[: self.valves.max_cols]

        if self._resolve_mode(mode) == "text" or HTMLResponse is None:
            return self._markdown_table(title, cols, fixed)
        page = self._wrap_html(title, self._html_table(title, cols, fixed))
        return HTMLResponse(
            content=page, headers={"Content-Disposition": "inline"}
        )

    # ================================================================
    # PUBLIC: render_comparison_table
    # ================================================================

    async def render_comparison_table(
        self,
        items: Any,
        criteria: Any,
        scores: Any,
        *,
        title: str = "Comparison",
        highlight_best: bool = True,
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Compare items across criteria with optional highlighting.

        :param items: List of item names
        :param criteria: List of criteria to compare on
        :param scores: Dict mapping item names to their criterion values
        :param title: Table title
        :param highlight_best: Mark best numeric values
        :param mode: "embed", "text", or "auto"

        Example:
        items = ["A", "B"], criteria = ["Cost", "Speed"]
        scores = {"A": {"Cost": 10, "Speed": 95}, "B": {"Cost": 15, "Speed": 80}}
        """
        items_l = self._coerce_str_list(items)
        crit_l = self._coerce_str_list(criteria)
        scores_d = self._coerce_json(scores, "dict")
        if not isinstance(scores_d, dict):
            scores_d = {}

        cols = ["Item"] + crit_l
        rows: List[Dict[str, Any]] = []
        for item in items_l:
            row: Dict[str, Any] = {"Item": item}
            s = scores_d.get(item, {})
            if not isinstance(s, dict):
                s = {}
            for c in crit_l:
                row[c] = s.get(c, "\u2014")
            rows.append(row)

        resolved = self._resolve_mode(mode)
        if resolved == "text" or HTMLResponse is None:
            if highlight_best:
                bv = self._find_best_values(crit_l, scores_d, items_l)
                for r in rows:
                    for c in crit_l:
                        if self._is_best(c, r.get(c), bv):
                            r[c] = f"{r[c]} \u2605"
            return self._markdown_table(title, cols, rows)

        bv = (
            self._find_best_values(crit_l, scores_d, items_l)
            if highlight_best
            else {}
        )
        page = self._wrap_html(
            title, self._html_comparison_table(title, cols, rows, bv)
        )
        return HTMLResponse(
            content=page, headers={"Content-Disposition": "inline"}
        )

    # ================================================================
    # PUBLIC: render_chart
    # ================================================================

    async def render_chart(
        self,
        x: Any,
        y: Any,
        *,
        title: str = "Chart",
        chart_type: ChartType = "line",
        mode: OutputMode = "auto",
        x_label: str = "",
        y_label: str = "",
    ) -> Any:
        """
        Render a chart (ASCII in text mode, Plotly in embed mode).

        :param x: X values (labels)
        :param y: Y values (numbers)
        :param title: Chart title
        :param chart_type: "bar", "line", or "scatter"
        :param mode: "embed", "text", or "auto"
        :param x_label: Optional x-axis label
        :param y_label: Optional y-axis label
        """
        xl = self._coerce_json(x, "list")
        yl = self._coerce_float_list(y)
        if not isinstance(xl, list):
            return "Invalid x: expected a list."
        if len(xl) != len(yl):
            return f"x and y must have the same length ({len(xl)} vs {len(yl)})."
        if not xl:
            return "No data provided."

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            return self._ascii_chart(xl, yl, title, chart_type, x_label, y_label)

        cid = f"c{abs(hash(title)) % 9999999}"
        trace = self._plotly_trace(xl, yl, chart_type)
        layout = self._plotly_layout(title, x_label, y_label)
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_multi_chart
    # ================================================================

    async def render_multi_chart(
        self,
        series: Any,
        *,
        title: str = "Chart",
        chart_type: ChartType = "line",
        mode: OutputMode = "auto",
        x_label: str = "",
        y_label: str = "",
    ) -> Any:
        """
        Render a chart with multiple series.

        :param series: List of {"name", "x", "y"} dicts
        :param title: Chart title
        :param chart_type: "bar", "line", or "scatter"
        :param mode: "embed", "text", or "auto"

        Example:
        [{"name": "Sales", "x": ["Jan","Feb"], "y": [100,150]},
         {"name": "Costs", "x": ["Jan","Feb"], "y": [80,90]}]
        """
        sl = self._coerce_json(series, "list")
        if not isinstance(sl, list):
            return "Invalid series: expected a list."
        fixed: List[Dict[str, Any]] = []
        for i, s in enumerate(sl):
            if isinstance(s, dict):
                fixed.append(s)
            else:
                return f"Invalid series at index {i}: expected dict."
        if not fixed:
            return "No series provided."

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            out = f"### {title}\n\n"
            for s in fixed:
                n = str(s.get("name", "Series"))
                sxl = self._coerce_json(s.get("x", []), "list")
                syl = self._coerce_float_list(s.get("y", []))
                if not isinstance(sxl, list):
                    sxl = []
                out += self._ascii_chart(sxl, syl, n, chart_type) + "\n\n"
            return out.rstrip() + "\n"

        traces: List[Dict[str, Any]] = []
        for s in fixed:
            n = str(s.get("name", "Series"))
            sxl = self._coerce_json(s.get("x", []), "list")
            syl = self._coerce_float_list(s.get("y", []))
            if not isinstance(sxl, list):
                sxl = []
            traces.append(self._plotly_trace(sxl, syl, chart_type, name=n))

        cid = f"mc{abs(hash(title)) % 9999999}"
        layout = self._plotly_layout(title, x_label, y_label)
        body = self._plotly_body(cid, traces, layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_heatmap
    # ================================================================

    async def render_heatmap(
        self,
        data: Any,
        row_labels: Any,
        col_labels: Any,
        *,
        title: str = "Heatmap",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a heatmap (ASCII blocks in text mode, Plotly in embed).

        :param data: 2D list of numeric values (rows x cols)
        :param row_labels: Labels for rows
        :param col_labels: Labels for columns
        :param title: Heatmap title
        :param mode: "embed", "text", or "auto"
        """
        dv = self._coerce_json(data, "list")
        rl = self._coerce_str_list(row_labels)
        cl = self._coerce_str_list(col_labels)

        fixed: List[List[float]] = []
        if isinstance(dv, list):
            for row in dv:
                rl2 = self._coerce_json(row, "list")
                if not isinstance(rl2, list):
                    continue
                out_row: List[float] = []
                for v in rl2:
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        out_row.append(float(v))
                    else:
                        try:
                            out_row.append(float(str(v).strip()))
                        except Exception:
                            out_row.append(0.0)
                fixed.append(out_row)

        if not fixed:
            return "No valid heatmap data."
        if len(fixed) > self.valves.max_rows:
            return f"Too many rows: {len(fixed)} > {self.valves.max_rows}."
        if not rl:
            rl = [f"Row {i + 1}" for i in range(len(fixed))]
        if not cl:
            cl = [
                f"Col {j + 1}"
                for j in range(max((len(r) for r in fixed), default=0))
            ]
        cl = cl[: self.valves.max_cols]
        fixed = [r[: len(cl)] for r in fixed]

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            return self._ascii_heatmap(fixed, rl[: len(fixed)], cl, title)

        z: List[List[float]] = []
        for row in fixed[: self.valves.max_rows]:
            rr = row[: len(cl)]
            rr += [0.0] * (len(cl) - len(rr))
            z.append(rr)

        hid = f"h{abs(hash(title)) % 9999999}"
        trace = {
            "type": "heatmap",
            "z": z,
            "x": cl,
            "y": rl[: len(z)],
            "hoverongaps": False,
        }
        layout = self._plotly_layout(title)
        layout["margin"] = {"l": 70, "r": 20, "t": 50, "b": 60}
        layout["xaxis"]["tickangle"] = -20

        body = self._plotly_body(hid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_metrics_grid
    # ================================================================

    async def render_metrics_grid(
        self,
        metrics: Any,
        *,
        title: str = "Metrics",
        columns: int = 3,
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render key metrics in a card grid.

        :param metrics: Dict of metric name to value
        :param title: Grid title
        :param columns: Number of columns (1-6)
        :param mode: "embed", "text", or "auto"

        Example:
        {"Revenue": "$1.2M", "Users": 15420, "Growth": "+23%"}
        """
        md = self._coerce_json(metrics, "dict")
        if not isinstance(md, dict) or not md:
            return "Invalid or empty metrics dict."

        resolved = self._resolve_mode(mode)
        if resolved == "text" or HTMLResponse is None:
            out = f"### {title}\n\n"
            for name, val in md.items():
                out += f"**{name}:** {val}  \n"
            return out

        cols = max(1, min(int(columns), 6))
        cards: List[str] = []
        for name, val in md.items():
            cards.append(
                f'<div style="background:var(--header);border-radius:var(--radius);'
                f'padding:18px;text-align:center;border:1px solid var(--outer)">'
                f'<div style="font-size:12px;color:var(--muted);margin-bottom:6px">'
                f"{html.escape(str(name))}</div>"
                f'<div style="font-size:26px;font-weight:700;color:var(--text)">'
                f"{html.escape(str(val))}</div></div>"
            )
        body = f"""<div class="card">
<div class="title">{html.escape(title)}</div>
<div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:12px">
{''.join(cards)}
</div></div>"""
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_timeline
    # ================================================================

    async def render_timeline(
        self,
        events: Any,
        *,
        title: str = "Timeline",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a timeline of events.

        :param events: List of {"date", "event", "details"} dicts
        :param title: Timeline title
        :param mode: "embed", "text", or "auto"

        Example:
        [{"date": "2024-01", "event": "Launch", "details": "Initial release"}]
        """
        ev = self._coerce_json(events, "list")
        if not isinstance(ev, list):
            return "Invalid events: expected a list."
        fixed: List[Dict[str, Any]] = []
        for i, e in enumerate(ev):
            if isinstance(e, dict):
                fixed.append(e)
            else:
                return f"Invalid event at index {i}: expected dict."
        if not fixed:
            return "No events provided."
        fixed = fixed[: self.valves.max_rows]

        resolved = self._resolve_mode(mode)
        if resolved == "text" or HTMLResponse is None:
            out = f"### {title}\n\n```\n"
            for e in fixed:
                d = str(e.get("date", ""))
                ev_s = str(e.get("event", ""))
                det = str(e.get("details", ""))
                out += f"{d:12} \u2502 {ev_s}\n"
                if det:
                    out += f"{'':12} \u2502 {det}\n"
                out += "\n"
            return out + "```"

        # Styled HTML timeline with border-left visual line
        items: List[str] = []
        for e in fixed:
            d = html.escape(str(e.get("date", "")))
            ev_s = html.escape(str(e.get("event", "")))
            det = html.escape(str(e.get("details", "")))
            det_html = (
                f'<div style="color:var(--muted);font-size:13px;margin-top:4px">'
                f"{det}</div>"
                if det
                else ""
            )
            items.append(
                f'<div style="display:flex;gap:16px;margin-bottom:20px">'
                f'<div style="min-width:90px;font-weight:600;color:var(--muted);'
                f'font-size:13px;padding-top:2px">{d}</div>'
                f'<div style="flex:1;border-left:2px solid var(--border);padding-left:16px">'
                f'<div style="font-weight:600">{ev_s}</div>'
                f"{det_html}</div></div>"
            )
        body = f"""<div class="card">
<div class="title">{html.escape(title)}</div>
{''.join(items)}
</div>"""
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_flowchart
    # ================================================================

    async def render_flowchart(
        self,
        steps: Any,
        *,
        title: str = "Flowchart",
    ) -> str:
        """
        Render an ASCII flowchart. Supports two formats:

        1. List of strings: sequential box-drawing flowchart
           ["Start", "Process", "End"]

        2. List of edge dicts: graph-style flowchart
           [{"from": "A", "to": "B", "label": "yes"}]

        :param steps: List of strings or edge dicts
        :param title: Flowchart title
        """
        v = self._coerce_json(steps, "list")
        if not isinstance(v, list) or not v:
            return "Invalid steps: expected a non-empty list."

        if isinstance(v[0], str):
            # Box-drawing sequential flowchart
            lines: List[str] = []
            for i, step in enumerate(v):
                step = str(step)
                w = min(max(len(step) + 4, 20), 60)
                lines.append("\u250c" + "\u2500" * (w - 2) + "\u2510")
                lines.append(
                    "\u2502 " + step.ljust(w - 4) + " \u2502"
                )
                lines.append("\u2514" + "\u2500" * (w - 2) + "\u2518")
                if i < len(v) - 1:
                    lines.append(" " * ((w - 1) // 2) + "\u2193")
            return f"### {title}\n\n```text\n" + "\n".join(lines) + "\n```"

        if isinstance(v[0], dict):
            # Edge-based graph
            edges: List[str] = []
            for i, s in enumerate(v[: self.valves.max_rows]):
                if not isinstance(s, dict):
                    return f"Invalid step at index {i}: expected dict."
                a = str(s.get("from", "")).strip()
                b = str(s.get("to", "")).strip()
                lbl = str(s.get("label", "")).strip()
                if a and b:
                    mid = f" --{lbl}--> " if lbl else " --> "
                    edges.append(f"[{a}]{mid}[{b}]")
            if not edges:
                return "No valid edges. Each step needs 'from' and 'to'."
            return (
                f"### {title}\n\n```text\n" + "\n".join(edges) + "\n```"
            )

        return "Invalid steps: expected strings or {from, to} dicts."

    # ================================================================
    # PUBLIC: render_tree
    # ================================================================

    async def render_tree(
        self,
        data: Any,
        *,
        title: str = "Tree",
        root_name: str = "Root",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render hierarchical data as a tree.

        Accepts two formats:
        1. Nested dict: {"src": {"main.py": None, "lib": {"utils.py": None}}}
        2. Edge list: [{"parent": "src", "child": "main.py"}]

        :param data: Nested dict or list of edge dicts
        :param title: Tree title
        :param root_name: Label for the root node
        :param mode: "embed", "text", or "auto"
        """
        v = self._coerce_json(data, "any")

        def walk_dict(
            node: Any, prefix: str = "", depth: int = 0
        ) -> List[str]:
            if depth > 12:
                return [prefix + "\u2026"]
            out: List[str] = []
            if isinstance(node, dict):
                items_list = list(node.items())
                for i, (k, val) in enumerate(items_list):
                    last = i == len(items_list) - 1
                    branch = "\u2514\u2500\u2500 " if last else "\u251c\u2500\u2500 "
                    out.append(prefix + branch + str(k))
                    ext = "    " if last else "\u2502   "
                    out.extend(walk_dict(val, prefix + ext, depth + 1))
            elif isinstance(node, list):
                for i, val in enumerate(node):
                    last = i == len(node) - 1
                    branch = "\u2514\u2500\u2500 " if last else "\u251c\u2500\u2500 "
                    if isinstance(val, (dict, list)):
                        out.append(prefix + branch + "...")
                        ext = "    " if last else "\u2502   "
                        out.extend(walk_dict(val, prefix + ext, depth + 1))
                    else:
                        out.append(prefix + branch + str(val))
            return out

        def walk_edges(edges: List[Dict[str, Any]]) -> str:
            children: Dict[str, List[str]] = {}
            all_nodes: Set[str] = set()
            child_set: Set[str] = set()
            for e in edges:
                p = str(e.get("parent", "")).strip()
                c = str(e.get("child", "")).strip()
                if p and c:
                    children.setdefault(p, []).append(c)
                    all_nodes.update([p, c])
                    child_set.add(c)
            root = (
                next(iter(all_nodes - child_set), root_name)
                if all_nodes
                else root_name
            )

            def build(
                n: str, prefix: str = "", depth: int = 0
            ) -> List[str]:
                if depth > 12:
                    return [prefix + "\u2026"]
                out: List[str] = []
                kids = children.get(n, [])
                for i, k in enumerate(kids):
                    last = i == len(kids) - 1
                    branch = "\u2514\u2500\u2500 " if last else "\u251c\u2500\u2500 "
                    out.append(prefix + branch + k)
                    ext = "    " if last else "\u2502   "
                    out.extend(build(k, prefix + ext, depth + 1))
                return out

            lines = [str(root)]
            lines.extend(build(str(root)))
            return "\n".join(lines)

        if isinstance(v, dict):
            text = root_name + "\n" + "\n".join(walk_dict(v))
        elif isinstance(v, list):
            fixed_edges: List[Dict[str, Any]] = []
            for i, e in enumerate(v[: self.valves.max_rows]):
                if isinstance(e, dict):
                    fixed_edges.append(e)
                else:
                    return f"Invalid edge at index {i}: expected dict."
            text = walk_edges(fixed_edges)
        else:
            return "Invalid data: expected a dict or list of {parent, child}."

        resolved = self._resolve_mode(mode)
        if resolved == "text" or HTMLResponse is None:
            return f"### {title}\n\n```text\n{text}\n```"

        body = f"""<div class="card">
<div class="title">{html.escape(title)}</div>
<pre class="vis">{html.escape(text)}</pre>
</div>"""
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_dashboard
    # ================================================================

    async def render_dashboard(
        self,
        components: Any,
        *,
        title: str = "Dashboard",
        layout: Literal["grid", "vertical"] = "vertical",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Combine multiple visualizations into one dashboard.

        :param components: List of {"type", "data"} dicts
        :param title: Dashboard title
        :param layout: "grid" or "vertical"
        :param mode: "embed", "text", or "auto"

        Supported component types:
          - "metrics": data = {"metrics": {...}, "title": "...", "columns": 3}
          - "chart": data = {"x": [...], "y": [...], "title": "...", "chart_type": "line"}
          - "table": data = {"rows": [...], "title": "..."}

        Example:
        [
            {"type": "metrics", "data": {"metrics": {"Users": 1000}, "title": "KPIs"}},
            {"type": "chart", "data": {"x": [1,2,3], "y": [10,20,15], "title": "Growth"}},
            {"type": "table", "data": {"rows": [{"a":1}], "title": "Details"}}
        ]
        """
        cl = self._coerce_json(components, "list")
        if not isinstance(cl, list) or not cl:
            return "Invalid components: expected a non-empty list."

        resolved = self._resolve_mode(mode)

        # ── Text mode ──
        if resolved == "text" or HTMLResponse is None:
            out = f"# {title}\n\n" + "\u2550" * 60 + "\n\n"
            for i, comp in enumerate(cl):
                if not isinstance(comp, dict):
                    continue
                ct = comp.get("type", "")
                cd = comp.get("data", {})
                if not isinstance(cd, dict):
                    cd = {}

                if ct == "metrics":
                    m = cd.get("metrics", {})
                    ct_title = cd.get("title", f"Metrics {i + 1}")
                    out += f"## {ct_title}\n\n"
                    if isinstance(m, dict):
                        for name, val in m.items():
                            out += f"**{name}:** {val}  \n"
                    out += "\n"
                elif ct == "chart":
                    cx = cd.get("x", [])
                    cy = cd.get("y", [])
                    ct_title = cd.get("title", f"Chart {i + 1}")
                    ctype = cd.get("chart_type", "line")
                    cxl = (
                        self._coerce_json(cx, "list")
                        if not isinstance(cx, list)
                        else cx
                    )
                    cyl = self._coerce_float_list(cy)
                    out += self._ascii_chart(cxl, cyl, ct_title, ctype) + "\n\n"
                elif ct == "table":
                    trows = cd.get("rows", [])
                    ct_title = cd.get("title", f"Table {i + 1}")
                    if (
                        isinstance(trows, list)
                        and trows
                        and isinstance(trows[0], dict)
                    ):
                        tcols = list(trows[0].keys())
                        out += self._markdown_table(ct_title, tcols, trows) + "\n\n"

                out += "\u2500" * 60 + "\n\n"
            return out

        # ── HTML mode ──
        sections: List[str] = []
        has_chart = False
        for i, comp in enumerate(cl):
            if not isinstance(comp, dict):
                continue
            ct = comp.get("type", "")
            cd = comp.get("data", {})
            if not isinstance(cd, dict):
                cd = {}

            if ct == "metrics":
                m = cd.get("metrics", {})
                ct_title = cd.get("title", f"Metrics {i + 1}")
                mcols = cd.get("columns", 3)
                if isinstance(m, dict) and m:
                    cards: List[str] = []
                    for name, val in m.items():
                        cards.append(
                            f'<div style="background:var(--header);border-radius:var(--radius);'
                            f'padding:16px;text-align:center;border:1px solid var(--outer)">'
                            f'<div style="font-size:12px;color:var(--muted);margin-bottom:6px">'
                            f"{html.escape(str(name))}</div>"
                            f'<div style="font-size:22px;font-weight:700">'
                            f"{html.escape(str(val))}</div></div>"
                        )
                    grid_cols = max(1, min(int(mcols), 6))
                    sections.append(
                        f'<div style="margin-bottom:20px">'
                        f'<div style="font-weight:700;margin-bottom:10px">'
                        f"{html.escape(ct_title)}</div>"
                        f'<div style="display:grid;grid-template-columns:repeat({grid_cols},1fr);gap:10px">'
                        f"{''.join(cards)}</div></div>"
                    )

            elif ct == "chart":
                has_chart = True
                cx = cd.get("x", [])
                cy = cd.get("y", [])
                ct_title = cd.get("title", f"Chart {i + 1}")
                ctype = cd.get("chart_type", "line")
                cxl = (
                    self._coerce_json(cx, "list")
                    if not isinstance(cx, list)
                    else cx
                )
                cyl = self._coerce_float_list(cy)
                cid = f"dc{i}_{abs(hash(ct_title)) % 9999}"
                trace = self._plotly_trace(cxl, cyl, ctype)
                lcfg = self._plotly_layout(ct_title)
                lcfg["margin"] = {"l": 50, "r": 20, "t": 40, "b": 40}
                sections.append(
                    f'<div style="margin-bottom:20px;border:1px solid var(--outer);'
                    f'border-radius:var(--radius);padding:12px">'
                    f'<div id="{cid}" style="width:100%;height:300px"></div>'
                    f"<script>"
                    f'Plotly.newPlot("{cid}",{json.dumps([trace])},'
                    f"{json.dumps(lcfg)},{{responsive:true,displayModeBar:false}});"
                    f"</script></div>"
                )

            elif ct == "table":
                trows = cd.get("rows", [])
                ct_title = cd.get("title", f"Table {i + 1}")
                if (
                    isinstance(trows, list)
                    and trows
                    and isinstance(trows[0], dict)
                ):
                    tcols = list(trows[0].keys())
                    sections.append(
                        f'<div style="margin-bottom:20px">'
                        f'<div style="font-weight:700;margin-bottom:10px">'
                        f"{html.escape(ct_title)}</div>"
                        f"{self._html_table_simple(tcols, trows)}</div>"
                    )

        grid_css = (
            "display:grid;grid-template-columns:1fr;gap:16px"
            if layout == "vertical"
            else "display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:16px"
        )
        plotly_script = (
            f'<script src="https://cdn.plot.ly/plotly-{self._PLOTLY_CDN}.min.js"></script>'
            if has_chart
            else ""
        )
        body = f"""{plotly_script}
<div class="card">
<div class="title" style="font-size:18px;margin-bottom:16px">{html.escape(title)}</div>
<div style="{grid_css}">{''.join(sections)}</div>
</div>"""
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_pie_chart
    # ================================================================

    async def render_pie_chart(
        self,
        labels: Any,
        values: Any,
        *,
        title: str = "Pie Chart",
        donut: bool = False,
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a pie or donut chart.

        :param labels: Category labels
        :param values: Numeric values for each category
        :param title: Chart title
        :param donut: If true, renders as a donut chart with a center hole
        :param mode: "embed", "text", or "auto"
        """
        ll = self._coerce_str_list(labels)
        vl = self._coerce_float_list(values)
        if not ll or not vl:
            return "No data provided."
        if len(ll) != len(vl):
            return f"labels and values must have the same length ({len(ll)} vs {len(vl)})."

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            total = sum(vl)
            if total <= 0:
                return f"### {title}\n\nNo positive values."
            pairs = sorted(zip(ll, vl), key=lambda p: p[1], reverse=True)
            bar_w = 30
            lines = [f"### {title}", "", "```text"]
            for label, val in pairs:
                pct = val / total * 100
                filled = int(pct / 100 * bar_w)
                bar = "\u2588" * filled + "\u2591" * (bar_w - filled)
                lines.append(f"{label:>15} [{bar}] {pct:5.1f}%")
            lines.append("```")
            return "\n".join(lines)

        cid = f"pie{abs(hash(title)) % 9999999}"
        trace: Dict[str, Any] = {
            "type": "pie",
            "labels": ll,
            "values": vl,
            "textinfo": "label+percent",
            "textfont": {"color": self._TEXT},
        }
        if donut:
            trace["hole"] = 0.4
        layout = self._plotly_layout(title)
        layout.pop("xaxis", None)
        layout.pop("yaxis", None)
        layout["legend"] = {"font": {"color": self._TEXT}}
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_gauge
    # ================================================================

    async def render_gauge(
        self,
        value: Any,
        *,
        title: str = "Gauge",
        min_val: float = 0,
        max_val: float = 100,
        unit: str = "",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a gauge indicator.

        :param value: Current value to display
        :param title: Gauge title
        :param min_val: Minimum scale value
        :param max_val: Maximum scale value
        :param unit: Unit label (e.g. "%", "ms")
        :param mode: "embed", "text", or "auto"
        """
        try:
            val = float(value)
        except (TypeError, ValueError):
            return "Invalid value: expected a number."
        if max_val <= min_val:
            return "max_val must be greater than min_val."

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            bar_w = 30
            pct = max(0.0, min(1.0, (val - min_val) / (max_val - min_val)))
            filled = int(pct * bar_w)
            bar = "\u2588" * filled + "\u2591" * (bar_w - filled)
            display = f"{val:.1f}{unit}" if unit else f"{val:.1f}"
            return f"### {title}\n\n```text\n[{bar}] {display}\n```"

        cid = f"ga{abs(hash(title)) % 9999999}"
        rng = max_val - min_val
        trace = {
            "type": "indicator",
            "mode": "gauge+number",
            "value": val,
            "number": {
                "suffix": f" {unit}" if unit else "",
                "font": {"color": self._TEXT},
            },
            "gauge": {
                "axis": {
                    "range": [min_val, max_val],
                    "tickfont": {"color": self._MUTED},
                },
                "bar": {"color": "#3b82f6"},
                "bgcolor": self._OUTER,
                "bordercolor": self._BORDER,
                "steps": [
                    {"range": [min_val, min_val + rng * 0.33], "color": "#7f1d1d"},
                    {
                        "range": [min_val + rng * 0.33, min_val + rng * 0.66],
                        "color": "#713f12",
                    },
                    {"range": [min_val + rng * 0.66, max_val], "color": "#14532d"},
                ],
            },
        }
        layout = self._plotly_layout(title)
        layout.pop("xaxis", None)
        layout.pop("yaxis", None)
        layout["margin"] = {"l": 30, "r": 30, "t": 50, "b": 10}
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_gantt
    # ================================================================

    async def render_gantt(
        self,
        tasks: Any,
        *,
        title: str = "Gantt Chart",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a Gantt chart (ASCII timeline in text mode, Plotly horizontal bars in embed).

        :param tasks: List of {"task", "start", "end", "group"?} dicts
        :param title: Chart title
        :param mode: "embed", "text", or "auto"

        Example:
        [{"task": "Design", "start": "2024-01-01", "end": "2024-01-15"},
         {"task": "Build", "start": "2024-01-10", "end": "2024-02-01"}]
        """
        from datetime import datetime as _dt

        tl = self._coerce_json(tasks, "list")
        if not isinstance(tl, list) or not tl:
            return "Invalid tasks: expected a non-empty list."
        fixed: List[Dict[str, Any]] = []
        for i, t in enumerate(tl):
            if not isinstance(t, dict):
                return f"Invalid task at index {i}: expected dict."
            task_name = str(t.get("task", f"Task {i + 1}"))
            start = str(t.get("start", ""))
            end = str(t.get("end", ""))
            if not start or not end:
                return f"Task '{task_name}' missing start or end date."
            fixed.append({
                "task": task_name,
                "start": start,
                "end": end,
                "group": str(t.get("group", "")),
            })

        _DATE_FMTS = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y-%m-%d %H:%M")

        def _parse_date(s: str) -> Any:
            for fmt in _DATE_FMTS:
                try:
                    return _dt.strptime(s, fmt)
                except ValueError:
                    continue
            return None

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            parsed: List[Dict[str, Any]] = []
            for t in fixed:
                s = _parse_date(t["start"])
                e = _parse_date(t["end"])
                parsed.append({"task": t["task"], "start": s, "end": e})

            valid = [p for p in parsed if p["start"] and p["end"]]
            if not valid:
                lines = [f"### {title}", "", "```text"]
                for t in fixed:
                    lines.append(f"{t['task']:20} {t['start']} \u2192 {t['end']}")
                lines.append("```")
                return "\n".join(lines)

            d_min = min(p["start"] for p in valid)
            d_max = max(p["end"] for p in valid)
            span = (d_max - d_min).days or 1
            bar_w = 40
            max_label = min(max(len(p["task"]) for p in valid), 20)
            lines = [f"### {title}", "", "```text"]
            for p in valid:
                offset = int((p["start"] - d_min).days / span * bar_w)
                length = max(1, int((p["end"] - p["start"]).days / span * bar_w))
                bar = " " * offset + "\u2588" * length
                bar = bar.ljust(bar_w)
                lines.append(f"{p['task']:{max_label}} |{bar}|")
            lines.append(
                f"{'':{max_label}}  "
                f"{d_min.strftime('%Y-%m-%d')}"
                f"{d_max.strftime('%Y-%m-%d'):>{bar_w - 10 + 1}}"
            )
            lines.append("```")
            return "\n".join(lines)

        # Plotly: horizontal bars with date x-axis
        cid = f"gt{abs(hash(title)) % 9999999}"
        task_names: List[str] = []
        base_dates: List[str] = []
        durations: List[float] = []
        hover: List[str] = []
        for t in reversed(fixed):
            task_names.append(t["task"])
            base_dates.append(t["start"])
            s = _parse_date(t["start"])
            e = _parse_date(t["end"])
            dur = ((e - s).days * 86400000) if s and e else 86400000
            durations.append(max(dur, 86400000))
            hover.append(f"{t['task']}: {t['start']} \u2192 {t['end']}")

        trace = {
            "type": "bar",
            "orientation": "h",
            "y": task_names,
            "x": durations,
            "base": base_dates,
            "marker": {"color": "#3b82f6"},
            "hovertext": hover,
            "hoverinfo": "text",
        }
        layout = self._plotly_layout(title)
        layout["xaxis"] = {"type": "date", "gridcolor": self._OUTER}
        layout["yaxis"] = {"gridcolor": self._OUTER, "automargin": True}
        layout["margin"] = {"l": 120, "r": 20, "t": 50, "b": 40}
        layout["bargap"] = 0.3
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_sankey
    # ================================================================

    async def render_sankey(
        self,
        nodes: Any,
        links: Any,
        *,
        title: str = "Sankey Diagram",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a Sankey flow diagram.

        :param nodes: List of node labels
        :param links: List of {"source", "target", "value"} dicts (indices or names)
        :param title: Chart title
        :param mode: "embed", "text", or "auto"

        Example:
        nodes = ["A", "B", "C"]
        links = [{"source": 0, "target": 1, "value": 10},
                 {"source": 1, "target": 2, "value": 8}]
        """
        nl = self._coerce_str_list(nodes)
        ll = self._coerce_json(links, "list")
        if not nl:
            return "No nodes provided."
        if not isinstance(ll, list) or not ll:
            return "Invalid links: expected a non-empty list."

        fixed_links: List[Dict[str, Any]] = []
        for i, link in enumerate(ll):
            if not isinstance(link, dict):
                return f"Invalid link at index {i}: expected dict."
            src = link.get("source", 0)
            tgt = link.get("target", 0)
            val = link.get("value", 1)
            if isinstance(src, str):
                try:
                    src = nl.index(src)
                except ValueError:
                    return f"Unknown source node: {src}"
            if isinstance(tgt, str):
                try:
                    tgt = nl.index(tgt)
                except ValueError:
                    return f"Unknown target node: {tgt}"
            try:
                val = float(val)
            except (TypeError, ValueError):
                val = 1.0
            fixed_links.append({"source": int(src), "target": int(tgt), "value": val})

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            lines = [f"### {title}", "", "```text"]
            for lk in fixed_links:
                s_name = (
                    nl[lk["source"]] if lk["source"] < len(nl) else f"#{lk['source']}"
                )
                t_name = (
                    nl[lk["target"]] if lk["target"] < len(nl) else f"#{lk['target']}"
                )
                lines.append(f"{s_name} --[{lk['value']:.0f}]--> {t_name}")
            lines.append("```")
            return "\n".join(lines)

        cid = f"sk{abs(hash(title)) % 9999999}"
        trace = {
            "type": "sankey",
            "node": {
                "label": nl,
                "color": ["#3b82f6"] * len(nl),
                "pad": 20,
                "thickness": 20,
            },
            "link": {
                "source": [lk["source"] for lk in fixed_links],
                "target": [lk["target"] for lk in fixed_links],
                "value": [lk["value"] for lk in fixed_links],
                "color": ["rgba(59,130,246,0.3)"] * len(fixed_links),
            },
        }
        layout = self._plotly_layout(title)
        layout.pop("xaxis", None)
        layout.pop("yaxis", None)
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_radar
    # ================================================================

    async def render_radar(
        self,
        categories: Any,
        series: Any,
        *,
        title: str = "Radar Chart",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a radar (spider) chart with one or more series.

        :param categories: List of axis labels
        :param series: List of {"name", "values"} dicts
        :param title: Chart title
        :param mode: "embed", "text", or "auto"

        Example:
        categories = ["Speed", "Power", "Range", "Defense"]
        series = [{"name": "Player A", "values": [90, 60, 80, 70]}]
        """
        cats = self._coerce_str_list(categories)
        sl = self._coerce_json(series, "list")
        if not cats:
            return "No categories provided."
        if not isinstance(sl, list) or not sl:
            return "Invalid series: expected a non-empty list."

        fixed: List[Dict[str, Any]] = []
        for i, s in enumerate(sl):
            if not isinstance(s, dict):
                return f"Invalid series at index {i}: expected dict."
            name = str(s.get("name", f"Series {i + 1}"))
            vals = self._coerce_float_list(s.get("values", []))
            if len(vals) != len(cats):
                return (
                    f"Series '{name}' has {len(vals)} values "
                    f"but {len(cats)} categories."
                )
            fixed.append({"name": name, "values": vals})

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            header = "| Category | " + " | ".join(s["name"] for s in fixed) + " |"
            sep = "| --- | " + " | ".join(["---"] * len(fixed)) + " |"
            rows: List[str] = []
            for j, cat in enumerate(cats):
                row = (
                    f"| {cat} | "
                    + " | ".join(f"{s['values'][j]:.1f}" for s in fixed)
                    + " |"
                )
                rows.append(row)
            return f"### {title}\n\n{header}\n{sep}\n" + "\n".join(rows)

        cid = f"rd{abs(hash(title)) % 9999999}"
        palette = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899"]
        traces: List[Dict[str, Any]] = []
        for i, s in enumerate(fixed):
            color = palette[i % len(palette)]
            traces.append({
                "type": "scatterpolar",
                "r": s["values"] + [s["values"][0]],
                "theta": cats + [cats[0]],
                "fill": "toself",
                "opacity": 0.6,
                "name": s["name"],
                "line": {"color": color},
            })
        layout = self._plotly_layout(title)
        layout.pop("xaxis", None)
        layout.pop("yaxis", None)
        layout["polar"] = {
            "bgcolor": self._PANEL,
            "radialaxis": {"gridcolor": self._OUTER, "color": self._MUTED},
            "angularaxis": {"gridcolor": self._OUTER, "color": self._TEXT},
        }
        layout["legend"] = {"font": {"color": self._TEXT}}
        body = self._plotly_body(cid, traces, layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_waterfall
    # ================================================================

    async def render_waterfall(
        self,
        labels: Any,
        values: Any,
        *,
        title: str = "Waterfall Chart",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a waterfall chart showing incremental changes.

        :param labels: Category labels (first = starting value, last = total)
        :param values: Numeric values (positive = increase, negative = decrease)
        :param title: Chart title
        :param mode: "embed", "text", or "auto"

        Example:
        labels = ["Revenue", "Costs", "Tax", "Profit"]
        values = [500, -200, -50, 250]
        """
        ll = self._coerce_str_list(labels)
        vl = self._coerce_float_list(values)
        if not ll or not vl:
            return "No data provided."
        if len(ll) != len(vl):
            return f"labels and values must have the same length ({len(ll)} vs {len(vl)})."

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            running = 0.0
            all_totals: List[float] = []
            for v in vl:
                running += v
                all_totals.append(running)
            max_abs = max(abs(t) for t in all_totals) if all_totals else 1.0
            if max_abs == 0:
                max_abs = 1.0
            bar_w = 30
            max_label = min(max(len(l) for l in ll), 15)
            lines = [f"### {title}", "", "```text"]
            running = 0.0
            for label, val in zip(ll, vl):
                running += val
                sign = "+" if val >= 0 else "-"
                filled = int(abs(running) / max_abs * bar_w)
                bar = "\u2588" * filled
                lines.append(
                    f"{label:{max_label}} {sign}{abs(val):>8.1f}  "
                    f"{bar:>{bar_w}}  = {running:.1f}"
                )
            lines.append("```")
            return "\n".join(lines)

        cid = f"wf{abs(hash(title)) % 9999999}"
        measures: List[str] = []
        for i in range(len(vl)):
            if i == 0:
                measures.append("absolute")
            elif i == len(vl) - 1:
                measures.append("total")
            else:
                measures.append("relative")
        trace = {
            "type": "waterfall",
            "x": ll,
            "y": vl,
            "measure": measures,
            "connector": {"line": {"color": self._BORDER}},
            "increasing": {"marker": {"color": "#22c55e"}},
            "decreasing": {"marker": {"color": "#ef4444"}},
            "totals": {"marker": {"color": "#3b82f6"}},
            "textposition": "outside",
            "textfont": {"color": self._TEXT},
        }
        layout = self._plotly_layout(title)
        layout["showlegend"] = False
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_funnel
    # ================================================================

    async def render_funnel(
        self,
        stages: Any,
        values: Any,
        *,
        title: str = "Funnel",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a funnel chart.

        :param stages: List of stage labels
        :param values: Numeric values for each stage (typically decreasing)
        :param title: Chart title
        :param mode: "embed", "text", or "auto"

        Example:
        stages = ["Visitors", "Signups", "Trials", "Paid"]
        values = [10000, 3000, 800, 200]
        """
        sl = self._coerce_str_list(stages)
        vl = self._coerce_float_list(values)
        if not sl or not vl:
            return "No data provided."
        if len(sl) != len(vl):
            return f"stages and values must have the same length ({len(sl)} vs {len(vl)})."

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            max_v = max(vl) if vl else 1.0
            if max_v <= 0:
                max_v = 1.0
            bar_w = 40
            lines = [f"### {title}", "", "```text"]
            for stage, val in zip(sl, vl):
                pct = val / max_v
                width = max(1, int(pct * bar_w))
                padding = (bar_w - width) // 2
                bar = " " * padding + "\u2588" * width
                pct_of_first = val / vl[0] * 100 if vl[0] > 0 else 0
                lines.append(
                    f"{stage:>15} {bar:<{bar_w}} "
                    f"{val:>10.0f} ({pct_of_first:5.1f}%)"
                )
            lines.append("```")
            return "\n".join(lines)

        cid = f"fn{abs(hash(title)) % 9999999}"
        trace = {
            "type": "funnel",
            "y": sl,
            "x": vl,
            "textinfo": "value+percent initial",
            "marker": {"color": "#3b82f6"},
            "textfont": {"color": self._TEXT},
        }
        layout = self._plotly_layout(title)
        layout.pop("xaxis", None)
        layout["yaxis"] = {"color": self._TEXT}
        layout["margin"] = {"l": 120, "r": 20, "t": 50, "b": 30}
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )

    # ================================================================
    # PUBLIC: render_candlestick
    # ================================================================

    async def render_candlestick(
        self,
        dates: Any,
        open: Any,
        high: Any,
        low: Any,
        close: Any,
        *,
        title: str = "Candlestick Chart",
        mode: OutputMode = "auto",
    ) -> Any:
        """
        Render a candlestick (OHLC) financial chart.

        :param dates: List of date strings
        :param open: List of opening prices
        :param high: List of high prices
        :param low: List of low prices
        :param close: List of closing prices
        :param title: Chart title
        :param mode: "embed", "text", or "auto"

        Example:
        dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
        open = [100, 105, 102], high = [110, 108, 107]
        low = [98, 101, 100], close = [105, 102, 106]
        """
        dl = self._coerce_str_list(dates)
        ol = self._coerce_float_list(open)
        hl = self._coerce_float_list(high)
        lo = self._coerce_float_list(low)
        cl = self._coerce_float_list(close)
        n = len(dl)
        if not n or len(ol) != n or len(hl) != n or len(lo) != n or len(cl) != n:
            return "All inputs must be non-empty lists of the same length."

        resolved = self._resolve_mode(mode)
        if (
            resolved == "text"
            or not self.valves.allow_external_cdn
            or HTMLResponse is None
        ):
            lines = [f"### {title}", ""]
            lines.append(
                f"| {'Date':>12} | {'Open':>8} | {'High':>8} "
                f"| {'Low':>8} | {'Close':>8} | {'Change':>8} |"
            )
            lines.append(
                f"| {'---':>12} | {'---':>8} | {'---':>8} "
                f"| {'---':>8} | {'---':>8} | {'---':>8} |"
            )
            for i in range(n):
                change = cl[i] - ol[i]
                arrow = "\u25b2" if change >= 0 else "\u25bc"
                lines.append(
                    f"| {dl[i]:>12} | {ol[i]:>8.2f} | {hl[i]:>8.2f} "
                    f"| {lo[i]:>8.2f} | {cl[i]:>8.2f} "
                    f"| {arrow}{abs(change):>7.2f} |"
                )
            return "\n".join(lines)

        cid = f"cs{abs(hash(title)) % 9999999}"
        trace = {
            "type": "candlestick",
            "x": dl,
            "open": ol,
            "high": hl,
            "low": lo,
            "close": cl,
            "increasing": {"line": {"color": "#22c55e"}},
            "decreasing": {"line": {"color": "#ef4444"}},
        }
        layout = self._plotly_layout(title)
        layout["xaxis"] = {
            "type": "date",
            "gridcolor": self._OUTER,
            "rangeslider": {"visible": False},
        }
        layout["yaxis"] = {"gridcolor": self._OUTER}
        body = self._plotly_body(cid, [trace], layout)
        return HTMLResponse(
            content=self._wrap_html(title, body),
            headers={"Content-Disposition": "inline"},
        )
