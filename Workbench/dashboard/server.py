from __future__ import annotations

import argparse
import base64
import hmac
import ipaddress
import json
import os
import re
import ssl
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen

try:
    from Workbench.dashboard.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, detect_locale, t
except ModuleNotFoundError as exc:
    if exc.name != "Workbench":
        raise
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from Workbench.dashboard.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, detect_locale, t


REPO_ROOT = Path(os.environ.get("WORKBENCH_ROOT", Path(__file__).resolve().parents[2])).resolve()
STATIC_ROOT = Path(__file__).resolve().with_name("static")
SAFE_SEGMENT_PATTERN = re.compile(r"^[^\x00-\x1f/\\:<>\"|?*]+$")
MODEL_TEXT_FILES = {
    "systemprompt.md",
    "mainprompt.md",
    "fachwissen.md",
    "beispielergebnis.md",
    "beispielergebnis.html",
    "beispielergebnis.json",
    "beispielergebnis.yaml",
    "beispielergebnis.yml",
    "beispielergebnis.py",
    "beispielergebnis.js",
    "beispielergebnis.css",
    "beispielergebnis.csv",
    "beispielergebnis.sql",
    "beispielergebnis.svg",
    "beispielergebnis.txt",
    "customgpt_infos.md",
}
CONFIGURATION_ERRORS: list[str] = []
TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


def record_configuration_error(message: str) -> None:
    if message not in CONFIGURATION_ERRORS:
        CONFIGURATION_ERRORS.append(message)


def configuration_errors() -> list[str]:
    return list(CONFIGURATION_ERRORS)


def env_int(name: str, default: int, *, minimum: int = 1, maximum: int | None = None) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw, 10)
    except ValueError:
        safe = raw.replace("\r", "\\r").replace("\n", "\\n")
        record_configuration_error(f"{name} must be a whole number; got {safe!r}.")
        return default
    if value < minimum or (maximum is not None and value > maximum):
        if maximum is None:
            expected = f"at least {minimum}"
        else:
            expected = f"between {minimum} and {maximum}"
        record_configuration_error(f"{name} must be a whole number {expected}; got {value}.")
        return default
    return value


def env_url(name: str, default: str) -> str:
    raw = os.environ.get(name, "").strip() or default
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        record_configuration_error(f"{name} must use http or https; got {parsed.scheme or 'no scheme'!r}.")
        return default
    if not parsed.netloc:
        record_configuration_error(f"{name} must include a host.")
        return default
    if parsed.username or parsed.password:
        record_configuration_error(f"{name} must not include embedded credentials.")
        return default
    return raw.rstrip("/")


MAX_BODY_BYTES = env_int("WORKBENCH_MAX_BODY_BYTES", 1048576)
MUTATION_GUARD_HEADER = "X-Workbench-Request"
MUTATION_GUARD_VALUE = "same-origin"
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}
MODEL_EXAMPLE_SUFFIXES = {
    ".md",
    ".html",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".css",
    ".csv",
    ".sql",
    ".svg",
    ".txt",
}
WRITE_ACTIONS = {"generate", "import-dry-run", "import-openwebui", "pull-openwebui"}
AUTOMATION_ACTIONS = {"check", "generate", "import-dry-run", "import-openwebui", "sync-status"}
DEFAULT_AUTOMATION_ACTIONS = ("check",)
MIN_AUTOMATION_INTERVAL_MINUTES = 5
MAX_AUTOMATION_INTERVAL_MINUTES = 1440
OPENWEBUI_STATUS_TIMEOUT_SECONDS = 5


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


configure_utf8_stdio()


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    normalized = raw.lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    safe = raw.replace("\r", "\\r").replace("\n", "\\n")
    record_configuration_error(f"{name} must be true or false; got {safe!r}.")
    return default


def env_action_tuple(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    values = [item.strip() for item in raw.split(",") if item.strip()]
    invalid = [item for item in values if item not in AUTOMATION_ACTIONS]
    if not values or invalid:
        allowed = ", ".join(sorted(AUTOMATION_ACTIONS))
        bad = ", ".join(invalid) if invalid else raw
        record_configuration_error(f"{name} contains unsupported action(s): {bad}. Allowed values: {allowed}.")
        return default
    return tuple(dict.fromkeys(values))


def rel(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def safe_path_segment(value: str) -> str | None:
    clean = value.strip()
    if not clean or clean in {".", ".."}:
        return None
    if not SAFE_SEGMENT_PATTERN.fullmatch(clean):
        return None
    return clean


def require_safe_path_segment(value: str, message: str) -> str:
    clean = safe_path_segment(value)
    if clean is None:
        raise ValueError(message)
    return clean


def static_file_path(raw_path: str) -> Path:
    decoded = unquote(raw_path).replace("\\", "/")
    parts = decoded.split("/")
    safe_parts = [require_safe_path_segment(part, t("invalid_static_path")) for part in parts if part]
    if len(safe_parts) != len(parts) or not safe_parts:
        raise ValueError(t("invalid_static_path"))
    return STATIC_ROOT.joinpath(*safe_parts)


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def format_mtime(path: Path) -> str | None:
    value = safe_mtime(path)
    if value is None:
        return None
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))


def format_local_time(value: float | None) -> str | None:
    if value is None:
        return None
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))


def redact(text: str, secrets: list[str]) -> str:
    result = text
    for secret in secrets:
        if secret:
            result = result.replace(secret, "[REDACTED]")
    return result


