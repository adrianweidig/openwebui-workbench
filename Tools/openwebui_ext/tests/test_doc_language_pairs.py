from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAIR_SCRIPT = ROOT / "scripts" / "check_doc_language_pairs.py"


def load_pair_module():
    spec = importlib.util.spec_from_file_location("test_check_doc_language_pairs_module", PAIR_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DocLanguagePairTests(unittest.TestCase):
    def test_expected_repository_language_pairs_are_present(self) -> None:
        module = load_pair_module()

        self.assertEqual(module.pair_issues(ROOT), [])

    def test_missing_pair_is_reported_by_path_only(self) -> None:
        module = load_pair_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("# Demo\n\n🌐 Sprachen: [Deutsch](README.md) | [English](README.en.md)\n", encoding="utf-8")
            previous_pairs = module.LANGUAGE_PAIRS
            module.LANGUAGE_PAIRS = [("README.md", "README.en.md")]
            try:
                issues = module.pair_issues(root)
            finally:
                module.LANGUAGE_PAIRS = previous_pairs

        self.assertEqual(issues, ["README.en.md fehlt"])


if __name__ == "__main__":
    unittest.main()
