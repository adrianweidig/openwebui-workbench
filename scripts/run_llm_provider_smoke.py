#!/usr/bin/env python3
"""Run a minimal external LLM provider smoke test without local model fallback."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


LOCAL_HOSTS = {
    "localhost",
    "host.docker.internal",
    "openwebui",
    "ollama",
    "ki-test-openwebui",
}


@dataclass(frozen=True)
class Provider:
    name: str
    key_env: str
    base_url_env: str
    default_base_url: str
    default_model: str
    api_style: str = "openai"


PROVIDERS: dict[str, Provider] = {
    "openrouter": Provider(
        "openrouter",
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
        "openai/gpt-4.1",
    ),
    "gemini": Provider(
        "gemini",
        "GEMINI_API_KEY",
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
        "gemini-2.5-pro",
        "gemini",
    ),
    "deepseek": Provider(
        "deepseek",
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com/v1",
        "deepseek-chat",
    ),
    "mistral": Provider(
        "mistral",
        "MISTRAL_API_KEY",
        "MISTRAL_BASE_URL",
        "https://api.mistral.ai/v1",
        "mistral-large-latest",
    ),
    "groq": Provider(
        "groq",
        "GROQ_API_KEY",
        "GROQ_BASE_URL",
        "https://api.groq.com/openai/v1",
        "llama-3.3-70b-versatile",
    ),
    "perplexity": Provider(
        "perplexity",
        "PERPLEXITY_API_KEY",
        "PERPLEXITY_BASE_URL",
        "https://api.perplexity.ai",
        "sonar-pro",
    ),
}

AUTO_PROVIDER_ORDER = ("openrouter", "gemini", "deepseek", "mistral", "groq", "perplexity")
REDACTED_SECRET = "[REDACTED]"
SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)([^\s,;\"'}]+)"),
    re.compile(r"(?i)(x-goog-api-key\s*[:=]\s*)([^\s,;\"'}]+)"),
    re.compile(r"(?i)([?&]key=)([^&\s\"'}]+)"),
)


class SmokeError(RuntimeError):
    pass


def _host_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise SmokeError(f"invalid provider base URL for live LLM smoke test: {url!r}")
    return parsed.hostname.lower()


def _reject_local_base_url(url: str) -> str:
    host = _host_from_url(url)
    if host in LOCAL_HOSTS or "." not in host or host.endswith((".localhost", ".local", ".internal", ".lan", ".home.arpa")):
        raise SmokeError(f"refusing local model endpoint for live LLM smoke test: {host}")
    try:
        addresses = [item[4][0] for item in socket.getaddrinfo(host, None)]
    except OSError:
        addresses = []
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise SmokeError(f"refusing private/local provider address for live LLM smoke test: {host}")
    return host


def _select_provider(name: str) -> Provider | None:
    if name != "auto":
        provider = PROVIDERS.get(name)
        if provider is None:
            raise SmokeError(f"unknown provider: {name}")
        return provider if os.environ.get(provider.key_env) else None
    for provider_name in AUTO_PROVIDER_ORDER:
        provider = PROVIDERS[provider_name]
        if os.environ.get(provider.key_env):
            return provider
    return None


def _known_secret_values() -> list[str]:
    values = [
        value
        for provider in PROVIDERS.values()
        for value in [os.environ.get(provider.key_env)]
        if value and len(value) >= 6
    ]
    return sorted(set(values), key=len, reverse=True)


def _redact_secrets(text: str) -> str:
    redacted = text
    for value in _known_secret_values():
        redacted = redacted.replace(value, REDACTED_SECRET)
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}{REDACTED_SECRET}", redacted)
    return redacted


def _request_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> Any:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        # Provider base URL is validated and local/private addresses are refused before this call.
        with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = _redact_secrets(exc.read().decode("utf-8", errors="replace"))[:400]
        raise SmokeError(f"provider HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SmokeError(f"provider request failed: {_redact_secrets(str(exc.reason))}") from exc


def _gemini_generate_content_url(base_url: str, model: str) -> str:
    encoded_model = urllib.parse.quote(model, safe="")
    return f"{base_url.rstrip('/')}/models/{encoded_model}:generateContent"


def _run_openai_style(provider: Provider, base_url: str, model: str, prompt: str, timeout: int) -> dict[str, Any]:
    api_key = os.environ.get(provider.key_env)
    if not api_key:
        raise SmokeError(f"missing provider key env: {provider.key_env}")
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0,
        "max_tokens": 16,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    status, data = _request_json(url, headers, payload, timeout)
    choices = data.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    content = str(message.get("content", ""))
    return {
        "http_status": status,
        "finish_reason": choices[0].get("finish_reason") if choices else None,
        "response_chars": len(content),
    }


def _run_gemini(provider: Provider, base_url: str, model: str, prompt: str, timeout: int) -> dict[str, Any]:
    api_key = os.environ.get(provider.key_env)
    if not api_key:
        raise SmokeError(f"missing provider key env: {provider.key_env}")
    url = _gemini_generate_content_url(base_url, model)
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 16,
        },
    }
    status, data = _request_json(url, {"Content-Type": "application/json", "x-goog-api-key": api_key}, payload, timeout)
    candidates = data.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    content = "".join(str(part.get("text", "")) for part in parts)
    return {
        "http_status": status,
        "finish_reason": candidates[0].get("finishReason") if candidates else None,
        "response_chars": len(content),
    }


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    provider = _select_provider(args.provider)
    if provider is None:
        if args.require:
            raise SmokeError("no configured external LLM provider key found")
        return {"ok": False, "skipped": True, "reason": "no configured external LLM provider key found"}

    base_url = args.base_url or os.environ.get(provider.base_url_env) or provider.default_base_url
    host = _reject_local_base_url(base_url)
    model = args.model or os.environ.get("LLM_PROVIDER_SMOKE_MODEL") or provider.default_model

    if provider.api_style == "gemini":
        detail = _run_gemini(provider, base_url, model, args.prompt, args.timeout)
    else:
        detail = _run_openai_style(provider, base_url, model, args.prompt, args.timeout)

    return {
        "ok": True,
        "provider": provider.name,
        "model": model,
        "base_url_host": host,
        **detail,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a minimal live LLM smoke test through external provider API keys only."
    )
    parser.add_argument(
        "--provider",
        default=os.environ.get("LLM_PROVIDER_SMOKE_PROVIDER", "auto"),
        choices=("auto", *PROVIDERS.keys()),
        help="External provider to use. The default auto selects the first configured provider key.",
    )
    parser.add_argument("--model", default=None, help="Provider model ID. Defaults to a strong provider model.")
    parser.add_argument("--base-url", default=None, help="Provider API base URL. Local/private endpoints are refused.")
    parser.add_argument(
        "--prompt",
        default="Return exactly: OK",
        help="Tiny smoke-test prompt. Do not include sensitive data.",
    )
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--require", action="store_true", help="Fail if no provider key is configured.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = run_smoke(args)
    except SmokeError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") or result.get("skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
