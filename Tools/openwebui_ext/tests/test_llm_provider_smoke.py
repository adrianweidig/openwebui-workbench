import os
import unittest

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


if __name__ == "__main__":
    unittest.main()
