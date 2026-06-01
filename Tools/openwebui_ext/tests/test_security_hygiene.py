from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SECURITY_SCRIPT = ROOT / "scripts" / "check_security_hygiene.py"


def load_security_module():
    spec = importlib.util.spec_from_file_location("test_check_security_hygiene_module", SECURITY_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SecurityHygieneTests(unittest.TestCase):
    def test_secret_findings_do_not_include_secret_value(self) -> None:
        module = load_security_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            secret_file = root / "config.yaml"
            secret_name = "OPENWEBUI_ADMIN_" + "TOKEN"
            secret_value = "abCD1234_" + "xyZ9876-secret"
            secret_file.write_text(f"{secret_name}: {secret_value}\n", encoding="utf-8")

            checked, findings = module.scan_paths([secret_file], root)

        self.assertEqual(checked, 1)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].path.as_posix(), "config.yaml")
        self.assertNotIn("abCD1234", findings[0].kind)

    def test_placeholder_values_are_ignored(self) -> None:
        module = load_security_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = root / "config.yaml"
            config.write_text('admin_token: "PASTE_OPENWEBUI_ADMIN_API_TOKEN_HERE"\n', encoding="utf-8")

            _checked, findings = module.scan_paths([config], root)

        self.assertEqual(findings, [])

    def test_powershell_helper_assignment_is_not_a_secret_value(self) -> None:
        module = load_security_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script = root / "configure.ps1"
            script.write_text(
                '$verifiedSecretHostFile = Test-WorkbenchHostFile -Name "WORKBENCH_AUTH_PASSWORD_HOST_FILE"\n',
                encoding="utf-8",
            )

            _checked, findings = module.scan_paths([script], root)

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
