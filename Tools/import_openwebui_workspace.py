#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# Paste values here only if you do not want to use scripts/openwebui_workspace_config.yaml
# or environment variables. Do not commit real tokens.
OPENWEBUI_ADMIN_TOKEN = "PASTE_OPENWEBUI_ADMIN_API_TOKEN_HERE"
OPENWEBUI_BASE_URL = "http://localhost:3000"
JUPYTER_URL = ""
JUPYTER_TOKEN = ""
JUPYTER_TIMEOUT_SECONDS = 30
JUPYTER_ALLOWED_WORKDIR = ""
ARTIFACT_ROOT = ""

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "Tools"
TOOLS_INDEX = TOOLS_DIR / "index.json"
OPENWEBUI_EXT = TOOLS_DIR / "openwebui_ext"
TOOLS_REGISTRY = TOOLS_DIR / "dist" / "openwebui-tool-registry.json"
FUNCTION_REGISTRY = TOOLS_DIR / "dist" / "openwebui-function-registry.json"
SKILLS_DIR = OPENWEBUI_EXT / "skills"
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
REQUIRED_MODEL_KNOWLEDGE_FILES = ("mainprompt.md", "fachwissen.md")
DEFAULT_CONFIG_NAME = "openwebui_workspace_config.yaml"

PLACEHOLDER_TOKENS = {"", "PASTE_OPENWEBUI_ADMIN_API_TOKEN_HERE", "YOUR_OPEN_WEBUI_API_KEY"}


@dataclass(frozen=True)
class ImportResult:
    kind: str
    created: int = 0
    updated: int = 0
    skipped: int = 0


