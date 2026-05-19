from __future__ import annotations

import importlib.util
import inspect
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS_DIR = ROOT / "Tools" / "openwebui_ext" / "tools"


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


if __name__ == "__main__":
    unittest.main()
