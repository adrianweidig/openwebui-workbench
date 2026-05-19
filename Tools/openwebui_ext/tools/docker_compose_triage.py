"""
title: Docker Compose Triage
description: Analyze pasted Docker Compose files and Docker/OpenWebUI error text without running containers.
version: 1.0.0
license: MIT
security: Text-only analysis. No container, shell, filesystem or network operations are performed.
"""

from __future__ import annotations

import re
from typing import Any, List

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


SECRET_RE = re.compile(r"(?i)(password|token|secret|api[_-]?key|authorization|cookie)")


class Tools:
    """OpenWebUI toolkit for Docker and Compose text triage."""

    class Valves(BaseModel):
        max_input_chars: int = Field(120000, description="Maximum compose or log text length.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def analyze_compose(self, compose_text: str, __event_emitter__: Any = None) -> str:
        """
        Analyze pasted Docker Compose content and flag likely deployment issues.
        :param compose_text: Compose YAML text supplied by the user.
        """
        if len(compose_text) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Analysiere Compose-Text", False)
        lines = compose_text.splitlines()
        findings: List[str] = []
        if not any("services:" in line for line in lines):
            findings.append("Keine `services:`-Sektion erkannt.")
        if "open-webui" in compose_text.lower() or "openwebui" in compose_text.lower():
            findings.append("OpenWebUI-Bezug erkannt; prüfe Port `8080` im Container und persistentes Volume `/app/backend/data`.")
        if re.search(r"(?m)^\s*network_mode:\s*host\s*$", compose_text):
            findings.append("`network_mode: host` reduziert Isolation; nur bewusst nutzen.")
        if re.search(r"(?m)^\s*privileged:\s*true\s*$", compose_text):
            findings.append("`privileged: true` ist riskant und für OpenWebUI normalerweise nicht erforderlich.")
        if SECRET_RE.search(compose_text):
            findings.append("Potentielle Secrets in Environment- oder Logtext erkannt; Werte nicht in Tickets oder Modellantworten wiederholen.")
        if not re.search(r"(?m)^\s*volumes:\s*$", compose_text):
            findings.append("Keine globale oder servicebezogene Volume-Sektion erkannt; persistente OpenWebUI-Daten könnten fehlen.")
        ports = re.findall(r"['\"]?(\d{2,5}):(\d{2,5})['\"]?", compose_text)
        duplicate_hosts = sorted({host for host, _ in ports if sum(1 for h, _ in ports if h == host) > 1})
        if duplicate_hosts:
            findings.append(f"Doppelte Host-Ports erkannt: {', '.join(duplicate_hosts)}.")
        await self._emit(__event_emitter__, "Compose-Analyse abgeschlossen", True)
        return "\n".join([
            "# Docker-Compose-Triage",
            f"- Zeilen: {len(lines)}",
            f"- Port-Mappings erkannt: {len(ports)}",
            "",
            "## Befunde",
            *(f"- {finding}" for finding in findings or ["Keine offensichtlichen Probleme erkannt."]),
            "",
            "## Sichere nächste Schritte",
            "- Konfiguration lokal mit `docker compose config` validieren.",
            "- Secrets über `.env`, Docker Secrets oder sichere Orchestrator-Konfiguration bereitstellen.",
            "- OpenWebUI-Datenvolume vor Änderungen sichern.",
        ])

    async def analyze_error_text(self, error_text: str, __event_emitter__: Any = None) -> str:
        """
        Analyze Docker or OpenWebUI error text and propose non-destructive checks.
        :param error_text: Error or log text supplied by the user.
        """
        if len(error_text) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Analysiere Fehlertext", False)
        text = error_text.lower()
        findings = []
        if "port is already allocated" in text or "bind: address already in use" in text:
            findings.append("Portkonflikt: Host-Port ändern oder belegenden Dienst identifizieren.")
        if "permission denied" in text:
            findings.append("Berechtigungsproblem: Volume-Rechte und Container-User prüfen.")
        if "connection refused" in text:
            findings.append("Verbindungsfehler: Zielcontainer, internes Netzwerk und Healthchecks prüfen.")
        if "no space left" in text:
            findings.append("Speicherplatzproblem: Docker-Volumes, Images und Host-Dateisystem prüfen.")
        if SECRET_RE.search(error_text):
            findings.append("Der Fehlertext enthält potentielle Secrets; vor Weitergabe redigieren.")
        await self._emit(__event_emitter__, "Fehleranalyse abgeschlossen", True)
        return "\n".join(["# Docker-/OpenWebUI-Fehleranalyse", "", "## Befunde", *(f"- {item}" for item in findings or ["Kein bekannter Fehlerindikator erkannt."])])

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
