from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
PRODUCT_I18N_MANIFEST = ROOT / "Modelle" / "i18n" / "product-locales.json"


class ModelProductI18nTests(unittest.TestCase):
    def test_product_locale_manifest_covers_common_languages(self) -> None:
        manifest = json.loads(PRODUCT_I18N_MANIFEST.read_text(encoding="utf-8"))
        locales = [item["code"] for item in manifest["locales"]]
        self.assertGreaterEqual(len(locales), 10)
        self.assertEqual(locales[:2], ["de", "en"])
        for locale in ["es", "fr", "pt-BR", "it", "nl", "pl", "tr", "ja", "zh-Hans"]:
            self.assertIn(locale, locales)

    def test_each_model_has_complete_product_i18n_profiles(self) -> None:
        manifest = json.loads(PRODUCT_I18N_MANIFEST.read_text(encoding="utf-8"))
        locales = [item["code"] for item in manifest["locales"]]
        for model_json in sorted(SINGLE_MODELS.glob("*/model.json")):
            data = json.loads(model_json.read_text(encoding="utf-8"))
            model = data[0]
            meta = model.get("meta", {})
            with self.subTest(model=model_json.parent.name):
                self.assertEqual(meta.get("defaultLocale"), "de")
                self.assertEqual(meta.get("fallbackLocale"), "en")
                self.assertEqual(meta.get("supportedLocales"), locales)
                self.assertEqual(sorted(meta.get("productI18n", {})), sorted(locales))
                for locale in locales:
                    profile = model_json.parent / "i18n" / f"{locale}.md"
                    self.assertTrue(profile.is_file(), profile)
                    self.assertGreater(profile.stat().st_size, 0)
                    entry = meta["productI18n"][locale]
                    self.assertEqual(entry["profile"], f"i18n/{locale}.md")
                    self.assertTrue(entry["name"].strip())
                    self.assertTrue(entry["description"].strip())
                combined_text = "\n".join(
                    (model_json.parent / "i18n" / f"{locale}.md").read_text(encoding="utf-8")
                    for locale in locales
                )
                self.assertIn("ä", combined_text)
                self.assertIn("日本語", combined_text)
                self.assertIn("简体中文", combined_text)


if __name__ == "__main__":
    unittest.main()
