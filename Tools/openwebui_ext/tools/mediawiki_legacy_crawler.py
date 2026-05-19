"""
title: MediaWiki Legacy Crawler
description: Crawl an internal MediaWiki instance through the MediaWiki API with support for legacy username/password login flows.
version: 1.0.0
license: MIT
security: Only configured MediaWiki hosts are reachable. Credentials are read from Valves or call parameters, never stored, and are redacted from outputs.
"""

from __future__ import annotations

import html
import http.cookiejar
import json
import re
import ssl
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


SENSITIVE_KEYS = {"password", "lgpassword", "token", "lgtoken", "csrftoken", "cookie", "authorization"}


class Tools:
    """OpenWebUI toolkit for bounded internal MediaWiki crawling."""

    citation = False

    class Valves(BaseModel):
        base_url: str = Field("", description="MediaWiki base URL, e.g. https://wiki.internal.example/wiki or https://wiki.internal.example.")
        api_path: str = Field("/api.php", description="Path to api.php when base_url does not already point to api.php.")
        username: str = Field("", description="MediaWiki username. Prefer Valves over prompt parameters.")
        password: str = Field("", description="MediaWiki password. Prefer Valves over prompt parameters.")
        allowed_hosts_csv: str = Field("", description="Optional comma-separated host allowlist. base_url host is always allowed.")
        timeout_seconds: int = Field(20, description="Request timeout per MediaWiki API call.")
        max_pages: int = Field(50, description="Default maximum pages per crawl.")
        max_page_chars: int = Field(12000, description="Maximum wikitext characters retained per page.")
        max_output_chars: int = Field(24000, description="Maximum characters returned to the chat.")
        include_content_by_default: bool = Field(False, description="Include page wikitext in crawl output by default.")
        allow_insecure_tls: bool = Field(False, description="Allow invalid TLS certificates for very old internal MediaWiki servers.")
        user_agent: str = Field("OpenWebUI-MediaWikiLegacyCrawler/1.0", description="User-Agent sent to the MediaWiki server.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def check_mediawiki(self, base_url: str = "", __event_emitter__: Any = None) -> str:
        """
        Check MediaWiki API availability and return version/site metadata.
        :param base_url: Optional MediaWiki base URL overriding the configured Valve.
        """
        await self._emit(__event_emitter__, "Prüfe MediaWiki-API", False)
        try:
            client = self._client(base_url)
            data = client.api_get({"action": "query", "meta": "siteinfo", "siprop": "general|namespaces"})
            general = data.get("query", {}).get("general", {})
            namespaces = data.get("query", {}).get("namespaces", {})
        except Exception as exc:
            await self._emit(__event_emitter__, "MediaWiki-Prüfung fehlgeschlagen", True)
            return f"Fehler: MediaWiki-API nicht erreichbar: {type(exc).__name__}: {self._redact(str(exc))}"
        await self._emit(__event_emitter__, "MediaWiki-API erreichbar", True)
        lines = [
            "# MediaWiki-Status",
            f"- API: `{self._redact(client.api_url)}`",
            f"- Sitename: `{self._text(general.get('sitename', 'unbekannt'))}`",
            f"- Generator: `{self._text(general.get('generator', 'unbekannt'))}`",
            f"- Hauptseite: `{self._redact(str(general.get('mainpage', 'unbekannt')))}`",
            f"- Namespaces: `{len(namespaces)}`",
        ]
        return "\n".join(lines)[: int(self.valves.max_output_chars)]

    async def login_check(
        self,
        base_url: str = "",
        username: str = "",
        password: str = "",
        __event_emitter__: Any = None,
    ) -> str:
        """
        Verify MediaWiki username/password login without returning credentials.
        :param base_url: Optional MediaWiki base URL overriding the configured Valve.
        :param username: Optional username overriding the configured Valve.
        :param password: Optional password overriding the configured Valve.
        """
        await self._emit(__event_emitter__, "Prüfe MediaWiki-Login", False)
        try:
            client = self._client(base_url)
            login_result = client.login(username or self.valves.username, password or self.valves.password)
            userinfo = client.api_get({"action": "query", "meta": "userinfo"})
        except Exception as exc:
            await self._emit(__event_emitter__, "MediaWiki-Login fehlgeschlagen", True)
            return f"Fehler: Login fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        await self._emit(__event_emitter__, "MediaWiki-Login erfolgreich", True)
        user = userinfo.get("query", {}).get("userinfo", {})
        groups = user.get("groups", [])
        return "\n".join(
            [
                "# MediaWiki-Login",
                f"- Status: `{self._text(login_result)}`",
                f"- Benutzer: `{self._text(user.get('name', 'unbekannt'))}`",
                f"- User-ID: `{self._text(user.get('id', 'unbekannt'))}`",
                f"- Gruppen: `{', '.join(map(str, groups)) if isinstance(groups, list) else self._text(groups)}`",
            ]
        )[: int(self.valves.max_output_chars)]

    async def fetch_page(
        self,
        title: str,
        base_url: str = "",
        username: str = "",
        password: str = "",
        include_content: bool = True,
        __event_emitter__: Any = None,
    ) -> str:
        """
        Fetch one MediaWiki page through the API.
        :param title: Exact page title.
        :param base_url: Optional MediaWiki base URL overriding the configured Valve.
        :param username: Optional username overriding the configured Valve.
        :param password: Optional password overriding the configured Valve.
        :param include_content: Include truncated wikitext content.
        """
        if not title.strip():
            return "Fehler: Seitentitel fehlt."
        await self._emit(__event_emitter__, "Lade MediaWiki-Seite", False)
        try:
            client = self._client(base_url)
            client.login_if_configured(username or self.valves.username, password or self.valves.password)
            pages = client.fetch_pages([title.strip()], include_content=include_content, max_page_chars=int(self.valves.max_page_chars))
        except Exception as exc:
            await self._emit(__event_emitter__, "MediaWiki-Seitenabruf fehlgeschlagen", True)
            return f"Fehler: Seitenabruf fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        await self._emit(__event_emitter__, "MediaWiki-Seite geladen", True)
        return self._format_pages(pages, include_content=include_content)

    async def crawl_pages(
        self,
        base_url: str = "",
        username: str = "",
        password: str = "",
        namespace: int = 0,
        prefix: str = "",
        max_pages: int = 0,
        include_content: Optional[bool] = None,
        __event_emitter__: Any = None,
    ) -> str:
        """
        Crawl page titles and optional wikitext content from an internal MediaWiki.
        :param base_url: Optional MediaWiki base URL overriding the configured Valve.
        :param username: Optional username overriding the configured Valve.
        :param password: Optional password overriding the configured Valve.
        :param namespace: MediaWiki namespace number, default 0.
        :param prefix: Optional title prefix filter.
        :param max_pages: Maximum number of pages. Defaults to Valve max_pages.
        :param include_content: Include truncated wikitext content. Defaults to Valve include_content_by_default.
        """
        limit = max(1, min(int(max_pages or self.valves.max_pages), 500))
        include = bool(self.valves.include_content_by_default if include_content is None else include_content)
        await self._emit(__event_emitter__, f"Crawle MediaWiki-Seitenliste ({limit})", False)
        try:
            client = self._client(base_url)
            client.login_if_configured(username or self.valves.username, password or self.valves.password)
            titles = client.list_pages(namespace=int(namespace), prefix=prefix.strip(), limit=limit)
            pages = client.fetch_pages(titles, include_content=include, max_page_chars=int(self.valves.max_page_chars))
        except Exception as exc:
            await self._emit(__event_emitter__, "MediaWiki-Crawl fehlgeschlagen", True)
            return f"Fehler: Crawl fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        await self._emit(__event_emitter__, f"MediaWiki-Crawl abgeschlossen: {len(pages)} Seiten", True)
        header = [
            "# MediaWiki-Crawl",
            f"- API: `{self._redact(client.api_url)}`",
            f"- Namespace: `{namespace}`",
            f"- Prefix: `{self._text(prefix) if prefix else '-'}`",
            f"- Seiten: `{len(pages)}`",
            f"- Inhalt enthalten: `{include}`",
            "",
        ]
        return ("\n".join(header) + self._format_pages(pages, include_content=include))[: int(self.valves.max_output_chars)]

    def _client(self, base_url: str = "") -> "_MediaWikiClient":
        configured = (base_url or self.valves.base_url).strip()
        if not configured:
            raise ValueError("MediaWiki base_url fehlt. Setze sie in den Tool-Valves oder übergib base_url.")
        api_url = self._api_url(configured)
        allowed_hosts = {host.strip().lower() for host in str(self.valves.allowed_hosts_csv).split(",") if host.strip()}
        configured_host = urllib.parse.urlparse(api_url).hostname
        if configured_host:
            allowed_hosts.add(configured_host.lower())
        parsed = urllib.parse.urlparse(api_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Nur http/https MediaWiki-URLs mit Host sind erlaubt.")
        if allowed_hosts and parsed.hostname.lower() not in allowed_hosts:
            raise ValueError("MediaWiki-Host ist nicht in der Allowlist.")
        return _MediaWikiClient(
            api_url=api_url,
            timeout=max(1, int(self.valves.timeout_seconds)),
            user_agent=str(self.valves.user_agent),
            insecure_tls=bool(self.valves.allow_insecure_tls),
        )

    def _api_url(self, base_url: str) -> str:
        parsed = urllib.parse.urlparse(base_url.strip())
        if not parsed.scheme:
            raise ValueError("MediaWiki base_url braucht http:// oder https://.")
        if parsed.path.endswith("/api.php"):
            return urllib.parse.urlunparse(parsed._replace(query="", fragment=""))
        path = parsed.path.rstrip("/") + "/" + str(self.valves.api_path).lstrip("/")
        return urllib.parse.urlunparse(parsed._replace(path=path, query="", fragment=""))

    def _format_pages(self, pages: List[Dict[str, Any]], include_content: bool) -> str:
        if not pages:
            return "Keine Seiten gefunden."
        lines: List[str] = []
        for page in pages:
            lines.extend(
                [
                    f"## {self._text(page.get('title', 'Ohne Titel'))}",
                    f"- Page-ID: `{self._text(page.get('pageid', 'unbekannt'))}`",
                    f"- Revision-ID: `{self._text(page.get('revid', 'unbekannt'))}`",
                    f"- Timestamp: `{self._text(page.get('timestamp', 'unbekannt'))}`",
                    f"- Bytes: `{self._text(page.get('bytes', 'unbekannt'))}`",
                ]
            )
            if include_content:
                lines.extend(["", "```text", self._redact(str(page.get("content", ""))), "```"])
            lines.append("")
        return "\n".join(lines)[: int(self.valves.max_output_chars)]

    def _text(self, value: Any) -> str:
        return html.unescape(str(value)).replace("`", "'")[:500]

    def _redact(self, value: str) -> str:
        value = re.sub(r"(?i)(lgpassword|password|token|secret|api[_-]?key)=([^&\s]+)", r"\1=[REDACTED]", value)
        value = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/=-]+", r"\1[REDACTED]", value)
        return value

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})


