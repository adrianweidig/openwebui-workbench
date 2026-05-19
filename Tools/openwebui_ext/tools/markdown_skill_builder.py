"""
title: Markdown Skill Builder
description: Generate importable OpenWebUI Skill Markdown from safe user goals.
version: 1.0.0
license: MIT
security: Refuses abusive skill goals and produces text only. No filesystem, network or command execution.
"""

from __future__ import annotations

import re
from typing import Any

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


ABUSE_RE = re.compile(r"(?i)(phishing|credential harvest|malware|ransomware|exploit|bypass security|stealth|keylogger|spam|social engineering)")


class Tools:
    """OpenWebUI toolkit for creating safe Markdown skills."""

    class Valves(BaseModel):
        max_goal_chars: int = Field(4000, description="Maximum goal length.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def build_skill(self, goal: str, preferred_name: str = "", audience: str = "technische Nutzer", __event_emitter__: Any = None) -> str:
        """
        Build an importable OpenWebUI Skill Markdown document.
        :param goal: User goal and desired workflow.
        :param preferred_name: Optional skill slug or display name.
        :param audience: Intended users of the skill.
        """
        if len(goal) > int(self.valves.max_goal_chars):
            return "Fehler: Zielbeschreibung ist zu lang."
        if ABUSE_RE.search(goal):
            return "Fehler: Für missbräuchliche oder sicherheitsumgehende Ziele wird kein Skill erzeugt."
        await self._emit(__event_emitter__, "Erzeuge Skill-Markdown", False)
        slug = self._slug(preferred_name or goal)
        description = f"Arbeitsanweisung für {audience}: {self._sentence(goal)}"
        content = f"""---
name: {slug}
description: {description}
---

# {slug}

## Rolle
Arbeite als präziser, sicherheitsbewusster Assistent für {audience}.

## Ziel
{self._sentence(goal)}

## Arbeitsweise
- Kläre fehlende Pflichtinformationen mit maximal drei Rückfragen.
- Nutze vorhandene Nutzereingaben und lokale Quellen als primäre Grundlage.
- Trenne Fakten, Annahmen und Empfehlungen sichtbar.
- Prüfe Tool-Ergebnisse kritisch und übernimm sie nicht blind.

## Grenzen
- Keine Secrets, Tokens oder personenbezogenen Daten unnötig wiederholen.
- Keine destruktiven, nicht autorisierten oder sicherheitsumgehenden Schritte vorschlagen.
- Bei rechtlichen, medizinischen, finanziellen oder sicherheitskritischen Aussagen Review-Pflicht nennen.

## Ausgabeformat
- Kurze Zusammenfassung
- Relevante Befunde oder Schritte
- Risiken und Annahmen
- Nächste konkrete Aktion
"""
        await self._emit(__event_emitter__, "Skill-Markdown erzeugt", True)
        return content

    def _slug(self, value: str) -> str:
        value = value.lower().strip()
        value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
        return (value or "custom-skill")[:64].strip("-")

    def _sentence(self, value: str) -> str:
        text = re.sub(r"\s+", " ", value).strip()
        if not text:
            return "Strukturierte, sichere Bearbeitung des beschriebenen Nutzerziels."
        return text[:500]

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
