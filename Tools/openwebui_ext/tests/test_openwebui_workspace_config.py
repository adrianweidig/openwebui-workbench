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

WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA = "workbench-file-context/v1"
WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID = "workbench_required_file_context_filter"
REQUIRED_FILTER_PREFIX = [
    WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID,
    "context_compressor_filter",
    "auto_tool_selector",
    "markdown_normalizer",
]
MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES = {
    "api-schnittstellenentwurf": "beispielergebnis.yaml",
    "codegenerierung": "beispielergebnis.py",
    "informationsextraktion": "beispielergebnis.json",
    "json-csv-log-analyse": "beispielergebnis.json",
    "n8n-workflow-architect": "beispielergebnis.json",
    "präsentationserstellung": "beispielergebnis.html",
    "report-dashboard-vorbereitung": "beispielergebnis.html",
    "tabellen-csv-datenanalyse": "beispielergebnis.py",
}


def legacy_example_file(model_id: str) -> str:
    return MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES.get(model_id, "beispielergebnis.md")


def golden_example_file(model_dir: Path) -> Path:
    candidates = sorted(model_dir.glob("Golden_Example.*"))
    assert len(candidates) == 1, f"{model_dir.name}: expected exactly one Golden_Example.<ext>, got {candidates}"
    return candidates[0]


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


def expected_base_model_id() -> str:
    plan = read_json(REGISTRATION_PLAN)
    value = str(plan.get("model_params_policy", {}).get("base_model_id") or "").strip()
    assert value, "registration plan must define model_params_policy.base_model_id"
    return value


