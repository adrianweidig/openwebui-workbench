"""
title: Tool Skill Overlay Planner
description: Design redundant model-specific tool and skill overlays with fallback coverage for offline OpenWebUI deployments.
version: 1.0.0
license: MIT
security: Processes supplied JSON/text only. Does not modify OpenWebUI, read files, call networks or execute commands.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Set

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Tools:
    """OpenWebUI toolkit for safe capability overlay design."""

    class Valves(BaseModel):
        max_input_chars: int = Field(220000, description="Maximum JSON/text input size.")
        minimum_redundancy: int = Field(2, description="Preferred number of independent capabilities per use case.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def build_overlay_matrix(self, models_json: str, tools_json: str, skills_json: str, use_cases_json: str, __event_emitter__: Any = None) -> str:
        """
        Build a model-to-tools/skills overlay matrix with redundancy notes.
        :param models_json: JSON array with model id/name and strengths fields.
        :param tools_json: JSON array with tool id/name, capabilities, risk, offline fields.
        :param skills_json: JSON array with skill id/name and capabilities fields.
        :param use_cases_json: JSON array with use case id/name and capabilities fields.
        """
        if sum(len(part) for part in [models_json, tools_json, skills_json, use_cases_json]) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge Overlay-Matrix", False)
        models = self._load_array(models_json, "models_json")
        tools = self._load_array(tools_json, "tools_json")
        skills = self._load_array(skills_json, "skills_json")
        use_cases = self._load_array(use_cases_json, "use_cases_json")
        for loaded in [models, tools, skills, use_cases]:
            if isinstance(loaded, str):
                return loaded
        lines = ["# Tool-/Skill-Overlay-Matrix", ""]
        for model in models:  # type: ignore[union-attr]
            if not isinstance(model, dict):
                continue
            model_name = self._name(model, "Modell")
            strengths = self._keywords(model.get("strengths", model.get("capabilities", "")))
            recommended_tools = self._rank_candidates(strengths, tools)  # type: ignore[arg-type]
            recommended_skills = self._rank_candidates(strengths, skills)  # type: ignore[arg-type]
            lines.append(f"## {model_name}")
            lines.append(f"- Tools: {self._names(recommended_tools[:8]) or 'keine eindeutige Zuordnung'}")
            lines.append(f"- Skills: {self._names(recommended_skills[:8]) or 'keine eindeutige Zuordnung'}")
            lines.append("- Regel: Native Tool Calling aktivieren; riskante Tools nur rollen-/modellbezogen freigeben.")
            lines.append("")
        lines.append("## Use-Case-Abdeckung")
        for use_case in use_cases:  # type: ignore[union-attr]
            if not isinstance(use_case, dict):
                continue
            needed = self._keywords(use_case.get("capabilities", use_case.get("needs", "")))
            candidates = self._rank_candidates(needed, list(tools) + list(skills))  # type: ignore[arg-type]
            count = len([item for item in candidates if item["score"] > 0])
            status = "ok" if count >= int(self.valves.minimum_redundancy) else "Lücke"
            lines.append(f"- {self._name(use_case, 'Use Case')}: {status}, {count} Treffer, Fallbacks: {self._names(candidates[:4]) or 'ergänzen'}")
        await self._emit(__event_emitter__, "Overlay-Matrix erzeugt", True)
        return "\n".join(lines)

    async def compare_capability_coverage(self, use_cases_json: str, capabilities_json: str, __event_emitter__: Any = None) -> str:
        """
        Compare required use cases against available capabilities.
        :param use_cases_json: JSON array with use case id/name and capabilities fields.
        :param capabilities_json: JSON array with tool/skill/model capabilities.
        """
        if len(use_cases_json) + len(capabilities_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Prüfe Capability-Abdeckung", False)
        use_cases = self._load_array(use_cases_json, "use_cases_json")
        capabilities = self._load_array(capabilities_json, "capabilities_json")
        if isinstance(use_cases, str):
            return use_cases
        if isinstance(capabilities, str):
            return capabilities
        lines = ["# Capability Coverage", ""]
        for use_case in use_cases:
            if not isinstance(use_case, dict):
                continue
            needed = self._keywords(use_case.get("capabilities", use_case.get("needs", "")))
            matched = self._rank_candidates(needed, capabilities)
            covered_keywords = set()
            for candidate in matched:
                if candidate["score"] > 0:
                    covered_keywords.update(needed.intersection(candidate["keywords"]))
            missing = sorted(needed - covered_keywords)
            lines.append(f"## {self._name(use_case, 'Use Case')}")
            lines.append(f"- Treffer: {self._names(matched[:6]) or 'keine'}")
            lines.append(f"- Fehlende Stichworte: {', '.join(missing[:20]) if missing else 'keine offensichtlichen'}")
            lines.append("")
        await self._emit(__event_emitter__, "Capability-Abdeckung geprüft", True)
        return "\n".join(lines).strip()

    async def suggest_fallback_stack(self, objective: str, candidates_json: str, __event_emitter__: Any = None) -> str:
        """
        Suggest a primary/secondary/manual fallback stack for a goal.
        :param objective: Desired task or use case.
        :param candidates_json: JSON array with tools/skills/models and capabilities/risk/offline fields.
        """
        if len(objective) + len(candidates_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge Fallback-Stack", False)
        candidates = self._load_array(candidates_json, "candidates_json")
        if isinstance(candidates, str):
            return candidates
        needed = self._keywords(objective)
        ranked = self._rank_candidates(needed, candidates)
        safe = [item for item in ranked if str(item["raw"].get("risk", "low")).lower() not in {"high", "danger", "dangerous"}]
        lines = ["# Fallback-Stack", f"- Ziel: {self._clean(objective, 500)}", ""]
        labels = ["Primär", "Sekundär", "Tertiär"]
        for label, item in zip(labels, safe[:3]):
            raw = item["raw"]
            offline = raw.get("offline", "unbekannt")
            lines.append(f"- {label}: {self._name(raw, 'Capability')} | offline: {offline} | Score: {item['score']}")
        lines.extend(["", "## Betriebsregel", "- Gleiche Use Cases mit mindestens zwei unabhängigen Werkzeugen/Skills abdecken.", "- Schreibende oder externe Werkzeuge nicht als automatischen Fallback aktivieren; bewusst pro Modell freigeben.", "- Fehlt ein Tool, soll das Modell auf Skill-Anleitung oder manuelle Checkliste zurückfallen können."])
        await self._emit(__event_emitter__, "Fallback-Stack erzeugt", True)
        return "\n".join(lines)

    def _load_array(self, text: str, label: str) -> List[Any] | str:
        try:
            data = json.loads(text or "[]")
        except json.JSONDecodeError as exc:
            return f"Fehler: {label} ist ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(data, list):
            return f"Fehler: {label} muss ein JSON-Array sein."
        return data

    def _rank_candidates(self, needed: Set[str], candidates: List[Any]) -> List[Dict[str, Any]]:
        ranked: List[Dict[str, Any]] = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            keywords = self._keywords(" ".join(str(candidate.get(key, "")) for key in ["id", "name", "title", "capabilities", "purpose", "tags", "description"]))
            score = len(needed.intersection(keywords))
            if candidate.get("offline") is True:
                score += 1
            ranked.append({"raw": candidate, "keywords": keywords, "score": score})
        return sorted(ranked, key=lambda item: (-item["score"], self._name(item["raw"], "")))

    def _keywords(self, value: Any) -> Set[str]:
        if isinstance(value, list):
            value = " ".join(str(item) for item in value)
        return {part.lower() for part in re.findall(r"[A-Za-zÄÖÜäöüß0-9_-]{3,}", str(value))}

    def _name(self, item: Dict[str, Any], fallback: str) -> str:
        return self._clean(str(item.get("name") or item.get("title") or item.get("id") or fallback), 120)

    def _names(self, ranked: List[Dict[str, Any]]) -> str:
        return ", ".join(self._name(item["raw"], "Capability") for item in ranked if item["score"] > 0)

    def _clean(self, value: str, limit: int) -> str:
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", value).strip()[:limit]

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
