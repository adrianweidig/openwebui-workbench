from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
VERIFY_SCRIPT = ROOT / "scripts" / "verify_openwebui_workspace.py"


def load_verify_module():
    spec = importlib.util.spec_from_file_location("test_verify_openwebui_workspace_module", VERIFY_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyOpenWebUIWorkspaceTests(unittest.TestCase):
    def test_default_verify_steps_are_non_mutating(self) -> None:
        module = load_verify_module()
        args = module.parse_args([])
        commands = [" ".join(step.command) for step in module.build_command_steps(args)]
        combined = "\n".join(commands)

        self.assertIn("compileall", combined)
        self.assertIn("check_doc_language_pairs.py", combined)
        self.assertIn("check_security_hygiene.py", combined)
        self.assertIn("validate_openwebui_extensions.py", combined)
        self.assertIn("configure_openwebui_tool_models.py", combined)
        self.assertIn("--check", combined)
        self.assertIn("import_openwebui_workspace.py", combined)
        self.assertIn("--dry-run", combined)
        self.assertIn("unittest discover", combined)
        self.assertNotIn("--write", combined)
        self.assertNotIn("--rebuild-zips", combined)
        self.assertNotIn("docker compose", combined)

    def test_docker_compose_step_is_opt_in(self) -> None:
        module = load_verify_module()
        args = module.parse_args(["--include-docker-compose"])
        steps = module.build_command_steps(args)
        commands = [" ".join(step.command) for step in steps]

        self.assertTrue(any("docker compose" in command for command in commands))
        self.assertTrue(any("docker-compose.enterprise-ca.yml" in command for command in commands))
        enterprise_step = next(step for step in steps if "enterprise CA" in step.label)
        self.assertEqual(enterprise_step.env["WORKBENCH_AUTH_PASSWORD"], "verify-only-placeholder")
        self.assertEqual(enterprise_step.env["WORKBENCH_ENTERPRISE_CA_HOST_FILE"], "/tmp/workbench-verify-ca.pem")

    def test_skipped_windows_docker_step_mentions_wsl_when_available(self) -> None:
        module = load_verify_module()
        step = module.CommandStep("Docker compose config", ["docker", "compose", "config"])

        def fake_which(name: str) -> str | None:
            if name == "wsl.exe":
                return "C:\\Windows\\System32\\wsl.exe"
            return None

        with patch.object(module.os, "name", "nt"), patch.object(module.shutil, "which", side_effect=fake_which):
            result = module.run_command_step(step)

        self.assertEqual(result.status, "Übersprungen")
        self.assertIn("wsl.exe ist verfügbar", result.detail)

    def test_json_validation_ignores_git_directory(self) -> None:
        module = load_verify_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "valid.json").write_text('{"ok": true}', encoding="utf-8")
            git_dir = root / ".git"
            git_dir.mkdir()
            (git_dir / "invalid.json").write_text("{broken", encoding="utf-8")

            result = module.validate_json_files(root)

        self.assertEqual(result.status, "Erfolgreich")
        self.assertIn("1 JSON-Dateien", result.detail)


if __name__ == "__main__":
    unittest.main()
