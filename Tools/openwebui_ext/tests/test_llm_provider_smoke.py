import os
import unittest
from unittest.mock import patch

from scripts import run_llm_provider_smoke as smoke


class LlmProviderSmokeTest(unittest.TestCase):
    def test_rejects_localhost_provider_base_url(self):
        with self.assertRaisesRegex(smoke.SmokeError, "refusing local model endpoint"):
            smoke._reject_local_base_url("http://localhost:11434/v1")

    def test_rejects_internal_docker_name_provider_base_url(self):
        with self.assertRaisesRegex(smoke.SmokeError, "refusing local model endpoint"):
            smoke._reject_local_base_url("http://ragflow/v1")

    def test_rejects_top_secret_provider_base_url(self):
        with self.assertRaisesRegex(smoke.SmokeError, "refusing local model endpoint"):
            smoke._reject_local_base_url("https://openwebui.top.secret/v1")

    def test_auto_selects_external_provider_key_without_printing_secret(self):
        old_env = os.environ.copy()
        try:
            os.environ.clear()
            os.environ["OPENROUTER_API_KEY"] = "secret-test-value"
            provider = smoke._select_provider("auto")
            self.assertIsNotNone(provider)
            self.assertEqual(provider.name, "openrouter")
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_skip_when_no_provider_key_and_not_required(self):
        old_env = os.environ.copy()
        try:
            os.environ.clear()
            args = smoke.parse_args([])
            result = smoke.run_smoke(args)
            self.assertTrue(result["skipped"])
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_gemini_uses_api_key_header_not_url_query(self):
        old_env = os.environ.copy()
        try:
            os.environ.clear()
            os.environ["GEMINI_API_KEY"] = "secret-test-value"
            provider = smoke.PROVIDERS["gemini"]
            with patch.object(smoke, "_request_json", return_value=(200, {"candidates": []})) as request_json:
                smoke._run_gemini(
                    provider,
                    "https://generativelanguage.googleapis.com/v1beta",
                    "gemini-2.5-pro",
                    "Return exactly: OK",
                    5,
                )
            url, headers, _payload, _timeout = request_json.call_args.args
            self.assertNotIn("secret-test-value", url)
            self.assertNotIn("?key=", url)
            self.assertEqual(headers["x-goog-api-key"], "secret-test-value")
        finally:
            os.environ.clear()
            os.environ.update(old_env)


if __name__ == "__main__":
    unittest.main()
