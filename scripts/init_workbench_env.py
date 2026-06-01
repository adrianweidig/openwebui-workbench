from __future__ import annotations

import argparse
import re
import secrets
import sys
from pathlib import Path
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "Deployment" / "workbench.env.example"
DEFAULT_OUTPUT = ROOT / ".env"
REQUIRED_KEYS = ("WEBUI_SECRET_KEY",)
TEMPLATE_KEYS = (*REQUIRED_KEYS, "WORKBENCH_AUTH_PASSWORD", "WORKBENCH_AUTH_PASSWORD_FILE")
AUTH_VALUE_KEYS = ("WORKBENCH_AUTH_PASSWORD", "WORKBENCH_AUTH_PASSWORD_FILE", "WORKBENCH_AUTH_PASSWORD_HOST_FILE")
AUTH_VALUE_LABEL = "WORKBENCH_AUTH_PASSWORD or WORKBENCH_AUTH_PASSWORD_FILE"
GENERATED_VALUES: dict[str, Callable[[], str]] = {
    "WEBUI_SECRET_KEY": lambda: secrets.token_urlsafe(48),
    "WORKBENCH_AUTH_PASSWORD": lambda: secrets.token_urlsafe(24),
}
ENV_LINE_RE = re.compile(r"^(?P<key>[A-Z0-9_]+)=(?P<value>.*)$")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or validate the local OpenWebUI Workbench .env file.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="env template to read")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="local .env file to create")
    parser.add_argument("--force", action="store_true", help="overwrite the output file if it already exists")
    parser.add_argument("--check", action="store_true", help="validate that the output file contains required values")
    return parser.parse_args(argv)


def env_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = ENV_LINE_RE.match(line.strip())
        if match:
            values[match.group("key")] = match.group("value").strip()
    return values


def render_env_template(template_text: str) -> tuple[str, list[str]]:
    generated: list[str] = []
    rendered: list[str] = []
    for line in template_text.splitlines():
        match = ENV_LINE_RE.match(line)
        if not match:
            rendered.append(line)
            continue
        key = match.group("key")
        value = match.group("value")
        if key in GENERATED_VALUES and not value.strip():
            value = GENERATED_VALUES[key]()
            generated.append(key)
        rendered.append(f"{key}={value}")
    return "\n".join(rendered).rstrip() + "\n", generated


def missing_template_keys(template_text: str) -> list[str]:
    values = env_values(template_text)
    return [key for key in TEMPLATE_KEYS if key not in values]


def write_env_file(template_path: Path, output_path: Path, force: bool = False) -> list[str]:
    if output_path.exists() and not force:
        raise FileExistsError(f"{output_path} already exists. Use --force only after backing up local values.")
    template_text = template_path.read_text(encoding="utf-8")
    missing_keys = missing_template_keys(template_text)
    if missing_keys:
        raise ValueError(f"{template_path} is missing required key(s): {', '.join(missing_keys)}")
    rendered, generated = render_env_template(template_text)
    output_path.write_text(rendered, encoding="utf-8", newline="\n")
    return generated


def missing_required_values(env_path: Path) -> list[str]:
    if not env_path.exists():
        return [*REQUIRED_KEYS, AUTH_VALUE_LABEL]
    values = env_values(env_path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_KEYS if not values.get(key, "").strip()]
    auth_required = values.get("WORKBENCH_REQUIRE_AUTH", "true").strip().lower()
    if auth_required not in {"0", "false", "no", "off"} and not any(
        values.get(key, "").strip() for key in AUTH_VALUE_KEYS
    ):
        missing.append(AUTH_VALUE_LABEL)
    return missing


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    template_path = args.template.resolve()
    output_path = args.output.resolve()
    try:
        if args.check:
            missing = missing_required_values(output_path)
            print("# Workbench env check")
            print(f"- Datei: {output_path}")
            if missing:
                print(f"- Fehlende Werte: {', '.join(missing)}")
                print("- Ergebnis: nicht startbereit")
                return 1
            print("- Erforderliche Werte: gesetzt")
            print("- Ergebnis: startbereit")
            return 0

        generated = write_env_file(template_path, output_path, args.force)
        print("# Workbench env initialization")
        print(f"- Vorlage: {template_path}")
        print(f"- Datei erstellt: {output_path}")
        print(f"- Generierte Werte: {', '.join(generated) if generated else 'keine'}")
        print("- Secret-Werte werden absichtlich nicht ausgegeben.")
        print("- Prüfen: python scripts/init_workbench_env.py --check")
        return 0
    except (FileExistsError, FileNotFoundError, PermissionError, ValueError) as exc:
        print("# Workbench env initialization failed", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
