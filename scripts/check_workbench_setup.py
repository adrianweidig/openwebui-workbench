from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from urllib.parse import ParseResult, urlparse

try:
    from scripts import init_workbench_env
except ModuleNotFoundError:  # pragma: no cover - direct script execution from scripts/
    import init_workbench_env  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "Deployment" / "workbench.env.example"
DEFAULT_ENV_FILE = ROOT / ".env"
DEFAULT_COMPOSE_FILE = ROOT / "Deployment" / "docker-compose.workbench.yml"
BOOLEAN_DEFAULTS = {
    "OPENWEBUI_TLS_VERIFY": "true",
    "WORKBENCH_ALLOW_WRITE": "true",
    "WEBUI_AUTH": "true",
    "DO_NOT_TRACK": "true",
    "SCARF_NO_ANALYTICS": "true",
    "ANONYMIZED_TELEMETRY": "false",
}
INTEGER_DEFAULTS = {
    "WORKBENCH_COMMAND_TIMEOUT_SECONDS": 300,
    "WORKBENCH_IMPORT_TIMEOUT_SECONDS": 1800,
    "WORKBENCH_IMPORT_HTTP_TIMEOUT_SECONDS": 600,
    "WORKBENCH_MAX_BODY_BYTES": 1048576,
}
OPTIONAL_FILE_KEYS = {
    "WORKBENCH_AUTH_PASSWORD_FILE": "file",
    "OPENWEBUI_ADMIN_TOKEN_FILE": "file",
    "OPENWEBUI_CA_FILE": "file",
    "OPENWEBUI_CA_PATH": "directory",
}
TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}
PRIVATE_KEY_RE = re.compile(r"BEGIN .*PRIVATE KEY")


@dataclass(frozen=True)
class CheckResult:
    level: str
    title: str
    detail: str = ""
    action: str = ""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check local OpenWebUI Workbench setup readiness without starting services."
    )
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="env template to validate")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE, help="local env file to validate")
    parser.add_argument("--compose-file", type=Path, default=DEFAULT_COMPOSE_FILE, help="compose file to validate")
    parser.add_argument("--require-docker", action="store_true", help="treat a missing Docker CLI as a failure")
    parser.add_argument(
        "--run-compose-config",
        action="store_true",
        help="run 'docker compose config' when Docker and the env file are available",
    )
    return parser.parse_args(argv)


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve())
    except OSError:
        return str(path)


def check_python_version() -> CheckResult:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        return CheckResult("ok", "Python", f"{version} is supported.")
    return CheckResult("fail", "Python", f"{version} is too old.", "Install Python 3.10 or newer.")


def check_template(template_path: Path) -> CheckResult:
    if not template_path.exists():
        return CheckResult(
            "fail",
            "Env template",
            f"{_display_path(template_path)} was not found.",
            "Restore Deployment/workbench.env.example before installation.",
        )
    try:
        template_text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        return CheckResult("fail", "Env template", str(exc), "Check file permissions.")
    missing = init_workbench_env.missing_template_keys(template_text)
    if missing:
        return CheckResult(
            "fail",
            "Env template",
            f"Required key(s) are missing: {', '.join(missing)}.",
            "Add the missing keys to the versioned template.",
        )
    return CheckResult("ok", "Env template", "Required keys are present.")


def check_env_file(env_path: Path) -> CheckResult:
    if not env_path.exists():
        return CheckResult(
            "warn",
            "Local .env",
            f"{_display_path(env_path)} does not exist.",
            "Run: python scripts/init_workbench_env.py",
        )
    try:
        missing = init_workbench_env.missing_required_values(env_path)
    except OSError as exc:
        return CheckResult("fail", "Local .env", str(exc), "Check file permissions.")
    if missing:
        return CheckResult(
            "fail",
            "Local .env",
            f"Required value(s) are missing or blank: {', '.join(missing)}.",
            "Run the init script after backing up local values, or fill the required keys manually.",
        )
    return CheckResult("ok", "Local .env", "Required values are set. Secret values were not printed.")


def _env_port(values: dict[str, str], key: str, default: int) -> tuple[int | None, str | None]:
    raw = values.get(key, "").strip() or str(default)
    if not raw.isdecimal():
        return None, f"{key} must be a number from 1 to 65535."
    port = int(raw)
    if port < 1 or port > 65535:
        return None, f"{key} must be a number from 1 to 65535."
    return port, None


