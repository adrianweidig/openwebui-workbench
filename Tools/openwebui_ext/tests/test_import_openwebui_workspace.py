from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
IMPORT_SCRIPT = ROOT / "Tools" / "import_openwebui_workspace.py"


def load_import_module():
    spec = importlib.util.spec_from_file_location("test_import_openwebui_workspace_module", IMPORT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeClient:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, str]] = []

    def request(self, method: str, path: str, payload=None, query=None):
        self.calls.append((method, path))
        key = path if not query else f"{path}?{urlencode(query)}"
        result = self.responses.get(key)
        if isinstance(result, Exception):
            raise result
        return result

    def upload_file(self, path: Path, process: bool = True):
        raise AssertionError(f"unexpected upload_file call for {path} with process={process}")


class ImportOpenWebUIWorkspaceTests(unittest.TestCase):
    def test_verify_imported_models_checks_model_and_knowledge_links(self) -> None:
        module = load_import_module()
        client = FakeClient(
            {
                "/api/v1/models/model?id=demo": {
                    "id": "demo",
                    "meta": {"knowledge": [{"id": "knowledge-1", "name": "Modellwissen - Demo"}]},
                }
            }
        )

        module.verify_imported_models(
            client,
            [{"id": "demo", "meta": {"knowledge": [{"id": "knowledge-1", "name": "Modellwissen - Demo"}]}}],
            expect_knowledge=True,
        )

        self.assertIn(("GET", "/api/v1/models/model"), client.calls)

    def test_verify_imported_models_rejects_missing_model(self) -> None:
        module = load_import_module()
        client = FakeClient({"/api/v1/models/model?id=demo": RuntimeError("not found")})

        with self.assertRaisesRegex(RuntimeError, "did not persist models"):
            module.verify_imported_models(client, [{"id": "demo", "meta": {}}], expect_knowledge=False)

    def test_verify_imported_models_rejects_missing_knowledge_link(self) -> None:
        module = load_import_module()
        client = FakeClient({"/api/v1/models/model?id=demo": {"id": "demo", "meta": {"knowledge": []}}})

        with self.assertRaisesRegex(RuntimeError, "Knowledge links"):
            module.verify_imported_models(
                client,
                [{"id": "demo", "meta": {"knowledge": [{"id": "knowledge-1"}]}}],
                expect_knowledge=True,
            )

    def test_import_models_rejects_unexpected_import_response(self) -> None:
        module = load_import_module()
        client = FakeClient({"/api/v1/models/import": "<html>not an api response</html>"})

        with patch.object(
            module,
            "load_models_with_knowledge",
            return_value=module.ModelLoadResult([{"id": "demo", "meta": {}}]),
        ):
            with self.assertRaisesRegex(RuntimeError, "Unexpected OpenWebUI model import response"):
                module.import_models(client, public=False, upload_knowledge=False)

    def test_upsert_knowledge_skips_unchanged_fingerprinted_files(self) -> None:
        module = load_import_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fachwissen.md"
            path.write_text("# Wissen\n\nOffline-Regel.\n", encoding="utf-8")
            fingerprint = module.knowledge_fingerprint([path])
            client = FakeClient(
                {
                    "/api/v1/knowledge/search?query=Modellwissen+-+Demo": {
                        "items": [
                            {
                                "id": "knowledge-1",
                                "name": "Modellwissen - Demo",
                                "description": f"Import-Fingerprint: {fingerprint}",
                            }
                        ]
                    },
                    "/api/v1/knowledge/knowledge-1/update": {"id": "knowledge-1"},
                    "/api/v1/knowledge/knowledge-1/files": [{"id": "file-1"}],
                }
            )

            result = module.upsert_knowledge_with_files(client, "demo", "Demo", [path], public=False)

        self.assertEqual(result.knowledge, {"id": "knowledge-1", "name": "Modellwissen - Demo"})
        self.assertFalse(result.changed)
        self.assertNotIn(("POST", "/api/v1/knowledge/knowledge-1/reset"), client.calls)


if __name__ == "__main__":
    unittest.main()
