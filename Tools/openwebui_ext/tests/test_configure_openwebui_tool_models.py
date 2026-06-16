from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONFIGURE_SCRIPT = ROOT / "scripts" / "configure_openwebui_tool_models.py"
DIST_ZIP_MANIFEST = ROOT / "scripts" / "dist_zip_manifest.py"


def load_configure_module():
    spec = importlib.util.spec_from_file_location("test_configure_openwebui_tool_models_module", CONFIGURE_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_dist_zip_manifest_module():
    spec = importlib.util.spec_from_file_location("test_dist_zip_manifest_module", DIST_ZIP_MANIFEST)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ConfigureOpenWebUIToolModelsTests(unittest.TestCase):
    def test_zip_drift_issues_accepts_current_archive(self) -> None:
        module = load_dist_zip_manifest_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "src" / "file.txt"
            source.parent.mkdir()
            source.write_text("aktuell", encoding="utf-8")
            target = root / "dist.zip"
            with zipfile.ZipFile(target, "w") as archive:
                archive.writestr("src/file.txt", source.read_bytes())

            issues = module.zip_drift_issues(root, target, [source])

        self.assertEqual(issues, [])

    def test_zip_drift_issues_accepts_lf_archive_for_crlf_text_source(self) -> None:
        module = load_dist_zip_manifest_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "src" / "file.html"
            source.parent.mkdir()
            source.write_bytes(b"<p>zeile eins</p>\r\n<p>zeile zwei</p>\r\n")
            target = root / "dist.zip"
            with zipfile.ZipFile(target, "w") as archive:
                archive.writestr("src/file.html", b"<p>zeile eins</p>\n<p>zeile zwei</p>\n")

            issues = module.zip_drift_issues(root, target, [source])

        self.assertEqual(issues, [])

    def test_zip_drift_issues_reports_stale_content(self) -> None:
        module = load_dist_zip_manifest_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "src" / "file.txt"
            source.parent.mkdir()
            source.write_text("aktuell", encoding="utf-8")
            target = root / "dist.zip"
            with zipfile.ZipFile(target, "w") as archive:
                archive.writestr("src/file.txt", b"alt")

            issues = module.zip_drift_issues(root, target, [source])

        self.assertTrue(any("veralteten Inhalt" in issue for issue in issues))

    def test_zip_drift_issues_reports_entry_order_drift(self) -> None:
        module = load_dist_zip_manifest_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "src" / "a.txt"
            second = root / "src" / "b.txt"
            first.parent.mkdir()
            first.write_text("eins", encoding="utf-8")
            second.write_text("zwei", encoding="utf-8")
            target = root / "dist.zip"
            with zipfile.ZipFile(target, "w") as archive:
                archive.writestr("src/b.txt", b"zwei")
                archive.writestr("src/a.txt", b"eins")

            issues = module.zip_drift_issues(root, target, [first, second])

        self.assertTrue(any("Eintragsreihenfolge" in issue for issue in issues))

    def test_zip_sources_use_platform_stable_order(self) -> None:
        module = load_configure_module()
        readme = ROOT / "Tools" / "jupyter" / "README.md"
        config = ROOT / "Tools" / "jupyter" / "jupyter_config.example.json"

        ordered = module.sorted_archive_paths([readme, config])

        self.assertEqual(ordered, [config, readme])

    def test_configure_model_preserves_model_json_runtime_preferences(self) -> None:
        module = load_configure_module()
        model = {
            "id": "allgemein",
            "name": "Allgemein Custom",
            "base_model_id": "mistral-medium-3.5-128b",
            "meta": {
                "capabilities": {
                    "builtin_tools": False,
                    "vision": False,
                    "file_upload": False,
                    "code_interpreter": False,
                    "status_updates": False,
                    "usage": False,
                },
                "toolIds": [],
                "filterIds": ["custom_filter"],
                "defaultFilterIds": ["custom_filter"],
                "skillIds": ["custom-skill"],
            },
            "params": {
                "temperature": 0.2,
                "top_p": 0.8,
                "stop": ["</stop>"],
                "function_calling": "none",
                "reasoning_effort": "medium",
                "parallel_tool_calls": False,
            },
        }

        tool_records = module.discover_tools()
        offline_tool_ids = [record.id for record in module.offline_default_tool_records(tool_records)]
        all_tool_ids = [record.id for record in tool_records if record.importable]

        configured = module.configure_model(model, offline_tool_ids, ["fallback_filter"], all_tool_ids)

        self.assertEqual(configured["base_model_id"], "mistral-medium-3.5-128b")
        self.assertEqual(configured["params"]["temperature"], 0.2)
        self.assertEqual(configured["params"]["top_p"], 0.8)
        self.assertEqual(configured["params"]["stop"], ["</stop>"])
        self.assertEqual(configured["params"]["function_calling"], "none")
        self.assertEqual(configured["params"]["reasoning_effort"], "medium")
        self.assertFalse(configured["params"]["parallel_tool_calls"])
        self.assertIn("system", configured["params"])
        self.assertEqual(configured["meta"]["toolIds"], [])
        self.assertIn("custom_filter", configured["meta"]["filterIds"])
        self.assertNotIn("fallback_filter", configured["meta"]["filterIds"])
        self.assertEqual(configured["meta"]["skillIds"], ["custom-skill"])
        self.assertFalse(configured["meta"]["capabilities"]["builtin_tools"])
        self.assertFalse(configured["meta"]["capabilities"]["vision"])
        self.assertFalse(configured["meta"]["capabilities"]["code_interpreter"])


if __name__ == "__main__":
    unittest.main()
