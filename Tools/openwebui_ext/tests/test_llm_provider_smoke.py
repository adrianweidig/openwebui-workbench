import io
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

    def test_provider_error_redaction_masks_keys_and_auth_fragments(self):
        old_env = os.environ.copy()
        try:
            os.environ.clear()
            sentinel_one = "secret" + "-test-value"
            sentinel_two = "another" + "-secret-value"
            sentinel_three = "query" + "-secret-value"
            os.environ["OPENROUTER_API_KEY"] = sentinel_one
            rendered = smoke._redact_secrets(
                f"Authorization: Bearer {sentinel_one}; "
                f"x-goog-api-key={sentinel_two}; "
                f"https://api.example.invalid/v1?key={sentinel_three}"
            )
            self.assertNotIn(sentinel_one, rendered)
            self.assertNotIn(sentinel_two, rendered)
            self.assertNotIn(sentinel_three, rendered)
            self.assertIn("Authorization: Bearer [REDACTED]", rendered)
            self.assertIn("x-goog-api-key=[REDACTED]", rendered)
            self.assertIn("?key=[REDACTED]", rendered)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_http_error_body_is_redacted_before_surface(self):
        old_env = os.environ.copy()
        try:
            os.environ.clear()
            os.environ["OPENROUTER_API_KEY"] = "secret-test-value"
            error = smoke.urllib.error.HTTPError(
                "https://api.example.invalid/v1/chat/completions",
                401,
                "Unauthorized",
                {},
                io.BytesIO(b'{"error":"secret-test-value Authorization: Bearer echoed-secret"}'),
            )
            with patch.object(smoke.urllib.request, "urlopen", side_effect=error):
                with self.assertRaises(smoke.SmokeError) as raised:
                    smoke._request_json(
                        "https://api.example.invalid/v1/chat/completions",
                        {"Authorization": "Bearer secret-test-value"},
                        {"messages": []},
                        5,
                    )
            rendered = str(raised.exception)
            self.assertNotIn("secret-test-value", rendered)
            self.assertNotIn("echoed-secret", rendered)
            self.assertIn("[REDACTED]", rendered)
        finally:
            os.environ.clear()
            os.environ.update(old_env)


if __name__ == "__main__":
    unittest.main()
