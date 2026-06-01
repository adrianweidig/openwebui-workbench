from __future__ import annotations

import argparse
import json
import os
import shlex
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
    env: dict[str, str] | None = None
    requires_docker: bool = False


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
    parser.add_argument(
        "--docker-command",
        type=command_prefix,
        default=["docker"],
        help='docker command prefix for compose checks, for example: "wsl.exe -d Debian -- docker"',
    )
    return parser.parse_args(argv)


def command_prefix(value: str) -> list[str]:
    parts = shlex.split(value)
    if not parts:
        raise argparse.ArgumentTypeError("docker command must not be empty")
    return parts


def build_command_steps(args: argparse.Namespace) -> list[CommandStep]:
    python = sys.executable
    steps = [
        CommandStep("Python syntax compile", [python, "-m", "compileall", "-q", "scripts", "Tools", "Workbench"]),
        CommandStep("German umlaut and UTF-8 check", [python, "scripts/check_german_umlauts.py"]),
        CommandStep("Documentation language pair check", [python, "scripts/check_doc_language_pairs.py"]),
        CommandStep("Security hygiene check", [python, "scripts/check_security_hygiene.py"]),
        CommandStep("Offline data budget check", [python, "scripts/check_offline_data_budget.py"]),
        CommandStep("KnowledgePack validation", [python, "scripts/validate_knowledgepacks.py"]),
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
        docker = list(args.docker_command)
        compose_auth_env = {
            "WEBUI_SECRET_KEY": "verify-only-placeholder",
            "WORKBENCH_AUTH_PASSWORD": "verify-only-placeholder",
            "WORKBENCH_ENTERPRISE_CA_HOST_FILE": "/tmp/workbench-verify-ca.pem",
            "WORKBENCH_AUTH_PASSWORD_HOST_FILE": "/tmp/workbench-auth-password.txt",
            "WORKBENCH_AUTH_PASSWORD_FILE": "/run/secrets/workbench-auth-password",
            "OPENWEBUI_ADMIN_TOKEN_HOST_FILE": "/tmp/openwebui-admin-token.txt",
            "OPENWEBUI_ADMIN_TOKEN_FILE": "/run/secrets/openwebui-admin-token",
        }
        steps.append(
            CommandStep(
                "Docker compose example config",
                [*docker, "compose", "-f", "Deployment/docker-compose.openwebui-offline.example.yml", "config"],
                requires_docker=True,
            )
        )
        steps.append(
            CommandStep(
                "Docker compose workbench config",
                [*docker, "compose", "-f", "Deployment/docker-compose.workbench.yml", "config"],
                env=compose_auth_env,
                requires_docker=True,
            )
        )
        steps.append(
            CommandStep(
                "Docker compose enterprise CA workbench config",
                [
                    *docker,
                    "compose",
                    "-f",
                    "Deployment/docker-compose.workbench.yml",
                    "-f",
                    "Deployment/docker-compose.enterprise-ca.yml",
                    "config",
                ],
                env=compose_auth_env,
                requires_docker=True,
            )
        )
        steps.append(
            CommandStep(
                "Docker compose workbench password-file config",
                [
                    *docker,
                    "compose",
                    "-f",
                    "Deployment/docker-compose.workbench.yml",
                    "-f",
                    "Deployment/docker-compose.workbench-password-file.yml",
                    "config",
                ],
                env=compose_auth_env,
                requires_docker=True,
            )
        )
        steps.append(
            CommandStep(
                "Docker compose OpenWebUI admin-token-file config",
                [
                    *docker,
                    "compose",
                    "-f",
                    "Deployment/docker-compose.workbench.yml",
                    "-f",
                    "Deployment/docker-compose.openwebui-admin-token-file.yml",
                    "config",
                ],
                env=compose_auth_env,
                requires_docker=True,
            )
        )
        steps.append(
            CommandStep(
                "Docker compose top.secret workbench config",
                [
                    *docker,
                    "compose",
                    "-f",
                    "Deployment/docker-compose.workbench.yml",
                    "-f",
                    "Deployment/docker-compose.top-secret.yml",
                    "config",
                ],
                env=compose_auth_env,
                requires_docker=True,
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


def _clean_command_output(output: str) -> str:
    return " ".join(output.replace("\x00", "").split())


def _looks_like_disabled_wsl_service(output: str) -> bool:
    normalized = _clean_command_output(output).lower()
    return "wsl/0x80070422" in normalized or (
        "dienst" in normalized and "deaktiviert" in normalized
    )


def _run_docker_step(step: CommandStep, env: dict[str, str] | None) -> StepResult:
    completed = subprocess.run(step.command, cwd=ROOT, env=env, capture_output=True, text=True)
    stdout = _clean_command_output(completed.stdout)
    stderr = _clean_command_output(completed.stderr)
    if stdout:
        print(stdout, flush=True)
    if stderr:
        print(stderr, flush=True)
    if completed.returncode == 0:
        return StepResult(step.label, "Erfolgreich")

    combined_output = f"{stdout} {stderr}"
    if _looks_like_disabled_wsl_service(combined_output):
        return StepResult(
            step.label,
            "Fehlgeschlagen",
            "WSLService ist deaktiviert oder nicht erreichbar; Docker-Compose-Prüfung über WSL kann nicht laufen",
        )
    return StepResult(step.label, "Fehlgeschlagen", f"Exit-Code {completed.returncode}")


def run_command_step(step: CommandStep) -> StepResult:
    if step.requires_docker and shutil.which(step.command[0]) is None:
        detail = f"{step.command[0]} ist in dieser Umgebung nicht verfügbar"
        if step.command[0] == "docker":
            detail = "docker ist in dieser Umgebung nicht verfügbar"
        if os.name == "nt" and shutil.which("wsl.exe"):
            detail += "; wsl.exe ist verfügbar, Docker-Compose-Prüfungen können aus einer WSL-Umgebung mit Docker erneut ausgeführt werden"
        return StepResult(step.label, "Übersprungen", detail)

    print(f"\n## {step.label}", flush=True)
    print(" ".join(step.command), flush=True)
    env = None
    if step.env:
        env = dict(os.environ)
        env.update(step.env)
    if step.requires_docker:
        return _run_docker_step(step, env)
    completed = subprocess.run(step.command, cwd=ROOT, env=env)
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
