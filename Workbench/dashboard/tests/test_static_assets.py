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

    def test_deep_link_query_params_are_read_and_written(self) -> None:
        app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("window.history.replaceState", app_js)
        for parameter in ("panel", "model", "file", "resource", "locale", "view", "modelSearch", "resourceSearch"):
            with self.subTest(parameter=parameter):
                self.assertIn(f'queryParams.get("{parameter}")', app_js)
                self.assertRegex(app_js, rf"params\.(?:set|delete)\(\"{parameter}\"")

    def test_view_mode_preferences_are_persisted(self) -> None:
        app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("function detectInitialViewMode", app_js)
        self.assertIn("SUPPORTED_VIEW_MODES", app_js)
        self.assertIn("localStorage.setItem(`workbench-${editor}-view`, nextMode)", app_js)
        self.assertIn("localStorage.getItem(`workbench-${editor}-view`)", app_js)

    def test_search_filters_are_persisted(self) -> None:
        app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("function detectInitialSearch", app_js)
        self.assertIn("function persistSearchValue", app_js)
        self.assertIn("localStorage.setItem(searchStorageKey(editor), value)", app_js)
        self.assertIn("localStorage.removeItem(searchStorageKey(editor))", app_js)
        self.assertIn('params.set("modelSearch", modelSearch)', app_js)
        self.assertIn('params.set("resourceSearch", resourceSearch)', app_js)

    def test_read_only_editor_controls_are_covered(self) -> None:
        app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn('t("editor.disabled.readOnly")', app_js)
        self.assertIn("function updateEditorWriteControls", app_js)
        self.assertIn("textarea.readOnly = readOnly", app_js)
        for control in (
            "add-model-file",
            "save-file",
            "delete-model-file",
            "add-resource",
            "save-resource",
            "delete-resource",
        ):
            with self.subTest(control=control):
                self.assertIn(f'setWriteControlState("{control}"', app_js)

    def test_automation_status_is_visible(self) -> None:
        collector = collect_index()
        app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        for element_id in ("signal-automation", "signal-automation-detail", "config-automation"):
            with self.subTest(element_id=element_id):
                self.assertIn(element_id, collector.ids)
        self.assertIn("function automationStatusText", app_js)
        self.assertIn("function automationDetailText", app_js)
        self.assertIn("automation.interval_minutes", app_js)

    def test_model_sync_status_is_visible_in_setup_checks(self) -> None:
        app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("status.model_sync", app_js)
        self.assertIn("function modelSyncLevel", app_js)
        self.assertIn("function modelSyncDetail", app_js)
        for status_key in ("conflict", "read_error", "local_only", "remote_inactive", "remote_only"):
            with self.subTest(status_key=status_key):
                self.assertIn(f'"{status_key}"', app_js)
        for message_key in (
            "setup.modelSyncReady",
            "setup.modelSyncReview",
            "setup.modelSyncConflict",
            "setup.modelSyncMissing",
            "setup.modelSyncDetail",
        ):
            with self.subTest(message_key=message_key):
                self.assertIn(f't("{message_key}"', app_js)


if __name__ == "__main__":
    unittest.main()
