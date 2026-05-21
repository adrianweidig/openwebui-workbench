from __future__ import annotations

import asyncio
import importlib.util
import inspect
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FILTERS_DIR = ROOT / "Tools" / "openwebui_ext" / "filters"


class OpenWebUIFilterImportTests(unittest.TestCase):
    def test_filters_are_importable_and_have_async_hooks(self) -> None:
        filter_files = sorted(FILTERS_DIR.glob("*.py"))
        self.assertGreaterEqual(len(filter_files), 1)
        for path in filter_files:
            with self.subTest(filter=path.name):
                spec = importlib.util.spec_from_file_location("test_filter_" + path.stem, path)
                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.loader if spec else None)
                module = importlib.util.module_from_spec(spec)
                assert spec and spec.loader
                spec.loader.exec_module(module)
                self.assertTrue(hasattr(module, "Filter"))
                filter_cls = module.Filter
                hooks = [
                    member
                    for name, member in inspect.getmembers(filter_cls, predicate=inspect.isfunction)
                    if name in {"inlet", "stream", "outlet"}
                ]
                self.assertGreater(len(hooks), 0)
                for hook in hooks:
                    self.assertTrue(inspect.iscoroutinefunction(hook), f"{path.name}:{hook.__name__} is not async")
                    self.assertIsNot(inspect.signature(hook).return_annotation, inspect._empty)

    def test_context_compressor_compresses_long_payload(self) -> None:
        path = FILTERS_DIR / "context_compressor_filter.py"
        spec = importlib.util.spec_from_file_location("test_context_compressor_filter", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        filter_obj = module.Filter()
        filter_obj.valves.default_context_window_tokens = 1200
        filter_obj.valves.trigger_ratio = 0.2
        filter_obj.valves.min_messages_before_compression = 4
        body = {
            "model": "test-model",
            "messages": [
                {"role": "system", "content": "Systemregeln bleiben erhalten."},
                *[
                    {"role": "user" if index % 2 else "assistant", "content": f"Nachricht {index}: " + ("abc " * 200)}
                    for index in range(14)
                ],
            ],
        }
        result = asyncio.run(filter_obj.inlet(body))
        text = "\n".join(str(message.get("content", "")) for message in result["messages"])
        self.assertIn(module.Filter.SUMMARY_MARKER, text)
        self.assertIn("context_compressor_filter", result["metadata"])
        self.assertTrue(result["metadata"]["context_compressor_filter"]["compressed"])
        self.assertLess(len(result["messages"]), 15)

    def test_context_compressor_hard_guard_handles_oversized_single_prompt(self) -> None:
        path = FILTERS_DIR / "context_compressor_filter.py"
        spec = importlib.util.spec_from_file_location("test_context_compressor_filter_hard_guard", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        filter_obj = module.Filter()
        filter_obj.valves.approximate_chars_per_token = 1.0
        filter_obj.valves.default_context_window_tokens = 131072
        filter_obj.valves.reserved_output_tokens = 4096
        filter_obj.valves.safety_margin_tokens = 2048
        huge_prompt = (
            "LETZTE ANWEISUNG: Analysiere diesen uebergrossen Kontext.\n"
            "Traceback: maximum context length exceeded\n"
            + ("x" * 170000)
            + "\nENDE DES KONTEXTS"
        )
        body = {
            "max_tokens": 0,
            "messages": [
                {"role": "system", "content": "Systemregeln bleiben erhalten."},
                {"role": "user", "content": huge_prompt},
            ],
        }
        result = asyncio.run(filter_obj.inlet(body))
        meta = result["metadata"]["context_compressor_filter"]
        text = "\n".join(str(message.get("content", "")) for message in result["messages"])
        self.assertTrue(meta["hard_guard_applied"])
        self.assertTrue(meta["normalized_zero_output_tokens"])
        self.assertLessEqual(meta["estimated_tokens_after"], meta["effective_input_budget_tokens"])
        self.assertNotIn("max_tokens", result)
        self.assertIn("Systemregeln bleiben erhalten.", text)
        self.assertIn(module.Filter.SUMMARY_MARKER, text)
        self.assertIn("LETZTE ANWEISUNG", text)

    def test_context_compressor_removes_zero_output_tokens_but_keeps_positive_values(self) -> None:
        path = FILTERS_DIR / "context_compressor_filter.py"
        spec = importlib.util.spec_from_file_location("test_context_compressor_filter_zero_tokens", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        filter_obj = module.Filter()
        body = {
            "max_tokens": 0,
            "options": {"max_tokens": "0", "num_predict": 0},
            "params": {"max_completion_tokens": 0, "max_new_tokens": 256},
            "payload": {"max_tokens": 0},
            "messages": [{"role": "user", "content": "kurzer Prompt"}],
        }
        result = asyncio.run(filter_obj.inlet(body))
        meta = result["metadata"]["context_compressor_filter"]
        self.assertTrue(meta["normalized_zero_output_tokens"])
        self.assertNotIn("max_tokens", result)
        self.assertNotIn("max_tokens", result["options"])
        self.assertNotIn("num_predict", result["options"])
        self.assertNotIn("max_completion_tokens", result["params"])
        self.assertEqual(result["params"]["max_new_tokens"], 256)
        self.assertNotIn("max_tokens", result["payload"])

    def test_markdown_normalizer_repairs_common_markdown(self) -> None:
        path = FILTERS_DIR / "markdown_normalizer.py"
        spec = importlib.util.spec_from_file_location("test_markdown_normalizer", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        filter_obj = module.Filter()
        body = {"messages": [{"role": "assistant", "content": "#Titel\n| A | B\n```python\nprint('ok')"}]}
        result = asyncio.run(filter_obj.outlet(body))
        content = result["messages"][-1]["content"]
        self.assertIn("# Titel", content)
        self.assertIn("| A | B|", content)
        self.assertEqual(content.count("```"), 2)

    def test_auto_tool_selector_adds_relevant_available_tools(self) -> None:
        path = FILTERS_DIR / "auto_tool_selector.py"
        spec = importlib.util.spec_from_file_location("test_auto_tool_selector", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        filter_obj = module.Filter()
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": "Bitte validiere dieses JSON und erstelle daraus ein Diagramm im Dashboard.",
                }
            ]
        }
        model = {
            "meta": {
                "toolIds": [
                    "json_csv_text_validator",
                    "visuals_toolkit_v4",
                    "parallel_tools",
                ]
            }
        }
        result = asyncio.run(filter_obj.inlet(body, __model__=model))
        self.assertIn("json_csv_text_validator", result["tool_ids"])
        self.assertIn("visuals_toolkit_v4", result["tool_ids"])
        self.assertIn("auto_tool_selector", result["metadata"])


if __name__ == "__main__":
    unittest.main()
