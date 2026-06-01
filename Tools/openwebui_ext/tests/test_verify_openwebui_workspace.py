from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace


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
        self.assertTrue(any("docker-compose.shared-targets.yml" in command for command in commands))
        self.assertTrue(any("docker-compose.enterprise-ca.yml" in command for command in commands))
        self.assertTrue(any("docker-compose.workbench-password-file.yml" in command for command in commands))
        self.assertTrue(any("docker-compose.openwebui-admin-token-file.yml" in command for command in commands))
        shared_step = next(step for step in steps if "shared-targets" in step.label)
        self.assertEqual(shared_step.env["WORKBENCH_SHARED_DOCKER_NETWORK"], "ki_infra_seu_test")
        self.assertEqual(shared_step.env["OPENWEBUI_BASE_URL"], "http://openwebui:8080")
        self.assertEqual(shared_step.env["RAGFLOW_BASE_URL"], "http://ragflow:9380")
        self.assertEqual(shared_step.env["SEAFILE_BASE_URL"], "http://seafile")
        self.assertTrue(shared_step.requires_docker)
        combined_secret_step = next(step for step in steps if "combined secret-file" in step.label)
        combined_secret_command = " ".join(combined_secret_step.command)
        self.assertIn("docker-compose.workbench-password-file.yml", combined_secret_command)
        self.assertIn("docker-compose.openwebui-admin-token-file.yml", combined_secret_command)
        self.assertEqual(combined_secret_step.env["WORKBENCH_AUTH_PASSWORD_HOST_FILE"], "/tmp/workbench-auth-password.txt")
        self.assertEqual(combined_secret_step.env["OPENWEBUI_ADMIN_TOKEN_HOST_FILE"], "/tmp/openwebui-admin-token.txt")
        self.assertTrue(combined_secret_step.requires_docker)
        enterprise_step = next(step for step in steps if "enterprise CA" in step.label)
        self.assertEqual(enterprise_step.env["WORKBENCH_AUTH_PASSWORD"], "verify-only-placeholder")
        self.assertEqual(enterprise_step.env["WORKBENCH_ENTERPRISE_CA_HOST_FILE"], "/tmp/workbench-verify-ca.pem")
        self.assertTrue(enterprise_step.requires_docker)
        password_file_step = next(step for step in steps if "password-file" in step.label)
        self.assertEqual(password_file_step.env["WORKBENCH_AUTH_PASSWORD_HOST_FILE"], "/tmp/workbench-auth-password.txt")
        self.assertEqual(password_file_step.env["WORKBENCH_AUTH_PASSWORD_FILE"], "/run/secrets/workbench-auth-password")
        token_file_step = next(step for step in steps if "admin-token-file" in step.label)
        self.assertEqual(token_file_step.env["OPENWEBUI_ADMIN_TOKEN_HOST_FILE"], "/tmp/openwebui-admin-token.txt")
        self.assertEqual(token_file_step.env["OPENWEBUI_ADMIN_TOKEN_FILE"], "/run/secrets/openwebui-admin-token")

    def test_docker_compose_steps_accept_custom_docker_command(self) -> None:
        module = load_verify_module()
        args = module.parse_args(["--include-docker-compose", "--docker-command", "wsl.exe -d Debian -- docker"])
        steps = module.build_command_steps(args)
        compose_step = next(step for step in steps if step.label == "Docker compose workbench config")

        self.assertEqual(compose_step.command[:5], ["wsl.exe", "-d", "Debian", "--", "docker"])
        self.assertIn("compose", compose_step.command)

    def test_skipped_windows_docker_step_mentions_wsl_when_available(self) -> None:
        module = load_verify_module()
        step = module.CommandStep("Docker compose config", ["docker", "compose", "config"], requires_docker=True)

        def fake_which(name: str) -> str | None:
            if name == "wsl.exe":
                return "C:\\Windows\\System32\\wsl.exe"
            return None

        with patch.object(module.os, "name", "nt"), patch.object(module.shutil, "which", side_effect=fake_which):
            result = module.run_command_step(step)

        self.assertEqual(result.status, "Übersprungen")
        self.assertIn("wsl.exe ist verfügbar", result.detail)

    def test_wsl_docker_step_reports_disabled_service_without_nul_noise(self) -> None:
        module = load_verify_module()
        step = module.CommandStep(
            "Docker compose config",
            ["wsl.exe", "-d", "Debian", "--", "docker", "compose", "config"],
            requires_docker=True,
        )
        disabled_wsl = (
            "D\x00e\x00r\x00 \x00a\x00n\x00g\x00e\x00g\x00e\x00b\x00e\x00n\x00e\x00 "
            "D\x00i\x00e\x00n\x00s\x00t\x00 \x00i\x00s\x00t\x00 \x00d\x00e\x00a\x00k\x00t\x00i\x00v\x00i\x00e\x00r\x00t\x00. "
            "F\x00e\x00h\x00l\x00e\x00r\x00c\x00o\x00d\x00e\x00:\x00 \x00W\x00s\x00l\x00/\x000\x00x\x008\x000\x000\x007\x000\x004\x002\x002\x00"
        )

        with (
            patch.object(module.shutil, "which", return_value="C:\\Windows\\System32\\wsl.exe"),
            patch.object(module.subprocess, "run") as run,
        ):
            run.return_value = SimpleNamespace(returncode=1, stdout="", stderr=disabled_wsl)
            result = module.run_command_step(step)

        self.assertEqual(result.status, "Fehlgeschlagen")
        self.assertIn("WSLService", result.detail)
        self.assertNotIn("\x00", result.detail)

    def test_wsl_docker_step_injects_compose_env_inside_wsl_command(self) -> None:
        module = load_verify_module()
        step = module.CommandStep(
            "Docker compose config",
            ["wsl.exe", "-d", "Debian", "--", "docker", "compose", "config"],
            env={"WEBUI_SECRET_KEY": "verify-only-placeholder"},
            requires_docker=True,
        )

        with (
            patch.object(module.shutil, "which", return_value="C:\\Windows\\System32\\wsl.exe"),
            patch.object(module.subprocess, "run") as run,
        ):
            run.return_value = SimpleNamespace(returncode=0, stdout="", stderr="")
            result = module.run_command_step(step)

        command = run.call_args.args[0]
        self.assertEqual(result.status, "Erfolgreich")
        self.assertEqual(command[:5], ["wsl.exe", "-d", "Debian", "--", "env"])
        self.assertIn("WEBUI_SECRET_KEY=verify-only-placeholder", command)
        self.assertIn("docker", command)

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
