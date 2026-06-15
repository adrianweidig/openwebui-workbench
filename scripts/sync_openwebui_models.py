#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
LOCAL_MODELS_ROOT = ROOT / "Modelle" / "einzelmodelle"
SYNC_ROOT = ROOT / "Artefakte" / "openwebui_sync"
STATUS_FILE = SYNC_ROOT / "status.json"
STATUS_MARKDOWN = SYNC_ROOT / "status.md"
REMOTE_MODELS_ROOT = SYNC_ROOT / "remote_models"

MANAGED_META_KEYS = {
    "capabilities",
    "defaultFeatureIds",
    "defaultFilterIds",
    "defaultLocale",
    "description",
    "fallbackLocale",
    "filterIds",
    "primaryToolIds",
    "productI18n",
    "productLocaleFiles",
    "profile_image_url",
    "recommendedSkillIds",
    "exampleKnowledgeFiles",
    "legacyExampleResult",
    "requiredFileContextFiles",
    "skillIds",
    "suggestion_prompts",
    "supportedLocales",
    "tags",
    "toolIds",
    "workbenchFileContext",
}
MANAGED_TOP_KEYS = ("id", "name", "base_model_id", "meta", "params")
PLACEHOLDER_TOKENS = {"", "PASTE_OPENWEBUI_ADMIN_API_TOKEN_HERE", "YOUR_OPEN_WEBUI_API_KEY"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def now_local() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def safe_snapshot_name(model_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", model_id).strip("._-")
    if not cleaned:
        cleaned = "model"
    suffix = hashlib.sha256(model_id.encode("utf-8")).hexdigest()[:12]
    return f"{cleaned[:90]}-{suffix}.json"


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    return value


def canonical_model(model: dict[str, Any]) -> dict[str, Any]:
    meta = model.get("meta") if isinstance(model.get("meta"), dict) else {}
    canonical: dict[str, Any] = {}
    for key in MANAGED_TOP_KEYS:
        if key == "meta":
            filtered_meta = {
                meta_key: normalize_value(meta[meta_key])
                for meta_key in sorted(MANAGED_META_KEYS)
                if meta_key in meta
            }
            if filtered_meta:
                canonical[key] = filtered_meta
            continue
        value = model.get(key)
        if value not in (None, ""):
            canonical[key] = normalize_value(value)
    return canonical


def diff_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    if type(left) is not type(right):
        return [prefix or "$"]
    if isinstance(left, dict):
        paths: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{prefix}.{key}" if prefix else str(key)
            if key not in left or key not in right:
                paths.append(child)
            else:
                paths.extend(diff_paths(left[key], right[key], child))
        return paths
    if isinstance(left, list):
        if left == right:
            return []
        return [prefix or "$"]
    if left != right:
        return [prefix or "$"]
    return []


def load_local_models(root: Path = LOCAL_MODELS_ROOT) -> dict[str, dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return models
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        model_json = directory / "model.json"
        if not model_json.exists():
            continue
        try:
            payload = read_json(model_json)
        except (OSError, json.JSONDecodeError) as exc:
            models[directory.name] = {
                "id": directory.name,
                "_sync_error": f"local model.json could not be read: {exc}",
                "_sync_path": model_json.relative_to(ROOT).as_posix(),
            }
            continue
        model = payload[0] if isinstance(payload, list) and payload and isinstance(payload[0], dict) else {}
        model = dict(model)
        model.setdefault("id", directory.name)
        model["_sync_path"] = model_json.relative_to(ROOT).as_posix()
        model["_sync_mtime"] = model_json.stat().st_mtime
        models[str(model.get("id") or directory.name)] = model
    return models


class OpenWebUIModelClient:
    def __init__(self, base_url: str, token: str, timeout: int, tls_verify: bool, ca_file: str, ca_path: str) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OpenWebUI base URL must be an http(s) URL with a host.")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        if not tls_verify:
            self.ssl_context = ssl._create_unverified_context()  # nosec B323
        elif ca_file or ca_path:
            self.ssl_context = ssl.create_default_context(cafile=ca_file or None, capath=ca_path or None)
        else:
            self.ssl_context = None

    def get_json(self, path: str, query: dict[str, str] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        request = Request(url, headers=self.headers, method="GET")
        with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:  # nosec B310
            raw = response.read()
            return json.loads(raw.decode("utf-8"))

    def list_models(self) -> list[dict[str, Any]]:
        response = self.get_json("/api/models")
        if isinstance(response, dict) and isinstance(response.get("data"), list):
            return [item for item in response["data"] if isinstance(item, dict)]
        if isinstance(response, list):
            return [item for item in response if isinstance(item, dict)]
        raise RuntimeError("OpenWebUI /api/models did not return a model list.")

    def model_detail(self, model_id: str, fallback: dict[str, Any]) -> dict[str, Any]:
        try:
            detail = self.get_json("/api/v1/models/model", {"id": model_id})
            if isinstance(detail, dict):
                return detail
        except HTTPError as exc:
            fallback = dict(fallback)
            fallback["_sync_detail_error"] = f"HTTP {exc.code}"
            return fallback
        except (URLError, OSError, json.JSONDecodeError) as exc:
            fallback = dict(fallback)
            fallback["_sync_detail_error"] = str(exc)
            return fallback
        return dict(fallback)

    def load_remote_models(self) -> dict[str, dict[str, Any]]:
        models: dict[str, dict[str, Any]] = {}
        for summary in self.list_models():
            model_id = str(summary.get("id") or "").strip()
            if not model_id:
                continue
            detail = self.model_detail(model_id, summary)
            detail.setdefault("id", model_id)
            models[model_id] = detail
        return models


def compare_models(local_models: dict[str, dict[str, Any]], remote_models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    counts = {
        "identical": 0,
        "local_only": 0,
        "remote_only": 0,
        "conflict": 0,
        "remote_inactive": 0,
        "read_error": 0,
    }
    for model_id in sorted(set(local_models) | set(remote_models)):
        local = local_models.get(model_id)
        remote = remote_models.get(model_id)
        item: dict[str, Any] = {
            "object_type": "model",
            "id": model_id,
            "name": (remote or local or {}).get("name") or model_id,
            "source": "both" if local and remote else "workbench" if local else "openwebui",
            "target": "manual-review",
            "status": "",
            "action": "",
            "diff_paths": [],
        }
        if local and local.get("_sync_path"):
            item["local_path"] = local["_sync_path"]
        if remote:
            item["remote_is_active"] = remote.get("is_active", True)
            item["remote_updated_at"] = remote.get("updated_at")
            item["remote_snapshot"] = f"Artefakte/openwebui_sync/remote_models/{safe_snapshot_name(model_id)}"
            if remote.get("_sync_detail_error"):
                item["remote_detail_error"] = remote["_sync_detail_error"]
        if local and local.get("_sync_error"):
            item["status"] = "read_error"
            item["action"] = "Local model must be fixed before synchronization."
            item["error"] = local["_sync_error"]
        elif local and not remote:
            item["status"] = "local_only"
            item["target"] = "openwebui"
            item["action"] = "Visible as a Workbench-only model; the existing Workbench-to-OpenWebUI import can create it."
        elif remote and not local:
            item["status"] = "remote_only"
            item["target"] = "workbench"
            item["action"] = "Remote model is visible through the OpenWebUI snapshot; no local source package was created automatically."
        elif local and remote:
            local_canonical = canonical_model(local)
            remote_canonical = canonical_model(remote)
            item["local_digest"] = digest(local_canonical)
            item["remote_digest"] = digest(remote_canonical)
            if remote.get("is_active") is False:
                item["status"] = "remote_inactive"
                item["action"] = "Remote model is inactive or disabled; no destructive local change is applied automatically."
            elif local_canonical == remote_canonical:
                item["status"] = "identical"
                item["target"] = "none"
                item["action"] = "No synchronization needed."
            else:
                paths = diff_paths(local_canonical, remote_canonical)
                item["status"] = "conflict"
                item["action"] = "Workbench and OpenWebUI differ in managed fields; no side is overwritten automatically."
                item["diff_paths"] = paths[:50]
                item["diff_count"] = len(paths)
                item["local"] = {path: value_at_path(local_canonical, path) for path in paths[:10]}
                item["remote"] = {path: value_at_path(remote_canonical, path) for path in paths[:10]}
        counts[item["status"]] = counts.get(item["status"], 0) + 1
        items.append(item)
    return {
        "generated_at": now_local(),
        "object_type": "model",
        "counts": counts,
        "total": len(items),
        "items": items,
    }


def value_at_path(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def write_snapshot(status: dict[str, Any], remote_models: dict[str, dict[str, Any]]) -> None:
    REMOTE_MODELS_ROOT.mkdir(parents=True, exist_ok=True)
    for model_id, model in remote_models.items():
        write_json(REMOTE_MODELS_ROOT / safe_snapshot_name(model_id), model)
    write_json(STATUS_FILE, status)
    STATUS_MARKDOWN.write_text(render_markdown_status(status), encoding="utf-8", newline="\n")


def render_markdown_status(status: dict[str, Any]) -> str:
    lines = [
        "# OpenWebUI Model Sync Status",
        "",
        f"- Generated: {status.get('generated_at')}",
        f"- Total: {status.get('total', 0)}",
        "",
        "## Counts",
    ]
    for key, value in sorted((status.get("counts") or {}).items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Items"])
    for item in status.get("items", []):
        detail = item.get("action", "")
        lines.append(f"- `{item.get('id')}`: {item.get('status')} - {detail}")
    lines.append("")
    return "\n".join(lines)


def parse_bool(value: str | None, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def read_token(args: argparse.Namespace) -> str:
    token = args.token or os.environ.get("OPENWEBUI_ADMIN_TOKEN", "")
    token_file = args.token_file or os.environ.get("OPENWEBUI_ADMIN_TOKEN_FILE", "")
    if not token and token_file:
        token = Path(token_file).read_text(encoding="utf-8").strip()
    token = token.strip()
    if token in PLACEHOLDER_TOKENS:
        raise RuntimeError("OPENWEBUI_ADMIN_TOKEN or OPENWEBUI_ADMIN_TOKEN_FILE is required.")
    return token


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare Workbench model packages with OpenWebUI model state.")
    parser.add_argument("--base-url", default=os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:3000"))
    parser.add_argument("--token", default="")
    parser.add_argument("--token-file", default=os.environ.get("OPENWEBUI_ADMIN_TOKEN_FILE", ""))
    parser.add_argument("--tls-verify", choices=("true", "false"), default=os.environ.get("OPENWEBUI_TLS_VERIFY", "true"))
    parser.add_argument("--ca-file", default=os.environ.get("OPENWEBUI_CA_FILE", ""))
    parser.add_argument("--ca-path", default=os.environ.get("OPENWEBUI_CA_PATH", ""))
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--write-snapshot", action="store_true", help="Write remote model snapshots and status under Artefakte/openwebui_sync.")
    parser.add_argument("--fail-on-conflict", action="store_true", help="Exit with code 3 when managed model differences are found.")
    parser.add_argument("--json", action="store_true", help="Print full JSON status instead of a compact text summary.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        token = read_token(args)
        client = OpenWebUIModelClient(
            base_url=args.base_url,
            token=token,
            timeout=args.timeout,
            tls_verify=parse_bool(args.tls_verify, True),
            ca_file=args.ca_file,
            ca_path=args.ca_path,
        )
        local_models = load_local_models()
        remote_models = client.load_remote_models()
        status = compare_models(local_models, remote_models)
        if args.write_snapshot:
            write_snapshot(status, remote_models)
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            counts = status["counts"]
            print("# OpenWebUI model sync status")
            print(f"- generated_at: {status['generated_at']}")
            print(f"- local_models: {len(local_models)}")
            print(f"- remote_models: {len(remote_models)}")
            for key in ("identical", "local_only", "remote_only", "conflict", "remote_inactive", "read_error"):
                print(f"- {key}: {counts.get(key, 0)}")
            if args.write_snapshot:
                print(f"- snapshot: {STATUS_FILE.relative_to(ROOT).as_posix()}")
            for item in status["items"]:
                if item["status"] not in {"identical"}:
                    print(f"  - {item['id']}: {item['status']} - {item['action']}")
        if args.fail_on_conflict and status["counts"].get("conflict", 0):
            return 3
        if status["counts"].get("read_error", 0):
            return 2
        return 0
    except (HTTPError, URLError, OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"OpenWebUI model sync failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