def read_secret_from_env(name: str, file_name: str) -> str:
    direct = os.environ.get(name, "").strip()
    if direct:
        return direct
    file_path = os.environ.get(file_name, "").strip()
    if not file_path:
        return ""
    try:
        return Path(file_path).read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def validate_secret_file_env(file_name: str) -> None:
    file_path = os.environ.get(file_name, "").strip()
    if not file_path:
        return
    path = Path(file_path)
    try:
        if not path.is_file():
            record_configuration_error(f"{file_name} must point to a readable file.")
            return
        with path.open("r", encoding="utf-8"):
            pass
    except OSError:
        record_configuration_error(f"{file_name} must point to a readable file.")


def validate_startup_configuration() -> None:
    validate_secret_file_env("WORKBENCH_AUTH_PASSWORD_FILE")
    validate_secret_file_env("OPENWEBUI_ADMIN_TOKEN_FILE")


def is_loopback_bind(host: str) -> bool:
    clean = host.strip().strip("[]").lower()
    if clean == "localhost":
        return True
    if not clean:
        return False
    try:
        return ipaddress.ip_address(clean).is_loopback
    except ValueError:
        return False


def bind_auth_error(host: str, config: "WorkbenchConfig") -> str:
    if is_loopback_bind(host) or config.auth_enabled:
        return ""
    return t("auth_required_for_non_loopback", config.locale)


def required_auth_error(config: "WorkbenchConfig") -> str:
    if not config.auth_required or config.auth_enabled:
        return ""
    return t("auth_required_for_runtime", config.locale)


def tls_verify_from_env() -> bool:
    return env_bool("OPENWEBUI_TLS_VERIFY", True)


def openwebui_ssl_context(tls_verify: bool | None = None, ca_file: str = "", ca_path: str = "") -> ssl.SSLContext | None:
    verify = tls_verify_from_env() if tls_verify is None else tls_verify
    if not verify:
        # Explicit admin opt-out via OPENWEBUI_TLS_VERIFY=false.
        return ssl._create_unverified_context()  # nosec B323
    cafile = ca_file or os.environ.get("OPENWEBUI_CA_FILE", "").strip() or None
    capath = ca_path or os.environ.get("OPENWEBUI_CA_PATH", "").strip() or None
    if cafile or capath:
        return ssl.create_default_context(cafile=cafile, capath=capath)
    return None


@dataclass(frozen=True)
class WorkbenchConfig:
    root: Path = REPO_ROOT
    allow_write: bool = env_bool("WORKBENCH_ALLOW_WRITE", True)
    auth_required: bool = env_bool("WORKBENCH_REQUIRE_AUTH", False)
    auth_username: str = os.environ.get("WORKBENCH_AUTH_USERNAME", "").strip()
    auth_password: str = read_secret_from_env("WORKBENCH_AUTH_PASSWORD", "WORKBENCH_AUTH_PASSWORD_FILE")
    openwebui_base_url: str = env_url("OPENWEBUI_BASE_URL", "http://openwebui:8080")
    openwebui_public_url: str = env_url("OPENWEBUI_PUBLIC_URL", "http://localhost:3000")
    command_timeout: int = env_int("WORKBENCH_COMMAND_TIMEOUT_SECONDS", 300)
    import_timeout: int = env_int("WORKBENCH_IMPORT_TIMEOUT_SECONDS", 1800)
    import_http_timeout: int = env_int("WORKBENCH_IMPORT_HTTP_TIMEOUT_SECONDS", 600)
    automation_enabled: bool = env_bool("WORKBENCH_AUTOMATION_ENABLED", True)
    automation_interval_minutes: int = env_int(
        "WORKBENCH_AUTOMATION_INTERVAL_MINUTES",
        30,
        minimum=MIN_AUTOMATION_INTERVAL_MINUTES,
        maximum=MAX_AUTOMATION_INTERVAL_MINUTES,
    )
    automation_actions: tuple[str, ...] = env_action_tuple("WORKBENCH_AUTOMATION_ACTIONS", DEFAULT_AUTOMATION_ACTIONS)
    automation_run_on_start: bool = env_bool("WORKBENCH_AUTOMATION_RUN_ON_START", False)
    tls_verify: bool = tls_verify_from_env()
    ca_file: str = os.environ.get("OPENWEBUI_CA_FILE", "").strip()
    ca_path: str = os.environ.get("OPENWEBUI_CA_PATH", "").strip()
    locale: str = detect_locale(os.environ.get("WORKBENCH_LOCALE"))

    @property
    def admin_token(self) -> str:
        return read_secret_from_env("OPENWEBUI_ADMIN_TOKEN", "OPENWEBUI_ADMIN_TOKEN_FILE")

    @property
    def auth_enabled(self) -> bool:
        return bool(self.auth_username and self.auth_password)