class OpenWebUIWorkspaceConfigTests(unittest.TestCase):
    def test_every_model_has_required_file_context_and_tool_inventory_prompt(self) -> None:
        model_files = sorted(SINGLE_MODELS.glob("*/model.json"))
        self.assertGreaterEqual(len(model_files), 1)
        expected_base_model = expected_base_model_id()
        skill_ids = {path.stem for path in SKILLS_DIR.glob("*.md") if path.name.upper() != "README.MD"}

        for model_file in model_files:
            with self.subTest(model=model_file.parent.name):
                model_id = model_file.parent.name
                golden_file = golden_example_file(model_file.parent)
                required_file_paths = ["mainprompt.md", "fachwissen.md", golden_file.name]
                for name in required_file_paths:
                    required_file = model_file.parent / name
                    self.assertTrue(required_file.exists(), f"Missing {required_file}")
                    self.assertGreater(required_file.stat().st_size, 0, f"Empty {required_file}")
                legacy_file = model_file.parent / legacy_example_file(model_id)
                self.assertTrue(legacy_file.exists(), f"Missing legacy example {legacy_file}")

                data = read_json(model_file)
                self.assertIsInstance(data, list)
                self.assertEqual(len(data), 1)
                model = data[0]
                meta = model.get("meta", {})
                params = model.get("params", {})
                system = params.get("system", "")

                self.assertEqual(model.get("base_model_id"), expected_base_model)
                self.assertIn("mainprompt.md", system)
                self.assertIn("fachwissen.md", system)
                self.assertIn("Golden_Example", system)
                self.assertIn("Werte alle drei", system)
                self.assertIn("beispiele/", system)
                self.assertIn("Erfinde keine Fakten", system)
                self.assertLessEqual(len(system), 2500)
                self.assertNotIn("## Workbench-Pflichtdateien", system)
                self.assertEqual(params.get("function_calling"), "native")
                self.assertEqual(params.get("reasoning_effort"), "high")
                self.assertEqual(params.get("temperature"), 0.7)
                self.assertEqual(params.get("top_p"), 0.95)
                self.assertIs(params.get("parallel_tool_calls"), True)
                self.assertNotIn("tool_choice", params)
                self.assertNotIn("requiredKnowledgeFiles", meta)
                self.assertEqual(meta.get("requiredFileContextFiles"), required_file_paths)
                self.assertEqual(meta.get("defaultFilterIds", [])[:4], REQUIRED_FILTER_PREFIX)
                file_context = meta.get("workbenchFileContext", {})
                self.assertEqual(file_context.get("schema"), WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA)
                self.assertEqual(file_context.get("injectionFilterId"), WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID)
                self.assertEqual(len(file_context.get("requiredFiles", [])), 3)
                self.assertEqual([item.get("path") for item in file_context.get("requiredFiles", [])], required_file_paths)
                self.assertTrue(all(item.get("attachAsOpenWebUIFile") for item in file_context.get("requiredFiles", [])))
                self.assertTrue(all(item.get("injectAsFullContext") for item in file_context.get("requiredFiles", [])))
                self.assertFalse(any(item.get("useKnowledgeRag") for item in file_context.get("requiredFiles", [])))
                self.assertTrue(all(str(item.get("content", "")).strip() for item in file_context.get("requiredFiles", [])))
                self.assertFalse(any(path in required_file_paths for path in meta.get("exampleKnowledgeFiles", [])))
                self.assertIn(legacy_example_file(model_id), meta.get("exampleKnowledgeFiles", []))
                self.assertTrue(meta.get("capabilities", {}).get("builtin_tools"))
                self.assertTrue(meta.get("capabilities", {}).get("vision"))
                self.assertGreater(len(meta.get("primaryToolIds", [])), 0)
                self.assertGreater(len(meta.get("skillIds", [])), 0)
                self.assertGreater(len(meta.get("recommendedSkillIds", [])), 0)
                self.assertEqual(meta.get("skillIds"), meta.get("recommendedSkillIds"))
                self.assertTrue(set(meta["skillIds"]).issubset(skill_ids))
                self.assertTrue(set(meta["recommendedSkillIds"]).issubset(skill_ids))
                self.assertTrue((model_file.parent / "beispiele").exists())
                self.assertGreater(len(list((model_file.parent / "beispiele").glob("*"))), 0)

    def test_generated_plan_and_summary_track_import_requirements(self) -> None:
        plan = read_json(REGISTRATION_PLAN)
        summary = read_json(MODEL_SUMMARY)
        tools = read_json(TOOL_REGISTRY)
        functions = read_json(FUNCTION_REGISTRY)
        expected_base_model = expected_base_model_id()

        self.assertIn("Tools/import_openwebui_workspace.py", plan.get("api_import_script", ""))
        self.assertIn("scripts/openwebui_workspace_config.yaml", plan.get("api_import_config_file", ""))
        self.assertIn("scripts/openwebui_workspace_config.example.yaml", plan.get("api_import_config_example", ""))
        order = plan.get("order", [])
        self.assertTrue(any(item.endswith("upload_model_required_file_context") for item in order))
        self.assertTrue(any(item.endswith("upload_model_example_knowledge") for item in order))
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
        self.assertEqual(plan.get("model_params_policy", {}).get("base_model_id"), expected_base_model)
        self.assertEqual(plan.get("model_file_context_policy", {}).get("required_files"), ["mainprompt.md", "fachwissen.md", "Golden_Example.<ext>"])
        self.assertEqual(plan.get("model_file_context_policy", {}).get("injection_filter"), WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID)
        self.assertEqual(plan.get("model_example_policy", {}).get("source_dir"), "beispiele/")
        self.assertEqual(plan.get("offline_addons_runtime", {}).get("container_playwright_browsers_path"), "/app/backend/data/cache/ms-playwright")
        self.assertIn(
            "function_valves.context_compressor_filter.reserved_output_tokens",
            plan.get("offline_addons_runtime", {}).get("config_keys", []),
        )
        self.assertEqual(plan.get("global_model_params_recommendation", {}).get("base_model_id"), expected_base_model)
        self.assertTrue(plan.get("global_model_params_recommendation", {}).get("parallel_tool_calls"))
        self.assertGreaterEqual(len(plan.get("skills_before_models", [])), 1)
        self.assertGreaterEqual(len(tools.get("tools", [])), 1)
        self.assertGreaterEqual(len(functions.get("functions", [])), 1)
        self.assertIn(WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID, {item.get("id") for item in functions.get("functions", [])})
        self.assertIn("openwebui-offline-addons", summary.get("openwebui_builtin_and_addon_policy", ""))

        for model in summary.get("models", []):
            with self.subTest(model=model.get("id")):
                self.assertTrue(model.get("has_short_bootloader_systemprompt"))
                self.assertTrue(model.get("vision_enabled"))
                self.assertEqual(model.get("function_calling"), "native")
                self.assertEqual(model.get("params", {}).get("reasoning_effort"), "high")
                self.assertEqual(model.get("params", {}).get("temperature"), 0.7)
                self.assertEqual(model.get("params", {}).get("top_p"), 0.95)
                self.assertIs(model.get("params", {}).get("parallel_tool_calls"), True)
                self.assertLessEqual(model.get("system_prompt_chars", 999999), 2500)
                self.assertEqual(model.get("required_file_context_files", [])[:2], ["mainprompt.md", "fachwissen.md"])
                self.assertTrue(any(str(path).startswith("Golden_Example.") for path in model.get("required_file_context_files", [])))
                self.assertFalse(any(path in {"mainprompt.md", "fachwissen.md"} or str(path).startswith("Golden_Example.") for path in model.get("example_knowledge_files", [])))
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
        self.assertTrue(runtime["model_file_context"]["enabled"])
        self.assertTrue(runtime["model_file_context"]["upload_required_files"])
        self.assertEqual(runtime["model_file_context"]["required_context_filter_id"], WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID)
        self.assertEqual(function_valves[WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID]["priority"], 850)
        self.assertLess(
            function_valves[WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID]["priority"],
            function_valves["context_compressor_filter"]["priority"],
        )
        self.assertEqual(function_valves["context_compressor_filter"]["reserved_output_tokens"], 4096)
        self.assertTrue(function_valves["context_compressor_filter"]["hard_guard_enabled"])


if __name__ == "__main__":
    unittest.main()
