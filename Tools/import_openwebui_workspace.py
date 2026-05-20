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


# Paste the admin API token here, or set OPENWEBUI_ADMIN_TOKEN.
OPENWEBUI_ADMIN_TOKEN = "PASTE_OPENWEBUI_ADMIN_API_TOKEN_HERE"

# Change this only if your OpenWebUI is not reachable on localhost:3000.
OPENWEBUI_BASE_URL = "http://localhost:3000"

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "Tools"
TOOLS_INDEX = TOOLS_DIR / "index.json"
OPENWEBUI_EXT = TOOLS_DIR / "openwebui_ext"
TOOLS_REGISTRY = TOOLS_DIR / "dist" / "openwebui-tool-registry.json"
FUNCTION_REGISTRY = TOOLS_DIR / "dist" / "openwebui-function-registry.json"
SKILLS_DIR = OPENWEBUI_EXT / "skills"
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"

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
    for path in sorted(SKILLS_DIR.glob("*.md")):
        if path.name.upper() == "README.MD":
            skipped += 1
            continue
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


def upsert_knowledge_with_file(client: OpenWebUIClient, model_id: str, model_name: str, fachwissen: Path, public: bool) -> dict[str, str]:
    name = f"Fachwissen - {model_name}"
    description = f"Fachwissen.md fuer das Modell {model_id} aus dem OpenWebUI Workspace."
    payload = {"name": name, "description": description, "access_grants": public_read_grants(public)}
    knowledge = find_knowledge_by_name(client, name)
    if knowledge:
        knowledge_id = knowledge["id"]
        client.request("POST", f"/api/v1/knowledge/{knowledge_id}/update", payload)
        client.request("POST", f"/api/v1/knowledge/{knowledge_id}/reset")
    else:
        created = client.request("POST", "/api/v1/knowledge/create", payload)
        knowledge_id = created["id"]
    uploaded = client.upload_file(fachwissen)
    file_id = uploaded["id"]
    client.request("POST", f"/api/v1/knowledge/{knowledge_id}/files/batch/add", [{"file_id": file_id}])
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
            fachwissen = model_file.parent / "fachwissen.md"
            if fachwissen.exists():
                knowledge = upsert_knowledge_with_file(
                    client,
                    model_id,
                    str(model.get("name") or model_id),
                    fachwissen,
                    public,
                )
                meta = model.setdefault("meta", {})
                existing = [item for item in meta.get("knowledge", []) if isinstance(item, dict)]
                meta["knowledge"] = [item for item in existing if item.get("id") != knowledge["id"]]
                meta["knowledge"].append(knowledge)
        models.append(model)
    return models


def import_models(client: OpenWebUIClient, public: bool, upload_knowledge: bool) -> ImportResult:
    models = load_models_with_knowledge(client, public=public, upload_knowledge=upload_knowledge)
    if not models:
        return ImportResult("models", skipped=1)
    client.request("POST", "/api/v1/models/import", {"models": models})
    return ImportResult("models", updated=len(models))


def print_results(results: list[ImportResult]) -> None:
    print("# OpenWebUI workspace import")
    for result in results:
        print(
            f"- {result.kind}: created={result.created}, updated={result.updated}, skipped={result.skipped}"
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import this repository's OpenWebUI tools, functions, skills, knowledge and models."
    )
    parser.add_argument("--base-url", default=os.getenv("OPENWEBUI_BASE_URL", OPENWEBUI_BASE_URL))
    parser.add_argument("--token", default=os.getenv("OPENWEBUI_ADMIN_TOKEN", OPENWEBUI_ADMIN_TOKEN))
    parser.add_argument("--public-read", action="store_true", help="Grant read access to all users where OpenWebUI permits it.")
    parser.add_argument("--skip-knowledge", action="store_true", help="Do not upload fachwissen.md files as Knowledge.")
    parser.add_argument(
        "--include-optional-network-tools",
        action="store_true",
        help="Also import optional network-capable tools. They remain unassigned unless model JSON references them.",
    )
    parser.add_argument("--timeout", type=int, default=120)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    token = str(args.token).strip()
    if token in PLACEHOLDER_TOKENS:
        print("Set OPENWEBUI_ADMIN_TOKEN or paste the admin token into OPENWEBUI_ADMIN_TOKEN in this script.", file=sys.stderr)
        return 2
    client = OpenWebUIClient(args.base_url, token, timeout=args.timeout)
    started = time.time()
    results = [
        import_tools(client, public=args.public_read, include_optional_network_tools=args.include_optional_network_tools),
        import_functions(client),
        import_skills(client, public=args.public_read),
        import_models(client, public=args.public_read, upload_knowledge=not args.skip_knowledge),
    ]
    print_results(results)
    print(f"- duration_seconds: {time.time() - started:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
