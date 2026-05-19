from __future__ import annotations

import asyncio
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS_DIR = ROOT / "Tools" / "openwebui_ext" / "tools"
JUPYTER_TOOL = ROOT / "Tools" / "jupyter" / "jupyter_tool.py"


def load(path: Path):
    spec = importlib.util.spec_from_file_location("behavior_" + path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tools()


class OpenWebUIToolBehaviorTests(unittest.TestCase):
    def assert_ok_text(self, value: str) -> None:
        self.assertIsInstance(value, str)
        self.assertGreater(len(value.strip()), 20)
        self.assertNotIn("Traceback", value)

    def test_air_gapped_jupyter_static_guard_works_without_server(self) -> None:
        tool = load(JUPYTER_TOOL)
        result = tool.run_python("import os\nprint(os.getcwd())")
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "blocked")

    def test_comfyui_workflow_inspector_smoke(self) -> None:
        tool = load(TOOLS_DIR / "comfyui_workflow_inspector.py")
        self.assert_ok_text(asyncio.run(tool.inspect_workflow('{"1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":"model.safetensors"}}}')))

    def test_docker_compose_triage_smoke(self) -> None:
        tool = load(TOOLS_DIR / "docker_compose_triage.py")
        self.assert_ok_text(asyncio.run(tool.analyze_compose("services:\n  web:\n    image: nginx:stable\n    ports:\n      - '8080:80'")))

    def test_github_repo_inspector_rejects_invalid_repo_without_network(self) -> None:
        tool = load(TOOLS_DIR / "github_repo_inspector.py")
        result = asyncio.run(tool.inspect_repository("not a repo"))
        self.assertIn("Fehler", result)

    def test_inline_visuals_toolkit_smoke(self) -> None:
        tool = load(TOOLS_DIR / "inline_visuals_toolkit_v3.py")
        result = asyncio.run(tool.create_svg_chart("Smoke", '[{"label":"A","value":2},{"label":"B","value":3}]'))
        self.assertIn("<svg", result)

    def test_json_csv_text_validator_smoke(self) -> None:
        tool = load(TOOLS_DIR / "json_csv_text_validator.py")
        result = asyncio.run(tool.validate_json('{"ok": true, "items": [1, 2]}'))
        self.assertIn("Status: gültig", result)

    def test_markdown_skill_builder_smoke(self) -> None:
        tool = load(TOOLS_DIR / "markdown_skill_builder.py")
        result = asyncio.run(tool.build_skill("Analysiere interne Logdateien defensiv.", preferred_name="log-analyse"))
        self.assertIn("name:", result)

    def test_offline_artifact_workbench_smoke(self) -> None:
        tool = load(TOOLS_DIR / "offline_artifact_workbench.py")
        with tempfile.TemporaryDirectory() as temp_dir:
            old_root = os.environ.get("OPENWEBUI_ARTIFACT_ROOT")
            os.environ["OPENWEBUI_ARTIFACT_ROOT"] = temp_dir
            try:
                result = asyncio.run(tool.create_html_document("Smoke", "<h1>OK</h1>", filename="smoke.html"))
                self.assertIn("Artefakt erzeugt", result)
                self.assertTrue((Path(temp_dir) / "smoke.html").exists())
            finally:
                if old_root is None:
                    os.environ.pop("OPENWEBUI_ARTIFACT_ROOT", None)
                else:
                    os.environ["OPENWEBUI_ARTIFACT_ROOT"] = old_root

    def test_openapi_schema_inspector_smoke(self) -> None:
        tool = load(TOOLS_DIR / "openapi_schema_inspector.py")
        result = asyncio.run(tool.inspect_openapi_json('{"openapi":"3.0.0","info":{"title":"Smoke","version":"1"},"paths":{"/x":{"get":{"summary":"Read"}}}}'))
        self.assertIn("/x", result)

    def test_parallel_task_planner_smoke(self) -> None:
        tool = load(TOOLS_DIR / "parallel_task_planner.py")
        result = asyncio.run(tool.build_parallel_execution_plan("Smoke", '[{"id":"a","task":"A"},{"id":"b","task":"B","depends_on":["a"]}]'))
        self.assert_ok_text(result)

    def test_repo_tree_analyzer_smoke(self) -> None:
        tool = load(TOOLS_DIR / "repo_tree_analyzer.py")
        result = asyncio.run(tool.analyze_tree("app.py\nREADME.md\nsrc/main.py\ntests/test_app.py"))
        self.assert_ok_text(result)

    def test_safe_http_fetcher_rejects_non_http_without_network(self) -> None:
        tool = load(TOOLS_DIR / "safe_http_fetcher.py")
        result = asyncio.run(tool.fetch_url("file:///etc/passwd"))
        self.assertIn("Fehler", result)

    def test_tool_skill_overlay_planner_smoke(self) -> None:
        tool = load(TOOLS_DIR / "tool_skill_overlay_planner.py")
        result = asyncio.run(tool.suggest_fallback_stack("JSON prüfen", '[{"id":"json_csv_text_validator","capabilities":["json"]},{"id":"jupyter","capabilities":["python"]}]'))
        self.assert_ok_text(result)


if __name__ == "__main__":
    unittest.main()
