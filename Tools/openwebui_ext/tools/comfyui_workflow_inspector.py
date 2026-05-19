"""
title: ComfyUI Workflow Inspector Offline
description: Inspect ComfyUI workflow JSON locally and create offline setup checklists for visual, audio and video tools.
version: 1.0.0
license: MIT
security: Processes supplied workflow JSON only. Does not connect to ComfyUI, read files, call networks or execute commands.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Dict, List

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Tools:
    """OpenWebUI toolkit for offline ComfyUI workflow review."""

    class Valves(BaseModel):
        max_input_chars: int = Field(500000, description="Maximum workflow JSON size.")
        max_nodes_reported: int = Field(80, description="Maximum nodes listed in the report.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def inspect_workflow(self, workflow_json: str, __event_emitter__: Any = None) -> str:
        """
        Inspect ComfyUI API workflow JSON without executing it.
        :param workflow_json: ComfyUI workflow JSON as exported for API usage.
        """
        if len(workflow_json) > int(self.valves.max_input_chars):
            return "Fehler: Workflow-JSON ist zu groß."
        await self._emit(__event_emitter__, "Analysiere ComfyUI-Workflow", False)
        try:
            workflow = json.loads(workflow_json)
        except json.JSONDecodeError as exc:
            return f"Fehler: Ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        nodes = self._nodes(workflow)
        if not nodes:
            return "Fehler: Keine ComfyUI-Knoten erkannt. Erwartet wird API-Workflow-JSON mit Knotenobjekten."
        classes = Counter(str(node.get("class_type", "Unknown")) for node in nodes)
        models = sorted(self._find_model_refs(nodes))
        inputs = [node for node in nodes if re.search(r"(?i)(load|image|audio|video|text|prompt)", str(node.get("class_type", "")))]
        outputs = [node for node in nodes if re.search(r"(?i)(save|preview|output|combine|vhs)", str(node.get("class_type", "")))]
        lines = ["# ComfyUI Workflow Inspection", f"- Knoten: {len(nodes)}", f"- Knotentypen: {len(classes)}", ""]
        lines.append("## Häufige Knotentypen")
        lines.extend(f"- {name}: {count}" for name, count in classes.most_common(20))
        lines.append("")
        lines.append("## Modell-/Dateireferenzen")
        lines.extend(f"- `{item}`" for item in models[:50])
        if not models:
            lines.append("- keine offensichtlichen Modellnamen erkannt")
        lines.append("")
        lines.append("## Eingabe-/Ausgabe-Kandidaten")
        lines.extend(f"- Input `{node.get('id')}`: {node.get('class_type')}" for node in inputs[: int(self.valves.max_nodes_reported)])
        lines.extend(f"- Output `{node.get('id')}`: {node.get('class_type')}" for node in outputs[: int(self.valves.max_nodes_reported)])
        lines.append("")
        lines.extend(self._risk_notes(nodes))
        await self._emit(__event_emitter__, "ComfyUI-Workflow analysiert", True)
        return "\n".join(lines)

    async def build_setup_checklist(self, workflow_type: str, required_models_json: str = "[]", required_nodes_json: str = "[]", __event_emitter__: Any = None) -> str:
        """
        Build an offline setup checklist for a ComfyUI-backed OpenWebUI tool.
        :param workflow_type: Visual/audio/video workflow category.
        :param required_models_json: JSON array of model/checkpoint filenames.
        :param required_nodes_json: JSON array of required custom node names.
        """
        if len(required_models_json) + len(required_nodes_json) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Erzeuge ComfyUI-Setup-Checkliste", False)
        models = self._load_array(required_models_json, "required_models_json")
        nodes = self._load_array(required_nodes_json, "required_nodes_json")
        if isinstance(models, str):
            return models
        if isinstance(nodes, str):
            return nodes
        lines = ["# ComfyUI Offline-Setup", f"- Workflow-Typ: {self._clean(workflow_type, 80)}", ""]
        lines.append("## Vor dem Import")
        lines.append("- ComfyUI in der Offline-Umgebung starten und nur lokal erreichbar machen.")
        lines.append("- OpenWebUI-Tool-Valves auf die lokale ComfyUI-URL setzen, keine Secrets in Dateien speichern.")
        lines.append("- Workflow als API-JSON exportieren und mit `inspect_workflow` prüfen.")
        lines.append("")
        lines.append("## Modelle")
        lines.extend(f"- `{self._clean(str(item), 160)}` bereitstellen" for item in models[:80])
        if not models:
            lines.append("- konkrete Modell-/Checkpointliste ergänzen")
        lines.append("")
        lines.append("## Custom Nodes")
        lines.extend(f"- `{self._clean(str(item), 160)}` offline installieren/prüfen" for item in nodes[:80])
        if not nodes:
            lines.append("- Custom-Node-Liste aus Workflow-Inspection ergänzen")
        lines.append("")
        lines.append("## Fallback")
        lines.append("- Wenn ComfyUI nicht verfügbar ist: Inline Visuals Toolkit V3 für SVG/Mermaid/HTML nutzen.")
        lines.append("- Wenn Mediengenerierung blockiert: Prompt, Parameter und erwartete Assets als reproduzierbare Checkliste ausgeben.")
        await self._emit(__event_emitter__, "ComfyUI-Setup-Checkliste erzeugt", True)
        return "\n".join(lines)

    def _nodes(self, workflow: Any) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        if isinstance(workflow, dict):
            for key, value in workflow.items():
                if isinstance(value, dict) and ("class_type" in value or "inputs" in value):
                    item = dict(value)
                    item["id"] = key
                    nodes.append(item)
                elif key == "nodes" and isinstance(value, list):
                    for node in value:
                        if isinstance(node, dict):
                            nodes.append(node)
        elif isinstance(workflow, list):
            nodes = [node for node in workflow if isinstance(node, dict)]
        return nodes

    def _find_model_refs(self, nodes: List[Dict[str, Any]]) -> set[str]:
        found: set[str] = set()
        for node in nodes:
            inputs = node.get("inputs", {})
            if not isinstance(inputs, dict):
                continue
            for key, value in inputs.items():
                if re.search(r"(?i)(model|ckpt|vae|lora|clip|unet|checkpoint|audio|video|image)", str(key)) and isinstance(value, str):
                    found.add(value[:180])
        return found

    def _risk_notes(self, nodes: List[Dict[str, Any]]) -> List[str]:
        labels = " ".join(str(node.get("class_type", "")) for node in nodes)
        lines = ["## Prüfpunkte"]
        if re.search(r"(?i)(loadimage|load audio|load video|path|upload)", labels):
            lines.append("- Eingabedateien und Pfade vor Ausführung im OpenWebUI-Volume begrenzen.")
        if re.search(r"(?i)(save|output)", labels):
            lines.append("- Ausgabeordner und Dateinamen prüfen; keine freien absoluten Pfade erlauben.")
        lines.append("- Lange Video-/Audio-Workflows mit Timeout und separatem Modellprofil betreiben.")
        return lines

    def _load_array(self, text: str, label: str) -> List[Any] | str:
        try:
            data = json.loads(text or "[]")
        except json.JSONDecodeError as exc:
            return f"Fehler: {label} ist ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(data, list):
            return f"Fehler: {label} muss ein JSON-Array sein."
        return data

    def _clean(self, value: str, limit: int) -> str:
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", value).strip()[:limit]

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
