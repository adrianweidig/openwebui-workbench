"""
title: GitHub Repo Inspector
description: Read-only GitHub repository metadata inspection with optional token support through Valves or OpenWebUI OAuth.
version: 1.0.0
license: MIT
offline: false
security: Performs read-only GET requests to api.github.com for explicit owner/repo inputs. Tokens are optional and never returned.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")
GITHUB_API_HOST = "api.github.com"


class Tools:
    """OpenWebUI toolkit for bounded GitHub repository review."""

    citation = False

    class Valves(BaseModel):
        github_token: str = Field("", description="Optional GitHub token for higher rate limits. Never shown in output.")
        timeout_seconds: int = Field(10, description="Request timeout.")
        user_agent: str = Field("OpenWebUI-GitHubRepoInspector/1.0", description="User-Agent sent to GitHub.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def inspect_repository(self, repository: str, include_release: bool = True, __oauth_token__: Optional[dict] = None, __event_emitter__: Any = None) -> str:
        """
        Inspect a GitHub repository by owner/name and summarize metadata, license and maintenance signals.
        :param repository: Repository in owner/name format.
        :param include_release: Include latest release metadata when available.
        """
        repository = repository.strip()
        if not REPO_RE.match(repository):
            return "Fehler: Repository muss im Format `owner/name` angegeben werden."
        await self._emit(__event_emitter__, "Lese GitHub-Metadaten", False)
        token = self._token(__oauth_token__)
        try:
            repo = self._get_json(f"https://api.github.com/repos/{repository}", token)
            readme = self._get_json(f"https://api.github.com/repos/{repository}/readme", token, optional=True)
            release = self._get_json(f"https://api.github.com/repos/{repository}/releases/latest", token, optional=True) if include_release else None
        except Exception as exc:
            await self._emit(__event_emitter__, "GitHub-Analyse fehlgeschlagen", True)
            return f"Fehler: GitHub-Abfrage fehlgeschlagen: {type(exc).__name__}: {self._redact(str(exc))}"
        await self._emit(__event_emitter__, "GitHub-Analyse abgeschlossen", True)
        url = str(repo.get("html_url", f"https://github.com/{repository}"))
        if __event_emitter__:
            await __event_emitter__({"type": "citation", "data": {"source": {"name": repository, "url": url}, "document": [repo.get("description") or ""], "metadata": [{"source": url}]}})
        return self._format(repository, repo, readme, release)

    async def evaluate_tool_candidate(self, repository: str, __oauth_token__: Optional[dict] = None, __event_emitter__: Any = None) -> str:
        """
        Evaluate a public GitHub repository as an OpenWebUI tool candidate using metadata only.
        :param repository: Repository in owner/name format.
        """
        report = await self.inspect_repository(repository, include_release=True, __oauth_token__=__oauth_token__, __event_emitter__=__event_emitter__)
        guidance = [
            "",
            "## Review-Entscheidungshilfe",
            "- Vor Übernahme einzelne Tool-Dateien lokal lesen und statisch prüfen.",
            "- Nur übernehmen, wenn Lizenz, Wartungsstand, Abhängigkeiten und Sicherheitsverhalten nachvollziehbar sind.",
            "- Tools mit Shell-Ausführung, Credential-Zugriff, ungefiltertem Netzwerkzugriff oder unbeschränktem Dateizugriff ablehnen.",
        ]
        return report + "\n" + "\n".join(guidance)

    def _token(self, oauth_token: Optional[dict]) -> str:
        if oauth_token and isinstance(oauth_token, dict) and oauth_token.get("access_token"):
            return str(oauth_token["access_token"])
        return str(getattr(self.valves, "github_token", "") or "")

    def _get_json(self, url: str, token: str, optional: bool = False) -> Optional[Dict[str, Any]]:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != GITHUB_API_HOST:
            raise ValueError("Only https://api.github.com URLs are allowed.")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": self.valves.user_agent, "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=max(1, int(self.valves.timeout_seconds))) as response:
                return json.loads(response.read(256000).decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as exc:
            if optional and exc.code in {403, 404}:
                return None
            raise

    def _format(self, repository: str, repo: Dict[str, Any], readme: Optional[Dict[str, Any]], release: Optional[Dict[str, Any]]) -> str:
        license_info = repo.get("license") or {}
        pushed = repo.get("pushed_at") or "unbekannt"
        archived = bool(repo.get("archived"))
        disabled = bool(repo.get("disabled"))
        score = 0
        score += 2 if license_info.get("spdx_id") else 0
        score += 1 if readme else 0
        score += 1 if not archived and not disabled else -2
        score += 1 if repo.get("stargazers_count", 0) >= 10 else 0
        recommendation = "prüfen" if score >= 3 else "nicht ohne manuelle Detailprüfung übernehmen"
        lines = [
            "# GitHub-Repository-Analyse",
            f"- Repository: `{repository}`",
            f"- Beschreibung: {self._text(repo.get('description') or 'keine')}",
            f"- URL: {repo.get('html_url')}",
            f"- Lizenz: {license_info.get('spdx_id') or 'nicht erkannt'}",
            f"- Stars/Forks: {repo.get('stargazers_count', 0)} / {repo.get('forks_count', 0)}",
            f"- Letzte Aktivität: {pushed}",
            f"- Archiviert/Deaktiviert: {archived} / {disabled}",
            f"- README über API gefunden: {bool(readme)}",
            f"- Letztes Release: {self._text(release.get('tag_name')) if release else 'keines oder nicht abrufbar'}",
            f"- Empfehlung: {recommendation}",
        ]
        return "\n".join(lines)

    def _text(self, value: Any) -> str:
        return str(value).replace("\n", " ").strip()[:300]

    def _redact(self, value: str) -> str:
        return re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/=-]+", r"\1[REDACTED]", value)

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
