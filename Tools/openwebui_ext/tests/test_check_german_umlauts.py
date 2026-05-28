from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
CHECK_SCRIPT = ROOT / "scripts" / "check_german_umlauts.py"


def load_check_module():
    spec = importlib.util.spec_from_file_location("test_check_german_umlauts_module", CHECK_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CheckGermanUmlautsTests(unittest.TestCase):
    def test_tracked_files_falls_back_when_git_is_missing(self) -> None:
        module = load_check_module()

        with patch.object(module.shutil, "which", return_value=None):
            files = module.tracked_files()

        rel_files = {path.relative_to(ROOT).as_posix() for path in files}
        self.assertIn("README.md", rel_files)
        self.assertIn("scripts/check_german_umlauts.py", rel_files)
        self.assertFalse(any(path.startswith("Artefakte/") for path in rel_files))


if __name__ == "__main__":
    unittest.main()
