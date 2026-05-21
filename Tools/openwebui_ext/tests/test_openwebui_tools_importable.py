from __future__ import annotations

import importlib.util
import inspect
import json
import unittest
from pathlib import Path
from typing import Any, get_type_hints

from pydantic import create_model


ROOT = Path(__file__).resolve().parents[3]
TOOLS_DIR = ROOT / "Tools" / "openwebui_ext" / "tools"
TOOL_IMPORT = ROOT / "Tools" / "dist" / "openwebui-tools-import.json"
OFFLINE_TOOL_IMPORT = ROOT / "Tools" / "dist" / "openwebui-tools-offline-import.json"
FUNCTION_IMPORT = ROOT / "Tools" / "dist" / "openwebui-functions-import.json"


class OpenWebUIToolImportTests(unittest.TestCase):
    def test_tools_are_importable_and_have_async_methods(self) -> None:
        tool_files = sorted(TOOLS_DIR.glob("*.py"))
        self.assertGreaterEqual(len(tool_files), 7)
        for path in tool_files:
            with self.subTest(tool=path.name):
                spec = importlib.util.spec_from_file_location("test_tool_" + path.stem, path)
                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.loader if spec else None)
                module = importlib.util.module_from_spec(spec)
                assert spec and spec.loader
                spec.loader.exec_module(module)
                self.assertTrue(hasattr(module, "Tools"))
                tools_cls = module.Tools
                methods = [
                    member
                    for name, member in inspect.getmembers(tools_cls, predicate=inspect.isfunction)
                    if not name.startswith("_") and name != "__init__"
                ]
                self.assertGreater(len(methods), 0)
                for method in methods:
                    self.assertTrue(inspect.iscoroutinefunction(method), f"{path.name}:{method.__name__} is not async")
                    signature = inspect.signature(method)
                    for param_name, param in signature.parameters.items():
                        if param_name == "self" or param_name.startswith("__"):
                            continue
                        self.assertIsNot(param.annotation, inspect._empty, f"{path.name}:{method.__name__}:{param_name} lacks annotation")
                    self.assertIsNot(signature.return_annotation, inspect._empty, f"{path.name}:{method.__name__} lacks return annotation")

    def test_tools_match_openwebui_gui_schema_generation(self) -> None:
        for path in [ROOT / "Tools" / "jupyter" / "jupyter_tool.py", *sorted(TOOLS_DIR.glob("*.py"))]:
            with self.subTest(tool=path.name):
                spec = importlib.util.spec_from_file_location("test_gui_tool_" + path.stem, path)
                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.loader if spec else None)
                module = importlib.util.module_from_spec(spec)
                assert spec and spec.loader
                spec.loader.exec_module(module)
                instance = module.Tools()
                methods = [
                    member
                    for name, member in inspect.getmembers(instance, predicate=callable)
                    if not name.startswith("_") and not inspect.isclass(member)
                ]
                self.assertGreater(len(methods), 0)
                for method in methods:
                    fields = {}
                    hints = get_type_hints(method)
                    for name, param in inspect.signature(method).parameters.items():
                        default = param.default if param.default is not param.empty else ...
                        fields[name] = (hints.get(name, Any), default)
                    model = create_model(method.__name__, **fields)
                    model.model_json_schema()

    def test_gui_import_bundles_have_openwebui_tool_form_shape(self) -> None:
        for bundle, expected_class in [
            (TOOL_IMPORT, "class Tools"),
            (OFFLINE_TOOL_IMPORT, "class Tools"),
            (FUNCTION_IMPORT, "class Filter"),
        ]:
            with self.subTest(bundle=bundle.name):
                data = json.loads(bundle.read_text(encoding="utf-8"))
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)
                seen = set()
                for item in data:
                    self.assertIsInstance(item, dict)
                    self.assertIsInstance(item.get("id"), str)
                    self.assertTrue(item["id"].isidentifier(), item["id"])
                    self.assertEqual(item["id"], item["id"].lower())
                    self.assertNotIn(item["id"], seen)
                    seen.add(item["id"])
                    self.assertIsInstance(item.get("name"), str)
                    self.assertIsInstance(item.get("content"), str)
                    self.assertIn(expected_class, item["content"])
                    self.assertIsInstance(item.get("meta"), dict)
                    self.assertIsInstance(item["meta"].get("description"), str)
                    if bundle == FUNCTION_IMPORT:
                        self.assertIn(item.get("type"), {"filter", "action", "pipe"})


if __name__ == "__main__":
    unittest.main()
