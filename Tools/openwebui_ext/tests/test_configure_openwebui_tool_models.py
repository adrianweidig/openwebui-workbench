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


if __name__ == "__main__":
    unittest.main()