class WorkbenchState:
    def __init__(self, config: WorkbenchConfig) -> None:
        self.config = config
        self.root = config.root.resolve()
        self.models_root = self.root / "Modelle" / "einzelmodelle"
        self.tools_root = self.root / "Tools" / "openwebui_ext" / "tools"
        self.skills_root = self.root / "Tools" / "openwebui_ext" / "skills"
        self.dist_root = self.root / "Modelle" / "dist"
        self.tools_dist_root = self.root / "Tools" / "dist"
        self.model_sync_status_file = self.root / "Artefakte" / "openwebui_sync" / "status.json"
        self.config_file = self.root / "scripts" / "openwebui_workspace_config.yaml"
        self.config_example = self.root / "scripts" / "openwebui_workspace_config.example.yaml"
        self.action_lock = threading.Lock()
        self.action_jobs: dict[str, dict[str, Any]] = {}
        self.automation_scheduler: WorkbenchAutomationScheduler | None = None

    def summary(self) -> dict[str, Any]:
        models = self.list_models()
        tools = self.list_tools()
        skills = self.list_skills()
        return {
            "root": str(self.root),
            "locale": {
                "default": DEFAULT_LOCALE,
                "configured": self.config.locale,
                "supported": list(SUPPORTED_LOCALES),
            },
            "write_enabled": self.config.allow_write,
            "dashboard": {
                "auth_required": self.config.auth_required,
                "auth_enabled": self.config.auth_enabled,
                "auth_username_configured": bool(self.config.auth_username),
                "auth_password_configured": bool(self.config.auth_password),
            },
            "openwebui": {
                "base_url": self.config.openwebui_base_url,
                "public_url": self.config.openwebui_public_url,
                "admin_token_configured": bool(self.config.admin_token),
                "tls_verify": self.config.tls_verify,
                "ca_file_configured": bool(self.config.ca_file),
                "ca_path_configured": bool(self.config.ca_path),
                "reachable": self.probe_openwebui(),
            },
            "counts": {
                "models": len(models),
                "tools": len(tools),
                "skills": len(skills),
                "model_dist_json": len(list(self.dist_root.glob("*.json"))) if self.dist_root.exists() else 0,
                "tool_dist_json": len(list(self.tools_dist_root.glob("*.json"))) if self.tools_dist_root.exists() else 0,
            },
            "config": {
                "local_config_exists": self.config_file.exists(),
                "config_path": rel(self.config_file),
                "config_example": rel(self.config_example),
            },
            "automation": self.automation_status(),
            "artifacts": self.artifact_status(),
            "model_sync": self.model_sync_status(),
        }

    def ensure_automation_scheduler(self) -> "WorkbenchAutomationScheduler":
        if self.automation_scheduler is None:
            self.automation_scheduler = WorkbenchAutomationScheduler(self)
        return self.automation_scheduler

    def automation_status(self) -> dict[str, Any]:
        scheduler = self.automation_scheduler
        payload: dict[str, Any] = {
            "enabled": self.config.automation_enabled,
            "interval_minutes": self.config.automation_interval_minutes,
            "minimum_interval_minutes": MIN_AUTOMATION_INTERVAL_MINUTES,
            "actions": list(self.config.automation_actions),
            "run_on_start": self.config.automation_run_on_start,
            "manual_actions": sorted(AUTOMATION_ACTIONS),
            "status": "disabled" if not self.config.automation_enabled else "configured",
            "next_run_at": None,
            "last_triggered_at": None,
            "last_trigger": "",
            "last_jobs": [],
            "last_skipped": [],
            "last_error": "",
            "thread_running": False,
        }
        if scheduler is not None:
            payload.update(scheduler.snapshot())
        return payload

    def probe_openwebui(self) -> dict[str, Any]:
        url = self.config.openwebui_base_url
        for path in ("/health", "/"):
            request = Request(f"{url}{path}", method="GET", headers={"Accept": "text/plain"})
            try:
                # Base URL is validated by env_url as http(s) without credentials.
                with urlopen(  # nosec B310
                    request,
                    timeout=OPENWEBUI_STATUS_TIMEOUT_SECONDS,
                    context=openwebui_ssl_context(self.config.tls_verify, self.config.ca_file, self.config.ca_path),
                ) as response:
                    return {"ok": True, "status": response.status, "path": path}
            except HTTPError as exc:
                if exc.code < 500:
                    return {"ok": True, "status": exc.code, "path": path}
            except URLError as exc:
                return {"ok": False, "error": str(exc.reason)}
            except OSError as exc:
                return {"ok": False, "error": str(exc)}
        return {"ok": False, "error": "not reachable"}

    def artifact_status(self) -> list[dict[str, Any]]:
        candidates = [
            (self.dist_root / "openwebui-models-import.json", "model_import", True),
            (self.dist_root / "openwebui-registration-plan.json", "registration_plan", True),
            (self.dist_root / "openwebui-model-params-summary.json", "parameter_summary", True),
            (self.dist_root / "openwebui-offline-artifacts.zip", "handover_zip", True),
            (self.tools_dist_root / "openwebui-tools-offline-import.json", "offline_tool_import", True),
            (self.tools_dist_root / "openwebui-functions-import.json", "function_import", True),
            (self.tools_dist_root / "openwebui-tools-skills-offline.zip", "tools_skills_zip", True),
            (self.tools_dist_root / "openwebui-tools-import.json", "optional_network_tools", False),
        ]
        items: list[dict[str, Any]] = []
        for path, kind, required in candidates:
            items.append(
                {
                    "path": rel(path),
                    "kind": kind,
                    "required": required,
                    "exists": path.exists(),
                    "mtime": format_mtime(path) if path.exists() else None,
                    "bytes": path.stat().st_size if path.exists() else 0,
                }
            )
        return items

    def model_sync_status(self) -> dict[str, Any]:
        if not self.model_sync_status_file.exists():
            return {
                "exists": False,
                "path": rel(self.model_sync_status_file),
                "generated_at": None,
                "counts": {},
                "items": [],
            }
        try:
            payload = read_json_file(self.model_sync_status_file)
        except (OSError, json.JSONDecodeError) as exc:
            return {
                "exists": True,
                "path": rel(self.model_sync_status_file),
                "generated_at": None,
                "counts": {},
                "items": [],
                "error": str(exc),
            }
        if not isinstance(payload, dict):
            return {
                "exists": True,
                "path": rel(self.model_sync_status_file),
                "generated_at": None,
                "counts": {},
                "items": [],
                "error": "status.json is not a JSON object",
            }
        return {
            "exists": True,
            "path": rel(self.model_sync_status_file),
            "generated_at": payload.get("generated_at"),
            "counts": payload.get("counts") if isinstance(payload.get("counts"), dict) else {},
            "items": payload.get("items") if isinstance(payload.get("items"), list) else [],
        }

    def list_models(self) -> list[dict[str, Any]]:
        if not self.models_root.exists():
            local_models: list[dict[str, Any]] = []
        else:
            local_models = []
            sync_items = {
                str(item.get("id")): item
                for item in self.model_sync_status().get("items", [])
                if isinstance(item, dict) and item.get("id")
            }
            for directory in sorted(path for path in self.models_root.iterdir() if path.is_dir()):
                model_id = directory.name
                model_json = directory / "model.json"
                payload: dict[str, Any] = {}
                if model_json.exists():
                    try:
                        raw = read_json_file(model_json)
                        if isinstance(raw, list) and raw and isinstance(raw[0], dict):
                            payload = raw[0]
                    except Exception:
                        payload = {}
                meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
                product_i18n = meta.get("productI18n") if isinstance(meta.get("productI18n"), dict) else {}
                files = self.model_files(model_id)
                sync_item = sync_items.get(model_id, {})
                local_models.append(
                    {
                        "id": model_id,
                        "name": payload.get("name") or model_id,
                        "base_model_id": payload.get("base_model_id") or "",
                        "description": meta.get("description") or "",
                        "default_locale": meta.get("defaultLocale") or "de",
                        "fallback_locale": meta.get("fallbackLocale") or "en",
                        "supported_locales": meta.get("supportedLocales") if isinstance(meta.get("supportedLocales"), list) else [],
                        "i18n": product_i18n,
                        "path": rel(directory),
                        "mtime": format_mtime(directory),
                        "files": files,
                        "tags": [
                            item.get("name")
                            for item in (meta.get("tags") or [])
                            if isinstance(item, dict) and item.get("name")
                        ],
                        "sync_status": sync_item.get("status", ""),
                        "sync_action": sync_item.get("action", ""),
                        "sync_diff_paths": sync_item.get("diff_paths", []),
                        "source": "workbench",
                    }
                )
        existing_ids = {model["id"] for model in local_models}
        remote_models: list[dict[str, Any]] = []
        for item in self.model_sync_status().get("items", []):
            if not isinstance(item, dict) or item.get("status") != "remote_only":
                continue
            model_id = str(item.get("id") or "")
            if not model_id or model_id in existing_ids:
                continue
            remote_models.append(
                {
                    "id": model_id,
                    "name": item.get("name") or model_id,
                    "base_model_id": "",
                    "description": item.get("action") or "OpenWebUI-only model snapshot.",
                    "default_locale": "de",
                    "fallback_locale": "en",
                    "supported_locales": [],
                    "i18n": {},
                    "path": item.get("remote_snapshot") or "",
                    "mtime": self.model_sync_status().get("generated_at"),
                    "files": [],
                    "tags": ["openwebui-only"],
                    "sync_status": item.get("status", ""),
                    "sync_action": item.get("action", ""),
                    "sync_diff_paths": item.get("diff_paths", []),
                    "source": "openwebui",
                    "remote_only": True,
                }
            )
        if remote_models:
            return [*local_models, *remote_models]
        return local_models

    def model_files(self, model_id: str) -> list[dict[str, Any]]:
        directory = self.model_dir(model_id)
        files: list[dict[str, Any]] = []
        for name in sorted(MODEL_TEXT_FILES):
            path = directory / name
            files.append(
                {
                    "name": name,
                    "exists": path.exists(),
                    "path": rel(path),
                    "bytes": path.stat().st_size if path.exists() else 0,
                    "mtime": format_mtime(path) if path.exists() else None,
                }
            )
        examples = directory / "beispiele"
        if examples.exists():
            for path in sorted(
                item for item in examples.glob("*") if item.is_file() and item.suffix.lower() in MODEL_EXAMPLE_SUFFIXES
            ):
                files.append(
                    {
                        "name": f"beispiele/{path.name}",
                        "exists": True,
                        "path": rel(path),
                        "bytes": path.stat().st_size,
                        "mtime": format_mtime(path),
                    }
                )
        i18n_dir = directory / "i18n"
        if i18n_dir.exists():
            for path in sorted(i18n_dir.glob("*.md")):
                files.append(
                    {
                        "name": f"i18n/{path.name}",
                        "exists": True,
                        "path": rel(path),
                        "bytes": path.stat().st_size,
                        "mtime": format_mtime(path),
                    }
                )
        return files

    def model_dir(self, model_id: str) -> Path:
        safe_model_id = require_safe_path_segment(model_id, t("invalid_model_id", self.config.locale))
        directory = self.models_root / safe_model_id
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(t("model_not_found", self.config.locale, model_id=model_id))
        return directory

    def normalize_model_file(self, model_id: str, name: str) -> Path:
        directory = self.model_dir(model_id)
        clean = name.strip().replace("\\", "/")
        if clean in MODEL_TEXT_FILES:
            safe_name = require_safe_path_segment(clean, t("invalid_model_filename", self.config.locale))
            return directory / safe_name
        if clean.startswith("beispiele/") and Path(clean).suffix.lower() in MODEL_EXAMPLE_SUFFIXES:
            example_name = clean.removeprefix("beispiele/")
            safe_example_name = require_safe_path_segment(example_name, t("invalid_example_filename", self.config.locale))
            return directory / "beispiele" / safe_example_name
        if clean.startswith("i18n/") and clean.endswith(".md"):
            locale_name = clean.removeprefix("i18n/")
            safe_locale_name = require_safe_path_segment(locale_name, t("invalid_model_filename", self.config.locale))
            return directory / "i18n" / safe_locale_name
        raise ValueError(t("only_model_markdown", self.config.locale))

    def read_model_file(self, model_id: str, name: str) -> dict[str, Any]:
        path = self.normalize_model_file(model_id, name)
        if not path.exists():
            return {"model_id": model_id, "name": name, "content": "", "exists": False, "path": rel(path)}
        return {
            "model_id": model_id,
            "name": name,
            "content": path.read_text(encoding="utf-8"),
            "exists": True,
            "path": rel(path),
            "mtime": format_mtime(path),
        }

    def write_model_file(self, model_id: str, name: str, content: str) -> dict[str, Any]:
        if not self.config.allow_write:
            raise PermissionError(t("write_disabled", self.config.locale))
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_BODY_BYTES:
            raise ValueError(t("content_too_large", self.config.locale, max_bytes=MAX_BODY_BYTES))
        path = self.normalize_model_file(model_id, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return self.read_model_file(model_id, name)

    def delete_model_file(self, model_id: str, name: str) -> dict[str, Any]:
        if not self.config.allow_write:
            raise PermissionError(t("write_disabled", self.config.locale))
        path = self.normalize_model_file(model_id, name)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(t("file_not_found", self.config.locale))
        path.unlink()
        return {"model_id": model_id, "name": name, "path": rel(path), "deleted": True}

    def list_tools(self) -> list[dict[str, Any]]:
        return self._list_markdown_or_python(self.tools_root, "*.py", "tool")

    def list_skills(self) -> list[dict[str, Any]]:
        return self._list_markdown_or_python(self.skills_root, "*.md", "skill")

    def _list_markdown_or_python(self, root: Path, pattern: str, kind: str) -> list[dict[str, Any]]:
        if not root.exists():
            return []
        items: list[dict[str, Any]] = []
        for path in sorted(root.glob(pattern)):
            if path.name == "__init__.py" or path.name.upper() == "README.MD":
                continue
            items.append(
                {
                    "id": path.stem,
                    "kind": kind,
                    "name": path.stem.replace("_", " ").replace("-", " ").title(),
                    "path": rel(path),
                    "bytes": path.stat().st_size,
                    "mtime": format_mtime(path),
                    "extension": path.suffix,
                }
            )
        return items

    def resource_path(self, kind: str, resource_id: str) -> Path:
        safe_resource_id = require_safe_path_segment(resource_id, t("invalid_resource_id", self.config.locale))
        if kind == "tool":
            path = self.tools_root / f"{safe_resource_id}.py"
        elif kind == "skill":
            path = self.skills_root / f"{safe_resource_id}.md"
        else:
            raise ValueError(t("resource_type", self.config.locale))
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(t("resource_not_found", self.config.locale, kind=kind, resource_id=resource_id))
        return path

    def resource_target_path(self, kind: str, resource_id: str) -> Path:
        safe_resource_id = require_safe_path_segment(resource_id, t("invalid_resource_id", self.config.locale))
        if kind == "tool":
            if not safe_resource_id.endswith(".py"):
                safe_resource_id = f"{safe_resource_id}.py"
            if safe_resource_id == "__init__.py":
                raise ValueError(t("invalid_resource_id", self.config.locale))
            return self.tools_root / safe_resource_id
        if kind == "skill":
            if not safe_resource_id.endswith(".md"):
                safe_resource_id = f"{safe_resource_id}.md"
            if safe_resource_id.upper() == "README.MD":
                raise ValueError(t("invalid_resource_id", self.config.locale))
            return self.skills_root / safe_resource_id
        raise ValueError(t("resource_type", self.config.locale))

    def read_resource(self, kind: str, resource_id: str) -> dict[str, Any]:
        path = self.resource_path(kind, resource_id)
        return {
            "kind": kind,
            "id": resource_id,
            "path": rel(path),
            "content": path.read_text(encoding="utf-8"),
            "bytes": path.stat().st_size,
            "mtime": format_mtime(path),
        }

    def write_resource(self, kind: str, resource_id: str, content: str) -> dict[str, Any]:
        if not self.config.allow_write:
            raise PermissionError(t("write_disabled", self.config.locale))
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_BODY_BYTES:
            raise ValueError(t("content_too_large", self.config.locale, max_bytes=MAX_BODY_BYTES))
        path = self.resource_path(kind, resource_id)
        path.write_text(content, encoding="utf-8", newline="\n")
        return self.read_resource(kind, resource_id)

    def create_resource(self, kind: str, resource_id: str, content: str) -> dict[str, Any]:
        if not self.config.allow_write:
            raise PermissionError(t("write_disabled", self.config.locale))
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_BODY_BYTES:
            raise ValueError(t("content_too_large", self.config.locale, max_bytes=MAX_BODY_BYTES))
        path = self.resource_target_path(kind, resource_id)
        if path.exists():
            raise ValueError(t("resource_exists", self.config.locale, resource_id=path.stem))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return self.read_resource(kind, path.stem)

    def delete_resource(self, kind: str, resource_id: str) -> dict[str, Any]:
        if not self.config.allow_write:
            raise PermissionError(t("write_disabled", self.config.locale))
        path = self.resource_path(kind, resource_id)
        path.unlink()
        return {"kind": kind, "id": resource_id, "path": rel(path), "deleted": True}

    def ensure_action_allowed(self, action: str) -> None:
        if action in WRITE_ACTIONS and not self.config.allow_write:
            raise PermissionError(t("write_disabled", self.config.locale))

    def run_action(self, action: str) -> dict[str, Any]:
        self.ensure_action_allowed(action)
        command_env: dict[str, str] = {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
        if action == "check":
            # Keep repository verification independent from the dashboard runtime mode.
            command_env["WORKBENCH_ALLOW_WRITE"] = "true"
            command = [sys.executable, "scripts/verify_openwebui_workspace.py"]
            label = "Verify workspace"
        elif action == "generate":
            command = [sys.executable, "scripts/configure_openwebui_tool_models.py", "--write", "--check", "--rebuild-zips"]
            label = "Generate registries and ZIPs"
        elif action == "import-dry-run":
            config_path = self.config_file if self.config_file.exists() else self.config_example
            command = [
                sys.executable,
                "scripts/configure_openwebui_tool_models.py",
                "--write",
                "--check",
                "--import-dry-run",
                "--config",
                str(config_path),
            ]
            label = "Import dry-run"
        elif action in {"sync-status", "pull-openwebui"}:
            token = self.config.admin_token
            if not token:
                raise PermissionError(t("token_missing", self.config.locale))
            command = [
                sys.executable,
                "scripts/sync_openwebui_models.py",
                "--base-url",
                self.config.openwebui_base_url,
                "--timeout",
                str(self.config.import_http_timeout),
            ]
            if action == "pull-openwebui":
                command.append("--write-snapshot")
            command_env.update(
                {
                    "OPENWEBUI_ADMIN_TOKEN": token,
                    "OPENWEBUI_TLS_VERIFY": "true" if self.config.tls_verify else "false",
                    "OPENWEBUI_CA_FILE": self.config.ca_file,
                    "OPENWEBUI_CA_PATH": self.config.ca_path,
                }
            )
            label = "Compare OpenWebUI models" if action == "sync-status" else "Snapshot OpenWebUI models"
        elif action == "import-openwebui":
            token = self.config.admin_token
            if not token and not self.config_file.exists():
                raise PermissionError(t("token_missing", self.config.locale))
            command = [
                sys.executable,
                "scripts/configure_openwebui_tool_models.py",
                "--write",
                "--check",
                "--rebuild-zips",
                "--import-openwebui",
            ]
            if self.config_file.exists():
                command.extend(["--config", str(self.config_file)])
            if os.environ.get("OPENWEBUI_BASE_URL"):
                command.extend(["--base-url", self.config.openwebui_base_url])
            if token:
                command.extend(["--token", token])
            command.extend(["--timeout", str(self.config.import_http_timeout)])
            command_env.update(
                {
                    "OPENWEBUI_TLS_VERIFY": "true" if self.config.tls_verify else "false",
                    "OPENWEBUI_CA_FILE": self.config.ca_file,
                    "OPENWEBUI_CA_PATH": self.config.ca_path,
                }
            )
            label = "Import to OpenWebUI"
            timeout = self.config.import_timeout
        else:
            raise ValueError(t("unknown_action", self.config.locale, action=action))
        if action != "import-openwebui":
            timeout = self.config.command_timeout

        started = time.time()
        completed = subprocess.run(
            command,
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env={**os.environ, **command_env},
        )
        output = redact(completed.stdout or "", [self.config.admin_token, self.config.auth_password])
        safe_command = [part if part != self.config.admin_token else "[REDACTED]" for part in command]
        return {
            "action": action,
            "label": label,
            "command": safe_command,
            "returncode": completed.returncode,
            "duration_seconds": round(time.time() - started, 1),
            "ok": completed.returncode == 0,
            "output": output[-20000:],
            "error": "" if completed.returncode == 0 else t("action_failed", self.config.locale, returncode=completed.returncode),
        }

    def start_action_job(self, action: str) -> dict[str, Any]:
        with self.action_lock:
            for job in self.action_jobs.values():
                if job.get("action") == action and job.get("running"):
                    return dict(job)
            job_id = uuid.uuid4().hex
            job = {
                "job_id": job_id,
                "action": action,
                "label": action,
                "running": True,
                "ok": None,
                "returncode": None,
                "duration_seconds": 0,
                "output": "",
                "error": "",
                "started_at": time.time(),
            }
            self.action_jobs[job_id] = job

        thread = threading.Thread(target=self._run_action_job, args=(job_id, action), daemon=True)
        thread.start()
        return dict(job)

    def _run_action_job(self, job_id: str, action: str) -> None:
        try:
            result = self.run_action(action)
        except Exception as exc:  # pragma: no cover - defensive background boundary
            result = {
                "action": action,
                "label": action,
                "returncode": None,
                "duration_seconds": 0,
                "ok": False,
                "output": "",
                "error": f"{type(exc).__name__}: {exc}",
            }
        with self.action_lock:
            job = self.action_jobs[job_id]
            job.update(result)
            job["job_id"] = job_id
            job["running"] = False
            job["finished_at"] = time.time()

    def action_job(self, job_id: str) -> dict[str, Any]:
        with self.action_lock:
            job = self.action_jobs.get(job_id)
            if not job:
                raise FileNotFoundError(t("route_not_found", self.config.locale))
            current = dict(job)
        if current.get("running"):
            current["duration_seconds"] = round(time.time() - float(current.get("started_at") or time.time()), 1)
        return current


class WorkbenchAutomationScheduler:
    def __init__(self, state: WorkbenchState) -> None:
        self.state = state
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.next_run_at: float | None = None
        self.last_triggered_at: float | None = None
        self.last_trigger = ""
        self.last_jobs: list[dict[str, Any]] = []
        self.last_skipped: list[dict[str, str]] = []
        self.last_error = ""

    @property
    def interval_seconds(self) -> int:
        return self.state.config.automation_interval_minutes * 60

    def start(self) -> None:
        if not self.state.config.automation_enabled:
            return
        with self.lock:
            if self.thread and self.thread.is_alive():
                return
            self.stop_event.clear()
            self.next_run_at = time.time() if self.state.config.automation_run_on_start else time.time() + self.interval_seconds
            self.thread = threading.Thread(target=self._run_loop, name="workbench-automation", daemon=True)
            self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

    def _run_loop(self) -> None:
        while not self.stop_event.is_set():
            with self.lock:
                due_at = self.next_run_at or (time.time() + self.interval_seconds)
            if self.stop_event.wait(max(0.5, due_at - time.time())):
                return
            self.run_once("scheduled")
            with self.lock:
                self.next_run_at = time.time() + self.interval_seconds

    def skip_reason(self, action: str) -> str:
        if action in WRITE_ACTIONS and not self.state.config.allow_write:
            return t("write_disabled", self.state.config.locale)
        if action == "import-openwebui" and not self.state.config.admin_token and not self.state.config_file.exists():
            return t("token_missing", self.state.config.locale)
        return ""

    def run_once(self, trigger: str = "manual") -> dict[str, Any]:
        jobs: list[dict[str, Any]] = []
        skipped: list[dict[str, str]] = []
        errors: list[str] = []
        for action in self.state.config.automation_actions:
            reason = self.skip_reason(action)
            if reason:
                skipped.append({"action": action, "reason": reason})
                continue
            try:
                job = self.state.start_action_job(action)
                jobs.append(
                    {
                        "action": action,
                        "job_id": str(job.get("job_id") or ""),
                        "running": bool(job.get("running")),
                        "ok": job.get("ok"),
                    }
                )
            except Exception as exc:  # pragma: no cover - defensive scheduler boundary
                errors.append(f"{action}: {type(exc).__name__}: {exc}")
        with self.lock:
            self.last_triggered_at = time.time()
            self.last_trigger = trigger
            self.last_jobs = jobs
            self.last_skipped = skipped
            self.last_error = "; ".join(errors)
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            thread_running = bool(self.thread and self.thread.is_alive())
            if not self.state.config.automation_enabled:
                status = "disabled"
            elif thread_running:
                status = "active"
            else:
                status = "configured"
            return {
                "enabled": self.state.config.automation_enabled,
                "interval_minutes": self.state.config.automation_interval_minutes,
                "minimum_interval_minutes": MIN_AUTOMATION_INTERVAL_MINUTES,
                "actions": list(self.state.config.automation_actions),
                "run_on_start": self.state.config.automation_run_on_start,
                "manual_actions": sorted(AUTOMATION_ACTIONS),
                "status": status,
                "next_run_at": format_local_time(self.next_run_at),
                "last_triggered_at": format_local_time(self.last_triggered_at),
                "last_trigger": self.last_trigger,
                "last_jobs": list(self.last_jobs),
                "last_skipped": list(self.last_skipped),
                "last_error": self.last_error,
                "thread_running": thread_running,
            }


STATE = WorkbenchState(WorkbenchConfig())


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "OpenWebUIWorkbench/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.send_json({"ok": True, "service": "openwebui-workbench"})
            return
        static_path: Path | None = None
        if parsed.path.startswith("/static/"):
            try:
                static_path = static_file_path(parsed.path.removeprefix("/static/"))
            except Exception as exc:
                self.handle_exception(exc)
                return
        if not self.require_auth():
            return
        try:
            if parsed.path == "/":
                self.send_static(STATIC_ROOT / "index.html", "text/html; charset=utf-8")
            elif static_path is not None:
                self.send_static(static_path, self.content_type(parsed.path))
            elif parsed.path == "/api/status":
                self.send_json(STATE.summary())
            elif parsed.path == "/api/models":
                self.send_json({"models": STATE.list_models()})
            elif parsed.path.startswith("/api/models/") and parsed.path.endswith("/file"):
                model_id = unquote(parsed.path.split("/")[3])
                name = parse_qs(parsed.query).get("name", ["systemprompt.md"])[0]
                self.send_json(STATE.read_model_file(model_id, name))
            elif parsed.path == "/api/tools":
                self.send_json({"tools": STATE.list_tools()})
            elif parsed.path == "/api/skills":
                self.send_json({"skills": STATE.list_skills()})
            elif parsed.path == "/api/resources":
                self.send_json({"tools": STATE.list_tools(), "skills": STATE.list_skills()})
            elif parsed.path.startswith("/api/resources/") and parsed.path.endswith("/file"):
                parts = parsed.path.split("/")
                kind = unquote(parts[3])
                resource_id = unquote(parts[4])
                self.send_json(STATE.read_resource(kind, resource_id))
            elif parsed.path.startswith("/api/action-jobs/"):
                job_id = unquote(parsed.path.removeprefix("/api/action-jobs/"))
                self.send_json(STATE.action_job(job_id))
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, self.message("route_not_found"))
        except Exception as exc:
            self.handle_exception(exc)

    def do_PUT(self) -> None:  # noqa: N802
        if not self.require_auth():
            return
        if not self.require_mutation_guard():
            return
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/models/") and parsed.path.endswith("/file"):
                model_id = unquote(parsed.path.split("/")[3])
                payload = self.read_json_body()
                self.send_json(STATE.write_model_file(model_id, str(payload.get("name") or ""), str(payload.get("content") or "")))
            elif parsed.path.startswith("/api/resources/") and parsed.path.endswith("/file"):
                parts = parsed.path.split("/")
                kind = unquote(parts[3])
                resource_id = unquote(parts[4])
                payload = self.read_json_body()
                self.send_json(STATE.write_resource(kind, resource_id, str(payload.get("content") or "")))
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, self.message("route_not_found"))
        except Exception as exc:
            self.handle_exception(exc)

    def do_POST(self) -> None:  # noqa: N802
        if not self.require_auth():
            return
        if not self.require_mutation_guard():
            return
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/actions/"):
                action = unquote(parsed.path.removeprefix("/api/actions/"))
                if action == "import-openwebui":
                    STATE.ensure_action_allowed(action)
                    self.send_json(STATE.start_action_job(action), HTTPStatus.ACCEPTED)
                    return
                result = STATE.run_action(action)
                status = HTTPStatus.OK if result["ok"] else HTTPStatus.BAD_GATEWAY
                self.send_json(result, status)
            elif parsed.path == "/api/automation/run":
                result = STATE.ensure_automation_scheduler().run_once("manual")
                self.send_json(result, HTTPStatus.ACCEPTED)
            elif parsed.path == "/api/resources":
                payload = self.read_json_body()
                self.send_json(
                    STATE.create_resource(
                        str(payload.get("kind") or ""),
                        str(payload.get("id") or ""),
                        str(payload.get("content") or ""),
                    ),
                    HTTPStatus.CREATED,
                )
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, self.message("route_not_found"))
        except Exception as exc:
            self.handle_exception(exc)

    def do_DELETE(self) -> None:  # noqa: N802
        if not self.require_auth():
            return
        if not self.require_mutation_guard():
            return
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/models/") and parsed.path.endswith("/file"):
                model_id = unquote(parsed.path.split("/")[3])
                name = parse_qs(parsed.query).get("name", [""])[0]
                self.send_json(STATE.delete_model_file(model_id, name))
            elif parsed.path.startswith("/api/resources/") and parsed.path.endswith("/file"):
                parts = parsed.path.split("/")
                kind = unquote(parts[3])
                resource_id = unquote(parts[4])
                self.send_json(STATE.delete_resource(kind, resource_id))
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, self.message("route_not_found"))
        except Exception as exc:
            self.handle_exception(exc)

    def require_auth(self) -> bool:
        if not STATE.config.auth_enabled:
            return True
        header = self.headers.get("Authorization", "")
        authenticated = False
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header.removeprefix("Basic ").strip(), validate=True).decode("utf-8")
                username, password = decoded.split(":", 1)
                user_ok = hmac.compare_digest(username, STATE.config.auth_username)
                password_ok = hmac.compare_digest(password, STATE.config.auth_password)
                authenticated = user_ok and password_ok
            except (ValueError, UnicodeDecodeError):
                authenticated = False
        if authenticated:
            return True
        self.send_auth_required()
        return False

    def require_mutation_guard(self) -> bool:
        if self.headers.get(MUTATION_GUARD_HEADER, "") == MUTATION_GUARD_VALUE:
            return True
        self.send_error_json(HTTPStatus.FORBIDDEN, self.message("csrf_required"))
        return False

    def send_auth_required(self) -> None:
        body = json.dumps({"ok": False, "error": self.message("auth_required")}, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("WWW-Authenticate", 'Basic realm="OpenWebUI Workbench", charset="UTF-8"')
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_static(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self.send_error_json(HTTPStatus.NOT_FOUND, self.message("file_not_found"))
            return
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_security_headers(self) -> None:
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json({"ok": False, "error": message}, status)

    def handle_exception(self, exc: Exception) -> None:
        if isinstance(exc, FileNotFoundError):
            self.send_error_json(HTTPStatus.NOT_FOUND, str(exc))
        elif isinstance(exc, PermissionError):
            self.send_error_json(HTTPStatus.FORBIDDEN, str(exc))
        elif isinstance(exc, (ValueError, TimeoutError, subprocess.TimeoutExpired)):
            self.send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
        else:
            self.send_error_json(HTTPStatus.INTERNAL_SERVER_ERROR, f"{type(exc).__name__}: {exc}")

    def read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BODY_BYTES:
            raise ValueError(self.message("request_too_large", max_bytes=MAX_BODY_BYTES))
        raw = self.rfile.read(length)
        if not raw:
            return {}
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(self.message("json_body_object"))
        return payload

    def current_locale(self) -> str:
        return detect_locale(
            self.headers.get("X-Workbench-Locale"),
            self.headers.get("Accept-Language"),
            STATE.config.locale,
        )

    def message(self, key: str, **params: object) -> str:
        return t(key, self.current_locale(), **params)

    @staticmethod
    def content_type(path: str) -> str:
        if path.endswith(".css"):
            return "text/css; charset=utf-8"
        if path.endswith(".js"):
            return "text/javascript; charset=utf-8"
        if path.endswith(".svg"):
            return "image/svg+xml"
        return "application/octet-stream"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.log_date_time_string(), fmt % args))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OpenWebUI Workbench dashboard.")
    parser.add_argument("--host", default=os.environ.get("WORKBENCH_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=env_int("WORKBENCH_PORT", 8088, maximum=65535))
    return parser.parse_args(argv)


def print_startup_errors(errors: list[str]) -> None:
    print("# OpenWebUI Workbench dashboard startup failed", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validate_startup_configuration()
    config_errors = configuration_errors()
    if config_errors:
        print_startup_errors(config_errors)
        return 1
    auth_error = required_auth_error(STATE.config)
    if auth_error:
        print_startup_errors([auth_error])
        return 1
    auth_error = bind_auth_error(args.host, STATE.config)
    if auth_error:
        print_startup_errors([auth_error])
        return 1
    try:
        server = ThreadingHTTPServer((args.host, args.port), WorkbenchHandler)
    except OSError as exc:
        print_startup_errors([f"Could not bind dashboard to {args.host}:{args.port}: {exc}"])
        return 1
    STATE.ensure_automation_scheduler().start()
    print(t("dashboard_listening", STATE.config.locale, host=args.host, port=args.port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
