from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Workbench.dashboard.server import WorkbenchConfig, WorkbenchState


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

    def test_rejects_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            self.state.read_model_file("demo-model", "../README.md")

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


if __name__ == "__main__":
    unittest.main()
