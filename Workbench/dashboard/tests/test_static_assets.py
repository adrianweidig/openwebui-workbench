from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATIC_ROOT = ROOT / "Workbench" / "dashboard" / "static"


class DashboardHtmlCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.i18n_keys: set[str] = set()
        self.panels: set[str] = set()
        self.asset_refs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if element_id := values.get("id"):
            self.ids.add(element_id)
        for key in ("data-i18n", "data-i18n-placeholder", "data-i18n-aria-label"):
            if value := values.get(key):
                self.i18n_keys.add(value)
        if panel := values.get("data-panel"):
            self.panels.add(panel)
        for key in ("href", "src"):
            value = values.get(key, "")
            if value.startswith("/static/"):
                self.asset_refs.add(value.removeprefix("/static/"))


def collect_index() -> DashboardHtmlCollector:
    collector = DashboardHtmlCollector()
    collector.feed((STATIC_ROOT / "index.html").read_text(encoding="utf-8"))
    return collector


def javascript_literal_i18n_keys() -> set[str]:
    app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    return set(re.findall(r"(?<![\w$])t\(\s*[\"']([^\"'`]+)[\"']", app_js))


class DashboardStaticAssetsTests(unittest.TestCase):
    def test_index_static_asset_references_exist(self) -> None:
        collector = collect_index()

        for asset in collector.asset_refs:
            with self.subTest(asset=asset):
                self.assertTrue((STATIC_ROOT / asset).is_file(), asset)

    def test_locale_files_cover_index_i18n_keys(self) -> None:
        collector = collect_index()

        for locale in ("de", "en"):
            with self.subTest(locale=locale):
                messages = json.loads((STATIC_ROOT / "locales" / f"{locale}.json").read_text(encoding="utf-8"))
                missing = sorted(collector.i18n_keys - set(messages))
                self.assertEqual(missing, [])

    def test_locale_files_cover_javascript_literal_i18n_keys(self) -> None:
        keys = javascript_literal_i18n_keys()

        for locale in ("de", "en"):
            with self.subTest(locale=locale):
                messages = json.loads((STATIC_ROOT / "locales" / f"{locale}.json").read_text(encoding="utf-8"))
                missing = sorted(keys - set(messages))
                self.assertEqual(missing, [])

    def test_navigation_panels_match_javascript_allowlist(self) -> None:
        collector = collect_index()
        app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
        match = re.search(r"SUPPORTED_PANELS\s*=\s*new Set\(\[(.*?)\]\)", app_js)
        self.assertIsNotNone(match)
        supported = set(re.findall(r'"([^"]+)"', match.group(1)))

        self.assertEqual(collector.panels, supported)
        for panel in collector.panels:
            self.assertIn(f"panel-{panel}", collector.ids)


if __name__ == "__main__":
    unittest.main()
