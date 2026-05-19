"""
title: Safe HTTP Fetcher
description: Bounded HTTP GET and HEAD inspection for public URLs with SSRF protections.
version: 1.0.0
license: MIT
security: Only http/https URLs are allowed. Private, loopback, link-local and multicast hosts are blocked by default. No cookies, secrets, POST requests, shell commands or filesystem access are used.
"""

from __future__ import annotations

import html
import ipaddress
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - OpenWebUI normally provides pydantic
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "proxy-authorization", "x-api-key"}


class _CheckedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, owner: "Tools") -> None:
        self.owner = owner
        self.redirect_count = 0

    def redirect_request(self, req: urllib.request.Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> urllib.request.Request:
        self.redirect_count += 1
        if self.redirect_count > self.owner.valves.max_redirects:
            raise urllib.error.HTTPError(newurl, code, "redirect limit reached", headers, fp)
        self.owner._validate_url(newurl)
        return urllib.request.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)


class Tools:
    """OpenWebUI toolkit for safe public HTTP inspection."""

    citation = False

    class Valves(BaseModel):
        timeout_seconds: int = Field(10, description="Network timeout per request.")
        max_response_bytes: int = Field(65536, description="Maximum bytes read from a response body.")
        max_redirects: int = Field(3, description="Maximum followed redirects.")
        allow_private_networks: bool = Field(False, description="Allow private or local IP ranges. Keep disabled for normal use.")
        user_agent: str = Field("OpenWebUI-SafeHTTPFetcher/1.0", description="User-Agent sent to public servers.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def fetch_url(self, url: str, method: str = "GET", extract_links: bool = True, __event_emitter__: Any = None) -> str:
        """
        Fetch a public URL with GET or HEAD and return status, safe headers and a truncated body summary.
        :param url: Public http or https URL.
        :param method: GET or HEAD.
        :param extract_links: Extract title and links from HTML bodies when true.
        """
        method = method.upper().strip()
        if method not in {"GET", "HEAD"}:
            return "Fehler: Nur GET und HEAD sind erlaubt."
        try:
            clean_url = self._validate_url(url)
        except ValueError as exc:
            return f"Fehler: {exc}"

        await self._emit(__event_emitter__, "Rufe öffentliche URL ab", False)
        request = urllib.request.Request(clean_url, method=method, headers={"User-Agent": self.valves.user_agent, "Accept": "text/html,application/json,text/plain,*/*;q=0.8"})
        opener = urllib.request.build_opener(_CheckedRedirect(self))
        try:
            with opener.open(request, timeout=max(1, int(self.valves.timeout_seconds))) as response:
                status = getattr(response, "status", response.getcode())
                final_url = response.geturl()
                headers = self._safe_headers(dict(response.headers.items()))
                raw = b"" if method == "HEAD" else response.read(max(0, int(self.valves.max_response_bytes)) + 1)
        except urllib.error.HTTPError as exc:
            raw = exc.read(min(max(0, int(self.valves.max_response_bytes)), 8192)) if method != "HEAD" else b""
            status = exc.code
            final_url = exc.url
            headers = self._safe_headers(dict(exc.headers.items()) if exc.headers else {})
        except Exception as exc:
            await self._emit(__event_emitter__, "HTTP-Abruf fehlgeschlagen", True)
            return f"Fehler: HTTP-Abruf fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"

        truncated = len(raw) > int(self.valves.max_response_bytes)
        raw = raw[: int(self.valves.max_response_bytes)]
        text = self._decode(raw, headers.get("content-type", ""))
        await self._emit(__event_emitter__, "HTTP-Abruf abgeschlossen", True)
        if __event_emitter__:
            await __event_emitter__({"type": "citation", "data": {"source": {"name": final_url, "url": final_url}, "document": [text[:1000]], "metadata": [{"source": final_url}]}})

        parts = [
            "# HTTP-Ergebnis",
            f"- URL: `{self._redact(final_url)}`",
            f"- Status: `{status}`",
            f"- Gekürzt: `{truncated}`",
            "",
            "## Header",
            self._format_headers(headers),
        ]
        if method == "GET":
            title, links = self._extract_html(text)
            if title or (extract_links and links):
                parts.extend(["", "## HTML-Auswertung"])
                if title:
                    parts.append(f"- Titel: {title}")
                if extract_links and links:
                    parts.append("- Links:")
                    parts.extend(f"  - {link}" for link in links[:20])
            parts.extend(["", "## Inhalt", "```text", self._redact(text[:4000]), "```"])
        return "\n".join(parts)

    async def check_status(self, url: str, __event_emitter__: Any = None) -> str:
        """
        Check a public URL via HEAD and return status and safe headers.
        :param url: Public http or https URL.
        """
        return await self.fetch_url(url=url, method="HEAD", extract_links=False, __event_emitter__=__event_emitter__)

    def _validate_url(self, url: str) -> str:
        if len(url) > 2048:
            raise ValueError("URL ist zu lang.")
        parsed = urllib.parse.urlparse(url.strip())
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Nur http und https sind erlaubt.")
        if not parsed.hostname:
            raise ValueError("URL enthält keinen Host.")
        host = parsed.hostname.rstrip(".")
        if not self.valves.allow_private_networks:
            infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), proto=socket.IPPROTO_TCP)
            for info in infos:
                ip = ipaddress.ip_address(info[4][0])
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
                    raise ValueError("Private, lokale oder reservierte Netzwerkziele sind blockiert.")
        return urllib.parse.urlunparse(parsed._replace(fragment=""))

    def _safe_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        return {k.lower(): ("[REDACTED]" if k.lower() in SENSITIVE_HEADERS else self._redact(str(v))[:500]) for k, v in headers.items()}

    def _format_headers(self, headers: Dict[str, str]) -> str:
        if not headers:
            return "_Keine Header verfügbar._"
        return "\n".join(f"- `{k}`: `{v}`" for k, v in sorted(headers.items()))

    def _decode(self, raw: bytes, content_type: str) -> str:
        charset = "utf-8"
        match = re.search(r"charset=([\w.-]+)", content_type, re.I)
        if match:
            charset = match.group(1)
        return raw.decode(charset, errors="replace")

    def _extract_html(self, text: str) -> Tuple[str, List[str]]:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        title = html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else ""
        links = []
        for match in re.finditer(r"<a\s+[^>]*href=[\"']([^\"']+)[\"']", text, re.I):
            href = html.unescape(match.group(1)).strip()
            if href.startswith(("http://", "https://")):
                links.append(self._redact(href)[:300])
        return title[:300], links

    def _redact(self, value: str) -> str:
        value = re.sub(r"(?i)(token|api[_-]?key|password|secret)=([^&\s]+)", r"\1=[REDACTED]", value)
        value = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/=-]+", r"\1[REDACTED]", value)
        return value

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
