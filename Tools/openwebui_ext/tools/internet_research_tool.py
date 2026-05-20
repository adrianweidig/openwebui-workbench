"""
title: Internet Research Tool
description: Public web search and page fetching for OpenWebUI with SSRF protections, timeouts and citations.
version: 1.0.0
license: MIT
offline: false
security: Only public http/https targets are allowed. Private, loopback, link-local, multicast and reserved networks are blocked by default. No cookies, POST requests, shell commands or filesystem access are used.
"""

from __future__ import annotations

import html
import ipaddress
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Tuple

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
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
        if self.redirect_count > 3:
            raise urllib.error.HTTPError(newurl, code, "redirect limit reached", headers, fp)
        self.owner._validate_url(newurl)
        return urllib.request.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)


class Tools:
    """OpenWebUI toolkit for bounded public internet research."""

    citation = True

    class Valves(BaseModel):
        search_endpoint: str = Field("https://duckduckgo.com/html/", description="Public HTML search endpoint.")
        timeout_seconds: int = Field(12, description="Network timeout per request.")
        max_response_bytes: int = Field(120000, description="Maximum bytes read from one response body.")
        max_results: int = Field(8, description="Maximum search results returned.")
        max_fetch_chars: int = Field(6000, description="Maximum extracted page text returned.")
        allow_private_networks: bool = Field(False, description="Allow private or local IP ranges. Keep disabled for normal internet use.")
        user_agent: str = Field("OpenWebUI-InternetResearch/1.0", description="User-Agent sent to public servers.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def search_web(self, query: str, max_results: int = 5, __event_emitter__: Any = None) -> str:
        """
        Search the public web and return result titles, URLs and snippets.
        :param query: Search query.
        :param max_results: Maximum number of results to return.
        """
        query = self._clean_query(query)
        if not query:
            return "Fehler: Suchanfrage fehlt."
        limit = self._limit(max_results)
        await self._emit(__event_emitter__, "Suche im öffentlichen Web", False)
        try:
            search_url = self._search_url(query)
            html_text, final_url = self._fetch_text(search_url)
            results = self._extract_search_results(html_text, limit)
        except Exception as exc:
            await self._emit(__event_emitter__, "Websuche fehlgeschlagen", True)
            return f"Fehler: Websuche fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        await self._emit(__event_emitter__, "Websuche abgeschlossen", True)
        if __event_emitter__:
            for result in results:
                await __event_emitter__({"type": "citation", "data": {"source": {"name": result["title"], "url": result["url"]}, "document": [result["snippet"]], "metadata": [{"source": result["url"]}]}})
        if not results:
            return f"# Websuche\n- Anfrage: {query}\n- Ergebnis: Keine Treffer aus `{self._redact(final_url)}` extrahiert."
        lines = ["# Websuche", f"- Anfrage: {query}", f"- Treffer: {len(results)}", ""]
        for index, result in enumerate(results, 1):
            lines.append(f"## {index}. {result['title']}")
            lines.append(f"- URL: {result['url']}")
            if result["snippet"]:
                lines.append(f"- Auszug: {result['snippet']}")
            lines.append("")
        return "\n".join(lines).strip()

    async def fetch_public_page(self, url: str, __event_emitter__: Any = None) -> str:
        """
        Fetch a public page and return title, safe headers and extracted text.
        :param url: Public http or https URL.
        """
        try:
            clean_url = self._validate_url(url)
        except ValueError as exc:
            return f"Fehler: {exc}"
        await self._emit(__event_emitter__, "Rufe öffentliche Seite ab", False)
        try:
            text, final_url, headers = self._fetch_text_with_headers(clean_url)
        except Exception as exc:
            await self._emit(__event_emitter__, "Seitenabruf fehlgeschlagen", True)
            return f"Fehler: Seitenabruf fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        title, body_text = self._extract_page_text(text)
        await self._emit(__event_emitter__, "Seitenabruf abgeschlossen", True)
        if __event_emitter__:
            await __event_emitter__({"type": "citation", "data": {"source": {"name": title or final_url, "url": final_url}, "document": [body_text[:1000]], "metadata": [{"source": final_url}]}})
        lines = [
            "# Öffentliche Seite",
            f"- URL: {self._redact(final_url)}",
            f"- Titel: {title or '_kein Titel_'}",
            "",
            "## Header",
            self._format_headers(headers),
            "",
            "## Inhalt",
            "```text",
            self._redact(body_text[: int(self.valves.max_fetch_chars)]),
            "```",
        ]
        return "\n".join(lines)

    async def build_research_brief(self, query: str, max_results: int = 5, fetch_top_results: bool = False, __event_emitter__: Any = None) -> str:
        """
        Create a compact research brief from public search results, optionally fetching top pages.
        :param query: Research question or search query.
        :param max_results: Maximum number of search results.
        :param fetch_top_results: Fetch the first matching pages for short evidence snippets.
        """
        query = self._clean_query(query)
        if not query:
            return "Fehler: Recherchefrage fehlt."
        limit = self._limit(max_results)
        await self._emit(__event_emitter__, "Erstelle Internet-Recherchebrief", False)
        try:
            html_text, _ = self._fetch_text(self._search_url(query))
            results = self._extract_search_results(html_text, limit)
        except Exception as exc:
            await self._emit(__event_emitter__, "Recherchebrief fehlgeschlagen", True)
            return f"Fehler: Recherchebrief fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        lines = ["# Internet-Recherchebrief", f"- Frage: {query}", f"- Suchtreffer: {len(results)}", ""]
        for index, result in enumerate(results, 1):
            lines.append(f"## Quelle {index}: {result['title']}")
            lines.append(f"- URL: {result['url']}")
            if result["snippet"]:
                lines.append(f"- Suchauszug: {result['snippet']}")
            if fetch_top_results:
                fetched = self._safe_fetch_excerpt(result["url"])
                if fetched:
                    lines.append(f"- Seiten-Auszug: {fetched}")
            lines.append("")
        lines.append("## Hinweis")
        lines.append("- Quellen kritisch prüfen; Suchauszüge ersetzen keine fachliche Validierung.")
        await self._emit(__event_emitter__, "Internet-Recherchebrief abgeschlossen", True)
        return "\n".join(lines).strip()

    def _search_url(self, query: str) -> str:
        endpoint = self._validate_url(str(self.valves.search_endpoint))
        separator = "&" if urllib.parse.urlparse(endpoint).query else "?"
        return f"{endpoint}{separator}{urllib.parse.urlencode({'q': query})}"

    def _fetch_text(self, url: str) -> Tuple[str, str]:
        text, final_url, _headers = self._fetch_text_with_headers(url)
        return text, final_url

    def _fetch_text_with_headers(self, url: str) -> Tuple[str, str, Dict[str, str]]:
        clean_url = self._validate_url(url)
        request = urllib.request.Request(clean_url, method="GET", headers={"User-Agent": str(self.valves.user_agent), "Accept": "text/html,application/xhtml+xml,text/plain,*/*;q=0.8"})
        opener = urllib.request.build_opener(_CheckedRedirect(self))
        with opener.open(request, timeout=max(1, int(self.valves.timeout_seconds))) as response:
            final_url = self._validate_url(response.geturl())
            headers = self._safe_headers(dict(response.headers.items()))
            raw = response.read(max(1, int(self.valves.max_response_bytes)) + 1)
        raw = raw[: int(self.valves.max_response_bytes)]
        return self._decode(raw, headers.get("content-type", "")), final_url, headers

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

    def _extract_search_results(self, html_text: str, limit: int) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        pattern = re.compile(r'<a[^>]+class=["\'][^"\']*result__a[^"\']*["\'][^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
        for match in pattern.finditer(html_text):
            url = self._normalize_result_url(match.group(1))
            title = self._strip_html(match.group(2))
            if not url or not title:
                continue
            snippet = self._snippet_after(html_text, match.end())
            if url not in {item["url"] for item in results}:
                results.append({"title": title[:220], "url": url[:500], "snippet": snippet[:500]})
            if len(results) >= limit:
                break
        return results

    def _normalize_result_url(self, raw_url: str) -> str:
        value = html.unescape(raw_url)
        if value.startswith("//"):
            value = "https:" + value
        parsed = urllib.parse.urlparse(value)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.netloc.endswith("duckduckgo.com") and query.get("uddg"):
            value = query["uddg"][0]
        try:
            return self._validate_url(value)
        except Exception:
            return ""

    def _snippet_after(self, html_text: str, start: int) -> str:
        chunk = html_text[start : start + 1800]
        match = re.search(r'<a[^>]+class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>(.*?)</a>', chunk, re.I | re.S)
        if not match:
            match = re.search(r'<div[^>]+class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>(.*?)</div>', chunk, re.I | re.S)
        return self._strip_html(match.group(1)) if match else ""

    def _extract_page_text(self, html_text: str) -> Tuple[str, str]:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.I | re.S)
        title = self._strip_html(title_match.group(1)) if title_match else ""
        cleaned = re.sub(r"(?is)<(script|style|noscript|svg|canvas).*?</\1>", " ", html_text)
        body = self._strip_html(cleaned)
        return title[:300], body

    def _safe_fetch_excerpt(self, url: str) -> str:
        try:
            text, _final_url, _headers = self._fetch_text_with_headers(url)
            _title, body = self._extract_page_text(text)
            return self._redact(body[:700])
        except Exception:
            return ""

    def _strip_html(self, value: str) -> str:
        value = re.sub(r"<[^>]+>", " ", value)
        value = html.unescape(value)
        return re.sub(r"\s+", " ", value).strip()

    def _safe_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        return {k.lower(): ("[REDACTED]" if k.lower() in SENSITIVE_HEADERS else self._redact(str(v))[:500]) for k, v in headers.items()}

    def _format_headers(self, headers: Dict[str, str]) -> str:
        if not headers:
            return "_Keine Header verfügbar._"
        return "\n".join(f"- `{key}`: `{value}`" for key, value in sorted(headers.items()))

    def _decode(self, raw: bytes, content_type: str) -> str:
        charset = "utf-8"
        match = re.search(r"charset=([\w.-]+)", content_type, re.I)
        if match:
            charset = match.group(1)
        return raw.decode(charset, errors="replace")

    def _clean_query(self, query: str) -> str:
        return re.sub(r"\s+", " ", str(query or "")).strip()[:500]

    def _limit(self, max_results: int) -> int:
        return max(1, min(int(max_results or 1), int(self.valves.max_results)))

    def _redact(self, value: str) -> str:
        value = re.sub(r"(?i)(token|api[_-]?key|password|secret)=([^&\s]+)", r"\1=[REDACTED]", value)
        value = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/=-]+", r"\1[REDACTED]", value)
        return value

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
