from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
LLM_PROVIDER_LOADER = Path.home() / ".codex" / "local-secrets" / "llm-providers" / "Invoke-WithLlmProviderEnv.ps1"


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
    parser.add_argument(
        "--include-llm-provider-smoke",
        action="store_true",
        help="run an explicit live LLM smoke test through external provider keys only; local model endpoints are refused",
    )
    parser.add_argument(
        "--require-llm-provider-smoke",
        action="store_true",
        help="make the live LLM provider smoke fail instead of skip when no external provider key is available",
    )
    parser.add_argument(
        "--llm-provider",
        default=os.environ.get("LLM_PROVIDER_SMOKE_PROVIDER", "auto"),
        help="external provider for the live LLM smoke, for example openrouter or gemini",
    )
    parser.add_argument(
        "--llm-provider-model",
        default=os.environ.get("LLM_PROVIDER_SMOKE_MODEL", ""),
        help="hosted provider model ID for the live LLM smoke; defaults to the provider's strong model",
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
    if args.include_llm_provider_smoke:
        steps.append(
            CommandStep(
                "External LLM provider smoke",
                llm_provider_smoke_command(
                    python,
                    provider=args.llm_provider,
                    model=args.llm_provider_model,
                    require=args.require_llm_provider_smoke,
                ),
            )
        )
    if args.include_docker_compose:
        docker = list(args.docker_command)
        verify_host_path = lambda name: str(PurePosixPath("/", "tmp", name))
        compose_auth_env = {
            "WEBUI_SECRET_KEY": "verify-only-placeholder",
            "WORKBENCH_AUTH_PASSWORD": "verify-only-placeholder",
            "WORKBENCH_ENTERPRISE_CA_HOST_FILE": verify_host_path("workbench-verify-ca.pem"),
            "WORKBENCH_AUTH_PASSWORD_HOST_FILE": verify_host_path("workbench-auth-password.txt"),
            "WORKBENCH_AUTH_PASSWORD_FILE": "/run/secrets/workbench-auth-password",
            "OPENWEBUI_ADMIN_TOKEN_HOST_FILE": verify_host_path("openwebui-admin-token.txt"),
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
                "Docker compose shared-targets workbench config",
                [*docker, "compose", "-f", "Deployment/docker-compose.shared-targets.yml", "config"],
                env={
                    **compose_auth_env,
                    "WORKBENCH_SHARED_DOCKER_NETWORK": "ki_infra_seu_test",
                    "OPENWEBUI_BASE_URL": "http://openwebui:8080",
                    "OPENWEBUI_PUBLIC_URL": "https://openwebui.top.secret",
                    "RAGFLOW_BASE_URL": "http://ragflow",
                    "SEAFILE_BASE_URL": "http://seafile",
                    "PORTAINER_URL": "http://portainer:9000",
                },
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
                "Docker compose combined secret-file config",
                [
                    *docker,
                    "compose",
                    "-f",
                    "Deployment/docker-compose.workbench.yml",
                    "-f",
                    "Deployment/docker-compose.workbench-password-file.yml",
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


def llm_provider_smoke_command(python: str, *, provider: str, model: str, require: bool) -> list[str]:
    smoke_command = [python, "scripts/run_llm_provider_smoke.py", "--provider", provider]
    if model:
        smoke_command.extend(["--model", model])
    if require:
        smoke_command.append("--require")
    if os.name == "nt" and LLM_PROVIDER_LOADER.is_file():
        command_array = ", ".join(powershell_literal(part) for part in smoke_command)
        invoke_command = f"& {powershell_literal(str(LLM_PROVIDER_LOADER))} -All -Command @({command_array})"
        return [
            powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            invoke_command,
        ]
    return smoke_command


def powershell_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def powershell_executable() -> str:
    return shutil.which("pwsh") or shutil.which("pwsh.exe") or "powershell"


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


def _command_with_wsl_env(command: Sequence[str], env: dict[str, str] | None) -> list[str]:
    if not env or not command:
        return list(command)
    if Path(command[0]).name.lower() not in {"wsl", "wsl.exe"}:
        return list(command)
    try:
        separator_index = list(command).index("--")
    except ValueError:
        return list(command)
    assignments = [f"{key}={value}" for key, value in sorted(env.items())]
    return [*command[: separator_index + 1], "env", *assignments, *command[separator_index + 1 :]]


def _run_docker_step(step: CommandStep, env: dict[str, str] | None) -> StepResult:
    command = _command_with_wsl_env(step.command, step.env)
    completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
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