class _MediaWikiClient:
    def __init__(self, api_url: str, timeout: int, user_agent: str, insecure_tls: bool) -> None:
        self.api_url = api_url
        self.timeout = timeout
        self.cookiejar = http.cookiejar.CookieJar()
        handlers: List[Any] = [urllib.request.HTTPCookieProcessor(self.cookiejar)]
        if insecure_tls:
            handlers.append(urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))
        self.opener = urllib.request.build_opener(*handlers)
        self.user_agent = user_agent
        self.logged_in = False

    def login_if_configured(self, username: str, password: str) -> None:
        if username or password:
            self.login(username, password)

    def login(self, username: str, password: str) -> str:
        if not username or not password:
            raise ValueError("Benutzername und Passwort sind für Login erforderlich.")
        # Modern MediaWiki token flow, available on newer old installs.
        try:
            token_data = self.api_get({"action": "query", "meta": "tokens", "type": "login"})
            token = token_data.get("query", {}).get("tokens", {}).get("logintoken")
            if token:
                result = self.api_post({"action": "login", "lgname": username, "lgpassword": password, "lgtoken": token})
                status = self._login_result(result)
                if status.lower() in {"success", "pass"}:
                    self.logged_in = True
                    return status
        except Exception:
            pass

        # Legacy MediaWiki <= 1.26 flow: first login call returns NeedToken.
        first = self.api_post({"action": "login", "lgname": username, "lgpassword": password})
        login = first.get("login", {})
        if str(login.get("result", "")).lower() in {"success", "pass"}:
            self.logged_in = True
            return str(login.get("result"))
        token = login.get("token")
        if not token:
            raise ValueError(f"Login fehlgeschlagen: {self._safe_json(first)}")
        second = self.api_post({"action": "login", "lgname": username, "lgpassword": password, "lgtoken": token})
        status = self._login_result(second)
        if status.lower() not in {"success", "pass"}:
            raise ValueError(f"Login fehlgeschlagen: {self._safe_json(second)}")
        self.logged_in = True
        return status

    def list_pages(self, namespace: int, prefix: str, limit: int) -> List[str]:
        titles: List[str] = []
        cont: Dict[str, Any] = {}
        while len(titles) < limit:
            params: Dict[str, Any] = {
                "action": "query",
                "list": "allpages",
                "apnamespace": str(namespace),
                "aplimit": str(min(50, limit - len(titles))),
            }
            if prefix:
                params["apprefix"] = prefix
            params.update(cont)
            data = self.api_get(params)
            for page in data.get("query", {}).get("allpages", []):
                title = page.get("title")
                if title:
                    titles.append(str(title))
                if len(titles) >= limit:
                    break
            cont = data.get("continue", {}) or data.get("query-continue", {}).get("allpages", {})
            if not cont:
                break
        return titles

    def fetch_pages(self, titles: List[str], include_content: bool, max_page_chars: int) -> List[Dict[str, Any]]:
        output: List[Dict[str, Any]] = []
        for chunk in self._chunks(titles, 20):
            if not chunk:
                continue
            params: Dict[str, Any] = {
                "action": "query",
                "prop": "revisions",
                "titles": "|".join(chunk),
                "rvprop": "ids|timestamp|user|size" + ("|content" if include_content else ""),
            }
            if include_content:
                params["rvslots"] = "main"
            data = self.api_get(params)
            pages = data.get("query", {}).get("pages", {})
            iterable = pages.values() if isinstance(pages, dict) else pages
            for page in iterable:
                rev = (page.get("revisions") or [{}])[0] if isinstance(page, dict) else {}
                content = self._revision_content(rev) if include_content else ""
                output.append(
                    {
                        "pageid": page.get("pageid"),
                        "title": page.get("title"),
                        "revid": rev.get("revid"),
                        "timestamp": rev.get("timestamp"),
                        "bytes": rev.get("size") or len(content),
                        "content": content[:max_page_chars],
                    }
                )
        return output

    def api_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", params)

    def api_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", params)

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        clean = {k: v for k, v in params.items() if v is not None}
        clean.setdefault("format", "json")
        encoded = urllib.parse.urlencode(clean).encode("utf-8")
        if method == "GET":
            url = self.api_url + "?" + encoded.decode("ascii")
            data = None
        else:
            url = self.api_url
            data = encoded
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json,text/javascript,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                raw = response.read(2_000_000)
        except urllib.error.HTTPError as exc:
            raw = exc.read(100_000)
            raise ValueError(f"MediaWiki HTTP {exc.code}: {raw.decode('utf-8', 'replace')[:500]}") from exc
        text = raw.decode("utf-8", "replace")
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"MediaWiki returned non-JSON response: {text[:500]}") from exc
        if isinstance(parsed, dict) and "error" in parsed:
            raise ValueError(f"MediaWiki API error: {self._safe_json(parsed['error'])}")
        return parsed if isinstance(parsed, dict) else {"result": parsed}

    def _revision_content(self, revision: Dict[str, Any]) -> str:
        if not isinstance(revision, dict):
            return ""
        slots = revision.get("slots")
        if isinstance(slots, dict):
            main = slots.get("main", {})
            if isinstance(main, dict):
                return str(main.get("content") or main.get("*") or "")
        return str(revision.get("content") or revision.get("*") or "")

    def _login_result(self, data: Dict[str, Any]) -> str:
        login = data.get("login", {}) if isinstance(data, dict) else {}
        return str(login.get("result") or data.get("result") or "Unknown")

    def _safe_json(self, data: Any) -> str:
        def scrub(value: Any) -> Any:
            if isinstance(value, dict):
                return {k: ("[REDACTED]" if str(k).lower() in SENSITIVE_KEYS else scrub(v)) for k, v in value.items()}
            if isinstance(value, list):
                return [scrub(item) for item in value]
            return value

        return json.dumps(scrub(data), ensure_ascii=False)[:1000]

    def _chunks(self, values: List[str], size: int) -> List[List[str]]:
        return [values[index : index + size] for index in range(0, len(values), size)]
