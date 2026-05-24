from __future__ import annotations

import argparse
import json
import os
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


REPO_ROOT = Path(os.environ.get("WORKBENCH_ROOT", Path(__file__).resolve().parents[2])).resolve()
STATIC_ROOT = Path(__file__).resolve().with_name("static")
MODEL_MARKDOWN_FILES = {
    "systemprompt.md",
    "mainprompt.md",
    "fachwissen.md",
    "beispielergebnis.md",
    "customgpt_infos.md",
}
MAX_BODY_BYTES = int(os.environ.get("WORKBENCH_MAX_BODY_BYTES", "1048576"))


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def rel(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def ensure_inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    resolved.relative_to(root.resolve())
    return resolved


def is_safe_path_segment(value: str) -> bool:
    if not value or value in {".", ".."}:
        return False
    if "/" in value or "\\" in value:
        return False
    return not any(ord(char) < 32 for char in value)


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


@dataclass(frozen=True)
class WorkbenchConfig:
    root: Path = REPO_ROOT
    allow_write: bool = env_bool("WORKBENCH_ALLOW_WRITE", True)
    openwebui_base_url: str = os.environ.get("OPENWEBUI_BASE_URL", "http://openwebui:8080").rstrip("/")
    openwebui_public_url: str = os.environ.get("OPENWEBUI_PUBLIC_URL", "http://localhost:3000").rstrip("/")
    command_timeout: int = int(os.environ.get("WORKBENCH_COMMAND_TIMEOUT_SECONDS", "300"))

    @property
    def admin_token(self) -> str:
        return read_secret_from_env("OPENWEBUI_ADMIN_TOKEN", "OPENWEBUI_ADMIN_TOKEN_FILE")


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
            "write_enabled": self.config.allow_write,
            "openwebui": {
                "base_url": self.config.openwebui_base_url,
                "public_url": self.config.openwebui_public_url,
                "admin_token_configured": bool(self.config.admin_token),
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
                with urlopen(request, timeout=2) as response:
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
            files = self.model_files(model_id)
            models.append(
                {
                    "id": model_id,
                    "name": payload.get("name") or model_id,
                    "base_model_id": payload.get("base_model_id") or "",
                    "description": ((payload.get("meta") or {}).get("description") if isinstance(payload.get("meta"), dict) else "") or "",
                    "path": rel(directory),
                    "mtime": format_mtime(directory),
                    "files": files,
                    "tags": [
                        item.get("name")
                        for item in ((payload.get("meta") or {}).get("tags") or [])
                        if isinstance(item, dict) and item.get("name")
                    ],
                }
            )
        return models

    def model_files(self, model_id: str) -> list[dict[str, Any]]:
        directory = self.model_dir(model_id)
        files: list[dict[str, Any]] = []
        for name in sorted(MODEL_MARKDOWN_FILES):
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
            for path in sorted(examples.glob("*.md")):
                files.append(
                    {
                        "name": f"beispiele/{path.name}",
                        "exists": True,
                        "path": rel(path),
                        "bytes": path.stat().st_size,
                        "mtime": format_mtime(path),
                    }
                )
        return files

    def model_dir(self, model_id: str) -> Path:
        if not is_safe_path_segment(model_id):
            raise ValueError("Ungültige Modell-ID.")
        directory = ensure_inside(self.models_root / model_id, self.models_root)
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(f"Modell nicht gefunden: {model_id}")
        return directory

    def normalize_model_file(self, model_id: str, name: str) -> Path:
        directory = self.model_dir(model_id)
        clean = name.strip().replace("\\", "/")
        if clean in MODEL_MARKDOWN_FILES:
            return ensure_inside(directory / clean, directory)
        if clean.startswith("beispiele/") and clean.endswith(".md") and "/" not in clean[len("beispiele/") :]:
            return ensure_inside(directory / clean, directory)
        raise ValueError("Nur freigegebene Markdown-Dateien eines Modellpakets dürfen bearbeitet werden.")

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
            raise PermissionError("Schreibzugriff ist deaktiviert.")
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_BODY_BYTES:
            raise ValueError(f"Dateiinhalt ist größer als {MAX_BODY_BYTES} Bytes.")
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
        if not is_safe_path_segment(resource_id):
            raise ValueError("Ungültige Ressourcen-ID.")
        if kind == "tool":
            path = ensure_inside(self.tools_root / f"{resource_id}.py", self.tools_root)
        elif kind == "skill":
            path = ensure_inside(self.skills_root / f"{resource_id}.md", self.skills_root)
        else:
            raise ValueError("Ressourcentyp muss `tool` oder `skill` sein.")
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Ressource nicht gefunden: {kind}/{resource_id}")
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
            raise PermissionError("Schreibzugriff ist deaktiviert.")
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_BODY_BYTES:
            raise ValueError(f"Dateiinhalt ist größer als {MAX_BODY_BYTES} Bytes.")
        path = self.resource_path(kind, resource_id)
        path.write_text(content, encoding="utf-8", newline="\n")
        return self.read_resource(kind, resource_id)

    def run_action(self, action: str) -> dict[str, Any]:
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
            token = self.config.admin_token
            if not token:
                raise PermissionError("OPENWEBUI_ADMIN_TOKEN oder OPENWEBUI_ADMIN_TOKEN_FILE ist nicht gesetzt.")
            command = [
                sys.executable,
                "scripts/configure_openwebui_tool_models.py",
                "--write",
                "--check",
                "--rebuild-zips",
                "--import-openwebui",
                "--base-url",
                self.config.openwebui_base_url,
                "--token",
                token,
            ]
            label = "Import to OpenWebUI"
        else:
            raise ValueError(f"Unbekannte Aktion: {action}")

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
        )
        output = redact(completed.stdout or "", [self.config.admin_token])
        safe_command = [part if part != self.config.admin_token else "[REDACTED]" for part in command]
        return {
            "action": action,
            "label": label,
            "command": safe_command,
            "returncode": completed.returncode,
            "duration_seconds": round(time.time() - started, 1),
            "ok": completed.returncode == 0,
            "output": output[-20000:],
        }


STATE = WorkbenchState(WorkbenchConfig())


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "OpenWebUIWorkbench/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self.send_static(STATIC_ROOT / "index.html", "text/html; charset=utf-8")
            elif parsed.path.startswith("/static/"):
                self.send_static(STATIC_ROOT / unquote(parsed.path.removeprefix("/static/")), self.content_type(parsed.path))
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
                self.send_error_json(HTTPStatus.NOT_FOUND, "Route nicht gefunden.")
        except Exception as exc:
            self.handle_exception(exc)

    def do_PUT(self) -> None:  # noqa: N802
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
                self.send_error_json(HTTPStatus.NOT_FOUND, "Route nicht gefunden.")
        except Exception as exc:
            self.handle_exception(exc)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/actions/"):
                action = unquote(parsed.path.removeprefix("/api/actions/"))
                result = STATE.run_action(action)
                status = HTTPStatus.OK if result["ok"] else HTTPStatus.BAD_GATEWAY
                self.send_json(result, status)
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Route nicht gefunden.")
        except Exception as exc:
            self.handle_exception(exc)

    def send_static(self, path: Path, content_type: str) -> None:
        resolved = ensure_inside(path, STATIC_ROOT)
        if not resolved.exists() or not resolved.is_file():
            self.send_error_json(HTTPStatus.NOT_FOUND, "Datei nicht gefunden.")
            return
        body = resolved.read_bytes()
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
            raise ValueError(f"Request ist größer als {MAX_BODY_BYTES} Bytes.")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON-Body muss ein Objekt sein.")
        return payload

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
    print(f"OpenWebUI Workbench dashboard listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
