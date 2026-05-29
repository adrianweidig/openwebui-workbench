from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGEPACK_ROOT = ROOT / "KnowledgePacks"
REQUIRED_TOP_LEVEL = {
    "schema",
    "id",
    "title",
    "version",
    "target_models",
    "offline_runtime",
    "max_total_bytes",
    "license",
    "snapshot_date",
    "artifacts",
}
REQUIRED_ARTIFACT = {
    "path",
    "media_type",
    "language",
    "size_bytes",
    "sha256",
    "source_type",
    "source_url",
    "update_method",
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate local KnowledgePack manifests.")
    parser.add_argument(
        "--strict-examples",
        action="store_true",
        help="also require example manifests to reference existing artifact files with hashes",
    )
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_manifest(path: Path, strict_examples: bool) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path.relative_to(ROOT).as_posix()}: JSON nicht lesbar: {type(exc).__name__}: {exc}"]

    rel = path.relative_to(ROOT).as_posix()
    require(isinstance(data, dict), f"{rel}: Manifest muss ein JSON-Objekt sein", errors)
    if not isinstance(data, dict):
        return errors

    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    require(not missing, f"{rel}: fehlende Pflichtfelder: {', '.join(missing)}", errors)
    require(data.get("schema") == "openwebui-workbench-knowledgepack/v1", f"{rel}: unbekanntes Schema", errors)
    require(isinstance(data.get("target_models"), list) and bool(data.get("target_models")), f"{rel}: target_models muss eine nichtleere Liste sein", errors)
    require(data.get("offline_runtime") is True, f"{rel}: offline_runtime muss true sein", errors)
    require(isinstance(data.get("max_total_bytes"), int) and data.get("max_total_bytes", 0) > 0, f"{rel}: max_total_bytes muss positiv sein", errors)

    artifacts = data.get("artifacts")
    require(isinstance(artifacts, list), f"{rel}: artifacts muss eine Liste sein", errors)
    if not isinstance(artifacts, list):
        return errors

    is_example = path.name.endswith(".example.json")
    for index, item in enumerate(artifacts):
        prefix = f"{rel}: artifacts[{index}]"
        require(isinstance(item, dict), f"{prefix}: muss ein Objekt sein", errors)
        if not isinstance(item, dict):
            continue
        missing_artifact = sorted(REQUIRED_ARTIFACT - set(item))
        require(not missing_artifact, f"{prefix}: fehlende Pflichtfelder: {', '.join(missing_artifact)}", errors)
        artifact_path_raw = item.get("path")
        require(isinstance(artifact_path_raw, str) and artifact_path_raw.strip(), f"{prefix}: path muss gesetzt sein", errors)
        require(isinstance(item.get("size_bytes"), int) and item.get("size_bytes", -1) >= 0, f"{prefix}: size_bytes muss >= 0 sein", errors)
        require(item.get("source_url") is None or isinstance(item.get("source_url"), str), f"{prefix}: source_url muss null oder String sein", errors)
        if not isinstance(artifact_path_raw, str) or not artifact_path_raw.strip():
            continue
        artifact_path = (path.parent / artifact_path_raw).resolve()
        require(str(artifact_path).startswith(str(path.parent.resolve())), f"{prefix}: path darf das KnowledgePack-Verzeichnis nicht verlassen", errors)
        if is_example and not strict_examples:
            continue
        if not artifact_path.exists():
            errors.append(f"{prefix}: Datei fehlt: {artifact_path.relative_to(ROOT).as_posix()}")
            continue
        actual_size = artifact_path.stat().st_size
        expected_size = item.get("size_bytes")
        if isinstance(expected_size, int) and expected_size != actual_size:
            errors.append(f"{prefix}: size_bytes {expected_size} passt nicht zu {actual_size}")
        expected_hash = item.get("sha256")
        if isinstance(expected_hash, str) and expected_hash:
            actual_hash = sha256(artifact_path)
            if expected_hash.lower() != actual_hash:
                errors.append(f"{prefix}: SHA256 passt nicht")
        else:
            errors.append(f"{prefix}: SHA256 fehlt für echtes Manifest")
    return errors


def iter_manifests() -> list[Path]:
    if not KNOWLEDGEPACK_ROOT.exists():
        return []
    return sorted(
        path
        for path in KNOWLEDGEPACK_ROOT.rglob("manifest*.json")
        if path.is_file() and ".git" not in path.parts
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manifests = iter_manifests()
    errors: list[str] = []
    for manifest in manifests:
        errors.extend(validate_manifest(manifest, args.strict_examples))

    print(f"KnowledgePack-Validierung: {len(manifests)} Manifestdatei(en) geprüft")
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
