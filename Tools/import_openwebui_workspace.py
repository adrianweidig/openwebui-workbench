#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import mimetypes
import os
import re
import ssl
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen


# Compatibility fallbacks only. Real deployments should use the ignored
# scripts/openwebui_workspace_config.yaml so endpoints, tokens, paths and valves
# stay in one local file. Do not commit real tokens.
OPENWEBUI_ADMIN_TOKEN = "PASTE_OPENWEBUI_ADMIN_API_TOKEN_HERE"
OPENWEBUI_BASE_URL = "http://localhost:3000"
JUPYTER_URL = ""
JUPYTER_TOKEN = ""
JUPYTER_TIMEOUT_SECONDS = 30
JUPYTER_ALLOWED_WORKDIR = ""
ARTIFACT_ROOT = ""
OFFLINE_ADDONS_ROOT = ""
OFFLINE_ADDONS_PYTHON_PATH = ""
PLAYWRIGHT_BROWSERS_PATH = ""
NLTK_DATA_PATH = ""
PREFER_PLAYWRIGHT_PDF = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "Tools"
TOOLS_INDEX = TOOLS_DIR / "index.json"
OPENWEBUI_EXT = TOOLS_DIR / "openwebui_ext"
TOOLS_REGISTRY = TOOLS_DIR / "dist" / "openwebui-tool-registry.json"
FUNCTION_REGISTRY = TOOLS_DIR / "dist" / "openwebui-function-registry.json"
PROMPT_IMPORT = TOOLS_DIR / "dist" / "openwebui-prompts-import.json"
SKILLS_DIR = OPENWEBUI_EXT / "skills"
PROMPTS_DIR = OPENWEBUI_EXT / "prompts"
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA = "workbench-file-context/v1"
WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID = "workbench_required_file_context_filter"
REQUIRED_FILE_CONTEXT_CACHE = ROOT / "Artefakte" / "temp" / "openwebui_required_file_context_uploads.json"
LEGACY_EXAMPLE_RESULT_FILE = "beispielergebnis.md"
MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES = {
    "api-schnittstellenentwurf": "beispielergebnis.yaml",
    "codegenerierung": "beispielergebnis.py",
    "informationsextraktion": "beispielergebnis.json",
    "json-csv-log-analyse": "beispielergebnis.json",
    "n8n-workflow-architect": "beispielergebnis.json",
    "präsentationserstellung": "beispielergebnis.html",
    "report-dashboard-vorbereitung": "beispielergebnis.html",
    "tabellen-csv-datenanalyse": "beispielergebnis.py",
}
MODEL_EXAMPLES_DIR_NAME = "beispiele"
MODEL_I18N_DIR_NAME = "i18n"
PRIMARY_MODEL_I18N_FILES = ("manifest.json", "de.md", "en.md")
DEFAULT_CONFIG_NAME = "openwebui_workspace_config.yaml"
IMPORT_LOCK_PATH = ROOT / "Artefakte" / "temp" / "openwebui_workspace_import.lock"
IMPORT_LOCK_STALE_SECONDS = 2 * 60 * 60

PLACEHOLDER_TOKENS = {"", "PASTE_OPENWEBUI_ADMIN_API_TOKEN_HERE", "YOUR_OPEN_WEBUI_API_KEY"}
TRANSIENT_HTTP_STATUS = {502, 503, 504}
TEXT_KNOWLEDGE_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".ipynb",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sql",
    ".svg",
    ".toml",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def log_progress(message: str) -> None:
    print(f"[import] {message}", flush=True)
PUBLIC_READ_GRANT = {"principal_type": "user", "principal_id": "*", "permission": "read"}


def is_not_found_error(exc: RuntimeError) -> bool:
    message = str(exc).lower()
    return (
        "http 404" in message
        or "http 405" in message
        or "could not find what you're looking for" in message
        or "could not find what youre looking for" in message
    )


def is_already_registered_error(exc: RuntimeError) -> bool:
    message = str(exc).lower()
    return "already registered" in message or "already exists" in message


def openwebui_ssl_context(tls_verify: bool, ca_file: str = "", ca_path: str = "") -> ssl.SSLContext | None:
    if not tls_verify:
        # Explicit local/admin opt-out via tls_verify=false.
        return ssl._create_unverified_context()  # nosec B323
    if ca_file or ca_path:
        return ssl.create_default_context(cafile=ca_file or None, capath=ca_path or None)
    return None


def require_http_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("OpenWebUI API requests must use http(s) URLs with a host.")
    return url


@dataclass(frozen=True)
class ImportResult:
    kind: str
    created: int = 0
    updated: int = 0
    skipped: int = 0


@dataclass(frozen=True)
class KnowledgeUpsertResult:
    knowledge: dict[str, str]
    changed: bool


@dataclass(frozen=True)
class ModelLoadResult:
    models: list[dict[str, Any]]
    knowledge_updated: int = 0
    knowledge_skipped: int = 0
    required_files_uploaded: int = 0
    required_files_reused: int = 0


class OpenWebUIClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: int = 120,
        auth_header: str = "Authorization",
        auth_scheme: str | None = "Bearer",
        tls_verify: bool = True,
        ca_file: str = "",
        ca_path: str = "",
    ) -> None:
        self.base_url = normalize_openwebui_base_url(base_url)
        self.timeout = timeout
        self.auth_header = auth_header.strip() or "Authorization"
        self.auth_scheme = "" if auth_scheme is None else str(auth_scheme).strip()
        self.ssl_context = openwebui_ssl_context(tls_verify, ca_file, ca_path)
        auth_value = token if not self.auth_scheme else f"{self.auth_scheme} {token}"
        self.headers = {
            self.auth_header: auth_value,
        }

    def api_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        return require_http_url(url)

    def request(
        self,
        method: str,
        path: str,
        payload: Any | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected: tuple[int, ...] = (200,),
        auth: bool = True,
    ) -> Any:
        body = None
        request_headers = dict(self.headers if auth else {})
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        if headers:
            request_headers.update(headers)
        url = self.api_url(path, query)
        for attempt in range(3):
            request = Request(url, data=body, headers=request_headers, method=method)
            try:
                # URL is built from the validated http(s) OpenWebUI base URL.
                with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:  # nosec B310
                    raw = response.read()
                    if response.status not in expected:
                        raise RuntimeError(f"{method} {path} returned HTTP {response.status}: {raw[:500]!r}")
                    if not raw:
                        return None
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        return json.loads(raw.decode("utf-8"))
                    try:
                        return json.loads(raw.decode("utf-8"))
                    except json.JSONDecodeError:
                        return raw.decode("utf-8", errors="replace")
            except HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                if exc.code in expected:
                    return None
                if exc.code in TRANSIENT_HTTP_STATUS and attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise RuntimeError(f"{method} {path} returned HTTP {exc.code}: {raw[:1000]}") from exc
            except URLError as exc:
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise RuntimeError(f"Cannot reach OpenWebUI at {self.base_url}: {exc}") from exc

    def request_any(
        self,
        method: str,
        paths: list[str],
        payload: Any | None = None,
        query: dict[str, Any] | None = None,
        expected: tuple[int, ...] = (200,),
    ) -> Any:
        last_not_found: RuntimeError | None = None
        for path in paths:
            try:
                return self.request(method, path, payload=payload, query=query, expected=expected)
            except RuntimeError as exc:
                if is_not_found_error(exc):
                    last_not_found = exc
                    continue
                raise
        if last_not_found:
            raise last_not_found
        raise RuntimeError(f"No API path candidates supplied for {method}")

    def upload_file(self, path: Path, process: bool = True) -> dict[str, Any]:
        boundary = f"----openwebui-workspace-{uuid.uuid4().hex}"
        content_type = (
            "text/plain; charset=utf-8"
            if path.suffix.lower() in TEXT_KNOWLEDGE_SUFFIXES
            else mimetypes.guess_type(path.name)[0] or "text/plain"
        )
        parts = [
            f"--{boundary}\r\n".encode("utf-8"),
            (
                f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode("utf-8"),
            path.read_bytes(),
            f"\r\n--{boundary}--\r\n".encode("utf-8"),
        ]
        body = b"".join(parts)
        headers = {
            **self.headers,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }
        request = Request(
            self.api_url(
                "/api/v1/files/",
                {
                    "process": "true" if process else "false",
                    "process_in_background": "false",
                },
            ),
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            # URL is built from the validated http(s) OpenWebUI base URL.
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:  # nosec B310
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Upload failed for {path}: HTTP {exc.code}: {raw[:1000]}") from exc

    def file_process_status(self, file_id: str) -> dict[str, Any]:
        return self.request("GET", f"/api/v1/files/{file_id}/process/status")

    def wait_for_file_processing(self, file_id: str, timeout_seconds: int = 180) -> str:
        deadline = time.time() + max(1, timeout_seconds)
        last_status = "unknown"
        while time.time() < deadline:
            try:
                status_payload = self.file_process_status(file_id)
            except RuntimeError as exc:
                if is_not_found_error(exc):
                    return "unknown"
                raise
            if isinstance(status_payload, dict):
                raw_status = status_payload.get("status") or status_payload.get("state") or status_payload.get("result")
                if raw_status:
                    last_status = str(raw_status)
                if last_status.lower() in {"completed", "complete", "processed", "success", "done"}:
                    return "completed"
                if last_status.lower() in {"failed", "error"}:
                    raise RuntimeError(f"OpenWebUI file processing failed for {file_id}: {status_payload}")
            time.sleep(2)
        return last_status


def normalize_openwebui_base_url(base_url: str) -> str:
    """The importer appends /api paths itself; config must point at the WebUI root."""
    normalized = str(base_url).strip().rstrip("/")
    for suffix in ("/api/v1", "/api"):
        if normalized.lower().endswith(suffix):
            normalized = normalized[: -len(suffix)].rstrip("/")
            break
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("openwebui.base_url must be an http(s) URL with a host.")
    return normalized


@contextmanager
def import_lock() -> Any:
    IMPORT_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    stale_seconds = int(os.environ.get("OPENWEBUI_IMPORT_LOCK_STALE_SECONDS") or IMPORT_LOCK_STALE_SECONDS)
    while True:
        try:
            fd = os.open(str(IMPORT_LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(json.dumps({"pid": os.getpid(), "created_at": time.time()}))
            break
        except FileExistsError as exc:
            try:
                age = time.time() - IMPORT_LOCK_PATH.stat().st_mtime
                details = IMPORT_LOCK_PATH.read_text(encoding="utf-8", errors="replace")
            except OSError:
                age = 0
                details = ""
            if age > stale_seconds:
                try:
                    IMPORT_LOCK_PATH.unlink()
                    continue
                except OSError:
                    pass
            raise RuntimeError(
                f"OpenWebUI import lock exists at {IMPORT_LOCK_PATH}. "
                f"Another import is probably running or was killed recently. Details: {details[:200]}"
            ) from exc
    try:
        yield
    finally:
        try:
            IMPORT_LOCK_PATH.unlink()
        except FileNotFoundError:
            pass


def auth_header_defaults(auth_header: str | None, auth_scheme: str | None = None) -> tuple[str, str]:
    header = (auth_header or "Authorization").strip() or "Authorization"
    if auth_scheme is not None:
        return header, str(auth_scheme).strip()
    if header.lower() == "authorization":
        return header, "Bearer"
    return header, ""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def path_sort_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix().casefold()
    except ValueError:
        return path.as_posix().casefold()


def strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_double:
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index]
    return line


def parse_config_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if lowered in {"null", "none", "~"}:
        return ""
    try:
        return int(value)
    except ValueError:
        return value


def read_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = strip_yaml_comment(raw_line).rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            raise ValueError(f"{path}: YAML lists are not supported in this lightweight config parser: {raw_line}")
        indent = len(line) - len(line.lstrip(" "))
        clean = line.strip()
        if ":" not in clean:
            raise ValueError(f"{path}: expected 'key: value' line: {raw_line}")
        key, raw_value = clean.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"{path}: empty config key: {raw_line}")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root
        if raw_value.strip() == "":
            node: dict[str, Any] = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            parent[key] = parse_config_scalar(raw_value)
    return root


def default_config_paths() -> list[Path]:
    return [
        ROOT / "scripts" / DEFAULT_CONFIG_NAME,
        Path(__file__).with_name(DEFAULT_CONFIG_NAME),
        ROOT / DEFAULT_CONFIG_NAME,
    ]


def load_config(path_value: str | None) -> tuple[dict[str, Any], Path | None]:
    if path_value:
        path = Path(path_value)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        return read_simple_yaml(path), path
    for path in default_config_paths():
        if path.exists():
            return read_simple_yaml(path), path
    return {}, None


def config_get(config: dict[str, Any], dotted_path: str, default: Any = None) -> Any:
    value: Any = config
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def config_section(config: dict[str, Any], dotted_path: str) -> dict[str, Any]:
    value = config_get(config, dotted_path, {})
    return value if isinstance(value, dict) else {}


def first_config_value(config: dict[str, Any], dotted_paths: list[str], default: Any = None) -> Any:
    for dotted_path in dotted_paths:
        value = config_get(config, dotted_path, None)
        if value not in (None, ""):
            return value
    return default


def as_bool(value: Any, default: bool = False) -> bool:
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def as_int(value: Any, default: int) -> int:
    if value in (None, ""):
        return default
    return int(value)


def clean_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in mapping.items() if value not in (None, "")}


def nested_clean_mapping(mapping: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cleaned: dict[str, dict[str, Any]] = {}
    for key, value in mapping.items():
        if not isinstance(value, dict):
            continue
        cleaned_value = clean_mapping(value)
        if cleaned_value:
            cleaned[str(key)] = cleaned_value
    return cleaned


def merge_valves(
    base: dict[str, dict[str, Any]],
    overrides: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    merged = {tool_id: dict(valves) for tool_id, valves in base.items()}
    for item_id, valves in overrides.items():
        current = merged.setdefault(item_id, {})
        current.update(clean_mapping(valves))
        if not current:
            merged.pop(item_id, None)
    return merged


def runtime_env_value(environment: dict[str, Any], name: str) -> Any:
    """Read a runtime value from YAML first, then from the process environment."""
    return environment.get(name) or os.environ.get(name)


def resolve_runtime_config(args: argparse.Namespace) -> dict[str, Any]:
    config, config_path = load_config(args.config)
    environment = clean_mapping(config_section(config, "environment"))
    explicit_tool_valves = nested_clean_mapping(config_section(config, "tool_valves"))
    explicit_function_valves = nested_clean_mapping(config_section(config, "function_valves"))
    base_url = (
        args.base_url
        or first_config_value(config, ["openwebui.base_url", "openwebui.url"])
        or runtime_env_value(environment, "OPENWEBUI_BASE_URL")
        or OPENWEBUI_BASE_URL
    )
    token = (
        args.token
        or first_config_value(config, ["openwebui.admin_token", "openwebui.api_key", "openwebui.token"])
        or runtime_env_value(environment, "OPENWEBUI_ADMIN_TOKEN")
        or OPENWEBUI_ADMIN_TOKEN
    )
    auth_header, auth_scheme = auth_header_defaults(
        args.auth_header
        or first_config_value(
            config,
            [
                "openwebui.auth_header",
                "openwebui.api_key_header",
                "openwebui.custom_api_key_header",
                "environment.OPENWEBUI_AUTH_HEADER",
                "environment.CUSTOM_API_KEY_HEADER",
            ],
        )
        or runtime_env_value(environment, "OPENWEBUI_AUTH_HEADER")
        or runtime_env_value(environment, "CUSTOM_API_KEY_HEADER"),
        args.auth_scheme
        if args.auth_scheme is not None
        else first_config_value(
            config,
            [
                "openwebui.auth_scheme",
                "openwebui.token_scheme",
                "environment.OPENWEBUI_AUTH_SCHEME",
            ],
            None,
        )
        or runtime_env_value(environment, "OPENWEBUI_AUTH_SCHEME"),
    )
    timeout = as_int(
        args.timeout
        if args.timeout is not None
        else first_config_value(config, ["openwebui.timeout_seconds", "import.timeout_seconds"], 120),
        120,
    )
    tls_verify = as_bool(
        args.tls_verify
        if args.tls_verify is not None
        else (
            os.environ.get("OPENWEBUI_TLS_VERIFY")
            or first_config_value(config, ["openwebui.tls_verify", "openwebui.verify_tls", "openwebui.ssl_verify"], True)
        ),
        True,
    )
    ca_file = str(
        args.ca_file
        or os.environ.get("OPENWEBUI_CA_FILE")
        or first_config_value(config, ["openwebui.ca_file", "openwebui.cafile", "openwebui.ca_bundle"], "")
        or ""
    ).strip()
    ca_path = str(
        args.ca_path
        or os.environ.get("OPENWEBUI_CA_PATH")
        or first_config_value(config, ["openwebui.ca_path", "openwebui.capath"], "")
        or ""
    ).strip()
    include_optional = args.include_optional_network_tools or as_bool(
        first_config_value(config, ["import.include_optional_network_tools"], False),
        False,
    )
    # Workspace imports are intentionally shared by default: imported tools,
    # skills, model knowledge and model profiles must be visible to all
    # OpenWebUI users. The legacy config key/CLI flag is kept for compatibility
    # but no longer disables public workspace publication.
    public_read = True
    skip_knowledge = args.skip_knowledge or as_bool(first_config_value(config, ["import.skip_knowledge"], False))
    model_file_context = {
        "enabled": as_bool(first_config_value(config, ["model_file_context.enabled"], True), True),
        "upload_required_files": as_bool(first_config_value(config, ["model_file_context.upload_required_files"], True), True),
        "poll_processing_status": as_bool(first_config_value(config, ["model_file_context.poll_processing_status"], True), True),
        "processing_timeout_seconds": as_int(
            first_config_value(config, ["model_file_context.processing_timeout_seconds"], 180),
            180,
        ),
        "attach_uploaded_files_to_model_meta": as_bool(
            first_config_value(config, ["model_file_context.attach_uploaded_files_to_model_meta"], True),
            True,
        ),
        "required_context_filter_id": str(
            first_config_value(
                config,
                ["model_file_context.required_context_filter_id"],
                WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID,
            )
            or WORKBENCH_REQUIRED_FILE_CONTEXT_FILTER_ID
        ),
        "knowledge_examples_only": as_bool(first_config_value(config, ["model_file_context.knowledge_examples_only"], True), True),
    }
    jupyter = {
        "OPENWEBUI_JUPYTER_URL": (
            args.jupyter_url
            or first_config_value(
                config,
                [
                    "tool_valves.air_gapped_jupyter_python.OPENWEBUI_JUPYTER_URL",
                    "jupyter.url",
                    "jupyter.base_url",
                    "environment.OPENWEBUI_JUPYTER_URL",
                ],
            )
            or JUPYTER_URL
        ),
        "OPENWEBUI_JUPYTER_TOKEN": (
            args.jupyter_token
            or first_config_value(
                config,
                [
                    "tool_valves.air_gapped_jupyter_python.OPENWEBUI_JUPYTER_TOKEN",
                    "jupyter.token",
                    "jupyter.api_token",
                    "environment.OPENWEBUI_JUPYTER_TOKEN",
                ],
            )
            or JUPYTER_TOKEN
        ),
        "OPENWEBUI_JUPYTER_TIMEOUT_SECONDS": (
            args.jupyter_timeout_seconds
            or first_config_value(
                config,
                [
                    "tool_valves.air_gapped_jupyter_python.OPENWEBUI_JUPYTER_TIMEOUT_SECONDS",
                    "jupyter.timeout_seconds",
                    "environment.OPENWEBUI_JUPYTER_TIMEOUT_SECONDS",
                ],
            )
            or JUPYTER_TIMEOUT_SECONDS
        ),
        "OPENWEBUI_JUPYTER_ALLOWED_WORKDIR": (
            args.jupyter_allowed_workdir
            or first_config_value(
                config,
                [
                    "tool_valves.air_gapped_jupyter_python.OPENWEBUI_JUPYTER_ALLOWED_WORKDIR",
                    "jupyter.allowed_workdir",
                    "jupyter.workdir",
                    "environment.OPENWEBUI_JUPYTER_ALLOWED_WORKDIR",
                ],
            )
            or JUPYTER_ALLOWED_WORKDIR
        ),
    }
    artifact_root = (
        args.artifact_root
        or first_config_value(
            config,
            [
                "tool_valves.offline_artifact_workbench.artifact_root",
                "artifacts.root",
                "artifact_root",
                "environment.OPENWEBUI_ARTIFACT_ROOT",
                "tools.offline_artifact_workbench.artifact_root",
            ],
        )
        or ARTIFACT_ROOT
    )
    prefer_playwright_pdf = (
        args.prefer_playwright_pdf
        if args.prefer_playwright_pdf is not None
        else first_config_value(
            config,
            [
                "tool_valves.offline_artifact_workbench.prefer_playwright_pdf",
                "addons.prefer_playwright_pdf",
                "offline_addons.prefer_playwright_pdf",
                "tools.offline_artifact_workbench.prefer_playwright_pdf",
            ],
            PREFER_PLAYWRIGHT_PDF,
        )
    )
    addons = {
        "offline_addons_root": (
            args.offline_addons_root
            or first_config_value(
                config,
                [
                    "tool_valves.offline_artifact_workbench.offline_addons_root",
                    "addons.root",
                    "offline_addons.root",
                    "environment.OPENWEBUI_OFFLINE_ADDONS_ROOT",
                ],
            )
            or OFFLINE_ADDONS_ROOT
        ),
        "offline_addons_python_path": (
            args.offline_addons_python_path
            or first_config_value(
                config,
                [
                    "tool_valves.offline_artifact_workbench.offline_addons_python_path",
                    "addons.python_path",
                    "addons.python_dir",
                    "offline_addons.python_path",
                    "environment.OPENWEBUI_OFFLINE_ADDONS_PYTHON_PATH",
                ],
            )
            or OFFLINE_ADDONS_PYTHON_PATH
        ),
        "playwright_browsers_path": (
            args.playwright_browsers_path
            or first_config_value(
                config,
                [
                    "tool_valves.offline_artifact_workbench.playwright_browsers_path",
                    "addons.playwright_browsers_path",
                    "offline_addons.playwright_browsers_path",
                    "environment.PLAYWRIGHT_BROWSERS_PATH",
                ],
            )
            or PLAYWRIGHT_BROWSERS_PATH
        ),
        "nltk_data_path": (
            args.nltk_data_path
            or first_config_value(
                config,
                [
                    "tool_valves.offline_artifact_workbench.nltk_data_path",
                    "addons.nltk_data",
                    "addons.nltk_data_path",
                    "offline_addons.nltk_data_path",
                    "environment.NLTK_DATA",
                ],
            )
            or NLTK_DATA_PATH
        ),
        "prefer_playwright_pdf": as_bool(prefer_playwright_pdf, True),
    }
    return {
        "config_path": config_path,
        "base_url": normalize_openwebui_base_url(str(base_url)),
        "token": str(token).strip(),
        "auth_header": auth_header,
        "auth_scheme": auth_scheme,
        "timeout": timeout,
        "tls_verify": tls_verify,
        "ca_file": ca_file,
        "ca_path": ca_path,
        "include_optional_network_tools": include_optional,
        "public_read": public_read,
        "skip_knowledge": skip_knowledge,
        "jupyter": jupyter,
        "artifact_root": str(artifact_root or ""),
        "addons": addons,
        "environment": environment,
        "tool_valves": explicit_tool_valves,
        "function_valves": explicit_function_valves,
        "model_file_context": model_file_context,
    }


def configured_tool_valves(runtime: dict[str, Any]) -> dict[str, dict[str, Any]]:
    valves: dict[str, dict[str, Any]] = {}
    jupyter = {
        key: value
        for key, value in runtime.get("jupyter", {}).items()
        if value not in (None, "")
    }
    if jupyter:
        valves["air_gapped_jupyter_python"] = jupyter
    artifact_root = runtime.get("artifact_root")
    artifact_valves: dict[str, Any] = {}
    if artifact_root:
        artifact_valves["artifact_root"] = artifact_root
    addons = runtime.get("addons", {})
    if isinstance(addons, dict):
        for key in [
            "offline_addons_root",
            "offline_addons_python_path",
            "playwright_browsers_path",
            "nltk_data_path",
        ]:
            value = addons.get(key)
            if value not in (None, ""):
                artifact_valves[key] = value
        if "prefer_playwright_pdf" in addons:
            artifact_valves["prefer_playwright_pdf"] = as_bool(addons.get("prefer_playwright_pdf"), True)
    if artifact_valves:
        valves["offline_artifact_workbench"] = artifact_valves
    return merge_valves(valves, runtime.get("tool_valves", {}))


def configured_function_valves(runtime: dict[str, Any]) -> dict[str, dict[str, Any]]:
    value = runtime.get("function_valves", {})
    return nested_clean_mapping(value) if isinstance(value, dict) else {}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-")
    return slug or "openwebui-item"


def parse_python_metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r'\s*"""(.*?)"""', text, flags=re.S)
    meta: dict[str, str] = {}
    if not match:
        return meta
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    return meta


def parse_skill(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    name = path.stem
    description = ""
    heading = re.search(r"^#\s+(.+)$", text, flags=re.M)
    if heading:
        name = heading.group(1).strip()
    for line in text.splitlines():
        clean = line.strip(" -*")
        if clean and not clean.startswith("#"):
            description = clean[:300]
            break
    return slugify(path.stem), name, description


def parse_markdown_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, normalized
    meta: dict[str, str] = {}
    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip().strip("\"'")
    if end_index is None:
        return {}, normalized
    return meta, "\n".join(lines[end_index + 1 :]).lstrip("\n")


def parse_csv_tags(value: str) -> list[str]:
    tags: list[str] = []
    for item in str(value or "").strip("[]").split(","):
        tag = item.strip().strip("\"'")
        if tag and tag not in tags:
            tags.append(tag)
    return tags or ["workbench"]


def normalize_prompt_command(value: str, fallback: str) -> str:
    command = str(value or fallback).strip().lstrip("/")
    command = re.sub(r"[^a-z0-9_-]+", "-", command.lower()).strip("-")
    return command or fallback


def load_tool_records(include_optional_network_tools: bool) -> list[dict[str, Any]]:
    registry = read_json(TOOLS_REGISTRY)
    excluded = set(registry.get("optional_network_tools_not_in_offline_default", []))
    records = []
    for record in registry.get("tools", []):
        if not record.get("importable"):
            continue
        if record.get("id") in excluded and not include_optional_network_tools:
            continue
        records.append(record)
    return records


def load_function_records() -> list[dict[str, Any]]:
    registry = read_json(FUNCTION_REGISTRY)
    return [record for record in registry.get("functions", []) if record.get("importable")]


def prompt_files() -> list[Path]:
    if not PROMPTS_DIR.exists():
        return []
    return sorted((path for path in PROMPTS_DIR.glob("*.md") if path.name.upper() != "README.MD"), key=path_sort_key)


def prompt_records_from_files() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in prompt_files():
        meta, body = parse_markdown_frontmatter(path)
        command = normalize_prompt_command(meta.get("command", path.stem), path.stem)
        content = body.strip() + "\n" if body.strip() else path.read_text(encoding="utf-8")
        records.append(
            {
                "id": path.stem,
                "command": command,
                "name": meta.get("name") or path.stem.replace("_", " ").replace("-", " ").title(),
                "content": content,
                "data": {"source_file": str(path.relative_to(ROOT)).replace("\\", "/")},
                "meta": {
                    "description": meta.get("description") or "OpenWebUI Workspace Prompt.",
                    "source": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "schema": "openwebui-workbench-prompt/v1",
                },
                "tags": parse_csv_tags(meta.get("tags", "workbench")),
            }
        )
    return records


def load_prompt_records() -> list[dict[str, Any]]:
    if PROMPT_IMPORT.exists():
        payload = read_json(PROMPT_IMPORT)
        if not isinstance(payload, list):
            raise RuntimeError(f"{PROMPT_IMPORT.relative_to(ROOT)} must be a JSON array")
        return [record for record in payload if isinstance(record, dict) and record.get("command") and record.get("content")]
    return prompt_records_from_files()


def get_existing(client: OpenWebUIClient, path: str) -> dict[str, Any] | None:
    try:
        value = client.request("GET", path)
        return value if isinstance(value, dict) else None
    except RuntimeError as exc:
        if is_not_found_error(exc):
            return None
        if "HTTP 401" in str(exc):
            return None
        raise


def get_existing_any(client: OpenWebUIClient, paths: list[str]) -> dict[str, Any] | None:
    try:
        value = client.request_any("GET", paths)
        return value if isinstance(value, dict) else None
    except RuntimeError as exc:
        if is_not_found_error(exc):
            return None
        raise


def check_openwebui_auth(client: OpenWebUIClient) -> None:
    try:
        client.request("GET", "/api/version", auth=False)
    except RuntimeError as exc:
        raise RuntimeError(
            f"OpenWebUI is not reachable at {client.base_url}. "
            "Set openwebui.base_url to the externally reachable WebUI root, not an /api or /api/v1 URL. "
            f"Probe failed: {exc}"
        ) from exc
    probe_paths = ["/api/v1/auths/", "/api/models"]
    probe_path = probe_paths[0]
    try:
        last_auth_error: RuntimeError | None = None
        for candidate in probe_paths:
            try:
                client.request("GET", candidate)
                return
            except RuntimeError as candidate_exc:
                if "HTTP 401" in str(candidate_exc):
                    last_auth_error = candidate_exc
                    continue
                raise
        if last_auth_error:
            raise last_auth_error
    except RuntimeError as exc:
        message = str(exc)
        if "HTTP 401" in message:
            header_hint = (
                "If a reverse proxy, SSO gateway or Basic Auth layer consumes the Authorization header, "
                "configure openwebui.auth_header: \"x-api-key\" and openwebui.auth_scheme: \"\" "
                "or match the OpenWebUI CUSTOM_API_KEY_HEADER setting."
            )
            if client.auth_header.lower() == "authorization":
                used = "Authorization: Bearer <token>"
            else:
                used = f"{client.auth_header}: <token>"
            raise RuntimeError(
                "OpenWebUI rejected the configured API credential with HTTP 401 before import started. "
                f"The importer used {used} against {client.base_url}{probe_path}. "
                "Verify that the token is an OpenWebUI API key or JWT for an admin user, that API keys are enabled, "
                "and that API key endpoint restrictions allow the required /api/v1 workspace routes. "
                f"{header_hint}"
            ) from exc
        raise


def public_read_grants(enabled: bool = True) -> list[dict[str, str]]:
    if not enabled:
        return []
    return [dict(PUBLIC_READ_GRANT)]


def access_payload(public: bool = True) -> dict[str, Any]:
    return {"access_grants": public_read_grants(public)}


def has_public_read_access(value: Any) -> bool:
    grants = value.get("access_grants", []) if isinstance(value, dict) else []
    return any(
        isinstance(grant, dict)
        and grant.get("principal_type") == PUBLIC_READ_GRANT["principal_type"]
        and grant.get("principal_id") == PUBLIC_READ_GRANT["principal_id"]
        and grant.get("permission") == PUBLIC_READ_GRANT["permission"]
        for grant in grants
    )


def require_public_read_access(value: Any, resource_type: str, resource_id: str) -> None:
    if has_public_read_access(value):
        return
    raise RuntimeError(
        f"OpenWebUI did not keep the public read grant for {resource_type} {resource_id}. "
        "Enable the matching public sharing permission in OpenWebUI or import with an admin token that may publish workspace resources."
    )


def update_tool_access(client: OpenWebUIClient, tool_id: str, public: bool = True) -> None:
    value = client.request_any(
        "POST",
        [
            f"/api/v1/tools/id/{tool_id}/access/update",
            f"/api/tools/id/{tool_id}/access/update",
        ],
        access_payload(public),
    )
    if public:
        require_public_read_access(value, "tool", tool_id)


def update_skill_access(client: OpenWebUIClient, skill_id: str, public: bool = True) -> None:
    value = client.request_any(
        "POST",
        [
            f"/api/v1/skills/id/{skill_id}/access/update",
            f"/api/skills/id/{skill_id}/access/update",
        ],
        access_payload(public),
    )
    if public:
        require_public_read_access(value, "skill", skill_id)


def update_prompt_access(client: OpenWebUIClient, prompt_id: str, public: bool = True) -> None:
    value = client.request_any(
        "POST",
        [
            f"/api/v1/prompts/id/{prompt_id}/access/update",
            f"/api/prompts/id/{prompt_id}/access/update",
        ],
        access_payload(public),
    )
    if public:
        require_public_read_access(value, "prompt", prompt_id)


def update_knowledge_access(client: OpenWebUIClient, knowledge_id: str, public: bool = True) -> None:
    value = client.request_any(
        "POST",
        [
            f"/api/v1/knowledge/{knowledge_id}/access/update",
            f"/api/knowledge/{knowledge_id}/access/update",
        ],
        access_payload(public),
    )
    if public:
        require_public_read_access(value, "knowledge", knowledge_id)


def update_model_access(client: OpenWebUIClient, model_id: str, model_name: str, public: bool = True) -> None:
    value = client.request_any(
        "POST",
        [
            "/api/v1/models/model/access/update",
            "/api/models/model/access/update",
        ],
        {"id": model_id, "name": model_name or model_id, **access_payload(public)},
    )
    if public:
        require_public_read_access(value, "model", model_id)


def function_bool(value: dict[str, Any] | None, names: tuple[str, ...]) -> bool | None:
    if not isinstance(value, dict):
        return None
    for name in names:
        if name in value:
            return bool(value[name])
    return None


def get_function(client: OpenWebUIClient, function_id: str) -> dict[str, Any]:
    value = client.request_any(
        "GET",
        [
            f"/api/v1/functions/id/{function_id}",
            f"/api/functions/id/{function_id}",
        ],
    )
    return value if isinstance(value, dict) else {}


def toggle_function_active(client: OpenWebUIClient, function_id: str) -> dict[str, Any]:
    value = client.request_any(
        "POST",
        [
            f"/api/v1/functions/id/{function_id}/toggle",
            f"/api/functions/id/{function_id}/toggle",
        ],
    )
    return value if isinstance(value, dict) else {}


def toggle_function_global(client: OpenWebUIClient, function_id: str) -> dict[str, Any]:
    value = client.request_any(
        "POST",
        [
            f"/api/v1/functions/id/{function_id}/toggle/global",
            f"/api/functions/id/{function_id}/toggle/global",
        ],
    )
    return value if isinstance(value, dict) else {}


def ensure_function_active_and_global(
    client: OpenWebUIClient,
    function_id: str,
    current: dict[str, Any] | None = None,
) -> None:
    function = current if isinstance(current, dict) else get_function(client, function_id)
    active_state = function_bool(function, ("is_active", "active", "enabled"))
    if active_state is False:
        function = toggle_function_active(client, function_id)

    global_state = function_bool(function, ("is_global", "global"))
    if global_state is None:
        function = get_function(client, function_id)
        global_state = function_bool(function, ("is_global", "global"))
    if global_state is None:
        raise RuntimeError(
            f"Function {function_id} response does not expose is_global; cannot safely publish it globally."
        )
    if global_state is False:
        toggle_function_global(client, function_id)

    function = get_function(client, function_id)
    if function_bool(function, ("is_active", "active", "enabled")) is not True:
        raise RuntimeError(f"Function {function_id} is not active after import.")
    if function_bool(function, ("is_global", "global")) is not True:
        raise RuntimeError(f"Function {function_id} is not global after import.")


def skill_files() -> list[Path]:
    return [path for path in sorted(SKILLS_DIR.glob("*.md")) if path.name.upper() != "README.MD"]


def legacy_example_result_file_name(model_id: str) -> str:
    return MODEL_LEGACY_EXAMPLE_FILE_OVERRIDES.get(model_id, LEGACY_EXAMPLE_RESULT_FILE)


def required_file_context_entries(model: dict[str, Any]) -> list[dict[str, Any]]:
    meta = model.get("meta") if isinstance(model.get("meta"), dict) else {}
    file_context = meta.get("workbenchFileContext") if isinstance(meta, dict) else {}
    if not isinstance(file_context, dict) or file_context.get("schema") != WORKBENCH_REQUIRED_FILE_CONTEXT_SCHEMA:
        raise RuntimeError(f"Model {model.get('id')} has no valid meta.workbenchFileContext")
    required = file_context.get("requiredFiles")
    if not isinstance(required, list) or len(required) != 3:
        raise RuntimeError(f"Model {model.get('id')} must define exactly three required file context files")
    entries = [item for item in required if isinstance(item, dict)]
    if len(entries) != 3:
        raise RuntimeError(f"Model {model.get('id')} required file context entries must be objects")
    return entries


def required_file_context_files(model_dir: Path, model: dict[str, Any]) -> list[Path]:
    files: list[Path] = []
    for item in required_file_context_entries(model):
        rel_path = str(item.get("path") or "").strip().replace("\\", "/")
        if not rel_path or rel_path.startswith("../") or "/../" in rel_path:
            raise RuntimeError(f"Unsafe required file context path for {model_dir.name}: {rel_path!r}")
        path = model_dir / rel_path
        files.append(path)
    missing = [path for path in files if not path.exists()]
    empty = [path for path in files if path.exists() and path.stat().st_size == 0]
    if missing or empty:
        details = []
        if missing:
            details.append("missing: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))
        if empty:
            details.append("empty: " + ", ".join(str(path.relative_to(ROOT)) for path in empty))
        raise RuntimeError(f"Model required file context is incomplete for {model_dir.name}: {'; '.join(details)}")
    for item, path in zip(required_file_context_entries(model), files):
        digest = hashlib.sha256(path.read_text(encoding="utf-8").strip().encode("utf-8")).hexdigest()
        if item.get("sha256") and item.get("sha256") != digest:
            raise RuntimeError(f"Model required file context sha256 mismatch for {model_dir.name}/{path.name}")
    return files


def model_example_files(model_dir: Path) -> list[Path]:
    examples_dir = model_dir / MODEL_EXAMPLES_DIR_NAME
    if not examples_dir.exists():
        return []
    return sorted(
        (path for path in examples_dir.rglob("*") if path.is_file() and path.suffix.lower() not in {".pyc", ".pyo", ".pyd"}),
        key=path_sort_key,
    )


def model_i18n_files(model_dir: Path) -> list[Path]:
    i18n_dir = model_dir / MODEL_I18N_DIR_NAME
    if not i18n_dir.exists():
        return []
    return [
        path
        for name in PRIMARY_MODEL_I18N_FILES
        if (path := i18n_dir / name).is_file() and path.suffix.lower() not in {".pyc", ".pyo", ".pyd"}
    ]


def model_knowledge_files(model_dir: Path) -> list[Path]:
    model_path = model_dir / "model.json"
    model: dict[str, Any] = {}
    if model_path.exists():
        data = read_json(model_path)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            model = data[0]
    meta = model.get("meta") if isinstance(model.get("meta"), dict) else {}
    configured = meta.get("exampleKnowledgeFiles") if isinstance(meta, dict) else None
    if isinstance(configured, list):
        files = []
        for rel_path in configured:
            clean = str(rel_path).strip().replace("\\", "/")
            if not clean or clean.startswith("../") or "/../" in clean:
                raise RuntimeError(f"Unsafe model knowledge path for {model_dir.name}: {clean!r}")
            files.append(model_dir / clean)
    else:
        files = []
        legacy = model_dir / legacy_example_result_file_name(model_dir.name)
        if legacy.exists():
            files.append(legacy)
        files.extend(model_example_files(model_dir))
        files.extend(model_i18n_files(model_dir))
    examples = model_example_files(model_dir)
    if not examples:
        raise RuntimeError(f"Model {model_dir.name} has no reusable example artifact under {model_dir / MODEL_EXAMPLES_DIR_NAME}")
    product_i18n = model_i18n_files(model_dir)
    if not product_i18n:
        raise RuntimeError(f"Model {model_dir.name} has no product i18n profiles under {model_dir / MODEL_I18N_DIR_NAME}")
    missing = [path for path in files if not path.exists()]
    if missing:
        raise RuntimeError(f"Model Knowledge files are incomplete for {model_dir.name}: missing {', '.join(str(path.relative_to(ROOT)) for path in missing)}")
    return files


def validate_workspace_payload(runtime: dict[str, Any]) -> list[ImportResult]:
    include_optional_network_tools = bool(runtime.get("include_optional_network_tools"))
    tool_count = len(load_tool_records(include_optional_network_tools))
    function_count = len(load_function_records())
    prompt_count = len(load_prompt_records())
    skills = skill_files()
    model_files = sorted(SINGLE_MODELS.glob("*/model.json"))
    prompt_commands: set[str] = set()
    for record in load_prompt_records():
        command = str(record.get("command") or "").strip().lstrip("/")
        if not command or not str(record.get("content") or "").strip():
            raise RuntimeError("Prompt import payload contains an empty command or content.")
        if command in prompt_commands:
            raise RuntimeError(f"Prompt import payload contains duplicate command: {command}")
        prompt_commands.add(command)
    for model_file in model_files:
        data = read_json(model_file)
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            raise RuntimeError(f"{model_file.relative_to(ROOT)} is not an importable OpenWebUI model JSON array")
        required_file_context_files(model_file.parent, data[0])
        model_knowledge_files(model_file.parent)
    return [
        ImportResult("tools", skipped=tool_count),
        ImportResult("tool_public_access", skipped=tool_count),
        ImportResult("tool_valves", skipped=len(configured_tool_valves(runtime))),
        ImportResult("functions", skipped=function_count),
        ImportResult("function_global_access", skipped=function_count),
        ImportResult("function_valves", skipped=len(configured_function_valves(runtime))),
        ImportResult("skills", skipped=len(skills)),
        ImportResult("skill_public_access", skipped=len(skills)),
        ImportResult("prompts", skipped=prompt_count),
        ImportResult("prompt_public_access", skipped=prompt_count),
        ImportResult("model_required_file_context", skipped=len(model_files) * 3),
        ImportResult("model_knowledge_collections", skipped=len(model_files)),
        ImportResult("knowledge_public_access", skipped=0 if runtime.get("skip_knowledge") else len(model_files)),
        ImportResult("models", skipped=len(model_files)),
        ImportResult("model_public_access", skipped=len(model_files)),
    ]


def import_tools(client: OpenWebUIClient, public: bool, include_optional_network_tools: bool) -> ImportResult:
    created = updated = 0
    indexed = read_json(TOOLS_INDEX)
    by_id = {entry["id"]: entry for entry in indexed.get("tools", [])}
    records = load_tool_records(include_optional_network_tools)
    log_progress(f"Tools importieren: {len(records)} Eintrag(e)")
    for index, record in enumerate(records, start=1):
        tool_id = record["id"]
        log_progress(f"Tool {index}/{len(records)}: {tool_id}")
        path = ROOT / record["path"]
        indexed_record = by_id.get(tool_id, {})
        meta = parse_python_metadata(path)
        payload = {
            "id": tool_id,
            "name": indexed_record.get("name") or record.get("name") or tool_id,
            "content": path.read_text(encoding="utf-8"),
            "meta": {"description": indexed_record.get("purpose") or meta.get("description") or record.get("purpose")},
            "access_grants": public_read_grants(public),
        }
        existing = get_existing_any(client, [f"/api/v1/tools/id/{tool_id}", f"/api/tools/id/{tool_id}"])
        if existing:
            client.request_any("POST", [f"/api/v1/tools/id/{tool_id}/update", f"/api/tools/id/{tool_id}/update"], payload)
            updated += 1
        else:
            try:
                client.request_any("POST", ["/api/v1/tools/create", "/api/tools/create"], payload)
                created += 1
            except RuntimeError as exc:
                if not is_already_registered_error(exc):
                    raise
                client.request_any("POST", [f"/api/v1/tools/id/{tool_id}/update", f"/api/tools/id/{tool_id}/update"], payload)
                updated += 1
        if public:
            update_tool_access(client, tool_id, public=True)
    return ImportResult("tools", created, updated)


def update_tool_valves(client: OpenWebUIClient, tool_id: str, valves: dict[str, Any]) -> None:
    client.request_any(
        "POST",
        [
            f"/api/v1/tools/id/{tool_id}/valves/update",
            f"/api/tools/id/{tool_id}/valves/update",
        ],
        valves,
    )


def import_tool_valves(client: OpenWebUIClient, runtime: dict[str, Any]) -> ImportResult:
    updated = skipped = 0
    valves_by_tool = configured_tool_valves(runtime)
    if valves_by_tool:
        log_progress(f"Tool-Valves aktualisieren: {len(valves_by_tool)} Eintrag(e)")
    for tool_id, valves in valves_by_tool.items():
        log_progress(f"Tool-Valves: {tool_id}")
        if not valves:
            skipped += 1
            continue
        try:
            update_tool_valves(client, tool_id, valves)
            updated += 1
        except RuntimeError as exc:
            if not is_not_found_error(exc):
                raise
            print(
                f"Warning: skipped tool valves for {tool_id}; OpenWebUI did not expose a matching tool valves endpoint or schema. {exc}",
                file=sys.stderr,
            )
            skipped += 1
    return ImportResult("tool_valves", updated=updated, skipped=skipped)


def update_function_valves(client: OpenWebUIClient, function_id: str, valves: dict[str, Any]) -> None:
    client.request_any(
        "POST",
        [
            f"/api/v1/functions/id/{function_id}/valves/update",
            f"/api/functions/id/{function_id}/valves/update",
        ],
        valves,
    )


def import_function_valves(client: OpenWebUIClient, runtime: dict[str, Any]) -> ImportResult:
    updated = skipped = 0
    valves_by_function = configured_function_valves(runtime)
    if valves_by_function:
        log_progress(f"Function-Valves aktualisieren: {len(valves_by_function)} Eintrag(e)")
    for function_id, valves in valves_by_function.items():
        log_progress(f"Function-Valves: {function_id}")
        if not valves:
            skipped += 1
            continue
        try:
            update_function_valves(client, function_id, valves)
            updated += 1
        except RuntimeError as exc:
            if not is_not_found_error(exc):
                raise
            print(
                f"Warning: skipped function/filter valves for {function_id}; OpenWebUI did not expose a matching valves endpoint or schema. {exc}",
                file=sys.stderr,
            )
            skipped += 1
    return ImportResult("function_valves", updated=updated, skipped=skipped)


def import_functions(client: OpenWebUIClient) -> ImportResult:
    created = updated = 0
    records = load_function_records()
    log_progress(f"Functions/Filter importieren: {len(records)} Eintrag(e)")
    for index, record in enumerate(records, start=1):
        log_progress(f"Function/Filter {index}/{len(records)}: {record['id']}")
        path = ROOT / record["path"]
        payload = {
            "id": record["id"],
            "name": record.get("name") or record["id"],
            "content": path.read_text(encoding="utf-8"),
            "meta": {"description": record.get("purpose")},
        }
        existing = get_existing(client, f"/api/v1/functions/id/{record['id']}")
        if existing:
            existing = client.request("POST", f"/api/v1/functions/id/{record['id']}/update", payload)
            updated += 1
        else:
            existing = client.request("POST", "/api/v1/functions/create", payload)
            created += 1
        ensure_function_active_and_global(client, record["id"], existing if isinstance(existing, dict) else None)
    return ImportResult("functions", created, updated)


def import_skills(client: OpenWebUIClient, public: bool) -> ImportResult:
    created = updated = skipped = 0
    skipped = 1 if (SKILLS_DIR / "README.md").exists() else 0
    paths = skill_files()
    log_progress(f"Skills importieren: {len(paths)} Eintrag(e)")
    for index, path in enumerate(paths, start=1):
        skill_id, name, description = parse_skill(path)
        log_progress(f"Skill {index}/{len(paths)}: {skill_id}")
        payload = {
            "id": skill_id,
            "name": name,
            "description": description,
            "content": path.read_text(encoding="utf-8"),
            "meta": {"tags": ["openwebui-workspace"]},
            "is_active": True,
            "access_grants": public_read_grants(public),
        }
        existing = get_existing(client, f"/api/v1/skills/id/{skill_id}")
        if existing:
            existing = client.request("POST", f"/api/v1/skills/id/{skill_id}/update", payload)
            if isinstance(existing, dict) and existing.get("is_active") is False:
                client.request("POST", f"/api/v1/skills/id/{skill_id}/toggle")
            updated += 1
        else:
            client.request("POST", "/api/v1/skills/create", payload)
            created += 1
        if public:
            update_skill_access(client, skill_id, public=True)
    return ImportResult("skills", created, updated, skipped)


def prompt_form(record: dict[str, Any], public: bool) -> dict[str, Any]:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    data = record.get("data") if isinstance(record.get("data"), dict) else {}
    tags = record.get("tags") if isinstance(record.get("tags"), list) else ["workbench"]
    return {
        "command": str(record.get("command") or record.get("id") or "").strip().lstrip("/"),
        "name": str(record.get("name") or record.get("command") or record.get("id") or "Workbench Prompt"),
        "content": str(record.get("content") or ""),
        "data": data,
        "meta": meta,
        "tags": [str(tag) for tag in tags if str(tag).strip()],
        "access_grants": public_read_grants(public),
    }


def get_prompt_by_command(client: OpenWebUIClient, command: str) -> dict[str, Any] | None:
    return get_existing_any(client, [f"/api/v1/prompts/command/{command}", f"/api/prompts/command/{command}"])


def import_prompts(client: OpenWebUIClient, public: bool) -> ImportResult:
    created = updated = 0
    records = load_prompt_records()
    log_progress(f"Promptvorlagen importieren: {len(records)} Eintrag(e)")
    for index, record in enumerate(records, start=1):
        command = normalize_prompt_command(str(record.get("command") or record.get("id") or ""), str(record.get("id") or "workbench-prompt"))
        log_progress(f"Promptvorlage {index}/{len(records)}: /{command}")
        record = {**record, "command": command}
        payload = prompt_form(record, public)
        existing = get_prompt_by_command(client, command)
        prompt_id = ""
        if existing:
            prompt_id = str(existing.get("id") or record.get("id") or command)
            existing = client.request_any(
                "POST",
                [f"/api/v1/prompts/id/{prompt_id}/update", f"/api/prompts/id/{prompt_id}/update"],
                payload,
            )
            updated += 1
        else:
            existing = client.request_any("POST", ["/api/v1/prompts/create", "/api/prompts/create"], payload)
            created += 1
            if isinstance(existing, dict):
                prompt_id = str(existing.get("id") or "")
        if public and prompt_id:
            try:
                update_prompt_access(client, prompt_id, public=True)
            except RuntimeError as exc:
                if not is_not_found_error(exc):
                    raise
                print(
                    f"Warning: skipped prompt public access update for {command}; OpenWebUI did not expose a matching prompt access endpoint. {exc}",
                    file=sys.stderr,
                )
    return ImportResult("prompts", created, updated)


def find_knowledge_by_name(client: OpenWebUIClient, name: str) -> dict[str, Any] | None:
    result = client.request("GET", "/api/v1/knowledge/search", query={"query": name})
    items = result.get("items", []) if isinstance(result, dict) else []
    for item in items:
        if item.get("name") == name:
            return item
    return None


def knowledge_fingerprint(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.as_posix()):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(path.stat().st_size).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def knowledge_description(model_id: str, files: list[Path], fingerprint: str) -> str:
    filenames = ", ".join(path.name for path in files)
    return (
        f"{filenames} für das Modell {model_id} aus dem OpenWebUI Workspace. "
        f"Import-Fingerprint: {fingerprint}"
    )


def knowledge_has_fingerprint(knowledge: dict[str, Any], fingerprint: str) -> bool:
    description = str(knowledge.get("description") or "")
    return fingerprint in description


def load_required_file_context_cache() -> dict[str, dict[str, Any]]:
    if not REQUIRED_FILE_CONTEXT_CACHE.exists():
        return {}
    try:
        data = read_json(REQUIRED_FILE_CONTEXT_CACHE)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_required_file_context_cache(cache: dict[str, dict[str, Any]]) -> None:
    REQUIRED_FILE_CONTEXT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    REQUIRED_FILE_CONTEXT_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def required_file_context_cache_key(model_id: str, rel_path: str, sha256: str) -> str:
    return f"{model_id}|{rel_path}|{sha256}"


def knowledge_file_count(client: OpenWebUIClient, knowledge_id: str) -> int:
    for path in (f"/api/v1/knowledge/{knowledge_id}/files", f"/api/knowledge/{knowledge_id}/files"):
        try:
            result = client.request("GET", path)
            if isinstance(result, list):
                return len(result)
            if isinstance(result, dict):
                total = result.get("total")
                if isinstance(total, int):
                    return total
                files = result.get("files")
                if files is None:
                    files = result.get("items")
                if isinstance(files, list):
                    return len(files)
        except RuntimeError as exc:
            if is_not_found_error(exc):
                continue
            raise
    return 0


def upsert_knowledge_with_files(client: OpenWebUIClient, model_id: str, model_name: str, files: list[Path], public: bool) -> KnowledgeUpsertResult:
    name = f"Modellwissen - {model_name}"
    fingerprint = knowledge_fingerprint(files)
    description = knowledge_description(model_id, files, fingerprint)
    payload = {"name": name, "description": description, "access_grants": public_read_grants(public)}
    log_progress(f"Knowledge prüfen: {name} ({len(files)} Datei(en))")
    knowledge = find_knowledge_by_name(client, name)
    if knowledge:
        knowledge_id = knowledge["id"]
        log_progress(f"Knowledge aktualisieren: {name}")
        client.request("POST", f"/api/v1/knowledge/{knowledge_id}/update", payload)
        if public:
            update_knowledge_access(client, knowledge_id, public=True)
        if knowledge_has_fingerprint(knowledge, fingerprint) and knowledge_file_count(client, knowledge_id) == len(files):
            log_progress(f"Knowledge unverändert: {name}")
            return KnowledgeUpsertResult({"id": knowledge_id, "name": name}, changed=False)
        log_progress(f"Knowledge zurücksetzen: {name}")
        client.request("POST", f"/api/v1/knowledge/{knowledge_id}/reset")
    else:
        log_progress(f"Knowledge erstellen: {name}")
        created = client.request("POST", "/api/v1/knowledge/create", payload)
        knowledge_id = created["id"]
        if public:
            update_knowledge_access(client, knowledge_id, public=True)
    file_refs = []
    for index, file_path in enumerate(files, start=1):
        log_progress(f"Knowledge-Datei {index}/{len(files)} hochladen: {model_id}/{file_path.name}")
        uploaded = client.upload_file(file_path, process=True)
        file_refs.append({"file_id": uploaded["id"]})
    add_response: Any | None = None
    try:
        log_progress(f"Knowledge-Dateien verknüpfen: {name} ({len(file_refs)} Datei(en))")
        add_response = client.request("POST", f"/api/v1/knowledge/{knowledge_id}/files/batch/add", file_refs)
    except RuntimeError as exc:
        if not is_not_found_error(exc):
            raise
        for file_ref in file_refs:
            log_progress(f"Knowledge-Datei einzeln verknüpfen: {name}/{file_ref['file_id']}")
            client.request("POST", f"/api/v1/knowledge/{knowledge_id}/file/add", file_ref)
    result = client.request("GET", f"/api/v1/knowledge/{knowledge_id}")
    files_response = result.get("files") if isinstance(result, dict) else None
    if files_response:
        linked_file_ids = {
            str(item.get("id") or item.get("file_id"))
            for item in files_response
            if isinstance(item, dict)
        }
        missing_file_ids = [item["file_id"] for item in file_refs if item["file_id"] not in linked_file_ids]
        if missing_file_ids:
            raise RuntimeError(f"Knowledge import did not link all files for {name}: {missing_file_ids}")
    linked_count = knowledge_file_count(client, knowledge_id)
    if linked_count < len(files):
        warnings = add_response.get("warnings") if isinstance(add_response, dict) else None
        warning_text = f" Warnings: {warnings}" if warnings else ""
        raise RuntimeError(
            f"Knowledge import linked only {linked_count}/{len(files)} files for {name}.{warning_text}"
        )
    log_progress(f"Knowledge fertig: {name} ({linked_count}/{len(files)} Datei(en) verknüpft)")
    return KnowledgeUpsertResult({"id": knowledge_id, "name": name}, changed=True)


def upload_required_file_context(
    client: OpenWebUIClient,
    model_dir: Path,
    model: dict[str, Any],
    runtime: dict[str, Any],
    cache: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, int]:
    model_id = str(model.get("id"))
    settings = runtime.get("model_file_context", {}) if isinstance(runtime.get("model_file_context"), dict) else {}
    if not as_bool(settings.get("enabled"), True):
        required_file_context_files(model_dir, model)
        return [], 0, 0
    required_entries = required_file_context_entries(model)
    uploaded_files: list[dict[str, Any]] = []
    uploaded = reused = 0
    should_upload = as_bool(settings.get("upload_required_files"), True)
    should_poll = as_bool(settings.get("poll_processing_status"), True)
    timeout_seconds = as_int(settings.get("processing_timeout_seconds", 180), 180)
    for entry in required_entries:
        rel_path = str(entry.get("path") or "").strip().replace("\\", "/")
        sha256 = str(entry.get("sha256") or "")
        path = model_dir / rel_path
        if not should_upload:
            log_progress(f"Pflichtdatei nicht hochgeladen: {model_id}/{rel_path}")
            uploaded_files.append(
                {
                    "role": entry.get("role"),
                    "path": rel_path,
                    "filename": entry.get("filename") or path.name,
                    "sha256": sha256,
                    "status": "not_uploaded",
                }
            )
            continue
        key = required_file_context_cache_key(model_id, rel_path, sha256)
        cached = cache.get(key) if isinstance(cache.get(key), dict) else None
        if cached and cached.get("fileId"):
            file_id = str(cached["fileId"])
            status = str(cached.get("status") or "cached")
            log_progress(f"Pflichtdatei aus Cache: {model_id}/{rel_path}")
            if should_poll:
                status = client.wait_for_file_processing(file_id, timeout_seconds=timeout_seconds)
            reused += 1
        else:
            log_progress(f"Pflichtdatei hochladen: {model_id}/{rel_path}")
            response = client.upload_file(path, process=True)
            file_id = str(response.get("id") or response.get("file_id") or "")
            if not file_id:
                raise RuntimeError(f"OpenWebUI did not return a file id for required file {path.relative_to(ROOT)}")
            status = client.wait_for_file_processing(file_id, timeout_seconds=timeout_seconds) if should_poll else "uploaded"
            uploaded += 1
        log_progress(f"Pflichtdatei bereit: {model_id}/{rel_path} ({status})")
        record = {
            "role": entry.get("role"),
            "path": rel_path,
            "filename": entry.get("filename") or path.name,
            "fileId": file_id,
            "sha256": sha256,
            "status": status,
        }
        uploaded_files.append(record)
        cache[key] = {**record, "modelId": model_id, "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    return uploaded_files, uploaded, reused


def load_models_with_knowledge(client: OpenWebUIClient, public: bool, upload_knowledge: bool, runtime: dict[str, Any]) -> ModelLoadResult:
    models: list[dict[str, Any]] = []
    knowledge_updated = 0
    knowledge_skipped = 0
    required_files_uploaded = 0
    required_files_reused = 0
    file_context_cache = load_required_file_context_cache()
    model_files = sorted(SINGLE_MODELS.glob("*/model.json"))
    log_progress(f"Modelle vorbereiten: {len(model_files)} Modell(e)")
    for index, model_file in enumerate(model_files, start=1):
        data = read_json(model_file)
        if not isinstance(data, list) or not data:
            continue
        model = data[0]
        model_id = str(model.get("id"))
        log_progress(f"Modell {index}/{len(model_files)} vorbereiten: {model_id}")
        meta = model.setdefault("meta", {})
        required_file_context_files(model_file.parent, model)
        uploaded_files, uploaded_count, reused_count = upload_required_file_context(
            client,
            model_file.parent,
            model,
            runtime,
            file_context_cache,
        )
        required_files_uploaded += uploaded_count
        required_files_reused += reused_count
        log_progress(
            f"Pflichtdateien für {model_id}: {uploaded_count} hochgeladen, {reused_count} wiederverwendet"
        )
        settings = runtime.get("model_file_context", {}) if isinstance(runtime.get("model_file_context"), dict) else {}
        if uploaded_files and as_bool(settings.get("attach_uploaded_files_to_model_meta"), True):
            workbench_file_context = meta.setdefault("workbenchFileContext", {})
            if isinstance(workbench_file_context, dict):
                workbench_file_context["uploadedFiles"] = uploaded_files
        if upload_knowledge:
            prompt_files = model_knowledge_files(model_file.parent)
            log_progress(f"Knowledge für {model_id}: {len(prompt_files)} Datei(en)")
            knowledge_result = upsert_knowledge_with_files(
                client,
                model_id,
                str(model.get("name") or model_id),
                prompt_files,
                public,
            )
            knowledge = knowledge_result.knowledge
            if knowledge_result.changed:
                knowledge_updated += 1
            else:
                knowledge_skipped += 1
            existing = [item for item in meta.get("knowledge", []) if isinstance(item, dict)]
            meta["knowledge"] = [item for item in existing if item.get("id") != knowledge["id"]]
            meta["knowledge"].append(knowledge)
        else:
            model_knowledge_files(model_file.parent)
            log_progress(f"Knowledge für {model_id}: übersprungen")
        if public:
            model["access_grants"] = public_read_grants(public)
        models.append(model)
    write_required_file_context_cache(file_context_cache)
    return ModelLoadResult(
        models,
        knowledge_updated=knowledge_updated,
        knowledge_skipped=knowledge_skipped,
        required_files_uploaded=required_files_uploaded,
        required_files_reused=required_files_reused,
    )


def import_models(client: OpenWebUIClient, public: bool, upload_knowledge: bool, runtime: dict[str, Any]) -> tuple[ImportResult, ModelLoadResult]:
    loaded = load_models_with_knowledge(client, public=public, upload_knowledge=upload_knowledge, runtime=runtime)
    models = loaded.models
    if not models:
        return ImportResult("models", skipped=1), loaded
    log_progress(f"Modelle in OpenWebUI importieren: {len(models)} Modell(e)")
    for index, model in enumerate(models, start=1):
        model_id = str(model.get("id") or "<unknown>")
        log_progress(f"OpenWebUI-Modellimport {index}/{len(models)}: {model_id}")
        response = client.request("POST", "/api/v1/models/import", {"models": [model]})
        if response is not True:
            raise RuntimeError(
                f"Unexpected OpenWebUI model import response for {model_id}: {type(response).__name__}"
            )
    log_progress("Importierte Modelle verifizieren")
    verify_imported_models(client, models, expect_knowledge=upload_knowledge)
    if public:
        log_progress(f"Modellzugriffe aktualisieren: {len(models)} Modell(e)")
        for index, model in enumerate(models, start=1):
            model_id = str(model.get("id"))
            log_progress(f"Modellzugriff {index}/{len(models)}: {model_id}")
            update_model_access(client, model_id, str(model.get("name") or model_id), public=True)
    return ImportResult("models", updated=len(models)), loaded


def verify_imported_models(client: OpenWebUIClient, models: list[dict[str, Any]], expect_knowledge: bool) -> None:
    missing: list[str] = []
    incomplete_knowledge: list[str] = []
    incomplete_skills: list[str] = []
    incomplete_required_context: list[str] = []
    required_context_in_knowledge: list[str] = []
    for model in models:
        model_id = str(model.get("id"))
        try:
            imported = client.request("GET", "/api/v1/models/model", query={"id": model_id})
        except RuntimeError:
            missing.append(model_id)
            continue
        if not isinstance(imported, dict) or imported.get("id") != model_id:
            missing.append(model_id)
            continue
        expected_meta = model.get("meta") if isinstance(model.get("meta"), dict) else {}
        expected_context = expected_meta.get("workbenchFileContext") if isinstance(expected_meta.get("workbenchFileContext"), dict) else {}
        expected_required = expected_context.get("requiredFiles") if isinstance(expected_context.get("requiredFiles"), list) else []
        expected_uploaded = expected_context.get("uploadedFiles") if isinstance(expected_context.get("uploadedFiles"), list) else []
        expected_file_ids = {
            str(item.get("fileId") or item.get("file_id"))
            for item in expected_uploaded
            if isinstance(item, dict) and (item.get("fileId") or item.get("file_id"))
        }
        expected_required_names = {
            str(item.get("filename") or item.get("path") or "").rsplit("/", 1)[-1]
            for item in expected_required
            if isinstance(item, dict)
        }
        expected_required_names = {name for name in expected_required_names if name}
        if expected_required or expected_file_ids:
            imported_meta = imported.get("meta") if isinstance(imported.get("meta"), dict) else {}
            imported_context = imported_meta.get("workbenchFileContext") if isinstance(imported_meta.get("workbenchFileContext"), dict) else {}
            imported_required = imported_context.get("requiredFiles") if isinstance(imported_context.get("requiredFiles"), list) else []
            imported_uploaded = imported_context.get("uploadedFiles") if isinstance(imported_context.get("uploadedFiles"), list) else []
            imported_file_ids = {
                str(item.get("fileId") or item.get("file_id"))
                for item in imported_uploaded
                if isinstance(item, dict) and (item.get("fileId") or item.get("file_id"))
            }
            if len(imported_required) != 3 or (expected_file_ids and not expected_file_ids.issubset(imported_file_ids)):
                incomplete_required_context.append(model_id)
        if expect_knowledge:
            expected_knowledge = [
                item
                for item in (model.get("meta") or {}).get("knowledge", [])
                if isinstance(item, dict) and item.get("id")
            ]
            imported_knowledge = [
                item
                for item in (imported.get("meta") or {}).get("knowledge", [])
                if isinstance(item, dict) and item.get("id")
            ]
            imported_ids = {str(item.get("id")) for item in imported_knowledge}
            if expected_knowledge and any(str(item.get("id")) not in imported_ids for item in expected_knowledge):
                incomplete_knowledge.append(model_id)
            if expected_required_names:
                for item in imported_knowledge:
                    knowledge_id = str(item.get("id") or "")
                    if not knowledge_id:
                        continue
                    knowledge_detail = client.request("GET", f"/api/v1/knowledge/{knowledge_id}")
                    if not isinstance(knowledge_detail, dict):
                        continue
                    knowledge_files = knowledge_detail.get("files")
                    if not isinstance(knowledge_files, list):
                        continue
                    file_names = {
                        str(file_item.get("filename") or file_item.get("name") or file_item.get("path") or "").rsplit("/", 1)[-1]
                        for file_item in knowledge_files
                        if isinstance(file_item, dict)
                    }
                    if expected_required_names.intersection(file_names):
                        required_context_in_knowledge.append(model_id)
                        break
        expected_skill_ids = [
            str(item)
            for item in (model.get("meta") or {}).get("skillIds", [])
            if item
        ]
        imported_skill_ids = [
            str(item)
            for item in (imported.get("meta") or {}).get("skillIds", [])
            if item
        ]
        if expected_skill_ids and any(item not in imported_skill_ids for item in expected_skill_ids):
            incomplete_skills.append(model_id)
    if missing:
        raise RuntimeError(f"OpenWebUI model import did not persist models: {', '.join(sorted(missing))}")
    if incomplete_knowledge:
        raise RuntimeError(
            "OpenWebUI model import did not persist Knowledge links for models: "
            + ", ".join(sorted(incomplete_knowledge))
        )
    if incomplete_required_context:
        raise RuntimeError(
            "OpenWebUI model import did not persist required file context links for models: "
            + ", ".join(sorted(incomplete_required_context))
        )
    if required_context_in_knowledge:
        raise RuntimeError(
            "OpenWebUI model import linked required file context files through Knowledge/RAG for models: "
            + ", ".join(sorted(required_context_in_knowledge))
        )
    if incomplete_skills:
        raise RuntimeError(
            "OpenWebUI model import did not persist Skill links for models: "
            + ", ".join(sorted(incomplete_skills))
        )


def print_results(results: list[ImportResult], title: str = "# OpenWebUI workspace import") -> None:
    print(title)
    for result in results:
        print(
            f"- {result.kind}: created={result.created}, updated={result.updated}, skipped={result.skipped}"
        )


def run_workspace_import(client: OpenWebUIClient, runtime: dict[str, Any]) -> int:
    started = time.time()
    tool_records = load_tool_records(bool(runtime["include_optional_network_tools"]))
    function_records = load_function_records()
    prompt_records = load_prompt_records()
    skills = skill_files()
    model_count = len(sorted(SINGLE_MODELS.glob("*/model.json")))
    log_progress(
        "Workspace-Import startet: "
        f"{len(tool_records)} Tools, {len(function_records)} Functions/Filter, "
        f"{len(skills)} Skills, {len(prompt_records)} Promptvorlagen, {model_count} Modelle"
    )
    log_progress("Phase 1/7: Tools")
    tool_import = import_tools(
        client,
        public=bool(runtime["public_read"]),
        include_optional_network_tools=bool(runtime["include_optional_network_tools"]),
    )
    log_progress("Phase 2/7: Tool-Valves")
    tool_valves = import_tool_valves(client, runtime)
    log_progress("Phase 3/7: Functions/Filter")
    function_import = import_functions(client)
    log_progress("Phase 4/7: Function-Valves")
    function_valves = import_function_valves(client, runtime)
    log_progress("Phase 5/7: Skills")
    skill_import = import_skills(client, public=bool(runtime["public_read"]))
    log_progress("Phase 6/7: Promptvorlagen")
    prompt_import = import_prompts(client, public=bool(runtime["public_read"]))
    log_progress("Phase 7/7: Modelle, Pflichtdateien und Knowledge")
    model_import, model_load = import_models(
        client,
        public=bool(runtime["public_read"]),
        upload_knowledge=not bool(runtime["skip_knowledge"]),
        runtime=runtime,
    )
    results = [
        tool_import,
        ImportResult("tool_public_access", updated=len(tool_records)),
        tool_valves,
        function_import,
        ImportResult("function_global_access", updated=len(function_records)),
        function_valves,
        skill_import,
        ImportResult("skill_public_access", updated=len(skills)),
        prompt_import,
        ImportResult("prompt_public_access", updated=len(prompt_records)),
        ImportResult(
            "model_required_file_context",
            created=model_load.required_files_uploaded,
            skipped=model_load.required_files_reused,
        ),
        ImportResult(
            "model_knowledge_collections",
            updated=0 if runtime["skip_knowledge"] else model_load.knowledge_updated,
            skipped=model_count if runtime["skip_knowledge"] else model_load.knowledge_skipped,
        ),
        ImportResult(
            "knowledge_public_access",
            updated=0 if runtime["skip_knowledge"] else model_count,
            skipped=model_count if runtime["skip_knowledge"] else 0,
        ),
        model_import,
        ImportResult("model_public_access", updated=model_count),
    ]
    print_results(results)
    print(f"- duration_seconds: {time.time() - started:.1f}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import this repository's OpenWebUI tools, functions, skills, prompt templates, knowledge and models."
    )
    parser.add_argument("--config", default=None, help="Central YAML config file. Defaults to scripts/openwebui_workspace_config.yaml when present.")
    parser.add_argument("--base-url", default=None, help="One-off override for openwebui.base_url from the central config.")
    parser.add_argument("--token", default=None, help="One-off override for openwebui.admin_token from the central config.")
    parser.add_argument("--auth-header", default=None, help="One-off override for the OpenWebUI API key header. Defaults to Authorization; use x-api-key or CUSTOM_API_KEY_HEADER when a proxy consumes Authorization.")
    parser.add_argument("--auth-scheme", default=None, help="One-off override for the auth scheme. Defaults to Bearer for Authorization and empty for custom API-key headers.")
    parser.add_argument("--tls-verify", choices=("true", "false"), default=None, help="Verify OpenWebUI HTTPS certificates. Set false only for trusted local self-signed endpoints.")
    parser.add_argument("--ca-file", default=None, help="CA bundle file for a private OpenWebUI HTTPS endpoint.")
    parser.add_argument("--ca-path", default=None, help="Directory with trusted CA certificates for a private OpenWebUI HTTPS endpoint.")
    parser.add_argument("--public-read", action="store_true", help="Compatibility flag; public read is enforced for workspace imports.")
    parser.add_argument("--skip-knowledge", action="store_true", help="Do not upload example/legacy/i18n files as model Knowledge. Required file context files are still uploaded when model_file_context.upload_required_files is enabled.")
    parser.add_argument(
        "--include-optional-network-tools",
        action="store_true",
        help="Also import optional network-capable tools. Offline defaults exclude them unless import.include_optional_network_tools is true in the YAML config.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate payload files and print counts without calling OpenWebUI.")
    parser.add_argument("--auth-check", action="store_true", help="Only probe OpenWebUI reachability and API-key authentication, then exit.")
    parser.add_argument("--jupyter-url", default=None, help="One-off override for the Jupyter tool valve. Prefer tool_valves.air_gapped_jupyter_python in the config.")
    parser.add_argument("--jupyter-token", default=None, help="One-off override for the Jupyter token tool valve.")
    parser.add_argument("--jupyter-timeout-seconds", type=int, default=None, help="One-off override for the Jupyter execution timeout tool valve.")
    parser.add_argument("--jupyter-allowed-workdir", default=None, help="One-off override for the allowed workdir tool valve.")
    parser.add_argument("--artifact-root", default=None, help="One-off override for the artifact root tool valve.")
    parser.add_argument("--offline-addons-root", default=None, help="One-off override for the offline add-ons root tool valve.")
    parser.add_argument("--offline-addons-python-path", default=None, help="One-off override for the offline add-ons Python path tool valve.")
    parser.add_argument("--playwright-browsers-path", default=None, help="One-off override for the Playwright browser cache tool valve.")
    parser.add_argument("--nltk-data-path", default=None, help="One-off override for the NLTK data path tool valve.")
    parser.add_argument("--prefer-playwright-pdf", action="store_true", default=None, help="One-off override to prefer local Playwright/Chromium for artifact PDF conversion.")
    parser.add_argument("--timeout", type=int, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = resolve_runtime_config(args)
    if args.dry_run:
        print_results(
            validate_workspace_payload(runtime),
            title="# OpenWebUI workspace import dry-run",
        )
        return 0
    token = str(runtime["token"]).strip()
    if token in PLACEHOLDER_TOKENS:
        print(
            "Configure openwebui.admin_token in scripts/openwebui_workspace_config.yaml or pass --token.",
            file=sys.stderr,
        )
        return 2
    client = OpenWebUIClient(
        runtime["base_url"],
        token,
        timeout=int(runtime["timeout"]),
        auth_header=str(runtime["auth_header"]),
        auth_scheme=str(runtime["auth_scheme"]),
        tls_verify=bool(runtime["tls_verify"]),
        ca_file=str(runtime["ca_file"]),
        ca_path=str(runtime["ca_path"]),
    )
    check_openwebui_auth(client)
    if args.auth_check:
        print(f"OpenWebUI auth check OK: {client.base_url} using header {client.auth_header}")
        return 0
    with import_lock():
        return run_workspace_import(client, runtime)


if __name__ == "__main__":
    raise SystemExit(main())
