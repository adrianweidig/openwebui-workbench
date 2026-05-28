from __future__ import annotations

import json
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
MODEL_SUMMARY = ROOT / "Modelle" / "dist" / "openwebui-model-params-summary.json"
REGISTRATION_PLAN = ROOT / "Modelle" / "dist" / "openwebui-registration-plan.json"
TOOL_REGISTRY = ROOT / "Tools" / "dist" / "openwebui-tool-registry.json"
FUNCTION_REGISTRY = ROOT / "Tools" / "dist" / "openwebui-function-registry.json"
SKILLS_DIR = ROOT / "Tools" / "openwebui_ext" / "skills"
IMPORT_SCRIPT = ROOT / "Tools" / "import_openwebui_workspace.py"
CONFIG_EXAMPLE = ROOT / "scripts" / "openwebui_workspace_config.example.yaml"

REQUIRED_KNOWLEDGE_FILES = ["mainprompt.md", "fachwissen.md", "beispielergebnis.md"]
MODEL_REQUIRED_KNOWLEDGE_FILE_OVERRIDES = {
    "api-schnittstellenentwurf": ["mainprompt.md", "fachwissen.md", "beispielergebnis.yaml"],
    "codegenerierung": ["mainprompt.md", "fachwissen.md", "beispielergebnis.py"],
    "informationsextraktion": ["mainprompt.md", "fachwissen.md", "beispielergebnis.json"],
    "json-csv-log-analyse": ["mainprompt.md", "fachwissen.md", "beispielergebnis.json"],
    "n8n-workflow-architect": ["mainprompt.md", "fachwissen.md", "beispielergebnis.json"],
    "präsentationserstellung": ["mainprompt.md", "fachwissen.md", "beispielergebnis.html"],
    "report-dashboard-vorbereitung": ["mainprompt.md", "fachwissen.md", "beispielergebnis.html"],
    "tabellen-csv-datenanalyse": ["mainprompt.md", "fachwissen.md", "beispielergebnis.py"],
}
def required_knowledge_files(model_id: str) -> list[str]:
    return MODEL_REQUIRED_KNOWLEDGE_FILE_OVERRIDES.get(model_id, REQUIRED_KNOWLEDGE_FILES)


