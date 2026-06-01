from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.sync_openwebui_models as model_sync


class OpenWebUIModelSyncTests(unittest.TestCase):
    def test_compare_models_classifies_bidirectional_states(self) -> None:
        identical = {
            "id": "same",
            "name": "Same",
            "base_model_id": "coder",
            "meta": {"description": "unchanged", "knowledge": [{"id": "remote-runtime"}]},
            "params": {"temperature": 0.2},
        }
        local = {
            "same": {
                "id": "same",
                "name": "Same",
                "base_model_id": "coder",
                "meta": {"description": "unchanged"},
                "params": {"temperature": 0.2},
            },
            "workbench-only": {"id": "workbench-only", "name": "Workbench Only"},
            "changed": {
                "id": "changed",
                "name": "Local Name",
                "meta": {"description": "local description"},
            },
            "inactive": {"id": "inactive", "name": "Inactive Local"},
        }
        remote = {
            "same": identical,
            "remote-only": {"id": "remote-only", "name": "Remote Only"},
            "changed": {
                "id": "changed",
                "name": "Remote Name",
                "meta": {"description": "remote description"},
            },
            "inactive": {"id": "inactive", "name": "Inactive Local", "is_active": False},
        }

        status = model_sync.compare_models(local, remote)
        by_id = {item["id"]: item for item in status["items"]}

        self.assertEqual(by_id["same"]["status"], "identical")
        self.assertEqual(by_id["workbench-only"]["status"], "local_only")
        self.assertEqual(by_id["remote-only"]["status"], "remote_only")
        self.assertEqual(by_id["inactive"]["status"], "remote_inactive")
        self.assertEqual(by_id["changed"]["status"], "conflict")
        self.assertIn("name", by_id["changed"]["diff_paths"])
        self.assertIn("meta.description", by_id["changed"]["diff_paths"])
        self.assertIn("no side is overwritten", by_id["changed"]["action"])

    def test_write_snapshot_persists_status_and_remote_models(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            status_file = root / "status.json"
            markdown_file = root / "status.md"
            remote_root = root / "remote_models"
            status = {
                "generated_at": "2026-06-01 12:00:00",
                "total": 1,
                "counts": {"remote_only": 1},
                "items": [{"id": "remote/model", "status": "remote_only", "action": "review"}],
            }

            with (
                patch.object(model_sync, "STATUS_FILE", status_file),
                patch.object(model_sync, "STATUS_MARKDOWN", markdown_file),
                patch.object(model_sync, "REMOTE_MODELS_ROOT", remote_root),
            ):
                model_sync.write_snapshot(status, {"remote/model": {"id": "remote/model", "name": "Remote"}})

            self.assertTrue(status_file.is_file())
            self.assertTrue(markdown_file.is_file())
            self.assertEqual(json.loads(status_file.read_text(encoding="utf-8"))["counts"]["remote_only"], 1)
            self.assertEqual(len(list(remote_root.glob("*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
