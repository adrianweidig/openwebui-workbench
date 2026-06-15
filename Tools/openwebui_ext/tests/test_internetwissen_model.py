from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "Modelle" / "einzelmodelle" / "internetwissen"
DIST_IMPORT = ROOT / "Modelle" / "dist" / "openwebui-models-import.json"
FORBIDDEN_NETWORK_TOOLS = {
    "safe_http_fetcher",
    "github_repo_inspector",
    "web_search_and_crawl",
    "openui_generative_ui",
    "mediawiki_legacy_crawler",
}


class InternetwissenModelContractTest(unittest.TestCase):
    def load_model(self) -> dict:
        data = json.loads((MODEL_DIR / "model.json").read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIsInstance(data[0], dict)
        return data[0]

    def test_model_profile_is_offline(self) -> None:
        model = self.load_model()
        self.assertEqual(model.get("id"), "internetwissen")
        meta = model.get("meta", {})
        capabilities = meta.get("capabilities", {})
        self.assertIs(capabilities.get("web_search"), False)
        tool_ids = set(meta.get("toolIds", []))
        primary_tool_ids = set(meta.get("primaryToolIds", []))
        self.assertFalse(tool_ids & FORBIDDEN_NETWORK_TOOLS)
        self.assertFalse(primary_tool_ids & FORBIDDEN_NETWORK_TOOLS)

    def test_required_file_context_files_exist(self) -> None:
        golden = sorted(MODEL_DIR.glob("Golden_Example.*"))
        self.assertEqual(len(golden), 1)
        for name in ["mainprompt.md", "fachwissen.md", golden[0].name]:
            self.assertTrue((MODEL_DIR / name).is_file(), name)
        self.assertTrue((MODEL_DIR / "beispielergebnis.md").is_file())

    def test_examples_and_i18n_exist(self) -> None:
        examples = sorted((MODEL_DIR / "beispiele").glob("*.md"))
        self.assertGreaterEqual(len(examples), 5)
        self.assertTrue((MODEL_DIR / "i18n" / "manifest.json").is_file())
        self.assertTrue((MODEL_DIR / "i18n" / "de.md").is_file())
        self.assertTrue((MODEL_DIR / "i18n" / "en.md").is_file())

    def test_examples_do_not_claim_live_web_verification(self) -> None:
        banned_phrases = [
            "ich habe die website geprüft",
            "ich habe live geprüft",
            "laut aktueller websuche",
            "die neueste version ist",
        ]
        for path in [MODEL_DIR / "beispielergebnis.md", *sorted((MODEL_DIR / "beispiele").glob("*.md"))]:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in banned_phrases:
                self.assertNotIn(phrase, text, path.as_posix())

    def test_dist_import_contains_internetwissen(self) -> None:
        data = json.loads(DIST_IMPORT.read_text(encoding="utf-8"))
        models = data.get("models") if isinstance(data, dict) else data
        self.assertIsInstance(models, list)
        self.assertIn("internetwissen", {item.get("id") for item in models if isinstance(item, dict)})


if __name__ == "__main__":
    unittest.main()