def knowledge_phrases(model_id: str) -> list[str]:
    return [*required_knowledge_files(model_id), "beispiele/", "i18n/", "laden und analysieren"]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_importer():
    spec = importlib.util.spec_from_file_location("test_import_openwebui_workspace", IMPORT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OpenWebUIWorkspaceConfigTests(unittest.TestCase):
    def test_every_model_has_required_knowledge_and_tool_inventory_prompt(self) -> None:
        model_files = sorted(SINGLE_MODELS.glob("*/model.json"))
        self.assertGreaterEqual(len(model_files), 1)
        skill_ids = {path.stem for path in SKILLS_DIR.glob("*.md") if path.name.upper() != "README.MD"}

        for model_file in model_files:
            with self.subTest(model=model_file.parent.name):
                model_id = model_file.parent.name
                for name in required_knowledge_files(model_id):
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

                self.assertIn("kurzer Bootloader", system)
                self.assertIn("Erfinde keine Fakten", system)
                self.assertIn("Toolhinweise", system)
                self.assertNotIn("## Verbindliche Tool- und Skill-Nutzung", system)
                self.assertNotIn("## Vision- und UI-Bildanalyse", system)
                self.assertLess(len(system), 1400)
                for phrase in knowledge_phrases(model_id):
                    self.assertIn(phrase, system)
                self.assertEqual(meta.get("requiredKnowledgeFiles"), required_knowledge_files(model_id))
                self.assertTrue(meta.get("capabilities", {}).get("vision"))
                self.assertGreater(len(meta.get("primaryToolIds", [])), 0)
                self.assertGreater(len(meta.get("recommendedSkillIds", [])), 0)
                self.assertTrue(set(meta["recommendedSkillIds"]).issubset(skill_ids))
                self.assertTrue((model_file.parent / "beispiele").exists())
                self.assertGreater(len(list((model_file.parent / "beispiele").glob("*"))), 0)

    def test_generated_plan_and_summary_track_import_requirements(self) -> None:
        plan = read_json(REGISTRATION_PLAN)
        summary = read_json(MODEL_SUMMARY)
        tools = read_json(TOOL_REGISTRY)
        functions = read_json(FUNCTION_REGISTRY)

        self.assertIn("Tools/import_openwebui_workspace.py", plan.get("api_import_script", ""))
        self.assertIn("scripts/openwebui_workspace_config.yaml", plan.get("api_import_config_file", ""))
        self.assertIn("scripts/openwebui_workspace_config.example.yaml", plan.get("api_import_config_example", ""))
        order = plan.get("order", [])
        self.assertTrue(any(item.endswith("upload_model_knowledge") for item in order))
        self.assertTrue(any(item.endswith("apply_tool_valves") for item in order))
        self.assertTrue(any(item.endswith("apply_function_filter_valves") for item in order))
        self.assertTrue(any(item.endswith("publish_tools_public") for item in order))
        self.assertTrue(any(item.endswith("enable_functions_global") for item in order))
        self.assertTrue(any(item.endswith("publish_models_public") for item in order))
        self.assertEqual(
            plan.get("api_import_config_policy", {}).get("source_of_truth"),
            "scripts/openwebui_workspace_config.yaml",
        )
        public_access_policy = plan.get("public_access_policy", {})
        self.assertEqual(public_access_policy.get("tools"), "public_read_grant_after_upsert")
        self.assertEqual(public_access_policy.get("skills"), "public_read_grant_after_upsert")
        self.assertEqual(public_access_policy.get("models"), "public_read_grant_after_import")
        self.assertEqual(public_access_policy.get("functions_and_filters"), "active_and_global_after_upsert")
        self.assertEqual(
            public_access_policy.get("grant"),
            {"principal_type": "user", "principal_id": "*", "permission": "read"},
        )
        self.assertEqual(plan.get("vision_policy", {}).get("specialist_model_id"), "mistral-vision-workbench")
        self.assertEqual(plan.get("model_example_policy", {}).get("default_required_knowledge_file"), "beispielergebnis.md")
        self.assertEqual(plan.get("model_knowledge_file_overrides"), MODEL_REQUIRED_KNOWLEDGE_FILE_OVERRIDES)
        self.assertEqual(plan.get("offline_addons_runtime", {}).get("container_playwright_browsers_path"), "/app/backend/data/cache/ms-playwright")
        self.assertIn(
            "function_valves.context_compressor_filter.reserved_output_tokens",
            plan.get("offline_addons_runtime", {}).get("config_keys", []),
        )
        self.assertEqual(plan.get("model_knowledge_files_required"), REQUIRED_KNOWLEDGE_FILES)
        self.assertGreaterEqual(len(plan.get("skills_before_models", [])), 1)
        self.assertGreaterEqual(len(tools.get("tools", [])), 1)
        self.assertGreaterEqual(len(functions.get("functions", [])), 1)
        self.assertIn("openwebui-offline-addons", summary.get("openwebui_builtin_and_addon_policy", ""))

        for model in summary.get("models", []):
            with self.subTest(model=model.get("id")):
                self.assertTrue(model.get("has_short_bootloader_systemprompt"))
                self.assertTrue(model.get("vision_enabled"))
                self.assertLess(model.get("system_prompt_chars", 999999), 1400)
                self.assertEqual(model.get("required_knowledge_files"), required_knowledge_files(str(model.get("id"))))
                for info in model.get("knowledge_files", {}).values():
                    self.assertTrue(info.get("exists"))
                    self.assertTrue(info.get("non_empty"))

    def test_config_yaml_example_resolves_openwebui_and_jupyter_values(self) -> None:
        importer = load_importer()
        args = importer.parse_args(["--config", str(CONFIG_EXAMPLE), "--dry-run"])
        runtime = importer.resolve_runtime_config(args)
        self.assertEqual(runtime["base_url"], "http://openwebui.example.local:3000")
        self.assertEqual(runtime["auth_header"], "Authorization")
        self.assertEqual(runtime["auth_scheme"], "Bearer")
        self.assertEqual(importer.normalize_openwebui_base_url("http://openwebui.example.local:3000/api"), "http://openwebui.example.local:3000")
        self.assertTrue(runtime["public_read"])
        self.assertEqual(
            importer.public_read_grants(),
            [{"principal_type": "user", "principal_id": "*", "permission": "read"}],
        )
        self.assertTrue(importer.has_public_read_access({"access_grants": importer.public_read_grants()}))
        self.assertFalse(importer.has_public_read_access({"access_grants": []}))
        self.assertTrue(
            importer.is_not_found_error(
                RuntimeError("POST /api/tools/id/air_gapped_jupyter_python/valves/update returned HTTP 404: We could not find what you're looking for")
            )
        )
        self.assertFalse(importer.is_not_found_error(RuntimeError("GET /api/models returned HTTP 401: Unauthorized")))
        self.assertEqual(runtime["jupyter"]["OPENWEBUI_JUPYTER_URL"], "http://jupyter:8888")
        self.assertEqual(runtime["environment"]["PLAYWRIGHT_BROWSERS_PATH"], "/app/backend/data/cache/ms-playwright")
        self.assertEqual(
            runtime["tool_valves"]["air_gapped_jupyter_python"]["OPENWEBUI_JUPYTER_URL"],
            "http://jupyter:8888",
        )
        self.assertEqual(runtime["addons"]["playwright_browsers_path"], "/app/backend/data/cache/ms-playwright")
        self.assertTrue(runtime["addons"]["prefer_playwright_pdf"])
        valves = importer.configured_tool_valves(runtime)
        self.assertIn("air_gapped_jupyter_python", valves)
        self.assertIn("offline_artifact_workbench", valves)
        self.assertEqual(valves["offline_artifact_workbench"]["playwright_browsers_path"], "/app/backend/data/cache/ms-playwright")
        self.assertTrue(valves["offline_artifact_workbench"]["prefer_playwright_pdf"])
        function_valves = importer.configured_function_valves(runtime)
        self.assertEqual(function_valves["context_compressor_filter"]["reserved_output_tokens"], 4096)
        self.assertTrue(function_valves["context_compressor_filter"]["hard_guard_enabled"])


if __name__ == "__main__":
    unittest.main()
