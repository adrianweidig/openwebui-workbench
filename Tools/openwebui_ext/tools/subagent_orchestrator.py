"""
title: Subagent Orchestrator
description: Build OpenWebUI-ready subagent rosters, delegation prompts and result merges for agentic offline workflows.
version: 1.0.0
license: MIT
offline: true
security: Processes supplied JSON/text only. It does not call models, tools, networks, files or shell commands.
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


DEFAULT_PROFILES = [
    {"name": "Recherche-Subagent", "capabilities": ["research", "web", "quellen", "internet"], "tools": ["internet_research_tool", "safe_http_fetcher"]},
    {"name": "Code-Subagent", "capabilities": ["code", "tests", "debugging", "refactoring"], "tools": ["air_gapped_jupyter_python", "repo_tree_analyzer"]},
    {"name": "Daten-Subagent", "capabilities": ["csv", "json", "daten", "analyse", "tabellen"], "tools": ["json_csv_text_validator", "air_gapped_jupyter_python"]},
    {"name": "Artefakt-Subagent", "capabilities": ["html", "pdf", "zip", "presentation", "diagramm"], "tools": ["offline_artifact_workbench", "inline_visuals_toolkit_v3"]},
    {"name": "Review-Subagent", "capabilities": ["review", "risiko", "sicherheit", "qa"], "tools": ["tool_skill_overlay_planner", "parallel_task_planner"]},
]


class Tools:
    """OpenWebUI toolkit for explicit subagent planning and prompt handoff."""

    class Valves(BaseModel):
        max_input_chars: int = Field(180000, description="Maximum JSON/text input size.")
        max_workstreams: int = Field(30, description="Maximum delegated workstreams.")
        default_timeout_minutes: int = Field(20, description="Suggested timeout for one subagent task.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def build_subagent_roster(self, available_models_json: str = "[]", available_tools_json: str = "[]", __event_emitter__: Any = None) -> str:
        """
        Build a practical subagent roster from available model and tool metadata.
        :param available_models_json: Optional JSON array with model id/name/capabilities fields.
        :param available_tools_json: Optional JSON array with tool id/name/purpose fields.
        """
        if len(available_models_json) + len(available_tools_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge Subagent-Roster", False)
        models = self._load_array(available_models_json, "available_models_json")
        tools = self._load_array(available_tools_json, "available_tools_json")
        if isinstance(models, str):
            return models
        if isinstance(tools, str):
            return tools
        tool_ids = {str(item.get("id") or item.get("name") or "") for item in tools if isinstance(item, dict)}
        lines = ["# Subagent-Roster", ""]
        for profile in DEFAULT_PROFILES:
            best_model = self._best_model(profile["capabilities"], models)
            usable_tools = [tool for tool in profile["tools"] if not tool_ids or tool in tool_ids]
            lines.append(f"## {profile['name']}")
            lines.append(f"- Modell: {best_model}")
            lines.append(f"- Fähigkeiten: {', '.join(profile['capabilities'])}")
            lines.append(f"- Tools: {', '.join(usable_tools) if usable_tools else 'nach Modellprofil'}")
            lines.append(f"- Timeout: {int(self.valves.default_timeout_minutes)} Minuten")
            lines.append("")
        await self._emit(__event_emitter__, "Subagent-Roster erzeugt", True)
        return "\n".join(lines).strip()

    async def build_subagent_jobs(self, goal: str, workstreams_json: str, subagent_profiles_json: str = "[]", __event_emitter__: Any = None) -> str:
        """
        Convert workstreams into OpenWebUI-ready subagent job cards.
        :param goal: Overall objective.
        :param workstreams_json: JSON array with title, task, context, capabilities, deliverable and dependencies fields.
        :param subagent_profiles_json: Optional JSON array with name, capabilities and tools fields.
        """
        if len(goal) + len(workstreams_json) + len(subagent_profiles_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge Subagent-Arbeitspakete", False)
        streams = self._load_array(workstreams_json, "workstreams_json")
        profiles = self._load_array(subagent_profiles_json, "subagent_profiles_json") if subagent_profiles_json.strip() else DEFAULT_PROFILES
        if isinstance(streams, str):
            return streams
        if isinstance(profiles, str):
            return profiles
        lines = ["# Subagent-Arbeitspakete", f"- Gesamtziel: {self._clean(goal, 500)}", ""]
        for index, stream in enumerate(streams[: int(self.valves.max_workstreams)], 1):
            item = stream if isinstance(stream, dict) else {"title": str(stream), "task": str(stream)}
            needed = self._keywords(item.get("capabilities", item.get("skills", "")))
            profile = self._best_profile(needed, profiles)
            title = self._clean(str(item.get("title") or item.get("task") or f"Arbeitspaket {index}"), 140)
            task = self._clean(str(item.get("task") or item.get("description") or title), 1200)
            context = self._clean(str(item.get("context") or ""), 1200)
            deliverable = self._clean(str(item.get("deliverable") or "kurzes Ergebnis mit Quellen, Annahmen, Risiken und nächsten Schritten"), 300)
            dependencies = self._join_list(item.get("dependencies", item.get("depends_on", [])))
            lines.append(f"## Job {index}: {title}")
            lines.append(f"- Subagent: {profile['name']}")
            lines.append(f"- Empfohlene Tools: {', '.join(profile['tools']) if profile['tools'] else 'modellabhängig'}")
            if dependencies:
                lines.append(f"- Abhängigkeiten: {dependencies}")
            lines.append("- Prompt:")
            lines.append("```text")
            lines.append(self._prompt(goal, profile["name"], task, context, deliverable))
            lines.append("```")
            lines.append("")
        await self._emit(__event_emitter__, "Subagent-Arbeitspakete erzeugt", True)
        return "\n".join(lines).strip()

    async def merge_subagent_results(self, results_json: str, __event_emitter__: Any = None) -> str:
        """
        Merge subagent outputs into a single decision-ready handover.
        :param results_json: JSON array with agent, status, answer, sources, artifacts, risks and next_steps fields.
        """
        if len(results_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Konsolidiere Subagent-Ergebnisse", False)
        results = self._load_array(results_json, "results_json")
        if isinstance(results, str):
            return results
        lines = ["# Konsolidiertes Subagent-Ergebnis", ""]
        lines.append("## Kurzstand")
        for item in results[: int(self.valves.max_workstreams)]:
            if not isinstance(item, dict):
                lines.append(f"- {self._clean(str(item), 300)}")
                continue
            agent = self._clean(str(item.get("agent") or item.get("source") or "Subagent"), 100)
            status = self._clean(str(item.get("status") or "unknown"), 40)
            answer = self._clean(str(item.get("answer") or item.get("summary") or ""), 700)
            lines.append(f"- `{agent}` [{status}]: {answer}")
        lines.append("")
        lines.append("## Quellen und Artefakte")
        for item in results[: int(self.valves.max_workstreams)]:
            if isinstance(item, dict):
                agent = self._clean(str(item.get("agent") or item.get("source") or "Subagent"), 100)
                sources = self._join_list(item.get("sources", []))
                artifacts = self._join_list(item.get("artifacts", item.get("files", [])))
                if sources or artifacts:
                    lines.append(f"- `{agent}` Quellen: {sources or '-'} | Artefakte: {artifacts or '-'}")
        lines.append("")
        lines.append("## Risiken und nächste Schritte")
        for item in results[: int(self.valves.max_workstreams)]:
            if isinstance(item, dict):
                risks = self._join_list(item.get("risks", []))
                next_steps = self._join_list(item.get("next_steps", []))
                if risks or next_steps:
                    agent = self._clean(str(item.get("agent") or item.get("source") or "Subagent"), 100)
                    lines.append(f"- `{agent}` Risiken: {risks or '-'} | Nächste Schritte: {next_steps or '-'}")
        await self._emit(__event_emitter__, "Subagent-Ergebnisse konsolidiert", True)
        return "\n".join(lines).strip()

    def _prompt(self, goal: str, agent_name: str, task: str, context: str, deliverable: str) -> str:
        parts = [
            f"Du bist {agent_name} in einem OpenWebUI-Subagent-Workflow.",
            f"Gesamtziel: {self._clean(goal, 800)}",
            f"Deine Aufgabe: {task}",
        ]
        if context:
            parts.append(f"Kontext: {context}")
        parts.extend(
            [
                f"Erwartetes Ergebnis: {deliverable}",
                "Arbeite unabhängig, nutze passende freigegebene Tools, kennzeichne Annahmen und nenne Quellen oder Artefakte.",
                "Gib am Ende ein kurzes JSON-nahes Handover mit status, summary, sources, artifacts, risks und next_steps aus.",
            ]
        )
        return "\n".join(parts)

    def _best_profile(self, needed: Set[str], profiles: List[Any]) -> Dict[str, Any]:
        normalized = [item for item in profiles if isinstance(item, dict)] or DEFAULT_PROFILES
        best = normalized[0]
        best_score = -1
        for profile in normalized:
            caps = self._keywords(profile.get("capabilities", profile.get("skills", "")))
            score = len(needed.intersection(caps))
            if score > best_score:
                best = profile
                best_score = score
        return {
            "name": self._clean(str(best.get("name") or best.get("model") or "Standard-Subagent"), 100),
            "tools": [self._clean(str(tool), 80) for tool in best.get("tools", []) if str(tool).strip()] if isinstance(best.get("tools", []), list) else [],
        }

    def _best_model(self, capabilities: List[str], models: List[Any]) -> str:
        if not models:
            return "passendes importiertes Aufgabenmodell"
        needed = self._keywords(capabilities)
        best_name, best_score = "passendes importiertes Aufgabenmodell", -1
        for model in models:
            if not isinstance(model, dict):
                continue
            haystack = " ".join(str(model.get(key, "")) for key in ["id", "name", "description", "capabilities", "tags"])
            score = len(needed.intersection(self._keywords(haystack)))
            if score > best_score:
                best_name = self._clean(str(model.get("name") or model.get("id") or best_name), 100)
                best_score = score
        return best_name

    def _load_array(self, text: str, label: str) -> List[Any] | str:
        try:
            data = json.loads(text or "[]")
        except json.JSONDecodeError as exc:
            return f"Fehler: {label} ist ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(data, list):
            return f"Fehler: {label} muss ein JSON-Array sein."
        return data

    def _keywords(self, value: Any) -> Set[str]:
        if isinstance(value, list):
            value = " ".join(str(item) for item in value)
        return {part.lower() for part in re.findall(r"[A-Za-zÄÖÜäöüß0-9_-]{3,}", str(value))}

    def _join_list(self, value: Any) -> str:
        if isinstance(value, str):
            value = [part.strip() for part in value.split(",") if part.strip()]
        if not isinstance(value, list):
            value = [value] if value else []
        return ", ".join(self._clean(str(item), 140) for item in value if str(item).strip())

    def _clean(self, value: str, limit: int) -> str:
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", value).strip()[:limit]

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
