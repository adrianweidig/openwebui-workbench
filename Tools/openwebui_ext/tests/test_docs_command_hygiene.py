from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DOCS_WITH_COMPOSE_COMMANDS = [
    ROOT / "README.md",
    ROOT / "README.en.md",
    ROOT / "Deployment" / "README.md",
    ROOT / "Workbench" / "README.md",
    ROOT / "docs" / "WORKBENCH_DASHBOARD.md",
    ROOT / "docs" / "en" / "WORKBENCH_DASHBOARD.md",
    ROOT / "TESTING.md",
]
WORKBENCH_COMPOSE_WITHOUT_ENV_FILE_RE = re.compile(
    r"docker compose\s+(?![^\n]*--env-file\s+\.env\b)[^\n]*-f\s+Deployment/docker-compose\.workbench\.yml"
)


class DocsCommandHygieneTests(unittest.TestCase):
    def test_workbench_compose_commands_use_env_file(self) -> None:
        for path in DOCS_WITH_COMPOSE_COMMANDS:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(WORKBENCH_COMPOSE_WITHOUT_ENV_FILE_RE.search(text))


if __name__ == "__main__":
    unittest.main()
