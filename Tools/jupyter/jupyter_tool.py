"""
title: Air-Gapped Jupyter Python Executor
description: Execute restricted Python code on a configured local or internal Jupyter server.
version: 1.0.0
"""

from __future__ import annotations

import ast
import json
import os
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - OpenWebUI normally provides pydantic
    BaseModel = object

    def Field(default=None, description: str = ""):
        return default


class SecurityPolicyError(ValueError):
    pass


class _SecurityVisitor(ast.NodeVisitor):
    DENIED_IMPORT_ROOTS = {
        "os",
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "aiohttp",
        "urllib",
        "http",
        "ftplib",
        "smtplib",
        "paramiko",
        "telnetlib",
        "ssl",
        "shutil",
        "pathlib",
        "glob",
        "importlib",
        "runpy",
        "ctypes",
        "multiprocessing",
        "threading",
        "pickle",
        "marshal",
        "zipfile",
        "tarfile",
    }
    DENIED_CALL_NAMES = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "input",
        "breakpoint",
        "open",
    }
    DENIED_ATTR_NAMES = {
        "system",
        "popen",
        "Popen",
        "run",
        "call",
        "check_call",
        "check_output",
        "remove",
        "unlink",
        "rmtree",
        "rename",
        "replace",
        "chmod",
        "chown",
        "kill",
        "connect",
    }
    FILE_FUNCTION_ATTRS = {
        "read_csv",
        "read_excel",
        "read_json",
        "read_parquet",
        "to_csv",
        "to_excel",
        "to_json",
        "to_parquet",
        "load_workbook",
        "Document",
        "Presentation",
    }

    def __init__(self, allowed_workdir: str):
        self.allowed_workdir = Path(allowed_workdir).resolve() if allowed_workdir else None

    def _fail(self, node: ast.AST, message: str) -> None:
        raise SecurityPolicyError(f"Line {getattr(node, 'lineno', '?')}: {message}")

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root in self.DENIED_IMPORT_ROOTS:
                self._fail(node, f"Import of '{root}' is not allowed by the Jupyter tool policy.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        root = (node.module or "").split(".", 1)[0]
        if root in self.DENIED_IMPORT_ROOTS:
            self._fail(node, f"Import from '{root}' is not allowed by the Jupyter tool policy.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        func = node.func
        if isinstance(func, ast.Name) and func.id in self.DENIED_CALL_NAMES:
            self._fail(node, f"Call to '{func.id}' is not allowed.")
        if isinstance(func, ast.Attribute):
            if func.attr in self.DENIED_ATTR_NAMES:
                self._fail(node, f"Call to attribute '{func.attr}' is not allowed.")
            if func.attr in self.FILE_FUNCTION_ATTRS:
                self._check_path_args(node)
        self.generic_visit(node)

    def _check_path_args(self, node: ast.Call) -> None:
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                self._check_path_literal(node, arg.value)

    def _check_path_literal(self, node: ast.AST, value: str) -> None:
        parsed = urllib.parse.urlparse(value)
        if parsed.scheme and len(parsed.scheme) > 1:
            self._fail(node, "URLs are not allowed as file paths.")
        if value.startswith("~"):
            self._fail(node, "Home-directory expansion is not allowed.")
        raw_parts = [part for part in re_split_path(value) if part]
        if ".." in raw_parts:
            self._fail(node, "Parent directory traversal is not allowed.")
        path = Path(value)
        if path.is_absolute():
            if not self.allowed_workdir:
                self._fail(node, "Absolute paths require OPENWEBUI_JUPYTER_ALLOWED_WORKDIR.")
            try:
                path.resolve().relative_to(self.allowed_workdir)
            except Exception:
                self._fail(node, "Absolute path is outside OPENWEBUI_JUPYTER_ALLOWED_WORKDIR.")


def re_split_path(value: str) -> List[str]:
    return value.replace("\\", "/").split("/")


def _validate_python_code(code: str, allowed_workdir: str = "") -> None:
    if not isinstance(code, str) or not code.strip():
        raise SecurityPolicyError("Code must be a non-empty Python string.")
    if len(code) > 20000:
        raise SecurityPolicyError("Code is too large for this controlled tool call.")
    for number, line in enumerate(code.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("!") or stripped.startswith("%"):
            raise SecurityPolicyError(f"Line {number}: shell and IPython magic commands are not allowed.")
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise SecurityPolicyError(f"Python syntax error before execution: {exc}") from exc
    _SecurityVisitor(allowed_workdir).visit(tree)


if BaseModel is object:
    class _Valves:
        OPENWEBUI_JUPYTER_URL = ""
        OPENWEBUI_JUPYTER_TOKEN = ""
        OPENWEBUI_JUPYTER_TIMEOUT_SECONDS = 30
        OPENWEBUI_JUPYTER_ALLOWED_WORKDIR = ""
else:
    class _Valves(BaseModel):
        OPENWEBUI_JUPYTER_URL: str = Field(default="", description="Local or internal Jupyter base URL, e.g. http://127.0.0.1:8888")
        OPENWEBUI_JUPYTER_TOKEN: str = Field(default="", description="Jupyter token. Leave empty only for a locally configured tokenless server.")
        OPENWEBUI_JUPYTER_TIMEOUT_SECONDS: int = Field(default=30, description="Execution timeout in seconds.")
        OPENWEBUI_JUPYTER_ALLOWED_WORKDIR: str = Field(default="", description="Allowed working directory on the Jupyter host.")


class _JupyterClient:
    def __init__(self, base_url: str, token: str, timeout_seconds: int):
        self.base_url = base_url.rstrip("/")
        self.token = token or ""
        self.timeout_seconds = max(1, int(timeout_seconds))
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OPENWEBUI_JUPYTER_URL must be an http(s) URL.")
        self.parsed = parsed

    def _url(self, path: str) -> str:
        query = {}
        if self.token:
            query["token"] = self.token
        suffix = urllib.parse.urlencode(query)
        url = f"{self.base_url}{path}"
        return f"{url}?{suffix}" if suffix else url

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def request(self, method: str, path: str, payload: Optional[dict] = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self._url(path), data=data, method=method, headers=self._headers())
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}

    def execute(self, code: str) -> dict:
        try:
            import websocket  # type: ignore
        except Exception:
            return {
                "ok": False,
                "status": "dependency_missing",
                "error": "Python package 'websocket-client' is required in the OpenWebUI tool runtime to talk to Jupyter channels.",
            }

        kernel_id = ""
        try:
            kernel = self.request("POST", "/api/kernels", {"name": "python3"})
            kernel_id = kernel.get("id", "")
            if not kernel_id:
                raise RuntimeError("Jupyter did not return a kernel id.")
            session_id = uuid.uuid4().hex
            msg_id = uuid.uuid4().hex
            ws_scheme = "wss" if self.parsed.scheme == "https" else "ws"
            qs = {"session_id": session_id}
            if self.token:
                qs["token"] = self.token
            ws_url = f"{ws_scheme}://{self.parsed.netloc}{self.parsed.path.rstrip('/')}/api/kernels/{kernel_id}/channels?{urllib.parse.urlencode(qs)}"
            ws = websocket.create_connection(ws_url, timeout=self.timeout_seconds)
            request = {
                "header": {
                    "msg_id": msg_id,
                    "username": "openwebui",
                    "session": session_id,
                    "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "msg_type": "execute_request",
                    "version": "5.3",
                },
                "parent_header": {},
                "metadata": {},
                "content": {
                    "code": code,
                    "silent": False,
                    "store_history": False,
                    "user_expressions": {},
                    "allow_stdin": False,
                    "stop_on_error": True,
                },
                "channel": "shell",
                "buffers": [],
            }
            ws.send(json.dumps(request))
            result = {
                "stdout": "",
                "stderr": "",
                "result": [],
                "display_data": [],
                "error_name": "",
                "error_value": "",
                "traceback": [],
            }
            deadline = time.time() + self.timeout_seconds
            status = "ok"
            while time.time() < deadline:
                raw = ws.recv()
                message = json.loads(raw)
                if message.get("parent_header", {}).get("msg_id") != msg_id:
                    continue
                msg_type = message.get("msg_type") or message.get("header", {}).get("msg_type")
                content = message.get("content", {})
                if msg_type == "stream":
                    if content.get("name") == "stderr":
                        result["stderr"] += content.get("text", "")
                    else:
                        result["stdout"] += content.get("text", "")
                elif msg_type in {"execute_result", "display_data"}:
                    data = content.get("data", {})
                    target = "result" if msg_type == "execute_result" else "display_data"
                    result[target].append(data.get("text/plain") or data)
                elif msg_type == "error":
                    status = "error"
                    result["error_name"] = content.get("ename", "")
                    result["error_value"] = content.get("evalue", "")
                    result["traceback"] = [_sanitize(item, self.token) for item in content.get("traceback", [])]
                elif msg_type == "execute_reply":
                    status = content.get("status", status)
                    break
            else:
                status = "timeout"
                try:
                    self.request("POST", f"/api/kernels/{kernel_id}/interrupt", {})
                except Exception:
                    pass
            try:
                ws.close()
            except Exception:
                pass
            return {"ok": status == "ok", "status": status, "execution": _sanitize_obj(result, self.token)}
        finally:
            if kernel_id:
                try:
                    self.request("DELETE", f"/api/kernels/{kernel_id}")
                except Exception:
                    pass


def _sanitize(text: Any, token: str) -> Any:
    if not isinstance(text, str):
        return text
    if token:
        text = text.replace(token, "<redacted-token>")
    return text


def _sanitize_obj(obj: Any, token: str) -> Any:
    if isinstance(obj, dict):
        return {key: _sanitize_obj(value, token) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_obj(value, token) for value in obj]
    return _sanitize(obj, token)


class Tools:
    def __init__(self):
        self.valves = _Valves()

    def run_python(self, code: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute restricted Python code on a configured Jupyter server and return structured output.

        The static guard blocks common shell, network, import, process and unsafe file operations.
        The real sandbox boundary is still the configured Jupyter server and its operating environment.
        """
        allowed_workdir = self._config("OPENWEBUI_JUPYTER_ALLOWED_WORKDIR")
        try:
            _validate_python_code(code, allowed_workdir)
        except SecurityPolicyError as exc:
            return {"ok": False, "status": "blocked", "error": str(exc)}

        url = self._config("OPENWEBUI_JUPYTER_URL")
        token = self._config("OPENWEBUI_JUPYTER_TOKEN")
        configured_timeout = timeout_seconds or self._config("OPENWEBUI_JUPYTER_TIMEOUT_SECONDS") or 30
        if not url:
            return {"ok": False, "status": "configuration_error", "error": "OPENWEBUI_JUPYTER_URL is not configured."}

        wrapped_code = self._wrap_code(code, allowed_workdir)
        try:
            client = _JupyterClient(url, token, int(configured_timeout))
            response = client.execute(wrapped_code)
        except urllib.error.URLError:
            response = {"ok": False, "status": "connection_error", "error": "Configured Jupyter server is not reachable."}
        except Exception as exc:
            response = {"ok": False, "status": "error", "error": _sanitize(str(exc), token)}
        response["security"] = {
            "static_policy_applied": True,
            "allowed_workdir": allowed_workdir or "not configured",
            "sandbox_boundary": "Actual isolation depends on the configured Jupyter server.",
        }
        return _sanitize_obj(response, token)

    def _config(self, name: str) -> Any:
        value = getattr(self.valves, name, None)
        if value in (None, ""):
            value = os.getenv(name, "")
        return value

    def _wrap_code(self, code: str, allowed_workdir: str) -> str:
        prefix = ""
        if allowed_workdir:
            safe_dir = json.dumps(allowed_workdir)
            prefix = (
                "import os as _openwebui_os\n"
                f"_openwebui_allowed_workdir = {safe_dir}\n"
                "_openwebui_os.makedirs(_openwebui_allowed_workdir, exist_ok=True)\n"
                "_openwebui_os.chdir(_openwebui_allowed_workdir)\n"
                "del _openwebui_os\n"
            )
        return prefix + code
