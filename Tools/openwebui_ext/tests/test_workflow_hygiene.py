from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class WorkflowHygieneTests(unittest.TestCase):
    def test_release_artifact_workflow_runs_on_pull_requests(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release-artifact.yml").read_text(encoding="utf-8")

        self.assertIn("pull_request:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertRegex(workflow, r"pull_request:\s*\n\s*branches:\s*\n\s*-\s+main")

    def test_release_artifact_workflow_sanitizes_ref_names(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release-artifact.yml").read_text(encoding="utf-8")

        self.assertIn("safe_branch=", workflow)
        self.assertIn("artifact_name=${root_dir}", workflow)
        self.assertIn("name: ${{ steps.package.outputs.artifact_name }}", workflow)
        self.assertNotIn("name: openwebui-workbench-${{ github.ref_name }}", workflow)


if __name__ == "__main__":
    unittest.main()
