"""
title: Offline Artifact Workbench
description: Create offline HTML documents, slide decks, optional PDFs and ZIP bundles in a controlled artifact directory.
version: 1.1.0
license: MIT
security: Writes only below the configured artifact root. Optional PDF conversion uses local Playwright, allowlisted converters or Python libraries when present. No internet access, arbitrary path reads or shell strings are used.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Tools:
    """OpenWebUI toolkit for offline artifact creation and handover."""

    class Valves(BaseModel):
        artifact_root: str = Field("/app/backend/data/offline_artifacts", description="Directory where generated artifacts are written.")
        offline_addons_root: str = Field("/app/backend/data", description="Root of the mounted OpenWebUI offline add-ons data tree.")
        offline_addons_python_path: str = Field("/app/backend/data/python", description="Additional offline Python package path prepared for OpenWebUI tools.")
        playwright_browsers_path: str = Field("/app/backend/data/cache/ms-playwright", description="Local Playwright browser cache path.")
        nltk_data_path: str = Field("/app/backend/data/nltk_data", description="Local NLTK data path prepared by the offline add-ons bundle.")
        prefer_playwright_pdf: bool = Field(True, description="Use local Playwright/Chromium for PDF rendering before WeasyPrint or wkhtmltopdf.")
        playwright_timeout_ms: int = Field(60000, description="Timeout for Playwright HTML rendering.")
        max_html_chars: int = Field(400000, description="Maximum HTML input size.")
        max_zip_files: int = Field(25, description="Maximum files per ZIP bundle.")
        allow_wkhtmltopdf: bool = Field(False, description="Allow local wkhtmltopdf conversion when installed.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def create_html_document(self, title: str, body_html: str, filename: str = "document.html", css: str = "", __event_emitter__: Any = None) -> str:
        """
        Create a complete print-ready HTML document in the artifact directory.
        :param title: Document title.
        :param body_html: Trusted HTML body content generated in chat or via Jupyter.
        :param filename: Output HTML filename.
        :param css: Optional additional CSS.
        """
        if len(body_html) > int(self.valves.max_html_chars):
            return "Fehler: HTML-Inhalt ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge HTML-Dokument", False)
        path = self._safe_output_path(filename, ".html")
        document = self._html_shell(title, body_html, css, landscape=False)
        path.write_text(document, encoding="utf-8")
        self._write_manifest(path, "html_document", {"title": title})
        await self._file_event(__event_emitter__, path)
        await self._emit(__event_emitter__, "HTML-Dokument erzeugt", True)
        return self._result("HTML-Dokument", path)

    async def create_slide_deck(self, title: str, slides_json: str, filename: str = "presentation.html", theme_css: str = "", __event_emitter__: Any = None) -> str:
        """
        Create a 16:9 print-ready HTML presentation from JSON slides.
        :param title: Presentation title.
        :param slides_json: JSON array with slide objects containing title, bullets and optional notes.
        :param filename: Output HTML filename.
        :param theme_css: Optional additional CSS.
        """
        if len(slides_json) > int(self.valves.max_html_chars):
            return "Fehler: Slides-JSON ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge HTML-Präsentation", False)
        try:
            slides = json.loads(slides_json)
        except json.JSONDecodeError as exc:
            return f"Fehler: Ungültiges Slides-JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(slides, list) or not slides:
            return "Fehler: Slides-JSON muss ein nicht-leeres Array sein."
        safe_slides = [self._normalize_slide(item, idx + 1) for idx, item in enumerate(slides[:80])]
        body = self._slides_body(title, safe_slides)
        path = self._safe_output_path(filename, ".html")
        path.write_text(self._html_shell(title, body, self._slide_css() + "\n" + theme_css, landscape=True), encoding="utf-8")
        self._write_manifest(path, "html_presentation", {"title": title, "slides": len(safe_slides)})
        await self._file_event(__event_emitter__, path)
        await self._emit(__event_emitter__, "HTML-Präsentation erzeugt", True)
        return self._result("HTML-Präsentation", path)

    async def convert_html_to_pdf(self, html_file: str, pdf_filename: str = "", __event_emitter__: Any = None) -> str:
        """
        Convert an existing generated HTML artifact to PDF when a local converter is available.
        :param html_file: HTML artifact path or filename below the artifact root.
        :param pdf_filename: Optional PDF output filename.
        """
        await self._emit(__event_emitter__, "Prüfe PDF-Konverter", False)
        source = self._safe_existing_path(html_file, ".html")
        target = self._safe_output_path(pdf_filename or (source.stem + ".pdf"), ".pdf")
        try:
            converted_by = ""
            if bool(self.valves.prefer_playwright_pdf):
                converted_by = await self._convert_with_playwright(source, target)
            if not converted_by:
                converted_by = self._convert_with_weasyprint(source, target)
            if not converted_by and bool(self.valves.allow_wkhtmltopdf):
                converted_by = self._convert_with_wkhtmltopdf(source, target)
        except Exception as exc:
            await self._emit(__event_emitter__, "PDF-Konvertierung fehlgeschlagen", True)
            return f"Fehler: PDF-Konvertierung fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        if not converted_by:
            return "Fehler: Kein lokaler PDF-Konverter verfügbar. Stelle den Offline-Addon-Stack mit Playwright bereit, installiere lokal `weasyprint` im OpenWebUI-Container oder aktiviere ein installiertes `wkhtmltopdf` über die Tool-Valve."
        self._write_manifest(target, "pdf", {"source": str(source.name), "converter": converted_by})
        await self._file_event(__event_emitter__, target)
        await self._emit(__event_emitter__, "PDF erzeugt", True)
        return self._result(f"PDF ({converted_by})", target)

    async def bundle_artifacts(self, artifact_files_json: str, zip_filename: str = "artifacts.zip", __event_emitter__: Any = None) -> str:
        """
        Bundle generated artifacts into a ZIP archive.
        :param artifact_files_json: JSON array of artifact filenames or paths below the artifact root.
        :param zip_filename: Output ZIP filename.
        """
        await self._emit(__event_emitter__, "Erzeuge ZIP-Paket", False)
        try:
            items = json.loads(artifact_files_json)
        except json.JSONDecodeError as exc:
            return f"Fehler: Ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(items, list) or len(items) > int(self.valves.max_zip_files):
            return "Fehler: Erwartet wird ein JSON-Array innerhalb der konfigurierten Dateigrenze."
        target = self._safe_output_path(zip_filename, ".zip")
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in items:
                source = self._safe_existing_path(str(item), "")
                archive.write(source, arcname=source.name)
        self._write_manifest(target, "zip_bundle", {"files": len(items)})
        await self._file_event(__event_emitter__, target)
        await self._emit(__event_emitter__, "ZIP-Paket erzeugt", True)
        return self._result("ZIP-Paket", target)

    def _root(self) -> Path:
        root = Path(os.environ.get("OPENWEBUI_ARTIFACT_ROOT", str(self.valves.artifact_root))).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _safe_output_path(self, filename: str, suffix: str) -> Path:
        name = Path(filename or f"artifact{suffix}").name
        name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip(" .") or f"artifact{suffix}"
        if not name.lower().endswith(suffix):
            name += suffix
        path = (self._root() / name).resolve()
        if self._root() not in path.parents and path != self._root():
            raise ValueError("Ausgabepfad liegt außerhalb des Artefaktverzeichnisses.")
        return path

    def _safe_existing_path(self, file_name: str, suffix: str) -> Path:
        candidate = Path(file_name)
        path = (candidate if candidate.is_absolute() else self._root() / candidate.name).resolve()
        if self._root() not in path.parents:
            raise ValueError("Datei liegt außerhalb des Artefaktverzeichnisses.")
        if suffix and path.suffix.lower() != suffix:
            raise ValueError(f"Erwartet wird eine `{suffix}`-Datei.")
        if not path.exists() or not path.is_file():
            raise ValueError("Artefaktdatei wurde nicht gefunden.")
        return path

    def _html_shell(self, title: str, body: str, css: str, landscape: bool) -> str:
        page = "A4 landscape" if landscape else "A4"
        base_css = f"""
