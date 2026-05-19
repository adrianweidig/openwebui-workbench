"""
title: Offline Parallel Task Planner
description: Split work into dependency-safe parallel waves and subagent assignments without executing external tools.
version: 1.0.0
license: MIT
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


class Tools:
    """OpenWebUI toolkit for conservative parallel-work planning."""

    class Valves(BaseModel):
        max_input_chars: int = Field(180000, description="Maximum JSON/text input size.")
        max_tasks: int = Field(120, description="Maximum tasks per plan.")
        default_timeout_minutes: int = Field(20, description="Default timeout for a delegated task.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def build_parallel_execution_plan(self, goal: str, tasks_json: str, __event_emitter__: Any = None) -> str:
        """
        Build dependency-safe execution waves from task JSON.
        :param goal: Overall objective.
        :param tasks_json: JSON array with id, title, depends_on, tool, subagent, risk fields.
        """
        if len(tasks_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Berechne parallele Ausführungswellen", False)
        try:
            tasks = self._parse_tasks(tasks_json)
            waves = self._waves(tasks)
        except ValueError as exc:
            return f"Fehler: {exc}"
        lines = ["# Parallelplan", f"- Ziel: {self._clean(goal, 500)}", f"- Aufgaben: {len(tasks)}", f"- Wellen: {len(waves)}", ""]
        for wave_index, wave in enumerate(waves, 1):
            lines.append(f"## Welle {wave_index}")
            for task_id in wave:
                task = tasks[task_id]
                actor = task.get("subagent") or task.get("tool") or "Hauptmodell"
                risk = task.get("risk") or "normal"
                lines.append(f"- `{task_id}` {task['title']} | Akteur: {actor} | Risiko: {risk}")
            lines.append("")
        lines.extend(self._safety_notes(tasks))
        await self._emit(__event_emitter__, "Parallelplan erzeugt", True)
        return "\n".join(lines).strip()

    async def split_for_subagents(self, goal: str, workstreams_json: str, subagent_profiles_json: str = "[]", __event_emitter__: Any = None) -> str:
        """
        Assign workstreams to subagent profiles by declared capability keywords.
        :param goal: Overall objective.
        :param workstreams_json: JSON array with title, capabilities and deliverable fields.
        :param subagent_profiles_json: JSON array with name, capabilities, tools and limits fields.
        """
        if len(workstreams_json) + len(subagent_profiles_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Ordne Subagenten zu", False)
        streams = self._load_array(workstreams_json, "workstreams_json")
        profiles = self._load_array(subagent_profiles_json, "subagent_profiles_json") if subagent_profiles_json.strip() else []
        if isinstance(streams, str):
            return streams
        if isinstance(profiles, str):
            return profiles
        lines = ["# Subagent-Aufteilung", f"- Ziel: {self._clean(goal, 500)}", ""]
        for index, stream in enumerate(streams[: int(self.valves.max_tasks)], 1):
            needed = self._keywords(stream.get("capabilities", stream.get("skills", "")) if isinstance(stream, dict) else "")
            best = self._best_profile(needed, profiles)
            title = self._clean(str(stream.get("title") or f"Arbeitsstrom {index}") if isinstance(stream, dict) else str(stream), 120)
            deliverable = self._clean(str(stream.get("deliverable") or "kurzes Ergebnis mit Annahmen und offenen Punkten") if isinstance(stream, dict) else "kurzes Ergebnis", 220)
            lines.append(f"## {title}")
            lines.append(f"- Subagent/Modell: {best}")
            lines.append(f"- Ergebnis: {deliverable}")
            lines.append(f"- Timeout: {int(self.valves.default_timeout_minutes)} Minuten")
            lines.append("- Regel: nur unabhängige Arbeit parallelisieren; abhängige Aufgaben in spätere Wellen legen.")
            lines.append("")
        await self._emit(__event_emitter__, "Subagent-Aufteilung erzeugt", True)
        return "\n".join(lines).strip()

    async def merge_parallel_results(self, results_json: str, __event_emitter__: Any = None) -> str:
        """
        Merge parallel worker/subagent result summaries into one handover.
        :param results_json: JSON array with source, status, summary, changed_files, risks and next_steps fields.
        """
        if len(results_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Konsolidiere parallele Ergebnisse", False)
        results = self._load_array(results_json, "results_json")
        if isinstance(results, str):
            return results
        lines = ["# Konsolidiertes Ergebnis", ""]
        statuses: Dict[str, int] = {}
        for item in results[: int(self.valves.max_tasks)]:
            status = self._clean(str(item.get("status", "unknown")) if isinstance(item, dict) else "unknown", 30)
            statuses[status] = statuses.get(status, 0) + 1
        lines.append("## Status")
        lines.extend(f"- {key}: {value}" for key, value in sorted(statuses.items()))
        lines.append("")
        lines.append("## Beiträge")
        for item in results[: int(self.valves.max_tasks)]:
            if not isinstance(item, dict):
                lines.append(f"- {self._clean(str(item), 240)}")
                continue
            source = self._clean(str(item.get("source") or item.get("agent") or "Quelle"), 80)
            summary = self._clean(str(item.get("summary") or item.get("result") or ""), 500)
            risks = self._join_list(item.get("risks", []))
            files = self._join_list(item.get("changed_files", []))
            lines.append(f"- `{source}`: {summary}")
            if files:
                lines.append(f"  Dateien: {files}")
            if risks:
                lines.append(f"  Risiken: {risks}")
        await self._emit(__event_emitter__, "Ergebnisse konsolidiert", True)
        return "\n".join(lines)

    def _parse_tasks(self, text: str) -> Dict[str, Dict[str, Any]]:
        raw = self._load_array(text, "tasks_json")
        if isinstance(raw, str):
            raise ValueError(raw.replace("Fehler: ", "", 1))
        tasks: Dict[str, Dict[str, Any]] = {}
        for index, item in enumerate(raw[: int(self.valves.max_tasks)], 1):
            if not isinstance(item, dict):
                item = {"title": str(item)}
            task_id = self._task_id(str(item.get("id") or f"task-{index}"))
            depends = item.get("depends_on", item.get("dependencies", []))
            if isinstance(depends, str):
                depends = [part.strip() for part in depends.split(",") if part.strip()]
            if not isinstance(depends, list):
                depends = []
            tasks[task_id] = {
                "id": task_id,
                "title": self._clean(str(item.get("title") or item.get("task") or task_id), 160),
                "depends_on": [self._task_id(str(dep)) for dep in depends],
                "tool": self._clean(str(item.get("tool") or ""), 80),
                "subagent": self._clean(str(item.get("subagent") or item.get("agent") or ""), 80),
                "risk": self._clean(str(item.get("risk") or ""), 40),
            }
        unknown = sorted({dep for task in tasks.values() for dep in task["depends_on"] if dep not in tasks})
        if unknown:
            raise ValueError(f"Unbekannte Abhängigkeiten: {', '.join(unknown)}")
        return tasks

    def _waves(self, tasks: Dict[str, Dict[str, Any]]) -> List[List[str]]:
        pending: Set[str] = set(tasks)
        done: Set[str] = set()
        waves: List[List[str]] = []
        while pending:
            ready = sorted(task_id for task_id in pending if set(tasks[task_id]["depends_on"]).issubset(done))
            if not ready:
                cycle = ", ".join(sorted(pending))
                raise ValueError(f"Zyklische oder blockierende Abhängigkeiten erkannt: {cycle}")
            waves.append(ready)
            done.update(ready)
            pending.difference_update(ready)
        return waves

    def _safety_notes(self, tasks: Dict[str, Dict[str, Any]]) -> List[str]:
        stateful = [task["id"] for task in tasks.values() if re.search(r"(?i)(write|delete|deploy|commit|push|datei|shell|docker)", task.get("tool", "") + " " + task["title"])]
        lines = ["## Sicherheitsregeln", "- Gemeinsame Schreibziele nicht parallel ausführen.", "- Netzwerk-, Shell- und Dateischreib-Tools mit Timeout und klarem Besitzer ausführen."]
        if stateful:
            lines.append(f"- Sequenziell prüfen wegen möglichem Zustand/Schreibzugriff: {', '.join(stateful)}")
        return lines

    def _load_array(self, text: str, label: str) -> List[Any] | str:
        try:
            data = json.loads(text or "[]")
        except json.JSONDecodeError as exc:
            return f"Fehler: {label} ist ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(data, list):
            return f"Fehler: {label} muss ein JSON-Array sein."
        return data

    def _best_profile(self, needed: Set[str], profiles: List[Any]) -> str:
        best_name, best_score = "Standard-Subagent", -1
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            caps = self._keywords(profile.get("capabilities", profile.get("skills", "")))
            score = len(needed.intersection(caps))
            if score > best_score:
                best_name = self._clean(str(profile.get("name") or profile.get("model") or "Subagent"), 80)
                best_score = score
        return best_name

    def _keywords(self, value: Any) -> Set[str]:
        if isinstance(value, list):
            value = " ".join(str(item) for item in value)
        return {part.lower() for part in re.findall(r"[A-Za-zÄÖÜäöüß0-9_-]{3,}", str(value))}

    def _task_id(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")[:60] or "task"

    def _join_list(self, value: Any) -> str:
        if not isinstance(value, list):
            value = [value] if value else []
        return ", ".join(self._clean(str(item), 120) for item in value if str(item).strip())

    def _clean(self, value: str, limit: int) -> str:
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", value).strip()[:limit]

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
