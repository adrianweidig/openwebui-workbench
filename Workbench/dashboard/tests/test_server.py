from __future__ import annotations

import base64
import contextlib
import io
import json
import os
import socket
import subprocess
import sys
import threading
import tempfile
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import Workbench.dashboard.server as dashboard_server
from Workbench.dashboard.i18n import detect_locale, normalize_locale, t
from Workbench.dashboard.server import WorkbenchAutomationScheduler, WorkbenchConfig, WorkbenchState, openwebui_ssl_context


class WorkbenchStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        model_dir = self.root / "Modelle" / "einzelmodelle" / "demo-model"
        model_dir.mkdir(parents=True)
        (model_dir / "model.json").write_text(
            json.dumps(
                [
                    {
                        "id": "demo-model",
                        "name": "Demo Model",
                        "base_model_id": "coder",
                        "meta": {
                            "description": "Demo",
                            "defaultLocale": "de",
                            "fallbackLocale": "en",
                            "supportedLocales": ["de", "en"],
                            "tags": [{"name": "test"}],
                            "productI18n": {
                                "de": {
                                    "name": "Demo-Modell",
                                    "description": "Beschreibung mit ä, ö, ü, ß und 日本語.",
                                    "suggestion": "Nutze das Demo-Modell.",
                                    "profile": "i18n/de.md",
                                },
                                "en": {
                                    "name": "Demo Model",
                                    "description": "English demo description.",
                                    "suggestion": "Use the demo model.",
                                    "profile": "i18n/en.md",
                                },
                            },
                        },
                    }
                ]
            ),
            encoding="utf-8",
        )
        (model_dir / "systemprompt.md").write_text("System\n", encoding="utf-8")
        (model_dir / "mainprompt.md").write_text("Main\n", encoding="utf-8")
        (model_dir / "fachwissen.md").write_text("Knowledge\n", encoding="utf-8")
        (model_dir / "Golden_Example.md").write_text("Golden\n", encoding="utf-8")
        (model_dir / "beispielergebnis.md").write_text("Example\n", encoding="utf-8")
        (model_dir / "i18n").mkdir()
        (model_dir / "i18n" / "de.md").write_text("# Demo-Modell\n", encoding="utf-8")
        (model_dir / "i18n" / "en.md").write_text("# Demo Model\n", encoding="utf-8")
        umlaut_dir = self.root / "Modelle" / "einzelmodelle" / "übersetzung-lokalisierung"
        umlaut_dir.mkdir(parents=True)
        (umlaut_dir / "model.json").write_text(
            json.dumps([{"id": "übersetzung-lokalisierung", "name": "Übersetzung Lokalisierung"}]),
            encoding="utf-8",
        )
        (umlaut_dir / "systemprompt.md").write_text("Umlaut\n", encoding="utf-8")
        (self.root / "Tools" / "openwebui_ext" / "tools").mkdir(parents=True)
        (self.root / "Tools" / "openwebui_ext" / "tools" / "demo_tool.py").write_text("# demo\n", encoding="utf-8")
        (self.root / "Tools" / "openwebui_ext" / "filters").mkdir(parents=True)
        (self.root / "Tools" / "openwebui_ext" / "filters" / "demo_filter.py").write_text(
            "class Filter:\n    async def inlet(self, body: dict) -> dict:\n        return body\n",
            encoding="utf-8",
        )
        (self.root / "Tools" / "openwebui_ext" / "skills").mkdir(parents=True)
        (self.root / "Tools" / "openwebui_ext" / "skills" / "demo-skill.md").write_text("# Demo Skill\n", encoding="utf-8")
        (self.root / "Tools" / "openwebui_ext" / "prompts").mkdir(parents=True)
        (self.root / "Tools" / "openwebui_ext" / "prompts" / "demo-prompt.md").write_text(
            "---\ncommand: demo-prompt\nname: Demo Prompt\n---\n\n# Demo Prompt\n",
            encoding="utf-8",
        )
        self.state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="",
                auth_password="",
            )
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_lists_model_packages(self) -> None:
        models = self.state.list_models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["id"], "demo-model")
        self.assertEqual(models[0]["name"], "Demo Model")
        self.assertEqual(models[0]["default_locale"], "de")
        self.assertEqual(models[0]["fallback_locale"], "en")
        self.assertEqual(models[0]["i18n"]["de"]["name"], "Demo-Modell")
        self.assertIn("日本語", models[0]["i18n"]["de"]["description"])
        self.assertIn("i18n/de.md", [item["name"] for item in models[0]["files"]])
        self.assertIn("Golden_Example.md", [item["name"] for item in models[0]["files"]])
        self.assertIn("test", models[0]["tags"])
        self.assertEqual(models[1]["id"], "übersetzung-lokalisierung")

    def test_lists_openwebui_only_models_from_sync_snapshot(self) -> None:
        sync_file = self.root / "Artefakte" / "openwebui_sync" / "status.json"
        sync_file.parent.mkdir(parents=True)
        sync_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-06-01 12:00:00",
                    "counts": {"remote_only": 1},
                    "items": [
                        {
                            "id": "remote-only",
                            "name": "Remote Only",
                            "status": "remote_only",
                            "action": "Review remote model.",
                            "remote_snapshot": "Artefakte/openwebui_sync/remote_models/remote-only.json",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        models = self.state.list_models()
        remote = next(model for model in models if model["id"] == "remote-only")

        self.assertTrue(remote["remote_only"])
        self.assertEqual(remote["source"], "openwebui")
        self.assertEqual(remote["sync_status"], "remote_only")
        self.assertEqual(remote["files"], [])

    def test_reads_and_writes_allowed_markdown(self) -> None:
        before = self.state.read_model_file("demo-model", "systemprompt.md")
        self.assertEqual(before["content"], "System\n")
        after = self.state.write_model_file("demo-model", "systemprompt.md", "Updated\n")
        self.assertEqual(after["content"], "Updated\n")

    def test_reads_and_writes_allowed_example_markdown(self) -> None:
        after = self.state.write_model_file("demo-model", "beispiele/demo.md", "Example note\n")
        self.assertEqual(after["content"], "Example note\n")
        self.assertTrue((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "beispiele" / "demo.md").is_file())

    def test_reads_and_writes_allowed_html_example(self) -> None:
        after = self.state.write_model_file("demo-model", "beispielergebnis.html", "<!doctype html>\n")
        self.assertEqual(after["content"], "<!doctype html>\n")
        self.assertTrue((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "beispielergebnis.html").is_file())

    def test_reads_and_writes_allowed_json_example(self) -> None:
        after = self.state.write_model_file("demo-model", "beispielergebnis.json", "{\"ok\": true}\n")
        self.assertEqual(after["content"], "{\"ok\": true}\n")
        self.assertTrue((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "beispielergebnis.json").is_file())

    def test_reads_and_writes_allowed_golden_example(self) -> None:
        after = self.state.write_model_file("demo-model", "Golden_Example.json", "{\"quality\": \"golden\"}\n")
        self.assertEqual(after["content"], "{\"quality\": \"golden\"}\n")
        self.assertTrue((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "Golden_Example.json").is_file())

    def test_reads_and_writes_allowed_json_file_under_examples(self) -> None:
        after = self.state.write_model_file("demo-model", "beispiele/demo.json", "{\"ok\": true}\n")
        self.assertEqual(after["content"], "{\"ok\": true}\n")
        self.assertTrue((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "beispiele" / "demo.json").is_file())

    def test_reads_and_writes_allowed_generated_example(self) -> None:
        after = self.state.write_model_file("demo-model", "beispiele/generated/demo.md", "Generated example\n")
        self.assertEqual(after["content"], "Generated example\n")
        self.assertTrue(
            (self.root / "Modelle" / "einzelmodelle" / "demo-model" / "beispiele" / "generated" / "demo.md").is_file()
        )

    def test_reads_and_writes_allowed_product_i18n_markdown(self) -> None:
        after = self.state.write_model_file("demo-model", "i18n/de.md", "# Aktualisiertes Profil\n")
        self.assertEqual(after["content"], "# Aktualisiertes Profil\n")
        self.assertTrue((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "i18n" / "de.md").is_file())

    def test_deletes_allowed_model_file(self) -> None:
        self.state.write_model_file("demo-model", "beispiele/delete-me.md", "Delete me\n")
        result = self.state.delete_model_file("demo-model", "beispiele/delete-me.md")
        self.assertTrue(result["deleted"])
        self.assertFalse((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "beispiele" / "delete-me.md").exists())

    def test_rejects_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            self.state.read_model_file("demo-model", "../README.md")
        with self.assertRaises(ValueError):
            self.state.read_model_file("demo-model", "beispiele/../systemprompt.md")
        with self.assertRaises(ValueError):
            self.state.read_model_file("demo-model", "beispiele/generated/bad:name.md")

    def test_rejects_unknown_model_id_shape(self) -> None:
        with self.assertRaises(ValueError):
            self.state.read_model_file("../demo-model", "systemprompt.md")

    def test_write_can_be_disabled(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, allow_write=False))
        with self.assertRaises(PermissionError):
            state.write_model_file("demo-model", "systemprompt.md", "Nope\n")

    def test_read_only_state_blocks_write_actions(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, allow_write=False, locale="de"))

        for action in ("generate", "import-dry-run", "import-openwebui", "pull-openwebui"):
            with self.subTest(action=action), self.assertRaisesRegex(PermissionError, "Schreibzugriff"):
                state.run_action(action)

    def test_read_only_state_allows_check_action(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, allow_write=False, locale="de"))
        completed = SimpleNamespace(returncode=0, stdout="ok\n")

        with patch("Workbench.dashboard.server.subprocess.run", return_value=completed) as run:
            result = state.run_action("check")

        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "check")
        self.assertEqual(result["output"], "ok\n")
        self.assertEqual(run.call_args.kwargs["cwd"], self.root)
        self.assertEqual(run.call_args.kwargs["env"]["WORKBENCH_ALLOW_WRITE"], "true")

    def test_delete_openwebui_models_calls_admin_api(self) -> None:
        with (
            patch.dict(os.environ, {"OPENWEBUI_ADMIN_TOKEN": "secret-token", "OPENWEBUI_ADMIN_TOKEN_FILE": ""}),
            patch.object(self.state, "openwebui_api_request", return_value=True) as request,
        ):
            result = self.state.delete_openwebui_models(["demo-model", "demo-model"])

        self.assertTrue(result["ok"])
        self.assertEqual(result["deleted"], ["demo-model"])
        request.assert_called_once_with(
            "POST",
            "/api/v1/models/model/delete",
            payload={"id": "demo-model"},
            query=None,
        )

    def test_read_only_state_blocks_openwebui_model_delete(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, allow_write=False, locale="de"))

        with self.assertRaisesRegex(PermissionError, "Schreibzugriff"):
            state.delete_openwebui_models(["demo-model"])

    def test_delete_openwebui_resources_calls_admin_api(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake_request(method: str, path: str, **_kwargs: object) -> object:
            calls.append((method, path))
            if path == "/api/v1/prompts/command/demo-prompt":
                return {"id": "prompt-db-id"}
            return True

        with (
            patch.dict(os.environ, {"OPENWEBUI_ADMIN_TOKEN": "secret-token", "OPENWEBUI_ADMIN_TOKEN_FILE": ""}),
            patch.object(self.state, "openwebui_api_request", side_effect=fake_request),
        ):
            result = self.state.delete_openwebui_resources("prompt", ["demo-prompt", "demo-prompt"])

        self.assertTrue(result["ok"])
        self.assertEqual(result["deleted"], ["demo-prompt"])
        self.assertIn(("GET", "/api/v1/prompts/command/demo-prompt"), calls)
        self.assertIn(("DELETE", "/api/v1/prompts/id/prompt-db-id/delete"), calls)

    def test_read_only_state_blocks_openwebui_resource_delete(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, allow_write=False, locale="de"))

        with self.assertRaisesRegex(PermissionError, "Schreibzugriff"):
            state.delete_openwebui_resources("tool", ["demo_tool"])

    def test_sync_status_action_uses_token_env_without_command_exposure(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="https://openwebui.top.secret",
                ca_file="/certs/top-secret-edge-root-ca.pem",
                locale="de",
            )
        )
        completed = SimpleNamespace(returncode=0, stdout="sync ok\n")

        with (
            patch.dict(os.environ, {"OPENWEBUI_ADMIN_TOKEN": "secret-token", "OPENWEBUI_ADMIN_TOKEN_FILE": ""}),
            patch("Workbench.dashboard.server.subprocess.run", return_value=completed) as run,
        ):
            result = state.run_action("sync-status")

        command = run.call_args.args[0]
        self.assertIn("scripts/sync_openwebui_models.py", command)
        self.assertNotIn("secret-token", command)
        self.assertEqual(run.call_args.kwargs["env"]["OPENWEBUI_ADMIN_TOKEN"], "secret-token")
        self.assertEqual(run.call_args.kwargs["env"]["OPENWEBUI_CA_FILE"], "/certs/top-secret-edge-root-ca.pem")
        self.assertTrue(result["ok"])

    def test_openwebui_base_model_options_include_remote_and_current_model(self) -> None:
        with patch.object(
            self.state,
            "openwebui_api_request",
            return_value={
                "data": [
                    {"id": "coder", "name": "Coder"},
                    {"id": "groq/llama", "name": "Groq Llama"},
                ]
            },
        ):
            payload = self.state.list_openwebui_base_models()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["selected"], "coder")
        self.assertIn("coder", [item["id"] for item in payload["models"]])
        self.assertIn("groq/llama", [item["id"] for item in payload["models"]])

    def test_generate_action_passes_selected_base_model_to_generator(self) -> None:
        completed = SimpleNamespace(returncode=0, stdout="generated\n")

        with patch("Workbench.dashboard.server.subprocess.run", return_value=completed) as run:
            result = self.state.run_action("generate", {"base_model_id": "groq/llama"})

        command = run.call_args.args[0]
        self.assertIn("--base-model-id", command)
        self.assertIn("groq/llama", command)
        self.assertEqual(run.call_args.kwargs["env"]["WORKBENCH_BASE_MODEL_ID"], "groq/llama")
        self.assertEqual(result["base_model_id"], "groq/llama")
        self.assertTrue(result["ok"])

    def test_reads_and_writes_tool_resource(self) -> None:
        before = self.state.read_resource("tool", "demo_tool")
        self.assertEqual(before["content"], "# demo\n")
        after = self.state.write_resource("tool", "demo_tool", "# updated\n")
        self.assertEqual(after["content"], "# updated\n")

    def test_reads_skill_resource(self) -> None:
        payload = self.state.read_resource("skill", "demo-skill")
        self.assertEqual(payload["content"], "# Demo Skill\n")

    def test_reads_function_and_prompt_resources(self) -> None:
        function_payload = self.state.read_resource("function", "demo_filter")
        prompt_payload = self.state.read_resource("prompt", "demo-prompt")

        self.assertIn("class Filter", function_payload["content"])
        self.assertIn("Demo Prompt", prompt_payload["content"])

    def test_creates_and_deletes_skill_resource(self) -> None:
        created = self.state.create_resource("skill", "new-skill", "# New Skill\n")
        self.assertEqual(created["id"], "new-skill")
        self.assertTrue((self.root / "Tools" / "openwebui_ext" / "skills" / "new-skill.md").is_file())
        deleted = self.state.delete_resource("skill", "new-skill")
        self.assertTrue(deleted["deleted"])
        self.assertFalse((self.root / "Tools" / "openwebui_ext" / "skills" / "new-skill.md").exists())

    def test_creates_tool_resource_with_py_suffix(self) -> None:
        created = self.state.create_resource("tool", "new_tool", "# New Tool\n")
        self.assertEqual(created["id"], "new_tool")
        self.assertTrue((self.root / "Tools" / "openwebui_ext" / "tools" / "new_tool.py").is_file())

    def test_creates_function_and_prompt_resources_with_expected_suffixes(self) -> None:
        function_created = self.state.create_resource("function", "new_filter", "class Filter:\n    pass\n")
        prompt_created = self.state.create_resource("prompt", "new-prompt", "# New Prompt\n")

        self.assertEqual(function_created["id"], "new_filter")
        self.assertEqual(prompt_created["id"], "new-prompt")
        self.assertTrue((self.root / "Tools" / "openwebui_ext" / "filters" / "new_filter.py").is_file())
        self.assertTrue((self.root / "Tools" / "openwebui_ext" / "prompts" / "new-prompt.md").is_file())

    def test_rejects_resource_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            self.state.read_resource("tool", "../demo_tool")

    def test_tls_context_can_disable_verification_for_local_https(self) -> None:
        context = openwebui_ssl_context(tls_verify=False)
        self.assertFalse(context.check_hostname)
        self.assertEqual(context.verify_mode.name, "CERT_NONE")

    def test_summary_reports_tls_settings(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, openwebui_base_url="http://127.0.0.1:9", tls_verify=False))
        summary = state.summary()
        self.assertFalse(summary["openwebui"]["tls_verify"])

    def test_summary_uses_admin_friendly_openwebui_status_timeout(self) -> None:
        class FakeResponse:
            status = 200

            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: object) -> None:
                return None

        state = WorkbenchState(WorkbenchConfig(root=self.root, openwebui_base_url="http://127.0.0.1:3000"))
        with patch.object(dashboard_server, "urlopen", return_value=FakeResponse()) as urlopen:
            summary = state.summary()

        self.assertTrue(summary["openwebui"]["reachable"]["ok"])
        self.assertGreaterEqual(urlopen.call_args.kwargs["timeout"], 5)

    def test_summary_reports_dashboard_auth_settings(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_required=True,
                auth_username="admin",
                auth_password="secret",
            )
        )
        summary = state.summary()
        self.assertTrue(summary["dashboard"]["auth_required"])
        self.assertTrue(summary["dashboard"]["auth_enabled"])
        self.assertTrue(summary["dashboard"]["auth_username_configured"])
        self.assertTrue(summary["dashboard"]["auth_password_configured"])

    def test_summary_reports_automation_defaults(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                automation_enabled=True,
                automation_interval_minutes=30,
                automation_actions=("check",),
            )
        )

        automation = state.summary()["automation"]

        self.assertTrue(automation["enabled"])
        self.assertEqual(automation["interval_minutes"], 30)
        self.assertEqual(automation["actions"], ["check"])
        self.assertEqual(automation["status"], "configured")

    def test_artifact_status_classifies_required_and_optional_handover_files(self) -> None:
        required_file = self.root / "Modelle" / "dist" / "openwebui-models-import.json"
        optional_file = self.root / "Tools" / "dist" / "openwebui-tools-import.json"
        required_file.parent.mkdir(parents=True)
        optional_file.parent.mkdir(parents=True)
        required_file.write_text("[]\n", encoding="utf-8")
        optional_file.write_text("[]\n", encoding="utf-8")

        artifacts = self.state.artifact_status()
        required = [item for item in artifacts if item["required"]]
        optional = [item for item in artifacts if not item["required"]]

        self.assertEqual(len(required), 8)
        self.assertEqual(len(optional), 1)
        self.assertEqual(optional[0]["kind"], "optional_network_tools")
        self.assertTrue(optional[0]["path"].endswith("Tools/dist/openwebui-tools-import.json"))
        self.assertTrue(next(item for item in artifacts if item["kind"] == "model_import")["exists"])

    def test_automation_scheduler_manual_run_starts_configured_actions(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                automation_actions=("check",),
            )
        )
        scheduler = WorkbenchAutomationScheduler(state)
        job = {"job_id": "job-1", "action": "check", "running": True, "ok": None}

        with patch.object(state, "start_action_job", return_value=job) as start_action:
            snapshot = scheduler.run_once("manual")

        start_action.assert_called_once_with("check")
        self.assertEqual(snapshot["last_trigger"], "manual")
        self.assertEqual(snapshot["last_jobs"][0]["job_id"], "job-1")
        self.assertEqual(snapshot["last_skipped"], [])

    def test_automation_scheduler_skips_unready_write_actions(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                allow_write=False,
                automation_actions=("generate",),
                locale="de",
            )
        )
        scheduler = WorkbenchAutomationScheduler(state)

        with patch.object(state, "start_action_job") as start_action:
            snapshot = scheduler.run_once("scheduled")

        start_action.assert_not_called()
        self.assertEqual(snapshot["last_jobs"], [])
        self.assertEqual(snapshot["last_skipped"][0]["action"], "generate")
        self.assertIn("Schreibzugriff", snapshot["last_skipped"][0]["reason"])

    def test_empty_workspace_lists_are_explicitly_empty(self) -> None:
        empty_state = WorkbenchState(WorkbenchConfig(root=self.root / "empty", openwebui_base_url="http://127.0.0.1:9"))

        summary = empty_state.summary()

        self.assertEqual(summary["counts"]["models"], 0)
        self.assertEqual(summary["counts"]["tools"], 0)
        self.assertEqual(summary["counts"]["functions"], 0)
        self.assertEqual(summary["counts"]["skills"], 0)
        self.assertEqual(summary["counts"]["prompts"], 0)
        self.assertEqual(empty_state.list_models(), [])
        self.assertEqual(empty_state.list_tools(), [])
        self.assertEqual(empty_state.list_functions(), [])
        self.assertEqual(empty_state.list_skills(), [])
        self.assertEqual(empty_state.list_prompts(), [])

    def test_i18n_defaults_to_german_and_supports_english(self) -> None:
        self.assertEqual(normalize_locale("fr-FR"), "de")
        self.assertEqual(detect_locale("en-US,en;q=0.9"), "en")
        self.assertEqual(t("auth_required", "de"), "Authentifizierung erforderlich.")
        self.assertEqual(t("auth_required", "en"), "Authentication required.")
        self.assertIn("Loopback", t("auth_required_for_non_loopback", "de"))
        self.assertIn("loopback", t("auth_required_for_non_loopback", "en"))
        self.assertIn("WORKBENCH_REQUIRE_AUTH", t("auth_required_for_runtime", "de"))
        self.assertIn("WORKBENCH_REQUIRE_AUTH", t("auth_required_for_runtime", "en"))

    def test_dashboard_server_defaults_to_localhost(self) -> None:
        with patch.dict(os.environ, {"WORKBENCH_HOST": "", "WORKBENCH_PORT": ""}, clear=False):
            os.environ.pop("WORKBENCH_HOST", None)
            os.environ.pop("WORKBENCH_PORT", None)
            dashboard_server.CONFIGURATION_ERRORS.clear()
            args = dashboard_server.parse_args([])

        self.assertEqual(args.host, "127.0.0.1")
        self.assertEqual(args.port, 8088)
        self.assertEqual(dashboard_server.configuration_errors(), [])

    def test_resources_route_lists_tools_functions_skills_and_prompts(self) -> None:
        base_url = self.start_server(self.state)

        status, response = self.request(base_url, path="/api/resources")

        payload = json.loads(response)
        self.assertEqual(status, 200)
        self.assertEqual(payload["tools"][0]["kind"], "tool")
        self.assertEqual(payload["functions"][0]["kind"], "function")
        self.assertEqual(payload["skills"][0]["kind"], "skill")
        self.assertEqual(payload["prompts"][0]["kind"], "prompt")

    def test_dashboard_server_invalid_numeric_env_exits_without_traceback(self) -> None:
        env = os.environ.copy()
        for name in (
            "WORKBENCH_COMMAND_TIMEOUT_SECONDS",
            "WORKBENCH_IMPORT_TIMEOUT_SECONDS",
            "WORKBENCH_IMPORT_HTTP_TIMEOUT_SECONDS",
            "WORKBENCH_MAX_BODY_BYTES",
            "WORKBENCH_PORT",
        ):
            env.pop(name, None)
        env["WORKBENCH_MAX_BODY_BYTES"] = "abc"
        env["WORKBENCH_PORT"] = "not-a-port"

        result = subprocess.run(
            [sys.executable, "-m", "Workbench.dashboard.server"],
            cwd=Path(__file__).resolve().parents[3],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("startup failed", result.stderr)
        self.assertIn("WORKBENCH_MAX_BODY_BYTES", result.stderr)
        self.assertIn("WORKBENCH_PORT", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_dashboard_server_invalid_boolean_env_exits_without_traceback(self) -> None:
        env = os.environ.copy()
        for name in ("OPENWEBUI_TLS_VERIFY", "WORKBENCH_ALLOW_WRITE"):
            env.pop(name, None)
        env["OPENWEBUI_TLS_VERIFY"] = "maybe"

        result = subprocess.run(
            [sys.executable, "-m", "Workbench.dashboard.server"],
            cwd=Path(__file__).resolve().parents[3],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("startup failed", result.stderr)
        self.assertIn("OPENWEBUI_TLS_VERIFY", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_dashboard_server_invalid_openwebui_url_exits_without_traceback(self) -> None:
        env = os.environ.copy()
        for name in ("OPENWEBUI_BASE_URL", "OPENWEBUI_PUBLIC_URL"):
            env.pop(name, None)
        env["OPENWEBUI_BASE_URL"] = "localhost:3000"
        env["OPENWEBUI_PUBLIC_URL"] = "https://user:password@localhost:3000"

        result = subprocess.run(
            [sys.executable, "-m", "Workbench.dashboard.server"],
            cwd=Path(__file__).resolve().parents[3],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("startup failed", result.stderr)
        self.assertIn("OPENWEBUI_BASE_URL", result.stderr)
        self.assertIn("OPENWEBUI_PUBLIC_URL", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_dashboard_server_invalid_secret_file_exits_without_traceback(self) -> None:
        env = os.environ.copy()
        for name in ("WORKBENCH_AUTH_PASSWORD", "WORKBENCH_AUTH_PASSWORD_FILE", "OPENWEBUI_ADMIN_TOKEN_FILE"):
            env.pop(name, None)
        env["WORKBENCH_AUTH_PASSWORD_FILE"] = str(self.root / "missing-password.txt")

        result = subprocess.run(
            [sys.executable, "-m", "Workbench.dashboard.server"],
            cwd=Path(__file__).resolve().parents[3],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("startup failed", result.stderr)
        self.assertIn("WORKBENCH_AUTH_PASSWORD_FILE", result.stderr)
        self.assertNotIn("missing-password", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_dashboard_server_bind_error_exits_without_traceback(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen(1)
            port = occupied.getsockname()[1]
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                code = dashboard_server.main(["--host", "127.0.0.1", "--port", str(port)])

        output = stderr.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("startup failed", output)
        self.assertIn(f"127.0.0.1:{port}", output)
        self.assertNotIn("Traceback", output)

    def test_non_loopback_bind_requires_auth(self) -> None:
        no_auth = WorkbenchConfig(root=self.root, auth_username="", auth_password="")
        with_auth = WorkbenchConfig(root=self.root, auth_username="workbench", auth_password="secret")

        self.assertEqual(dashboard_server.bind_auth_error("127.0.0.1", no_auth), "")
        self.assertEqual(dashboard_server.bind_auth_error("localhost", no_auth), "")
        self.assertEqual(dashboard_server.bind_auth_error("::1", no_auth), "")
        self.assertIn("WORKBENCH_AUTH_PASSWORD", dashboard_server.bind_auth_error("0.0.0.0", no_auth))
        self.assertEqual(dashboard_server.bind_auth_error("0.0.0.0", with_auth), "")

    def test_required_auth_requires_password_or_password_file(self) -> None:
        no_password = WorkbenchConfig(
            root=self.root,
            auth_required=True,
            auth_username="workbench",
            auth_password="",
        )
        with_password = WorkbenchConfig(
            root=self.root,
            auth_required=True,
            auth_username="workbench",
            auth_password="secret",
        )
        not_required = WorkbenchConfig(
            root=self.root,
            auth_required=False,
            auth_username="workbench",
            auth_password="",
        )

        self.assertIn("WORKBENCH_AUTH_PASSWORD", dashboard_server.required_auth_error(no_password))
        self.assertEqual(dashboard_server.required_auth_error(with_password), "")
        self.assertEqual(dashboard_server.required_auth_error(not_required), "")

    def test_dashboard_server_required_auth_error_exits_without_traceback(self) -> None:
        env = os.environ.copy()
        for name in ("WORKBENCH_AUTH_PASSWORD", "WORKBENCH_AUTH_PASSWORD_FILE"):
            env.pop(name, None)
        env["WORKBENCH_AUTH_USERNAME"] = "workbench"
        env["WORKBENCH_REQUIRE_AUTH"] = "true"

        result = subprocess.run(
            [sys.executable, "-m", "Workbench.dashboard.server"],
            cwd=Path(__file__).resolve().parents[3],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("startup failed", result.stderr)
        self.assertIn("WORKBENCH_REQUIRE_AUTH", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_import_action_uses_local_config_and_returns_failure_output(self) -> None:
        config_dir = self.root / "scripts"
        config_dir.mkdir(parents=True)
        (config_dir / "openwebui_workspace_config.yaml").write_text(
            "openwebui:\n  base_url: http://127.0.0.1:3000\n  admin_token: YOUR_OPEN_WEBUI_API_KEY\n",
            encoding="utf-8",
        )
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://openwebui:8080",
                import_timeout=1800,
                import_http_timeout=600,
                locale="de",
            )
        )
        completed = SimpleNamespace(returncode=2, stdout="import failed\n")

        with (
            patch.dict(os.environ, {"OPENWEBUI_BASE_URL": "", "OPENWEBUI_ADMIN_TOKEN": "", "OPENWEBUI_ADMIN_TOKEN_FILE": ""}),
            patch("Workbench.dashboard.server.subprocess.run", return_value=completed) as run,
        ):
            result = state.run_action("import-openwebui")

        command = run.call_args.kwargs["args"] if "args" in run.call_args.kwargs else run.call_args.args[0]
        self.assertIn("--config", command)
        self.assertIn("--timeout", command)
        self.assertIn("600", command)
        self.assertNotIn("--base-url", command)
        self.assertEqual(run.call_args.kwargs["timeout"], 1800)
        self.assertFalse(result["ok"])
        self.assertEqual(result["output"], "import failed\n")
        self.assertEqual(result["error"], "Aktion fehlgeschlagen (Exit-Code 2). Details stehen in der Ausgabe.")

    def test_import_openwebui_requires_token_or_local_config(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://openwebui:8080",
                locale="de",
            )
        )

        with (
            patch.dict(os.environ, {"OPENWEBUI_ADMIN_TOKEN": "", "OPENWEBUI_ADMIN_TOKEN_FILE": ""}),
            self.assertRaisesRegex(PermissionError, "OPENWEBUI_ADMIN_TOKEN"),
        ):
            state.run_action("import-openwebui")

    def test_import_action_can_run_as_background_job_without_duplicate_start(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, openwebui_base_url="http://openwebui:8080", locale="de"))
        release = threading.Event()

        def fake_run_action(
            action: str,
            options: dict[str, object] | None = None,
            progress_callback: object | None = None,
        ) -> dict[str, object]:
            if callable(progress_callback):
                progress_callback("running log\n")
            release.wait(timeout=2)
            return {
                "action": action,
                "label": "Import to OpenWebUI",
                "returncode": 0,
                "duration_seconds": 1.0,
                "ok": True,
                "output": "done\n",
                "error": "",
            }

        with patch.object(state, "run_action", side_effect=fake_run_action):
            first = state.start_action_job("import-openwebui")
            second = state.start_action_job("import-openwebui")
            self.assertTrue(first["running"])
            self.assertEqual(first["job_id"], second["job_id"])
            for _ in range(20):
                progress = state.action_job(first["job_id"])
                if progress["output"]:
                    break
                threading.Event().wait(0.05)
            self.assertEqual(progress["output"], "running log\n")
            release.set()
            for _ in range(20):
                current = state.action_job(first["job_id"])
                if not current["running"]:
                    break
                threading.Event().wait(0.05)

        self.assertFalse(current["running"])
        self.assertTrue(current["ok"])
        self.assertEqual(current["output"], "done\n")

    def test_basic_auth_protects_dashboard_routes(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        base_url = self.start_server(state)

        self.assertEqual(self.request_status(base_url), 401)
        self.assertEqual(self.request_status(base_url, self.basic_auth("admin", "wrong")), 401)
        self.assertEqual(self.request_status(base_url, self.basic_auth("admin", "secret")), 200)

    def test_healthz_remains_available_when_auth_is_enabled(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        base_url = self.start_server(state)
        status, body = self.request(base_url, path="/healthz")

        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"ok": True, "service": "openwebui-workbench"})

    def test_responses_include_browser_security_headers(self) -> None:
        base_url = self.start_server(self.state)

        status, _body, headers = self.request_with_headers(base_url, path="/")

        self.assertEqual(status, 200)
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(headers["Referrer-Policy"], "no-referrer")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertIn("img-src 'self' data:", headers["Content-Security-Policy"])

    def test_mutating_routes_require_workbench_request_header(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        base_url = self.start_server(state)
        body = json.dumps({"kind": "skill", "id": "csrf-skill", "content": "# CSRF Skill\n"})
        auth = self.basic_auth("admin", "secret")

        status, response = self.request(base_url, authorization=auth, path="/api/resources", method="POST", body=body)
        self.assertEqual(status, 403)
        self.assertIn("same-origin", json.loads(response)["error"].lower())

        status, response = self.request(
            base_url,
            authorization=auth,
            path="/api/resources",
            method="POST",
            body=body,
            headers={"X-Workbench-Request": "same-origin"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(json.loads(response)["id"], "csrf-skill")

    def test_action_routes_require_workbench_request_header(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        base_url = self.start_server(state)
        auth = self.basic_auth("admin", "secret")

        status, response = self.request(base_url, authorization=auth, path="/api/actions/check", method="POST", body="{}")
        self.assertEqual(status, 403)
        self.assertIn("same-origin", json.loads(response)["error"].lower())

        result = {
            "action": "check",
            "label": "Verify workspace",
            "returncode": 0,
            "duration_seconds": 0.1,
            "ok": True,
            "output": "ok\n",
            "error": "",
        }
        job = {
            "job_id": "job-1",
            "action": "check",
            "running": True,
            "ok": None,
            "output": "",
        }
        with patch.object(state, "start_action_job", return_value=job) as start_job:
            status, response = self.request(
                base_url,
                authorization=auth,
                path="/api/actions/check",
                method="POST",
                body="{}",
                headers={"X-Workbench-Request": "same-origin"},
            )

        self.assertEqual(status, 202)
        self.assertEqual(json.loads(response)["job_id"], "job-1")
        start_job.assert_called_once_with("check", {})

    def test_openwebui_model_delete_route_requires_workbench_request_header(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        base_url = self.start_server(state)
        auth = self.basic_auth("admin", "secret")
        body = json.dumps({"ids": ["demo-model"]})

        status, response = self.request(
            base_url,
            authorization=auth,
            path="/api/openwebui/models/delete",
            method="POST",
            body=body,
        )
        self.assertEqual(status, 403)
        self.assertIn("same-origin", json.loads(response)["error"].lower())

        with patch.object(state, "delete_openwebui_models", return_value={"ok": True, "deleted": ["demo-model"], "failed": [], "requested": ["demo-model"]}) as delete:
            status, response = self.request(
                base_url,
                authorization=auth,
                path="/api/openwebui/models/delete",
                method="POST",
                body=body,
                headers={"X-Workbench-Request": "same-origin"},
            )

        self.assertEqual(status, 200)
        self.assertEqual(json.loads(response)["deleted"], ["demo-model"])
        delete.assert_called_once_with(["demo-model"])

    def test_openwebui_resource_delete_route_requires_workbench_request_header(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        base_url = self.start_server(state)
        auth = self.basic_auth("admin", "secret")
        body = json.dumps({"kind": "prompt", "ids": ["demo-prompt"]})

        status, response = self.request(
            base_url,
            authorization=auth,
            path="/api/openwebui/resources/delete",
            method="POST",
            body=body,
        )
        self.assertEqual(status, 403)
        self.assertIn("same-origin", json.loads(response)["error"].lower())

        result = {"ok": True, "kind": "prompt", "deleted": ["demo-prompt"], "failed": [], "requested": ["demo-prompt"]}
        with patch.object(state, "delete_openwebui_resources", return_value=result) as delete:
            status, response = self.request(
                base_url,
                authorization=auth,
                path="/api/openwebui/resources/delete",
                method="POST",
                body=body,
                headers={"X-Workbench-Request": "same-origin"},
            )

        self.assertEqual(status, 200)
        self.assertEqual(json.loads(response)["deleted"], ["demo-prompt"])
        delete.assert_called_once_with("prompt", ["demo-prompt"])

    def test_automation_run_route_requires_workbench_request_header(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        state.automation_scheduler = SimpleNamespace(run_once=lambda trigger: {"trigger": trigger, "last_jobs": []})
        base_url = self.start_server(state)
        auth = self.basic_auth("admin", "secret")

        try:
            status, response = self.request(base_url, authorization=auth, path="/api/automation/run", method="POST", body="{}")
        except ConnectionAbortedError:
            status, response = self.request(base_url, authorization=auth, path="/api/automation/run", method="POST", body="{}")
        self.assertEqual(status, 403)
        self.assertIn("same-origin", json.loads(response)["error"].lower())

        status, response = self.request(
            base_url,
            authorization=auth,
            path="/api/automation/run",
            method="POST",
            body="{}",
            headers={"X-Workbench-Request": "same-origin"},
        )
        self.assertEqual(status, 202)
        self.assertEqual(json.loads(response)["trigger"], "manual")

    def test_read_only_action_route_rejects_background_write_action(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                allow_write=False,
                openwebui_base_url="http://127.0.0.1:9",
                locale="de",
                auth_username="",
                auth_password="",
            )
        )
        base_url = self.start_server(state)

        with patch.object(state, "start_action_job") as start_job:
            status, response = self.request(
                base_url,
                path="/api/actions/import-openwebui",
                method="POST",
                body="{}",
                headers={"X-Workbench-Request": "same-origin"},
            )

        self.assertEqual(status, 403)
        self.assertIn("Schreibzugriff", json.loads(response)["error"])
        start_job.assert_not_called()

    def test_basic_auth_uses_accept_language_when_available(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        base_url = self.start_server(state)
        status, body = self.request(base_url, headers={"Accept-Language": "en-US,en;q=0.9"})
        self.assertEqual(status, 401)
        self.assertEqual(json.loads(body)["error"], "Authentication required.")

    def test_static_route_rejects_encoded_path_traversal(self) -> None:
        base_url = self.start_server(self.state)
        self.assertEqual(self.request_status(base_url, path="/static/..%2F..%2FREADME.md"), 400)

    def request_status(self, base_url: str, authorization: str = "", path: str = "/api/status") -> int:
        status, _body = self.request(base_url, authorization=authorization, path=path)
        return status

    def request(
        self,
        base_url: str,
        authorization: str = "",
        path: str = "/api/status",
        headers: dict[str, str] | None = None,
        method: str = "GET",
        body: str | None = None,
    ) -> tuple[int, str]:
        status, body, _headers = self.request_with_headers(base_url, authorization, path, headers, method, body)
        return status, body

    def request_with_headers(
        self,
        base_url: str,
        authorization: str = "",
        path: str = "/api/status",
        headers: dict[str, str] | None = None,
        method: str = "GET",
        body: str | None = None,
    ) -> tuple[int, str, dict[str, str]]:
        host_port = base_url.removeprefix("http://")
        host, raw_port = host_port.rsplit(":", 1)
        connection = HTTPConnection(host, int(raw_port), timeout=5)
        try:
            request_headers = dict(headers or {})
            if authorization:
                request_headers["Authorization"] = authorization
            if body is not None:
                request_headers.setdefault("Content-Type", "application/json")
            connection.request(method, path, body=body, headers=request_headers)
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            return response.status, body, dict(response.getheaders())
        finally:
            connection.close()

    def start_server(self, state: WorkbenchState) -> str:
        previous_state = dashboard_server.STATE
        dashboard_server.STATE = state
        server = ThreadingHTTPServer(("127.0.0.1", 0), dashboard_server.WorkbenchHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def cleanup() -> None:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            dashboard_server.STATE = previous_state

        self.addCleanup(cleanup)
        host, port = server.server_address
        return f"http://{host}:{port}"

    @staticmethod
    def basic_auth(username: str, password: str) -> str:
        token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        return f"Basic {token}"


if __name__ == "__main__":
    unittest.main()
