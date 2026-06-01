from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import check_workbench_setup


class _FakeHttpResponse:
    def __init__(self, status: int = 200) -> None:
        self.status = status

    def __enter__(self) -> "_FakeHttpResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        return False


class CheckWorkbenchSetupTests(unittest.TestCase):
    def _write_minimal_files(self, root: Path) -> tuple[Path, Path, Path]:
        template = root / "workbench.env.example"
        env_file = root / ".env"
        compose_file = root / "docker-compose.workbench.yml"
        template.write_text(
            "WEBUI_SECRET_KEY=\nWORKBENCH_AUTH_PASSWORD=\nWORKBENCH_AUTH_PASSWORD_FILE=\nWORKBENCH_LOCALE=de\n",
            encoding="utf-8",
        )
        compose_file.write_text("services:\n  workbench:\n    image: local/workbench:test\n", encoding="utf-8")
        return template, env_file, compose_file

    def test_missing_env_and_docker_are_warnings_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Env template"], "ok")
            self.assertEqual(levels["Local .env"], "warn")
            self.assertEqual(levels["Docker CLI"], "warn")
            self.assertEqual(check_workbench_setup.summarize(results), "warnings")

    def test_blank_required_env_value_fails_without_printing_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            required_secret_key = "WEBUI" + "_SECRET" + "_KEY"
            sentinel = "DO_NOT_PRINT_VALUE"
            env_file.write_text(f"{required_secret_key}={sentinel}\nWORKBENCH_AUTH_PASSWORD=\n", encoding="utf-8")

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            self.assertEqual(check_workbench_setup.summarize(results), "failed")
            self.assertIn("WORKBENCH_AUTH_PASSWORD", rendered)
            self.assertNotIn(sentinel, rendered)

    def test_missing_docker_can_be_required_for_admin_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                require_docker=True,
                lookup_docker=False,
            )

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Local .env"], "ok")
            self.assertEqual(levels["Docker CLI"], "fail")
            self.assertEqual(check_workbench_setup.summarize(results), "failed")

    def test_missing_windows_docker_mentions_wsl_when_available(self) -> None:
        with (
            patch.object(check_workbench_setup.os, "name", "nt"),
            patch.object(check_workbench_setup.shutil, "which", return_value="C:\\Windows\\System32\\wsl.exe"),
        ):
            result = check_workbench_setup.check_docker(None, require_docker=False)

        self.assertEqual(result.level, "warn")
        self.assertIn("wsl.exe is available", result.detail)
        self.assertIn("WSL", result.detail)

    def test_custom_docker_command_is_reported_without_path_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")

            with patch.object(check_workbench_setup.subprocess, "run") as run:
                run.return_value = SimpleNamespace(returncode=0, stdout="Docker Compose version v2.0.0", stderr="")
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    docker_command=["wsl.exe", "-d", "Debian", "--", "docker"],
                    lookup_docker=False,
                )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Docker CLI"], "ok")
            self.assertIn("wsl.exe -d Debian -- docker", rendered)
            self.assertIn("compose version check passed", rendered)

    def test_custom_wsl_docker_command_reports_disabled_wsl_service(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")

            disabled_wsl = (
                "Der angegebene Dienst kann nicht gestartet werden. "
                "Er ist deaktiviert oder nicht mit aktivierten Geräten verbunden. "
                "Fehlercode: Wsl/0x80070422"
            )
            with patch.object(check_workbench_setup.subprocess, "run") as run:
                run.return_value = SimpleNamespace(returncode=1, stdout="", stderr=disabled_wsl)
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    docker_command=["wsl.exe", "-d", "Debian", "--", "docker"],
                    require_docker=True,
                    lookup_docker=False,
                )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Docker CLI"], "fail")
            self.assertIn("disabled service", rendered)
            self.assertIn("WSLService", rendered)
            self.assertEqual(check_workbench_setup.summarize(results), "failed")

    def test_compose_config_is_skipped_when_docker_preflight_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")

            with patch.object(check_workbench_setup.subprocess, "run") as run:
                run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="Fehlercode: Wsl/0x80070422")
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    docker_command=["wsl.exe", "-d", "Debian", "--", "docker"],
                    require_docker=True,
                    run_compose=True,
                    lookup_docker=False,
                )
            rendered = check_workbench_setup.render_results(results)

            self.assertEqual(run.call_count, 1)
            self.assertIn("Docker CLI preflight failed", rendered)
            self.assertIn("Compose config", rendered)
            self.assertEqual(check_workbench_setup.summarize(results), "failed")

    def test_compose_config_is_skipped_when_compose_file_preflight_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            missing_override = Path(temp_dir) / "missing-override.yml"
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")

            with patch.object(check_workbench_setup.subprocess, "run") as run:
                run.return_value = SimpleNamespace(returncode=0, stdout="Docker Compose version v2.0.0", stderr="")
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    compose_overrides=[missing_override],
                    docker_command=["custom-docker"],
                    require_docker=True,
                    run_compose=True,
                    lookup_docker=False,
                )
            rendered = check_workbench_setup.render_results(results)

            self.assertEqual(run.call_count, 1)
            self.assertIn("Compose override", rendered)
            self.assertIn("compose files failed preflight", rendered)
            self.assertEqual(check_workbench_setup.summarize(results), "failed")

    def test_compose_config_is_skipped_when_required_compose_variables_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            override = Path(temp_dir) / "docker-compose.secret.yml"
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")
            override.write_text(
                "services:\n"
                "  workbench:\n"
                "    volumes:\n"
                "      - ${WORKBENCH_AUTH_PASSWORD_HOST_FILE:?Set password file}:/run/secrets/workbench-auth-password:ro\n",
                encoding="utf-8",
            )

            with patch.object(check_workbench_setup.subprocess, "run") as run:
                run.return_value = SimpleNamespace(returncode=0, stdout="Docker Compose version v2.0.0", stderr="")
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    compose_overrides=[override],
                    docker_command=["custom-docker"],
                    require_docker=True,
                    run_compose=True,
                    lookup_docker=False,
                )
            rendered = check_workbench_setup.render_results(results)

            self.assertEqual(run.call_count, 1)
            self.assertIn("Required compose variable(s) missing: WORKBENCH_AUTH_PASSWORD_HOST_FILE", rendered)
            self.assertIn("required compose variables are missing", rendered)
            self.assertEqual(check_workbench_setup.summarize(results), "failed")

    def test_compose_config_uses_custom_docker_command_and_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory(dir=check_workbench_setup.ROOT) as temp_dir:
            root = Path(temp_dir)
            env_file = root / ".env"
            compose_file = root / "docker-compose.yml"
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")
            compose_file.write_text("services: {}\n", encoding="utf-8")

            with patch.object(check_workbench_setup.subprocess, "run") as run:
                run.return_value = SimpleNamespace(returncode=0)
                result = check_workbench_setup.run_compose_config(
                    ["wsl.exe", "-d", "Debian", "--", "docker"],
                    compose_file,
                    env_file,
                )

            command = run.call_args.args[0]
            self.assertEqual(result.level, "ok")
            self.assertEqual(command[:5], ["wsl.exe", "-d", "Debian", "--", "docker"])
            self.assertIn("--env-file", command)
            self.assertIn("-f", command)
            self.assertFalse(any(str(check_workbench_setup.ROOT) in part for part in command))

    def test_compose_config_accepts_multiple_override_files(self) -> None:
        with tempfile.TemporaryDirectory(dir=check_workbench_setup.ROOT) as temp_dir:
            root = Path(temp_dir)
            env_file = root / ".env"
            compose_file = root / "docker-compose.yml"
            password_override = root / "docker-compose.password.yml"
            token_override = root / "docker-compose.token.yml"
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")
            compose_file.write_text("services:\n  workbench:\n    image: local/workbench:test\n", encoding="utf-8")
            password_override.write_text("services:\n  workbench:\n    environment:\n      A: B\n", encoding="utf-8")
            token_override.write_text("services:\n  workbench:\n    environment:\n      C: D\n", encoding="utf-8")

            with patch.object(check_workbench_setup.subprocess, "run") as run:
                run.return_value = SimpleNamespace(returncode=0)
                results = check_workbench_setup.evaluate_setup(
                    check_workbench_setup.DEFAULT_TEMPLATE,
                    env_file,
                    compose_file,
                    compose_overrides=[password_override, token_override],
                    run_compose=True,
                    docker_command=["custom-docker"],
                    lookup_docker=False,
                )

            command = run.call_args.args[0]
            f_positions = [index for index, part in enumerate(command) if part == "-f"]
            rendered = check_workbench_setup.render_results(results)
            self.assertEqual(len(f_positions), 3)
            self.assertIn("docker-compose.password.yml", command[f_positions[1] + 1])
            self.assertIn("docker-compose.token.yml", command[f_positions[2] + 1])
            self.assertIn("2 override file(s)", rendered)
            self.assertEqual(check_workbench_setup.summarize(results), "ready")

    def test_default_ports_are_valid_when_port_values_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text("WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n", encoding="utf-8")

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )

            levels = {result.title: result.level for result in results}
            rendered = check_workbench_setup.render_results(results)
            self.assertEqual(levels["Port config"], "ok")
            self.assertIn("OPENWEBUI_PORT=3000", rendered)
            self.assertIn("WORKBENCH_PORT=8088", rendered)
            self.assertEqual(levels["OpenWebUI URLs"], "ok")
            self.assertIn("OPENWEBUI_BASE_URL=http://openwebui:8080", rendered)
            self.assertIn("OPENWEBUI_PUBLIC_URL=http://localhost:3000", rendered)
            self.assertEqual(levels["Boolean config"], "ok")
            self.assertIn("OPENWEBUI_TLS_VERIFY=true", rendered)
            self.assertEqual(levels["Numeric config"], "ok")
            self.assertIn("WORKBENCH_COMMAND_TIMEOUT_SECONDS=300", rendered)
            self.assertIn("WORKBENCH_AUTOMATION_INTERVAL_MINUTES=30", rendered)
            self.assertEqual(levels["Automation config"], "ok")
            self.assertIn("WORKBENCH_AUTOMATION_ACTIONS=check", rendered)

    def test_invalid_port_value_fails_without_printing_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            sentinel = "DO_NOT_PRINT_VALUE"
            env_file.write_text(
                f"WEBUI_SECRET_KEY={sentinel}\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_PORT=abc\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Port config"], "fail")
            self.assertIn("WORKBENCH_PORT", rendered)
            self.assertNotIn(sentinel, rendered)

    def test_duplicate_service_ports_fail_before_compose_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nOPENWEBUI_PORT=8088\nWORKBENCH_PORT=8088\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )

            levels = {result.title: result.level for result in results}
            rendered = check_workbench_setup.render_results(results)
            self.assertEqual(levels["Port config"], "fail")
            self.assertIn("both resolve to 8088", rendered)

    def test_invalid_openwebui_url_fails_without_printing_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            sentinel = "DO_NOT_PRINT_VALUE"
            env_file.write_text(
                f"WEBUI_SECRET_KEY={sentinel}\nWORKBENCH_AUTH_PASSWORD=set\nOPENWEBUI_BASE_URL=localhost:3000\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["OpenWebUI URLs"], "fail")
            self.assertIn("OPENWEBUI_BASE_URL", rendered)
            self.assertNotIn(sentinel, rendered)

    def test_openwebui_urls_reject_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nOPENWEBUI_PUBLIC_URL=https://user:secret@openwebui.local\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["OpenWebUI URLs"], "fail")
            self.assertIn("must not include credentials", rendered)
            self.assertNotIn("secret", rendered)

    def test_optional_portainer_url_is_validated_without_runtime_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "PORTAINER_URL=https://portainer.local:9443\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Optional service URLs"], "ok")
            self.assertIn("PORTAINER_URL=https://portainer.local:9443", rendered)

    def test_optional_shared_target_urls_are_validated_without_runtime_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "RAGFLOW_BASE_URL=http://ragflow:9380\n"
                "SEAFILE_BASE_URL=http://seafile\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Optional service URLs"], "ok")
            self.assertIn("RAGFLOW_BASE_URL=http://ragflow:9380", rendered)
            self.assertIn("SEAFILE_BASE_URL=http://seafile", rendered)

    def test_optional_portainer_url_rejects_credentials_without_printing_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "PORTAINER_URL=https://admin:secret@portainer.local\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Optional service URLs"], "fail")
            self.assertIn("PORTAINER_URL must not include credentials", rendered)
            self.assertNotIn("secret", rendered)

    def test_invalid_boolean_value_fails_before_runtime_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nOPENWEBUI_TLS_VERIFY=maybe\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Boolean config"], "fail")
            self.assertIn("OPENWEBUI_TLS_VERIFY", rendered)

    def test_boolean_variants_are_accepted_and_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nOPENWEBUI_TLS_VERIFY=off\nWORKBENCH_ALLOW_WRITE=YES\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Boolean config"], "ok")
            self.assertIn("OPENWEBUI_TLS_VERIFY=false", rendered)
            self.assertIn("WORKBENCH_ALLOW_WRITE=true", rendered)

    def test_invalid_numeric_runtime_value_fails_before_dashboard_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_COMMAND_TIMEOUT_SECONDS=abc\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Numeric config"], "fail")
            self.assertIn("WORKBENCH_COMMAND_TIMEOUT_SECONDS", rendered)

    def test_positive_numeric_runtime_values_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "WORKBENCH_COMMAND_TIMEOUT_SECONDS=120\n"
                "WORKBENCH_IMPORT_TIMEOUT_SECONDS=240\n"
                "WORKBENCH_IMPORT_HTTP_TIMEOUT_SECONDS=60\n"
                "WORKBENCH_MAX_BODY_BYTES=2048\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Numeric config"], "ok")
            self.assertIn("WORKBENCH_COMMAND_TIMEOUT_SECONDS=120", rendered)
            self.assertIn("WORKBENCH_MAX_BODY_BYTES=2048", rendered)

    def test_invalid_automation_interval_fails_before_dashboard_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_AUTOMATION_INTERVAL_MINUTES=1\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Numeric config"], "fail")
            self.assertIn("WORKBENCH_AUTOMATION_INTERVAL_MINUTES", rendered)

    def test_invalid_automation_action_fails_before_dashboard_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_AUTOMATION_ACTIONS=check,delete-all\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Automation config"], "fail")
            self.assertIn("delete-all", rendered)

    def test_missing_enterprise_ca_host_file_fails_before_compose_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            missing_ca = Path(temp_dir) / "missing-ca.pem"
            env_file.write_text(
                f"WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_ENTERPRISE_CA_HOST_FILE={missing_ca}\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "fail")
            self.assertIn("WORKBENCH_ENTERPRISE_CA_HOST_FILE", rendered)

    def test_missing_enterprise_ca_host_file_can_warn_for_portainer_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            missing_ca = Path(temp_dir) / "docker-host-only-ca.pem"
            env_file.write_text(
                f"WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_ENTERPRISE_CA_HOST_FILE={missing_ca}\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
                allow_unverified_root_ca_path=True,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "warn")
            self.assertIn("Docker/Portainer host path", rendered)
            self.assertIn("Verify the PEM certificate", rendered)

    def test_enterprise_ca_host_file_rejects_private_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            ca_file = Path(temp_dir) / "root-ca.pem"
            ca_file.write_text("-----BEGIN PRIVATE KEY-----\nnot-a-key\n-----END PRIVATE KEY-----\n", encoding="utf-8")
            env_file.write_text(
                f"WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_ENTERPRISE_CA_HOST_FILE={ca_file}\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "fail")
            self.assertIn("certificates only", rendered)

    def test_enterprise_ca_host_file_still_rejects_private_keys_with_portainer_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            ca_file = Path(temp_dir) / "root-ca.pem"
            ca_file.write_text("-----BEGIN PRIVATE KEY-----\nnot-a-key\n-----END PRIVATE KEY-----\n", encoding="utf-8")
            env_file.write_text(
                f"WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_ENTERPRISE_CA_HOST_FILE={ca_file}\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
                allow_unverified_root_ca_path=True,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "fail")
            self.assertIn("certificates only", rendered)

    def test_enterprise_ca_host_file_accepts_pem_certificate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            ca_file = Path(temp_dir) / "root-ca.pem"
            ca_file.write_text("-----BEGIN CERTIFICATE-----\nnot-a-real-cert\n-----END CERTIFICATE-----\n", encoding="utf-8")
            env_file.write_text(
                f"WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\nWORKBENCH_ENTERPRISE_CA_HOST_FILE={ca_file}\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "ok")

    def test_missing_container_only_file_references_are_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            sentinel = "DO_NOT_PRINT_VALUE"
            env_file.write_text(
                f"WEBUI_SECRET_KEY={sentinel}\nWORKBENCH_AUTH_PASSWORD=set\n"
                "WORKBENCH_AUTH_PASSWORD_FILE=/run/secrets/workbench-password\n"
                "OPENWEBUI_ADMIN_TOKEN_FILE=/run/secrets/openwebui-token\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "warn")
            self.assertIn("container-only secret or CA paths", rendered)
            self.assertNotIn(sentinel, rendered)

    def test_admin_token_host_file_is_validated_without_reading_secret_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            token_file = Path(temp_dir) / "openwebui-admin-token.txt"
            token_file.write_text("DO_NOT_PRINT_TOKEN_VALUE\n", encoding="utf-8")
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                f"OPENWEBUI_ADMIN_TOKEN_HOST_FILE={token_file}\n"
                "OPENWEBUI_ADMIN_TOKEN_FILE=/run/secrets/openwebui-admin-token\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "ok")
            self.assertNotIn("DO_NOT_PRINT_TOKEN_VALUE", rendered)

    def test_workbench_password_host_file_is_validated_without_reading_secret_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            password_file = Path(temp_dir) / "workbench-password.txt"
            password_file.write_text("DO_NOT_PRINT_PASSWORD_VALUE\n", encoding="utf-8")
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=\n"
                f"WORKBENCH_AUTH_PASSWORD_HOST_FILE={password_file}\n"
                "WORKBENCH_AUTH_PASSWORD_FILE=/run/secrets/workbench-auth-password\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Local .env"], "ok")
            self.assertEqual(levels["File references"], "ok")
            self.assertNotIn("DO_NOT_PRINT_PASSWORD_VALUE", rendered)

    def test_missing_workbench_password_host_file_can_warn_for_portainer_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            missing_password_file = Path(temp_dir) / "docker-host-only-workbench-password.txt"
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=\n"
                f"WORKBENCH_AUTH_PASSWORD_HOST_FILE={missing_password_file}\n"
                "WORKBENCH_AUTH_PASSWORD_FILE=/run/secrets/workbench-auth-password\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
                allow_unverified_secret_file_path=True,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Local .env"], "ok")
            self.assertEqual(levels["File references"], "warn")
            self.assertIn("WORKBENCH_AUTH_PASSWORD_HOST_FILE", rendered)
            self.assertIn("Docker/Portainer host path", rendered)
            self.assertIn("Verify the password file", rendered)

    def test_workbench_password_host_file_requires_container_mount_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            password_file = Path(temp_dir) / "workbench-password.txt"
            password_file.write_text("DO_NOT_PRINT_PASSWORD_VALUE\n", encoding="utf-8")
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=\n"
                f"WORKBENCH_AUTH_PASSWORD_HOST_FILE={password_file}\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Local .env"], "ok")
            self.assertEqual(levels["File references"], "fail")
            self.assertIn("WORKBENCH_AUTH_PASSWORD_FILE is empty", rendered)
            self.assertNotIn("DO_NOT_PRINT_PASSWORD_VALUE", rendered)

    def test_missing_admin_token_host_file_fails_without_portainer_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            missing_token_file = Path(temp_dir) / "docker-host-only-token.txt"
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                f"OPENWEBUI_ADMIN_TOKEN_HOST_FILE={missing_token_file}\n"
                "OPENWEBUI_ADMIN_TOKEN_FILE=/run/secrets/openwebui-admin-token\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "fail")
            self.assertIn("OPENWEBUI_ADMIN_TOKEN_HOST_FILE", rendered)

    def test_missing_admin_token_host_file_can_warn_for_portainer_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            missing_token_file = Path(temp_dir) / "docker-host-only-token.txt"
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                f"OPENWEBUI_ADMIN_TOKEN_HOST_FILE={missing_token_file}\n"
                "OPENWEBUI_ADMIN_TOKEN_FILE=/run/secrets/openwebui-admin-token\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
                allow_unverified_secret_file_path=True,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "warn")
            self.assertIn("Docker/Portainer host path", rendered)
            self.assertIn("Verify the token file", rendered)

    def test_admin_token_host_file_requires_container_mount_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            token_file = Path(temp_dir) / "openwebui-admin-token.txt"
            token_file.write_text("DO_NOT_PRINT_TOKEN_VALUE\n", encoding="utf-8")
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                f"OPENWEBUI_ADMIN_TOKEN_HOST_FILE={token_file}\n",
                encoding="utf-8",
            )

            results = check_workbench_setup.evaluate_setup(
                template,
                env_file,
                compose_file,
                lookup_docker=False,
            )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["File references"], "fail")
            self.assertIn("OPENWEBUI_ADMIN_TOKEN_FILE is empty", rendered)
            self.assertNotIn("DO_NOT_PRINT_TOKEN_VALUE", rendered)

    def test_runtime_probe_checks_openwebui_and_portainer_without_token(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "OPENWEBUI_PUBLIC_URL=http://localhost:3000\n",
                encoding="utf-8",
            )
            auth_required = check_workbench_setup.HTTPError(
                "https://portainer.local/api/status",
                401,
                "Unauthorized",
                hdrs=None,
                fp=None,
            )

            with patch.object(check_workbench_setup, "urlopen") as open_url:
                open_url.side_effect = [_FakeHttpResponse(200), auth_required]
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    lookup_docker=False,
                    probe_runtime=True,
                    portainer_url="https://portainer.local",
                )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Runtime OpenWebUI"], "ok")
            self.assertEqual(levels["Runtime Portainer"], "ok")
            self.assertIn("requires authentication", rendered)
            self.assertEqual(open_url.call_count, 2)

    def test_runtime_probe_uses_portainer_url_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "OPENWEBUI_PUBLIC_URL=http://localhost:3000\n"
                "PORTAINER_URL=https://portainer.local\n",
                encoding="utf-8",
            )

            with patch.object(check_workbench_setup, "urlopen") as open_url:
                open_url.return_value = _FakeHttpResponse(200)
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    lookup_docker=False,
                    probe_runtime=True,
                )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Runtime OpenWebUI"], "ok")
            self.assertEqual(levels["Runtime Portainer"], "ok")
            self.assertIn("https://portainer.local/api/status", rendered)
            self.assertEqual(open_url.call_count, 2)

    def test_cli_portainer_url_overrides_env_file_for_runtime_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "OPENWEBUI_PUBLIC_URL=http://localhost:3000\n"
                "PORTAINER_URL=https://portainer-from-env.local\n",
                encoding="utf-8",
            )

            with patch.object(check_workbench_setup, "urlopen") as open_url:
                open_url.return_value = _FakeHttpResponse(200)
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    lookup_docker=False,
                    probe_runtime=True,
                    portainer_url="https://portainer-from-cli.local",
                )
            rendered = check_workbench_setup.render_results(results)

            self.assertIn("https://portainer-from-cli.local/api/status", rendered)
            self.assertIn("PORTAINER_URL=https://portainer-from-env.local", rendered)

    def test_runtime_probe_failure_can_be_required_for_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "OPENWEBUI_PUBLIC_URL=http://localhost:3000\n",
                encoding="utf-8",
            )

            with patch.object(check_workbench_setup, "urlopen") as open_url:
                open_url.side_effect = check_workbench_setup.URLError("connection refused")
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    lookup_docker=False,
                    probe_runtime=True,
                    require_runtime=True,
                    portainer_url="https://portainer.local",
                )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Runtime OpenWebUI"], "fail")
            self.assertEqual(levels["Runtime Portainer"], "fail")
            self.assertIn("connection refused", rendered)
            self.assertEqual(check_workbench_setup.summarize(results), "failed")

    def test_runtime_probe_rejects_portainer_url_credentials_without_printing_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template, env_file, compose_file = self._write_minimal_files(Path(temp_dir))
            env_file.write_text(
                "WEBUI_SECRET_KEY=set\nWORKBENCH_AUTH_PASSWORD=set\n"
                "OPENWEBUI_PUBLIC_URL=http://localhost:3000\n",
                encoding="utf-8",
            )

            with patch.object(check_workbench_setup, "urlopen") as open_url:
                open_url.return_value = _FakeHttpResponse(200)
                results = check_workbench_setup.evaluate_setup(
                    template,
                    env_file,
                    compose_file,
                    lookup_docker=False,
                    probe_runtime=True,
                    portainer_url="https://admin:secret@portainer.local",
                )
            rendered = check_workbench_setup.render_results(results)

            levels = {result.title: result.level for result in results}
            self.assertEqual(levels["Runtime OpenWebUI"], "ok")
            self.assertEqual(levels["Runtime Portainer"], "warn")
            self.assertIn("PORTAINER_URL must not include credentials", rendered)
            self.assertNotIn("secret", rendered)


if __name__ == "__main__":
    unittest.main()