@page {{ size: {page}; margin: 14mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #111827; background: #ffffff; line-height: 1.45; }}
h1, h2, h3 {{ page-break-after: avoid; }}
img, table, pre {{ max-width: 100%; }}
section {{ break-inside: avoid; }}
"""
        return "<!doctype html>\n<html lang=\"de\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" + f"<title>{html.escape(title)}</title>\n<style>\n{base_css}\n{css}\n</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n"

    def _slide_css(self) -> str:
        return """
@page { size: 297mm 167.0625mm; margin: 0; }
body { background: #f8fafc; }
.slide { width: 297mm; min-height: 167.0625mm; padding: 18mm 22mm; page-break-after: always; background: #ffffff; display: flex; flex-direction: column; justify-content: center; }
.slide h1 { font-size: 34pt; margin: 0 0 10mm; }
.slide h2 { font-size: 26pt; margin: 0 0 8mm; }
.slide ul { font-size: 17pt; margin: 0; padding-left: 9mm; }
.slide li { margin: 0 0 4mm; }
.slide .notes { margin-top: 10mm; font-size: 10pt; color: #475569; }
"""

    def _slides_body(self, title: str, slides: List[Dict[str, Any]]) -> str:
        parts = [f"<section class=\"slide\"><h1>{html.escape(title)}</h1><p>Offline erzeugte HTML-Präsentation</p></section>"]
        for slide in slides:
            bullets = "".join(f"<li>{html.escape(item)}</li>" for item in slide["bullets"])
            notes = f"<p class=\"notes\">{html.escape(slide['notes'])}</p>" if slide["notes"] else ""
            parts.append(f"<section class=\"slide\"><h2>{html.escape(slide['title'])}</h2><ul>{bullets}</ul>{notes}</section>")
        return "\n".join(parts)

    def _normalize_slide(self, item: Any, index: int) -> Dict[str, Any]:
        if not isinstance(item, dict):
            return {"title": f"Folie {index}", "bullets": [str(item)[:300]], "notes": ""}
        title = str(item.get("title") or f"Folie {index}")[:180]
        raw_bullets = item.get("bullets") or item.get("points") or []
        if isinstance(raw_bullets, str):
            raw_bullets = [raw_bullets]
        bullets = [str(point)[:300] for point in list(raw_bullets)[:8]] or ["Inhalt ergänzen"]
        notes = str(item.get("notes") or "")[:1000]
        return {"title": title, "bullets": bullets, "notes": notes}

    def _convert_with_weasyprint(self, source: Path, target: Path) -> str:
        try:
            from weasyprint import HTML  # type: ignore
        except Exception:
            return ""
        HTML(filename=str(source)).write_pdf(str(target))
        return "weasyprint"

    async def _convert_with_playwright(self, source: Path, target: Path) -> str:
        self._prepare_offline_addons_runtime()
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except Exception:
            return ""
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.goto(source.resolve().as_uri(), wait_until="networkidle", timeout=int(self.valves.playwright_timeout_ms))
                    await page.pdf(path=str(target), print_background=True, prefer_css_page_size=True)
                finally:
                    await browser.close()
        except Exception:
            if target.exists():
                try:
                    target.unlink()
                except Exception:
                    pass
            return ""
        return "playwright"

    def _convert_with_wkhtmltopdf(self, source: Path, target: Path) -> str:
        exe = shutil.which("wkhtmltopdf")
        if not exe:
            return ""
        subprocess.run([exe, "--disable-local-file-access", str(source), str(target)], check=True, timeout=60)
        return "wkhtmltopdf"

    def _prepare_offline_addons_runtime(self) -> None:
        root_value = str(getattr(self.valves, "offline_addons_root", "") or os.environ.get("OPENWEBUI_OFFLINE_ADDONS_ROOT", "")).strip()
        root = Path(root_value).expanduser().resolve() if root_value else None

        python_path = str(getattr(self.valves, "offline_addons_python_path", "") or os.environ.get("OPENWEBUI_OFFLINE_ADDONS_PYTHON_PATH", "")).strip()
        if not python_path and root:
            python_path = str(root / "python")
        if python_path:
            candidate = Path(python_path).expanduser().resolve()
            if candidate.exists() and str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))

        browsers_path = str(getattr(self.valves, "playwright_browsers_path", "") or os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")).strip()
        if not browsers_path and root:
            browsers_path = str(root / "cache" / "ms-playwright")
        if browsers_path:
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

        nltk_path = str(getattr(self.valves, "nltk_data_path", "") or os.environ.get("NLTK_DATA", "")).strip()
        if not nltk_path and root:
            nltk_path = str(root / "nltk_data")
        if nltk_path:
            os.environ.setdefault("NLTK_DATA", nltk_path)

    def _write_manifest(self, path: Path, artifact_type: str, meta: Dict[str, Any]) -> None:
        manifest = {"artifact": path.name, "type": artifact_type, "meta": meta}
        path.with_suffix(path.suffix + ".manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    def _result(self, label: str, path: Path) -> str:
        return "\n".join(["# Artefakt erzeugt", f"- Typ: {label}", f"- Datei: `{path}`", f"- Größe: {path.stat().st_size} Bytes", "", "Hinweis: Für direkte Downloads muss das Artefaktverzeichnis in der OpenWebUI-Instanz als erreichbarer Datei-/Volume-Pfad eingebunden sein."])

    def _redact(self, value: str) -> str:
        return re.sub(r"(?i)(token|api[_-]?key|password|secret)=([^&\s]+)", r"\1=[REDACTED]", value)

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})

    async def _file_event(self, emitter: Any, path: Path) -> None:
        if emitter:
            await emitter({"type": "chat:message:files", "data": {"files": [{"name": path.name, "path": str(path)}]}})