class OpenWebUIClient:
    def __init__(self, base_url: str, token: str, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def api_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        return url

    def request(
        self,
        method: str,
        path: str,
        payload: Any | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected: tuple[int, ...] = (200,),
    ) -> Any:
        body = None
        request_headers = dict(self.headers)
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        if headers:
            request_headers.update(headers)
        request = Request(self.api_url(path, query), data=body, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
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
            raise RuntimeError(f"{method} {path} returned HTTP {exc.code}: {raw[:1000]}") from exc
        except URLError as exc:
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
                if "HTTP 404" in str(exc):
                    last_not_found = exc
                    continue
                raise
        if last_not_found:
            raise last_not_found
        raise RuntimeError(f"No API path candidates supplied for {method}")

    def upload_file(self, path: Path) -> dict[str, Any]:
        boundary = f"----openwebui-workspace-{uuid.uuid4().hex}"
        content_type = mimetypes.guess_type(path.name)[0] or "text/plain"
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
            self.api_url("/api/v1/files/", {"process": "true", "process_in_background": "false"}),
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Upload failed for {path}: HTTP {exc.code}: {raw[:1000]}") from exc


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def resolve_runtime_config(args: argparse.Namespace) -> dict[str, Any]:
    config, config_path = load_config(args.config)
    base_url = (
        args.base_url
        or os.getenv("OPENWEBUI_BASE_URL")
        or first_config_value(config, ["openwebui.base_url", "openwebui.url"])
        or OPENWEBUI_BASE_URL
    )
    token = (
        args.token
        or os.getenv("OPENWEBUI_ADMIN_TOKEN")
        or first_config_value(config, ["openwebui.admin_token", "openwebui.api_key", "openwebui.token"])
        or OPENWEBUI_ADMIN_TOKEN
    )
    timeout = as_int(
        args.timeout
        if args.timeout is not None
        else first_config_value(config, ["openwebui.timeout_seconds", "import.timeout_seconds"], 120),
        120,
    )
    include_optional = args.include_optional_network_tools or as_bool(
        first_config_value(config, ["import.include_optional_network_tools"], True),
        True,
    )
    public_read = args.public_read or as_bool(first_config_value(config, ["import.public_read"], False))
    skip_knowledge = args.skip_knowledge or as_bool(first_config_value(config, ["import.skip_knowledge"], False))
    jupyter = {
        "OPENWEBUI_JUPYTER_URL": (
            args.jupyter_url
            or os.getenv("OPENWEBUI_JUPYTER_URL")
            or first_config_value(config, ["jupyter.url", "jupyter.base_url"], JUPYTER_URL)
        ),
        "OPENWEBUI_JUPYTER_TOKEN": (
            args.jupyter_token
            or os.getenv("OPENWEBUI_JUPYTER_TOKEN")
            or first_config_value(config, ["jupyter.token", "jupyter.api_token"], JUPYTER_TOKEN)
        ),
        "OPENWEBUI_JUPYTER_TIMEOUT_SECONDS": (
            args.jupyter_timeout_seconds
            or os.getenv("OPENWEBUI_JUPYTER_TIMEOUT_SECONDS")
            or first_config_value(config, ["jupyter.timeout_seconds"], JUPYTER_TIMEOUT_SECONDS)
        ),
        "OPENWEBUI_JUPYTER_ALLOWED_WORKDIR": (
            args.jupyter_allowed_workdir
            or os.getenv("OPENWEBUI_JUPYTER_ALLOWED_WORKDIR")
            or first_config_value(config, ["jupyter.allowed_workdir", "jupyter.workdir"], JUPYTER_ALLOWED_WORKDIR)
        ),
    }
    artifact_root = (
        args.artifact_root
        or os.getenv("OPENWEBUI_ARTIFACT_ROOT")
        or first_config_value(
            config,
            ["artifacts.root", "artifact_root", "tools.offline_artifact_workbench.artifact_root"],
            ARTIFACT_ROOT,
        )
    )
    return {
        "config_path": config_path,
        "base_url": str(base_url).rstrip("/"),
        "token": str(token).strip(),
        "timeout": timeout,
        "include_optional_network_tools": include_optional,
        "public_read": public_read,
        "skip_knowledge": skip_knowledge,
        "jupyter": jupyter,
        "artifact_root": str(artifact_root or ""),
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
    if artifact_root:
        valves["offline_artifact_workbench"] = {"artifact_root": artifact_root}
    return valves


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


def get_existing(client: OpenWebUIClient, path: str) -> dict[str, Any] | None:
    try:
        value = client.request("GET", path)
        return value if isinstance(value, dict) else None
    except RuntimeError as exc:
        if "HTTP 404" in str(exc) or "HTTP 401" in str(exc):
            return None
        raise


def public_read_grants(enabled: bool) -> list[dict[str, str]]:
    if not enabled:
        return []
    return [{"principal_type": "user", "principal_id": "*", "permission": "read"}]


def skill_files() -> list[Path]:
    return [path for path in sorted(SKILLS_DIR.glob("*.md")) if path.name.upper() != "README.MD"]


def required_model_knowledge_files(model_dir: Path) -> list[Path]:
    files = [model_dir / name for name in REQUIRED_MODEL_KNOWLEDGE_FILES]
    missing = [path for path in files if not path.exists()]
    empty = [path for path in files if path.exists() and path.stat().st_size == 0]
    if missing or empty:
        details = []
        if missing:
            details.append("missing: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))
        if empty:
            details.append("empty: " + ", ".join(str(path.relative_to(ROOT)) for path in empty))
        raise RuntimeError(f"Model knowledge files are incomplete for {model_dir.name}: {'; '.join(details)}")
    return files


def validate_workspace_payload(runtime: dict[str, Any]) -> list[ImportResult]:
    include_optional_network_tools = bool(runtime.get("include_optional_network_tools"))
    tool_count = len(load_tool_records(include_optional_network_tools))
    function_count = len(load_function_records())
    skills = skill_files()
    model_files = sorted(SINGLE_MODELS.glob("*/model.json"))
    for model_file in model_files:
        data = read_json(model_file)
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            raise RuntimeError(f"{model_file.relative_to(ROOT)} is not an importable OpenWebUI model JSON array")
        required_model_knowledge_files(model_file.parent)
    return [
        ImportResult("tools", skipped=tool_count),
        ImportResult("functions", skipped=function_count),
        ImportResult("skills", skipped=len(skills)),
        ImportResult("tool_valves", skipped=len(configured_tool_valves(runtime))),
        ImportResult("model_knowledge_collections", skipped=len(model_files)),
        ImportResult("models", skipped=len(model_files)),
    ]


def import_tools(client: OpenWebUIClient, public: bool, include_optional_network_tools: bool) -> ImportResult:
    created = updated = 0
    indexed = read_json(TOOLS_INDEX)
    by_id = {entry["id"]: entry for entry in indexed.get("tools", [])}
    for record in load_tool_records(include_optional_network_tools):
        path = ROOT / record["path"]
        indexed_record = by_id.get(record["id"], {})
        meta = parse_python_metadata(path)
        payload = {
            "id": record["id"],
            "name": indexed_record.get("name") or record.get("name") or record["id"],
            "content": path.read_text(encoding="utf-8"),
            "meta": {"description": indexed_record.get("purpose") or meta.get("description") or record.get("purpose")},
            "access_grants": public_read_grants(public),
        }
        existing = get_existing(client, f"/api/v1/tools/id/{record['id']}")
        if existing:
            payload["access_grants"] = existing.get("access_grants") or payload["access_grants"]
            client.request("POST", f"/api/v1/tools/id/{record['id']}/update", payload)
            updated += 1
        else:
            client.request("POST", "/api/v1/tools/create", payload)
            created += 1
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
    for tool_id, valves in configured_tool_valves(runtime).items():
        if not valves:
            skipped += 1
            continue
        update_tool_valves(client, tool_id, valves)
        updated += 1
    return ImportResult("tool_valves", updated=updated, skipped=skipped)


def import_functions(client: OpenWebUIClient) -> ImportResult:
    created = updated = 0
    for record in load_function_records():
        path = ROOT / record["path"]
        payload = {
            "id": record["id"],
            "name": record.get("name") or record["id"],
            "content": path.read_text(encoding="utf-8"),
            "meta": {"description": record.get("purpose")},
        }
        existing = get_existing(client, f"/api/v1/functions/id/{record['id']}")
        if existing:
            client.request("POST", f"/api/v1/functions/id/{record['id']}/update", payload)
            updated += 1
        else:
            existing = client.request("POST", "/api/v1/functions/create", payload)
            created += 1
        if isinstance(existing, dict) and existing.get("is_active") is False:
            client.request("POST", f"/api/v1/functions/id/{record['id']}/toggle")
    return ImportResult("functions", created, updated)


def import_skills(client: OpenWebUIClient, public: bool) -> ImportResult:
    created = updated = skipped = 0
    skipped = 1 if (SKILLS_DIR / "README.md").exists() else 0
    for path in skill_files():
        skill_id, name, description = parse_skill(path)
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
            payload["access_grants"] = existing.get("access_grants") or payload["access_grants"]
            client.request("POST", f"/api/v1/skills/id/{skill_id}/update", payload)
            if existing.get("is_active") is False:
                client.request("POST", f"/api/v1/skills/id/{skill_id}/toggle")
            updated += 1
        else:
            client.request("POST", "/api/v1/skills/create", payload)
            created += 1
    return ImportResult("skills", created, updated, skipped)


def find_knowledge_by_name(client: OpenWebUIClient, name: str) -> dict[str, Any] | None:
    result = client.request("GET", "/api/v1/knowledge/search", query={"query": name})
    items = result.get("items", []) if isinstance(result, dict) else []
    for item in items:
        if item.get("name") == name:
            return item
    return None


def upsert_knowledge_with_files(client: OpenWebUIClient, model_id: str, model_name: str, files: list[Path], public: bool) -> dict[str, str]:
    name = f"Modellwissen - {model_name}"
    filenames = ", ".join(path.name for path in files)
    description = f"{filenames} für das Modell {model_id} aus dem OpenWebUI Workspace."
    payload = {"name": name, "description": description, "access_grants": public_read_grants(public)}
    knowledge = find_knowledge_by_name(client, name)
    if knowledge:
        knowledge_id = knowledge["id"]
        client.request("POST", f"/api/v1/knowledge/{knowledge_id}/update", payload)
        client.request("POST", f"/api/v1/knowledge/{knowledge_id}/reset")
    else:
        created = client.request("POST", "/api/v1/knowledge/create", payload)
        knowledge_id = created["id"]
    file_refs = []
    for file_path in files:
        uploaded = client.upload_file(file_path)
        file_refs.append({"file_id": uploaded["id"]})
    result = client.request("POST", f"/api/v1/knowledge/{knowledge_id}/files/batch/add", file_refs)
    if isinstance(result, dict) and result.get("warnings"):
        raise RuntimeError(f"Knowledge import failed for {name}: {result['warnings']}")
    if isinstance(result, dict) and "files" in result:
        linked_file_ids = {
            str(item.get("id") or item.get("file_id"))
            for item in result.get("files") or []
            if isinstance(item, dict)
        }
        missing_file_ids = [item["file_id"] for item in file_refs if item["file_id"] not in linked_file_ids]
        if missing_file_ids:
            raise RuntimeError(f"Knowledge import did not link all files for {name}: {missing_file_ids}")
    return {"id": knowledge_id, "name": name}


def load_models_with_knowledge(client: OpenWebUIClient, public: bool, upload_knowledge: bool) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    for model_file in sorted(SINGLE_MODELS.glob("*/model.json")):
        data = read_json(model_file)
        if not isinstance(data, list) or not data:
            continue
        model = data[0]
        model_id = str(model.get("id"))
        if upload_knowledge:
            prompt_files = required_model_knowledge_files(model_file.parent)
            knowledge = upsert_knowledge_with_files(
                client,
                model_id,
                str(model.get("name") or model_id),
                prompt_files,
                public,
            )
            meta = model.setdefault("meta", {})
            existing = [item for item in meta.get("knowledge", []) if isinstance(item, dict)]
            meta["knowledge"] = [item for item in existing if item.get("id") != knowledge["id"]]
            meta["knowledge"].append(knowledge)
        else:
            required_model_knowledge_files(model_file.parent)
        models.append(model)
    return models


def import_models(client: OpenWebUIClient, public: bool, upload_knowledge: bool) -> ImportResult:
    models = load_models_with_knowledge(client, public=public, upload_knowledge=upload_knowledge)
    if not models:
        return ImportResult("models", skipped=1)
    client.request("POST", "/api/v1/models/import", {"models": models})
    return ImportResult("models", updated=len(models))


def print_results(results: list[ImportResult], title: str = "# OpenWebUI workspace import") -> None:
    print(title)
    for result in results:
        print(
            f"- {result.kind}: created={result.created}, updated={result.updated}, skipped={result.skipped}"
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import this repository's OpenWebUI tools, functions, skills, knowledge and models."
    )
    parser.add_argument("--config", default=None, help="YAML config file. Defaults to scripts/openwebui_workspace_config.yaml when present.")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--public-read", action="store_true", help="Grant read access to all users where OpenWebUI permits it.")
    parser.add_argument("--skip-knowledge", action="store_true", help="Do not upload mainprompt.md and fachwissen.md files as Knowledge.")
    parser.add_argument(
        "--include-optional-network-tools",
        action="store_true",
        help="Also import optional network-capable tools. This is the default unless import.include_optional_network_tools is false in the YAML config.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate payload files and print counts without calling OpenWebUI.")
    parser.add_argument("--jupyter-url", default=None, help="Jupyter URL as seen from the OpenWebUI backend/container.")
    parser.add_argument("--jupyter-token", default=None, help="Jupyter token for the air_gapped_jupyter_python tool valve.")
    parser.add_argument("--jupyter-timeout-seconds", type=int, default=None, help="Jupyter execution timeout tool valve.")
    parser.add_argument("--jupyter-allowed-workdir", default=None, help="Allowed workdir as seen by the Jupyter host/container.")
    parser.add_argument("--artifact-root", default=None, help="Artifact root as seen by the OpenWebUI backend/container.")
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
            "Set OPENWEBUI_ADMIN_TOKEN, paste OPENWEBUI_ADMIN_TOKEN in this script, or configure openwebui.admin_token in scripts/openwebui_workspace_config.yaml.",
            file=sys.stderr,
        )
        return 2
    client = OpenWebUIClient(runtime["base_url"], token, timeout=int(runtime["timeout"]))
    started = time.time()
    results = [
        import_tools(
            client,
            public=bool(runtime["public_read"]),
            include_optional_network_tools=bool(runtime["include_optional_network_tools"]),
        ),
        import_tool_valves(client, runtime),
        import_functions(client),
        import_skills(client, public=bool(runtime["public_read"])),
        import_models(
            client,
            public=bool(runtime["public_read"]),
            upload_knowledge=not bool(runtime["skip_knowledge"]),
        ),
    ]
    print_results(results)
    print(f"- duration_seconds: {time.time() - started:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
