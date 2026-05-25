from __future__ import annotations

import base64
import json
import threading
import tempfile
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

import Workbench.dashboard.server as dashboard_server
from Workbench.dashboard.i18n import detect_locale, normalize_locale, t
from Workbench.dashboard.server import WorkbenchConfig, WorkbenchState, openwebui_ssl_context


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
                        "meta": {"description": "Demo", "tags": [{"name": "test"}]},
                    }
                ]
            ),
            encoding="utf-8",
        )
        (model_dir / "systemprompt.md").write_text("System\n", encoding="utf-8")
        (model_dir / "mainprompt.md").write_text("Main\n", encoding="utf-8")
        (model_dir / "fachwissen.md").write_text("Knowledge\n", encoding="utf-8")
        (model_dir / "beispielergebnis.md").write_text("Example\n", encoding="utf-8")
        umlaut_dir = self.root / "Modelle" / "einzelmodelle" / "übersetzung-lokalisierung"
        umlaut_dir.mkdir(parents=True)
        (umlaut_dir / "model.json").write_text(
            json.dumps([{"id": "übersetzung-lokalisierung", "name": "Übersetzung Lokalisierung"}]),
            encoding="utf-8",
        )
        (umlaut_dir / "systemprompt.md").write_text("Umlaut\n", encoding="utf-8")
        (self.root / "Tools" / "openwebui_ext" / "tools").mkdir(parents=True)
        (self.root / "Tools" / "openwebui_ext" / "tools" / "demo_tool.py").write_text("# demo\n", encoding="utf-8")
        (self.root / "Tools" / "openwebui_ext" / "skills").mkdir(parents=True)
        (self.root / "Tools" / "openwebui_ext" / "skills" / "demo-skill.md").write_text("# Demo Skill\n", encoding="utf-8")
        self.state = WorkbenchState(WorkbenchConfig(root=self.root, openwebui_base_url="http://127.0.0.1:9"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_lists_model_packages(self) -> None:
        models = self.state.list_models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["id"], "demo-model")
        self.assertEqual(models[0]["name"], "Demo Model")
        self.assertIn("test", models[0]["tags"])
        self.assertEqual(models[1]["id"], "übersetzung-lokalisierung")

    def test_reads_and_writes_allowed_markdown(self) -> None:
        before = self.state.read_model_file("demo-model", "systemprompt.md")
        self.assertEqual(before["content"], "System\n")
        after = self.state.write_model_file("demo-model", "systemprompt.md", "Updated\n")
        self.assertEqual(after["content"], "Updated\n")

    def test_reads_and_writes_allowed_example_markdown(self) -> None:
        after = self.state.write_model_file("demo-model", "beispiele/demo.md", "Example note\n")
        self.assertEqual(after["content"], "Example note\n")
        self.assertTrue((self.root / "Modelle" / "einzelmodelle" / "demo-model" / "beispiele" / "demo.md").is_file())

    def test_rejects_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            self.state.read_model_file("demo-model", "../README.md")
        with self.assertRaises(ValueError):
            self.state.read_model_file("demo-model", "beispiele/../systemprompt.md")
        with self.assertRaises(ValueError):
            self.state.read_model_file("demo-model", "beispiele/sub/path.md")

    def test_rejects_unknown_model_id_shape(self) -> None:
        with self.assertRaises(ValueError):
            self.state.read_model_file("../demo-model", "systemprompt.md")

    def test_write_can_be_disabled(self) -> None:
        state = WorkbenchState(WorkbenchConfig(root=self.root, allow_write=False))
        with self.assertRaises(PermissionError):
            state.write_model_file("demo-model", "systemprompt.md", "Nope\n")

    def test_reads_and_writes_tool_resource(self) -> None:
        before = self.state.read_resource("tool", "demo_tool")
        self.assertEqual(before["content"], "# demo\n")
        after = self.state.write_resource("tool", "demo_tool", "# updated\n")
        self.assertEqual(after["content"], "# updated\n")

    def test_reads_skill_resource(self) -> None:
        payload = self.state.read_resource("skill", "demo-skill")
        self.assertEqual(payload["content"], "# Demo Skill\n")

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

    def test_summary_reports_dashboard_auth_settings(self) -> None:
        state = WorkbenchState(
            WorkbenchConfig(
                root=self.root,
                openwebui_base_url="http://127.0.0.1:9",
                auth_username="admin",
                auth_password="secret",
            )
        )
        summary = state.summary()
        self.assertTrue(summary["dashboard"]["auth_enabled"])
        self.assertTrue(summary["dashboard"]["auth_username_configured"])
        self.assertTrue(summary["dashboard"]["auth_password_configured"])

    def test_i18n_defaults_to_german_and_supports_english(self) -> None:
        self.assertEqual(normalize_locale("fr-FR"), "de")
        self.assertEqual(detect_locale("en-US,en;q=0.9"), "en")
        self.assertEqual(t("auth_required", "de"), "Authentifizierung erforderlich.")
        self.assertEqual(t("auth_required", "en"), "Authentication required.")

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

    def request(self, base_url: str, authorization: str = "", path: str = "/api/status", headers: dict[str, str] | None = None) -> tuple[int, str]:
        host_port = base_url.removeprefix("http://")
        host, raw_port = host_port.rsplit(":", 1)
        connection = HTTPConnection(host, int(raw_port), timeout=5)
        try:
            request_headers = dict(headers or {})
            if authorization:
                request_headers["Authorization"] = authorization
            connection.request("GET", path, headers=request_headers)
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            return response.status, body
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
