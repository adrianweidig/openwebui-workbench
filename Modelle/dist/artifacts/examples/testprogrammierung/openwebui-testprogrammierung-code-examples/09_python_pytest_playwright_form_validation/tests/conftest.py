from __future__ import annotations

from pathlib import Path


def pytest_configure() -> None:
    # The JUnit XML output directory must exist before pytest opens the report file.
    Path("test-results").mkdir(exist_ok=True)
