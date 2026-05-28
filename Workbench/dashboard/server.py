from __future__ import annotations

import argparse
import base64
import hmac
import json
import os
import re
import ssl
import subprocess
import sys
import time
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
    "customgpt_infos.md",
}
MAX_BODY_BYTES = int(os.environ.get("WORKBENCH_MAX_BODY_BYTES", "1048576"))


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


configure_utf8_stdio()


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


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


def tls_verify_from_env() -> bool:
    return env_bool("OPENWEBUI_TLS_VERIFY", True)


def openwebui_ssl_context(tls_verify: bool | None = None, ca_file: str = "", ca_path: str = "") -> ssl.SSLContext | None:
    verify = tls_verify_from_env() if tls_verify is None else tls_verify
    if not verify:
        return ssl._create_unverified_context()
    cafile = ca_file or os.environ.get("OPENWEBUI_CA_FILE", "").strip() or None
    capath = ca_path or os.environ.get("OPENWEBUI_CA_PATH", "").strip() or None
    if cafile or capath:
        return ssl.create_default_context(cafile=cafile, capath=capath)
    return None


@dataclass(frozen=True)
class WorkbenchConfig:
    root: Path = REPO_ROOT
    allow_write: bool = env_bool("WORKBENCH_ALLOW_WRITE", True)
    auth_username: str = os.environ.get("WORKBENCH_AUTH_USERNAME", "").strip()
    auth_password: str = read_secret_from_env("WORKBENCH_AUTH_PASSWORD", "WORKBENCH_AUTH_PASSWORD_FILE")
    openwebui_base_url: str = os.environ.get("OPENWEBUI_BASE_URL", "http://openwebui:8080").rstrip("/")
    openwebui_public_url: str = os.environ.get("OPENWEBUI_PUBLIC_URL", "http://localhost:3000").rstrip("/")
    command_timeout: int = int(os.environ.get("WORKBENCH_COMMAND_TIMEOUT_SECONDS", "300"))
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
        self.config_file = self.root / "scripts" / "openwebui_workspace_config.yaml"
        self.config_example = self.root / "scripts" / "openwebui_workspace_config.example.yaml"

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
            "artifacts": self.artifact_status(),
        }

    def probe_openwebui(self) -> dict[str, Any]:
        url = self.config.openwebui_base_url
        for path in ("/health", "/"):
            request = Request(f"{url}{path}", method="GET", headers={"Accept": "text/plain"})
            try:
                with urlopen(
                    request,
                    timeout=2,
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
            self.dist_root / "openwebui-models-import.json",
            self.dist_root / "openwebui-registration-plan.json",
            self.dist_root / "openwebui-model-params-summary.json",
            self.dist_root / "openwebui-offline-artifacts.zip",
            self.tools_dist_root / "openwebui-tools-import.json",
            self.tools_dist_root / "openwebui-tools-offline-import.json",
            self.tools_dist_root / "openwebui-functions-import.json",
            self.tools_dist_root / "openwebui-tools-skills-offline.zip",
        ]
        items: list[dict[str, Any]] = []
        for path in candidates:
            items.append(
                {
                    "path": rel(path),
                    "exists": path.exists(),
                    "mtime": format_mtime(path) if path.exists() else None,
                    "bytes": path.stat().st_size if path.exists() else 0,
                }
            )
        return items

    def list_models(self) -> list[dict[str, Any]]:
        if not self.models_root.exists():
            return []
        models: list[dict[str, Any]] = []
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
            models.append(
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
                }
            )
        return models

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
                item for item in examples.glob("*") if item.is_file() and item.suffix.lower() in {".md", ".html"}
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
        if clean.startswith("beispiele/") and Path(clean).suffix.lower() in {".md", ".html"}:
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

    def run_action(self, action: str) -> dict[str, Any]:
        command_env: dict[str, str] = {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
        if action == "check":
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
        elif action == "import-openwebui":
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
            token = self.config.admin_token
            if token:
                command.extend(["--token", token])
            command_env.update(
                {
                    "OPENWEBUI_TLS_VERIFY": "true" if self.config.tls_verify else "false",
                    "OPENWEBUI_CA_FILE": self.config.ca_file,
                    "OPENWEBUI_CA_PATH": self.config.ca_path,
                }
            )
            label = "Import to OpenWebUI"
        else:
            raise ValueError(t("unknown_action", self.config.locale, action=action))

        started = time.time()
        completed = subprocess.run(
            command,
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=self.config.command_timeout,
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


STATE = WorkbenchState(WorkbenchConfig())


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "OpenWebUIWorkbench/1.0"

    def do_GET(self) -> None:  # noqa: N802
        if not self.require_auth():
            return
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self.send_static(STATIC_ROOT / "index.html", "text/html; charset=utf-8")
            elif parsed.path.startswith("/static/"):
                self.send_static(static_file_path(parsed.path.removeprefix("/static/")), self.content_type(parsed.path))
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
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, self.message("route_not_found"))
        except Exception as exc:
            self.handle_exception(exc)

    def do_PUT(self) -> None:  # noqa: N802
        if not self.require_auth():
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
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/actions/"):
                action = unquote(parsed.path.removeprefix("/api/actions/"))
                result = STATE.run_action(action)
                status = HTTPStatus.OK if result["ok"] else HTTPStatus.BAD_GATEWAY
                self.send_json(result, status)
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

    def send_auth_required(self) -> None:
        body = json.dumps({"ok": False, "error": self.message("auth_required")}, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("WWW-Authenticate", 'Basic realm="OpenWebUI Workbench", charset="UTF-8"')
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
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
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

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
    parser.add_argument("--host", default=os.environ.get("WORKBENCH_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("WORKBENCH_PORT", "8088")))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), WorkbenchHandler)
    print(t("dashboard_listening", STATE.config.locale, host=args.host, port=args.port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
