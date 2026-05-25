from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CommandStep:
    label: str
    command: list[str]


@dataclass(frozen=True)
class StepResult:
    label: str
    status: str
    detail: str = ""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local OpenWebUI workspace verification suite.")
    parser.add_argument(
        "--include-docker-compose",
        action="store_true",
        help="also validate the example compose file with `docker compose config` when Docker is available",
    )
    parser.add_argument(
        "--skip-unit-tests",
        action="store_true",
        help="skip unittest discovery for faster diagnosis runs",
    )
    return parser.parse_args(argv)


def build_command_steps(args: argparse.Namespace) -> list[CommandStep]:
    python = sys.executable
    steps = [
        CommandStep("Python syntax compile", [python, "-m", "compileall", "-q", "scripts", "Tools", "Workbench"]),
        CommandStep("German umlaut and UTF-8 check", [python, "scripts/check_german_umlauts.py"]),
        CommandStep("OpenWebUI extension validation", [python, "scripts/validate_openwebui_extensions.py"]),
        CommandStep("Tool/model generator check", [python, "scripts/configure_openwebui_tool_models.py", "--check"]),
        CommandStep(
            "OpenWebUI import dry-run",
            [python, "Tools/import_openwebui_workspace.py", "--dry-run", "--config", "scripts/openwebui_workspace_config.example.yaml"],
        ),
    ]
    if not args.skip_unit_tests:
        steps.append(CommandStep("Unit tests", [python, "-m", "unittest", "discover", "Tools.openwebui_ext.tests"]))
        steps.append(CommandStep("Workbench dashboard tests", [python, "-m", "unittest", "discover", "Workbench.dashboard.tests"]))
    if args.include_docker_compose:
        steps.append(CommandStep("Docker compose example config", ["docker", "compose", "-f", "Deployment/docker-compose.openwebui-offline.example.yml", "config"]))
        steps.append(CommandStep("Docker compose workbench config", ["docker", "compose", "-f", "Deployment/docker-compose.workbench.yml", "config"]))
        steps.append(
            CommandStep(
                "Docker compose top.secret workbench config",
                [
                    "docker",
                    "compose",
                    "-f",
                    "Deployment/docker-compose.workbench.yml",
                    "-f",
                    "Deployment/docker-compose.top-secret.yml",
                    "config",
                ],
            )
        )
    return steps


def iter_json_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.json")):
        if ".git" in path.parts:
            continue
        yield path


def validate_json_files(root: Path) -> StepResult:
    checked = 0
    for path in iter_json_files(root):
        checked += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rel = path.relative_to(root).as_posix()
            return StepResult("JSON validation", "Fehlgeschlagen", f"{rel}: {type(exc).__name__}: {exc}")
    return StepResult("JSON validation", "Erfolgreich", f"{checked} JSON-Dateien gelesen")


def run_command_step(step: CommandStep) -> StepResult:
    if step.command[0] == "docker" and shutil.which("docker") is None:
        return StepResult(step.label, "Übersprungen", "docker ist in dieser Umgebung nicht verfügbar")

    print(f"\n## {step.label}", flush=True)
    print(" ".join(step.command), flush=True)
    completed = subprocess.run(step.command, cwd=ROOT)
    if completed.returncode != 0:
        return StepResult(step.label, "Fehlgeschlagen", f"Exit-Code {completed.returncode}")
    return StepResult(step.label, "Erfolgreich")


def print_summary(results: list[StepResult]) -> None:
    print("\n# Verification summary")
    for result in results:
        detail = f" - {result.detail}" if result.detail else ""
        print(f"- {result.status}: {result.label}{detail}")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    results: list[StepResult] = []

    for step in build_command_steps(args):
        result = run_command_step(step)
        results.append(result)
        if result.status == "Fehlgeschlagen":
            print_summary(results)
            return 1
        if result.status == "Übersprungen":
            print(f"\n## {step.label}\n{result.detail}", flush=True)

    results.append(validate_json_files(ROOT))
    print_summary(results)
    return 1 if any(result.status == "Fehlgeschlagen" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
