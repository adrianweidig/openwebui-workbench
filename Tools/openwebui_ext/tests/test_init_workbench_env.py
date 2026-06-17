from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts import init_workbench_env


class InitWorkbenchEnvTests(unittest.TestCase):
    def test_creates_env_with_generated_required_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "workbench.env.example"
            output = root / ".env"
            template.write_text(
                "WORKBENCH_AUTH_PASSWORD=\nWORKBENCH_AUTH_PASSWORD_FILE=\nOPENWEBUI_ADMIN_TOKEN=\nWORKBENCH_LOCALE=en\n",
                encoding="utf-8",
            )

            generated = init_workbench_env.write_env_file(template, output)

            values = init_workbench_env.env_values(output.read_text(encoding="utf-8"))
            self.assertEqual(generated, ["WORKBENCH_AUTH_PASSWORD"])
            self.assertGreaterEqual(len(values["WORKBENCH_AUTH_PASSWORD"]), 24)
            self.assertEqual(values["OPENWEBUI_ADMIN_TOKEN"], "")
            self.assertEqual(values["WORKBENCH_LOCALE"], "en")

    def test_refuses_to_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "workbench.env.example"
            output = root / ".env"
            template.write_text("WORKBENCH_AUTH_PASSWORD=\nWORKBENCH_AUTH_PASSWORD_FILE=\n", encoding="utf-8")
            output.write_text("WORKBENCH_AUTH_PASSWORD=keep\n", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                init_workbench_env.write_env_file(template, output)

            self.assertEqual(output.read_text(encoding="utf-8"), "WORKBENCH_AUTH_PASSWORD=keep\n")

    def test_refuses_template_missing_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "workbench.env.example"
            output = root / ".env"
            template.write_text("WORKBENCH_LOCALE=en\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                init_workbench_env.write_env_file(template, output)

            self.assertFalse(output.exists())

    def test_check_reports_missing_required_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("WORKBENCH_AUTH_PASSWORD=\n", encoding="utf-8")

            self.assertEqual(
                init_workbench_env.missing_required_values(env_file),
                ["WORKBENCH_AUTH_PASSWORD or WORKBENCH_AUTH_PASSWORD_FILE"],
            )

    def test_check_accepts_auth_password_file_alternative(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(
                "WORKBENCH_REQUIRE_AUTH=true\n"
                "WORKBENCH_AUTH_PASSWORD=\n"
                "WORKBENCH_AUTH_PASSWORD_FILE=/run/secrets/workbench-auth-password\n",
                encoding="utf-8",
            )

            self.assertEqual(init_workbench_env.missing_required_values(env_file), [])

    def test_check_allows_disabled_auth_for_local_only_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(
                "WORKBENCH_REQUIRE_AUTH=false\nWORKBENCH_AUTH_PASSWORD=\n",
                encoding="utf-8",
            )

            self.assertEqual(init_workbench_env.missing_required_values(env_file), [])

    def test_cli_reports_existing_file_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "workbench.env.example"
            output = root / ".env"
            template.write_text("WORKBENCH_AUTH_PASSWORD=\nWORKBENCH_AUTH_PASSWORD_FILE=\n", encoding="utf-8")
            output.write_text("WORKBENCH_AUTH_PASSWORD=keep\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = init_workbench_env.main(["--template", str(template), "--output", str(output)])

            self.assertEqual(exit_code, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("initialization failed", stderr.getvalue())
            self.assertIn("already exists", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
