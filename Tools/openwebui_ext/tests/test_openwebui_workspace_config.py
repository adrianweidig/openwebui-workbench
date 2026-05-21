from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
MODEL_SUMMARY = ROOT / "Modelle" / "dist" / "openwebui-model-params-summary.json"
REGISTRATION_PLAN = ROOT / "Modelle" / "dist" / "openwebui-registration-plan.json"
TOOL_REGISTRY = ROOT / "Tools" / "dist" / "openwebui-tool-registry.json"
FUNCTION_REGISTRY = ROOT / "Tools" / "dist" / "openwebui-function-registry.json"
SKILLS_DIR = ROOT / "Tools" / "openwebui_ext" / "skills"

REQUIRED_KNOWLEDGE_FILES = ["mainprompt.md", "fachwissen.md"]
TOOL_FORCE_MARKER = "## Verbindliche Tool- und Skill-Nutzung"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class OpenWebUIWorkspaceConfigTests(unittest.TestCase):
    def test_every_model_has_required_knowledge_and_tool_inventory_prompt(self) -> None:
        model_files = sorted(SINGLE_MODELS.glob("*/model.json"))
        self.assertGreaterEqual(len(model_files), 1)
        skill_ids = {path.stem for path in SKILLS_DIR.glob("*.md") if path.name.upper() != "README.MD"}

        for model_file in model_files:
            with self.subTest(model=model_file.parent.name):
                for name in REQUIRED_KNOWLEDGE_FILES:
                    knowledge_file = model_file.parent / name
                    self.assertTrue(knowledge_file.exists(), f"Missing {knowledge_file}")
                    self.assertGreater(knowledge_file.stat().st_size, 0, f"Empty {knowledge_file}")

                data = read_json(model_file)
                self.assertIsInstance(data, list)
                self.assertEqual(len(data), 1)
                model = data[0]
                meta = model.get("meta", {})
                params = model.get("params", {})
                system = params.get("system", "")

                self.assertIn(TOOL_FORCE_MARKER, system)
                self.assertIn("Tool-/Skill-Inventur", system)
                self.assertEqual(meta.get("requiredKnowledgeFiles"), REQUIRED_KNOWLEDGE_FILES)
                self.assertGreater(len(meta.get("primaryToolIds", [])), 0)
                self.assertGreater(len(meta.get("recommendedSkillIds", [])), 0)
                self.assertTrue(set(meta["recommendedSkillIds"]).issubset(skill_ids))

    def test_generated_plan_and_summary_track_import_requirements(self) -> None:
        plan = read_json(REGISTRATION_PLAN)
        summary = read_json(MODEL_SUMMARY)
        tools = read_json(TOOL_REGISTRY)
        functions = read_json(FUNCTION_REGISTRY)

        self.assertIn("Tools/import_openwebui_workspace.py", plan.get("api_import_script", ""))
        self.assertIn("4_upload_model_knowledge", plan.get("order", []))
        self.assertEqual(plan.get("model_knowledge_files_required"), REQUIRED_KNOWLEDGE_FILES)
        self.assertGreaterEqual(len(plan.get("skills_before_models", [])), 1)
        self.assertGreaterEqual(len(tools.get("tools", [])), 1)
        self.assertGreaterEqual(len(functions.get("functions", [])), 1)

        for model in summary.get("models", []):
            with self.subTest(model=model.get("id")):
                self.assertTrue(model.get("has_tool_force_profile"))
                self.assertEqual(model.get("required_knowledge_files"), REQUIRED_KNOWLEDGE_FILES)
                for info in model.get("knowledge_files", {}).values():
                    self.assertTrue(info.get("exists"))
                    self.assertTrue(info.get("non_empty"))


if __name__ == "__main__":
    unittest.main()