def check_env_ports(env_path: Path) -> CheckResult:
    try:
        values = init_workbench_env.env_values(env_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return CheckResult("fail", "Port config", str(exc), "Check file permissions.")

    openwebui_port, openwebui_error = _env_port(values, "OPENWEBUI_PORT", 3000)
    workbench_port, workbench_error = _env_port(values, "WORKBENCH_PORT", 8088)
    errors = [error for error in (openwebui_error, workbench_error) if error]
    if errors:
        return CheckResult("fail", "Port config", " ".join(errors), "Use distinct numeric host ports in the local .env.")
    if openwebui_port == workbench_port:
        return CheckResult(
            "fail",
            "Port config",
            f"OPENWEBUI_PORT and WORKBENCH_PORT both resolve to {openwebui_port}.",
            "Set one of the ports to a different value before running docker compose.",
        )
    return CheckResult(
        "ok",
        "Port config",
        f"OPENWEBUI_PORT={openwebui_port}, WORKBENCH_PORT={workbench_port}.",
    )


def _display_url(parsed: ParseResult) -> str:
    host = parsed.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{host}{port}"


def _env_url(values: dict[str, str], key: str, default: str) -> tuple[ParseResult | None, str | None]:
    raw = values.get(key, "").strip() or default
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        return None, f"{key} must start with http:// or https://."
    if not parsed.hostname:
        return None, f"{key} must include a host name."
    try:
        parsed.port
    except ValueError:
        return None, f"{key} has an invalid port."
    if parsed.username or parsed.password:
        return None, f"{key} must not include credentials."
    return parsed, None


def check_openwebui_urls(env_path: Path) -> CheckResult:
    try:
        values = init_workbench_env.env_values(env_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return CheckResult("fail", "OpenWebUI URLs", str(exc), "Check file permissions.")

    base_url, base_error = _env_url(values, "OPENWEBUI_BASE_URL", "http://openwebui:8080")
    public_url, public_error = _env_url(values, "OPENWEBUI_PUBLIC_URL", "http://localhost:3000")
    errors = [error for error in (base_error, public_error) if error]
    if errors:
        return CheckResult(
            "fail",
            "OpenWebUI URLs",
            " ".join(errors),
            "Use full http:// or https:// URLs without credentials in the local .env.",
        )
    assert base_url is not None
    assert public_url is not None
    return CheckResult(
        "ok",
        "OpenWebUI URLs",
        f"OPENWEBUI_BASE_URL={_display_url(base_url)}, OPENWEBUI_PUBLIC_URL={_display_url(public_url)}.",
    )


def _env_bool(values: dict[str, str], key: str, default: str) -> tuple[str | None, str | None]:
    raw = values.get(key, "").strip() or default
    normalized = raw.lower()
    if normalized in TRUE_VALUES:
        return "true", None
    if normalized in FALSE_VALUES:
        return "false", None
    return None, f"{key} must be true or false."


def check_boolean_values(env_path: Path) -> CheckResult:
    try:
        values = init_workbench_env.env_values(env_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return CheckResult("fail", "Boolean config", str(exc), "Check file permissions.")

    normalized_values: list[str] = []
    errors: list[str] = []
    for key, default in BOOLEAN_DEFAULTS.items():
        normalized, error = _env_bool(values, key, default)
        if error:
            errors.append(error)
        else:
            normalized_values.append(f"{key}={normalized}")
    if errors:
        return CheckResult(
            "fail",
            "Boolean config",
            " ".join(errors),
            "Use explicit true/false, 1/0, yes/no or on/off values in the local .env.",
        )
    return CheckResult("ok", "Boolean config", ", ".join(normalized_values) + ".")


def _env_positive_int(values: dict[str, str], key: str, default: int) -> tuple[int | None, str | None]:
    raw = values.get(key, "").strip() or str(default)
    if not raw.isdecimal():
        return None, f"{key} must be a positive whole number."
    value = int(raw)
    if value < 1:
        return None, f"{key} must be a positive whole number."
    return value, None


def check_numeric_values(env_path: Path) -> CheckResult:
    try:
        values = init_workbench_env.env_values(env_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return CheckResult("fail", "Numeric config", str(exc), "Check file permissions.")

    normalized_values: list[str] = []
    errors: list[str] = []
    for key, default in INTEGER_DEFAULTS.items():
        value, error = _env_positive_int(values, key, default)
        if error:
            errors.append(error)
        else:
            normalized_values.append(f"{key}={value}")
    if errors:
        return CheckResult(
            "fail",
            "Numeric config",
            " ".join(errors),
            "Use positive whole numbers for timeout and size values in the local .env.",
        )
    return CheckResult("ok", "Numeric config", ", ".join(normalized_values) + ".")


def _env_path(raw: str, env_path: Path) -> Path:
    path = Path(raw)
    if path.is_absolute() or raw.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", raw):
        return path
    return env_path.parent / path


def _validate_pem_certificate_file(path: Path, key: str) -> tuple[str | None, str | None]:
    if not path.is_file():
        return f"{key} points to a missing file.", "Check the host path before running docker compose."
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"{key} must be a readable PEM text file.", "Use a PEM-encoded certificate bundle."
    except OSError as exc:
        return f"{key} could not be read: {exc}.", "Check file permissions."
    if PRIVATE_KEY_RE.search(text):
        return f"{key} must contain certificates only, not private keys.", "Use a public root CA certificate bundle."
    if "BEGIN CERTIFICATE" not in text:
        return f"{key} does not look like a PEM certificate bundle.", "Use a PEM file with at least one certificate."
    return None, None


def check_file_references(env_path: Path) -> CheckResult:
    try:
        values = init_workbench_env.env_values(env_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return CheckResult("fail", "File references", str(exc), "Check file permissions.")

    failures: list[str] = []
    warnings: list[str] = []
    actions: list[str] = []

    enterprise_ca = values.get("WORKBENCH_ENTERPRISE_CA_HOST_FILE", "").strip()
    if enterprise_ca:
        ca_path = _env_path(enterprise_ca, env_path)
        error, action = _validate_pem_certificate_file(ca_path, "WORKBENCH_ENTERPRISE_CA_HOST_FILE")
        if error:
            failures.append(error)
            if action:
                actions.append(action)

    for key, kind in OPTIONAL_FILE_KEYS.items():
        raw = values.get(key, "").strip()
        if not raw:
            continue
        path = _env_path(raw, env_path)
        if kind == "directory":
            exists = path.is_dir()
            expected = "directory"
        else:
            exists = path.is_file()
            expected = "file"
        if not exists:
            warnings.append(f"{key} is set but was not found as a local {expected}.")

    if failures:
        return CheckResult(
            "fail",
            "File references",
            " ".join(failures),
            " ".join(dict.fromkeys(actions)) or "Fix the referenced host files before startup.",
        )
    if warnings:
        return CheckResult(
            "warn",
            "File references",
            " ".join(warnings),
            "If these are container-only secret or CA paths, verify the matching mount before startup.",
        )
    return CheckResult("ok", "File references", "No invalid local file references found.")


def check_compose_file(compose_path: Path) -> CheckResult:
    if not compose_path.exists():
        return CheckResult(
            "fail",
            "Compose file",
            f"{_display_path(compose_path)} was not found.",
            "Restore Deployment/docker-compose.workbench.yml.",
        )
    return CheckResult("ok", "Compose file", f"{_display_path(compose_path)} exists.")


def check_docker(docker_path: str | None, require_docker: bool) -> CheckResult:
    if docker_path:
        return CheckResult("ok", "Docker CLI", f"Found at {docker_path}.")
    level = "fail" if require_docker else "warn"
    wsl_hint = ""
    if os.name == "nt" and shutil.which("wsl.exe"):
        wsl_hint = " wsl.exe is available; if Docker is installed in WSL, run this setup doctor from the WSL checkout or mount."
    return CheckResult(
        level,
        "Docker CLI",
        f"docker was not found in PATH.{wsl_hint}",
        "Install Docker, expose the Docker CLI on PATH, or run from an environment where docker compose is available.",
    )


def run_compose_config(docker_path: str, compose_path: Path, env_path: Path) -> CheckResult:
    if not env_path.exists():
        return CheckResult(
            "warn",
            "Compose config",
            "Skipped because the local env file does not exist.",
            "Run: python scripts/init_workbench_env.py",
        )
    command = [
        docker_path,
        "compose",
        "--env-file",
        str(env_path),
        "-f",
        str(compose_path),
        "config",
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CheckResult("fail", "Compose config", str(exc), "Run docker compose config manually for details.")
    if completed.returncode != 0:
        return CheckResult(
            "fail",
            "Compose config",
            f"docker compose config exited with code {completed.returncode}.",
            "Run the same command manually; do not paste secret values into issue reports.",
        )
    return CheckResult("ok", "Compose config", "docker compose config completed successfully.")


def evaluate_setup(
    template_path: Path,
    env_path: Path,
    compose_path: Path,
    *,
    require_docker: bool = False,
    run_compose: bool = False,
    docker_path: str | None = None,
    lookup_docker: bool = True,
) -> list[CheckResult]:
    docker_executable = docker_path if docker_path is not None else (shutil.which("docker") if lookup_docker else None)
    results = [
        check_python_version(),
        check_template(template_path),
        check_env_file(env_path),
        check_compose_file(compose_path),
        check_docker(docker_executable, require_docker),
    ]
    if env_path.exists():
        results.append(check_env_ports(env_path))
        results.append(check_openwebui_urls(env_path))
        results.append(check_boolean_values(env_path))
        results.append(check_numeric_values(env_path))
        results.append(check_file_references(env_path))
    if run_compose:
        if docker_executable:
            results.append(run_compose_config(docker_executable, compose_path, env_path))
        else:
            results.append(
                CheckResult(
                    "fail" if require_docker else "warn",
                    "Compose config",
                    "Skipped because Docker is not available.",
                    "Install Docker or omit --run-compose-config in minimal validation environments.",
                )
            )
    return results


def summarize(results: Sequence[CheckResult]) -> str:
    if any(result.level == "fail" for result in results):
        return "failed"
    if any(result.level == "warn" for result in results):
        return "warnings"
    return "ready"


def render_results(results: Sequence[CheckResult]) -> str:
    lines = ["# Workbench setup doctor"]
    for result in results:
        label = result.level.upper()
        lines.append(f"- {label}: {result.title} - {result.detail}")
        if result.action:
            lines.append(f"  Next: {result.action}")
    lines.append(f"- Result: {summarize(results)}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    results = evaluate_setup(
        args.template,
        args.env_file,
        args.compose_file,
        require_docker=args.require_docker,
        run_compose=args.run_compose_config,
    )
    print(render_results(results))
    return 1 if any(result.level == "fail" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
