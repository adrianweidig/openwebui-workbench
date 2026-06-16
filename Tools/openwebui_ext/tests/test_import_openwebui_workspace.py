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

    def request_any(self, method: str, paths: list[str], payload=None, query=None, expected=(200,)):
        last_result = None
        for path in paths:
            last_result = self.request(method, path, payload=payload, query=query)
            if last_result is not None:
                return last_result
        return last_result

    def upload_file(self, path: Path, process: bool = True):
        raise AssertionError(f"unexpected upload_file call for {path} with process={process}")


class ImportOpenWebUIWorkspaceTests(unittest.TestCase):
    def test_verify_imported_models_checks_model_and_knowledge_links(self) -> None:
        module = load_import_module()
        client = FakeClient(
            {
                "/api/v1/models/model?id=demo": {
                    "id": "demo",
                    "meta": {
                        "knowledge": [{"id": "knowledge-1", "name": "Modellwissen - Demo"}],
                        "skillIds": ["code-review-deep"],
                    },
                }
            }
        )

        module.verify_imported_models(
            client,
            [{"id": "demo", "meta": {"knowledge": [{"id": "knowledge-1", "name": "Modellwissen - Demo"}], "skillIds": ["code-review-deep"]}}],
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

    def test_verify_imported_models_rejects_missing_skill_link(self) -> None:
        module = load_import_module()
        client = FakeClient({"/api/v1/models/model?id=demo": {"id": "demo", "meta": {"skillIds": []}}})

        with self.assertRaisesRegex(RuntimeError, "Skill links"):
            module.verify_imported_models(
                client,
                [{"id": "demo", "meta": {"skillIds": ["code-review-deep"]}}],
                expect_knowledge=False,
            )

    def test_verify_imported_models_checks_required_file_context_links(self) -> None:
        module = load_import_module()
        file_context = {
            "requiredFiles": [
                {"filename": "mainprompt.md", "path": "mainprompt.md"},
                {"filename": "fachwissen.md", "path": "fachwissen.md"},
                {"filename": "Golden_Example.md", "path": "Golden_Example.md"},
            ],
            "uploadedFiles": [
                {"filename": "mainprompt.md", "fileId": "file-main"},
                {"filename": "fachwissen.md", "fileId": "file-knowledge"},
                {"filename": "Golden_Example.md", "fileId": "file-golden"},
            ],
        }
        client = FakeClient({"/api/v1/models/model?id=demo": {"id": "demo", "meta": {"workbenchFileContext": file_context}}})

        module.verify_imported_models(
            client,
            [{"id": "demo", "meta": {"workbenchFileContext": file_context}}],
            expect_knowledge=False,
        )

    def test_verify_imported_models_rejects_missing_required_file_context_links(self) -> None:
        module = load_import_module()
        expected_context = {
            "requiredFiles": [
                {"filename": "mainprompt.md", "path": "mainprompt.md"},
                {"filename": "fachwissen.md", "path": "fachwissen.md"},
                {"filename": "Golden_Example.md", "path": "Golden_Example.md"},
            ],
            "uploadedFiles": [{"filename": "mainprompt.md", "fileId": "file-main"}],
        }
        client = FakeClient(
            {
                "/api/v1/models/model?id=demo": {
                    "id": "demo",
                    "meta": {"workbenchFileContext": {"requiredFiles": expected_context["requiredFiles"], "uploadedFiles": []}},
                }
            }
        )

        with self.assertRaisesRegex(RuntimeError, "required file context links"):
            module.verify_imported_models(
                client,
                [{"id": "demo", "meta": {"workbenchFileContext": expected_context}}],
                expect_knowledge=False,
            )

    def test_verify_imported_models_rejects_required_files_in_knowledge(self) -> None:
        module = load_import_module()
        file_context = {
            "requiredFiles": [
                {"filename": "mainprompt.md", "path": "mainprompt.md"},
                {"filename": "fachwissen.md", "path": "fachwissen.md"},
                {"filename": "Golden_Example.md", "path": "Golden_Example.md"},
            ],
            "uploadedFiles": [{"filename": "mainprompt.md", "fileId": "file-main"}],
        }
        client = FakeClient(
            {
                "/api/v1/models/model?id=demo": {
                    "id": "demo",
                    "meta": {
                        "knowledge": [{"id": "knowledge-1", "name": "Modellwissen - Demo"}],
                        "workbenchFileContext": file_context,
                    },
                },
                "/api/v1/knowledge/knowledge-1": {"files": [{"filename": "mainprompt.md"}]},
            }
        )

        with self.assertRaisesRegex(RuntimeError, "Knowledge/RAG"):
            module.verify_imported_models(
                client,
                [
                    {
                        "id": "demo",
                        "meta": {
                            "knowledge": [{"id": "knowledge-1"}],
                            "workbenchFileContext": file_context,
                        },
                    }
                ],
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
                module.import_models(
                    client,
                    public=False,
                    upload_knowledge=False,
                    runtime={"model_file_context": {"enabled": False, "upload_required_files": False}},
                )

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

    def test_upsert_knowledge_resets_fingerprinted_collection_with_extra_files(self) -> None:
        module = load_import_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "beispiel.md"
            path.write_text("# Beispiel\n", encoding="utf-8")
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
                    "/api/v1/knowledge/knowledge-1/files": [{"id": "file-1"}, {"id": "file-extra"}],
                    "/api/v1/knowledge/knowledge-1/reset": {"ok": True},
                    "/api/v1/knowledge/knowledge-1/files/batch/add": {"ok": True},
                    "/api/v1/knowledge/knowledge-1": {"files": [{"id": "file-new"}]},
                }
            )

            with patch.object(client, "upload_file", return_value={"id": "file-new"}):
                result = module.upsert_knowledge_with_files(client, "demo", "Demo", [path], public=False)

        self.assertTrue(result.changed)
        self.assertIn(("POST", "/api/v1/knowledge/knowledge-1/reset"), client.calls)

    def test_import_prompts_updates_existing_prompt_by_command(self) -> None:
        module = load_import_module()
        client = FakeClient(
            {
                "/api/v1/prompts/command/demo-prompt": {"id": "prompt-1", "command": "demo-prompt"},
                "/api/v1/prompts/id/prompt-1/update": {"id": "prompt-1"},
                "/api/v1/prompts/id/prompt-1/access/update": {"access_grants": [module.PUBLIC_READ_GRANT]},
            }
        )
        records = [
            {
                "id": "demo-prompt",
                "command": "demo-prompt",
                "name": "Demo Prompt",
                "content": "Nutze diese Promptvorlage für einen Importtest.\n",
                "data": {"source_file": "Tools/openwebui_ext/prompts/demo-prompt.md"},
                "meta": {"description": "Demo"},
                "tags": ["workbench"],
            }
        ]

        with patch.object(module, "load_prompt_records", return_value=records):
            result = module.import_prompts(client, public=True)

        self.assertEqual(result.updated, 1)
        self.assertIn(("GET", "/api/v1/prompts/command/demo-prompt"), client.calls)
        self.assertIn(("POST", "/api/v1/prompts/id/prompt-1/update"), client.calls)
        self.assertIn(("POST", "/api/v1/prompts/id/prompt-1/access/update"), client.calls)


if __name__ == "__main__":
    unittest.main()
