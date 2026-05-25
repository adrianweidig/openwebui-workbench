"""
title: Auto Tool Selector
type: filter
description: Offline-safe inlet filter that enables relevant local OpenWebUI tools and configured MCP tool servers for the current message.
version: 1.1.0-offline.1
license: MIT
offline: true
security: Adapted from the public OpenWebUI auto-tool-selector export. This version does not call external networks or an LLM; it only updates the current request payload.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Filter:
    """OpenWebUI inlet filter for tool-first chats in offline workspaces."""

    LOCAL_TOOL_RULES: Sequence[Tuple[str, Sequence[str]]] = (
        ("ask_user", ("unklar", "ruckfrage", "rückfrage", "clarify", "missing input", "fehlende eingabe", "ambiguous", "frage den nutzer")),
        ("json_csv_text_validator", ("json", "csv", "yaml", "xml", "tabelle", "tabular", "log", "validier", "schema", "strukturierte")),
        ("air_gapped_jupyter_python", ("python", "berechne", "calculate", "analyse", "statistik", "daten", "dataframe", "plot", "transform")),
        ("repo_tree_analyzer", ("repo", "repository", "code", "diff", "review", "refactor", "test", "dateibaum", "git")),
        ("offline_artifact_workbench", ("html", "pdf", "zip", "prasentation", "praesentation", "presentation", "artefakt", "handover", "dokument")),
        ("inline_visuals_toolkit_v3", ("diagramm", "diagram", "chart", "mermaid", "svg", "dashboard", "visual", "grafik")),
        ("visuals_toolkit_v4", ("diagramm", "diagram", "chart", "mermaid", "dashboard", "visual", "ascii", "wireframe")),
        ("docker_compose_triage", ("docker", "compose", "container", "image", "volume", "openwebui fehler", "betrieb")),
        ("openapi_schema_inspector", ("openapi", "swagger", "api schema", "mcp", "schnittstelle", "toolserver")),
        ("parallel_task_planner", ("parallel", "mehrere teilaufgaben", "arbeitspaket", "plan", "abhangigkeit", "abhängigkeit", "wellen")),
        ("parallel_tools", ("parallel", "mehrere tools", "gleichzeitig", "concurrent", "tool calls", "batch")),
        ("subagent_orchestrator", ("subagent", "agent", "rolle", "delegier", "parallel agent", "mehrere rollen")),
        ("sub_agent", ("subagent", "agent", "rolle", "delegier", "parallel agent", "isoliert")),
        ("tool_skill_overlay_planner", ("skill", "tool", "modell", "overlay", "zuordnung", "fallback")),
        ("llm_council", ("council", "modellrat", "mehrere modelle", "second opinion", "unsicher", "abwagen", "abwaegen", "validieren")),
        ("comfyui_workflow_inspector", ("comfyui", "workflow", "bild", "image", "audio", "video", "node graph")),
        ("markdown_skill_builder", ("skill erstellen", "skill markdown", "openwebui skill", "skill authoring")),
        ("mediawiki_legacy_crawler", ("mediawiki", "wiki", "legacy crawler", "intranet wiki")),
        ("safe_http_fetcher", ("http", "https", "url", "website", "fetch", "head request")),
        ("github_repo_inspector", ("github", "pull request", "issue", "release", "repo url")),
        ("web_search_and_crawl", ("websuche", "web search", "crawl", "searxng", "crawl4ai", "internet")),
        ("openui_generative_ui", ("generative ui", "openui", "rich ui", "formular", "interface", "app screen")),
    )

    class Valves(BaseModel):
        priority: int = Field(50, description="Filter execution order. Lower values run before most request-shaping filters.")
        enable_local_tool_selection: bool = Field(True, description="Add matching local OpenWebUI tool IDs when they are available.")
        enable_mcp_tool_selection: bool = Field(True, description="Add matching MCP server tool IDs from OpenWebUI server connections.")
        max_selected_local_tools: int = Field(8, description="Maximum local tool IDs to add per request.")
        max_selected_mcp_servers: int = Field(6, description="Maximum MCP server tool IDs to add per request.")
        strict_available_tools_only: bool = Field(True, description="Only add local tool IDs already available on the model/request.")
        emit_status: bool = Field(True, description="Emit a short OpenWebUI status event when tools are selected.")

    def __init__(self) -> None:
        self.valves = self.Valves()
        self.toggle = True

    async def inlet(
        self,
        body: Dict[str, Any],
        __event_emitter__: Any = None,
        __request__: Any = None,
        __user__: Optional[Dict[str, Any]] = None,
        __model__: Optional[Dict[str, Any]] = None,
        __metadata__: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Select tools before OpenWebUI sends the request to the model."""
        text = self._conversation_text(body)
        if not text:
            return body

        existing_tool_ids = self._string_list(body.get("tool_ids"))
        available_local_ids = self._available_local_tool_ids(body, __model__, __metadata__)
        selected_local: List[str] = []
        if bool(self.valves.enable_local_tool_selection):
            selected_local = self._select_local_tools(text, available_local_ids)

        selected_mcp: List[str] = []
        if bool(self.valves.enable_mcp_tool_selection):
            selected_mcp = self._select_mcp_servers(text, __request__)

        merged = self._merge_unique(existing_tool_ids, selected_local, selected_mcp)
        if merged:
            body["tool_ids"] = merged

        if selected_local or selected_mcp:
            metadata = body.setdefault("metadata", {})
            if isinstance(metadata, dict):
                metadata["auto_tool_selector"] = {
                    "selected_tool_ids": selected_local,
                    "selected_mcp_tool_ids": selected_mcp,
                }
            if bool(self.valves.emit_status):
                selected = ", ".join(selected_local + selected_mcp)
                await self._emit(__event_emitter__, f"Auto Tool Selector enabled: {selected}", done=True)

        return body

    def _select_local_tools(self, text: str, available_ids: Set[str]) -> List[str]:
        normalized = self._normalize(text)
        scored: List[Tuple[int, int, str]] = []
        for index, (tool_id, keywords) in enumerate(self.LOCAL_TOOL_RULES):
            if bool(self.valves.strict_available_tools_only) and tool_id not in available_ids:
                continue
            score = sum(1 for keyword in keywords if keyword in normalized)
            if score:
                scored.append((score, index, tool_id))
        scored.sort(key=lambda item: (-item[0], item[1], item[2]))
        limit = max(0, int(self.valves.max_selected_local_tools))
        return [tool_id for _, _, tool_id in scored[:limit]]

    def _select_mcp_servers(self, text: str, request: Any) -> List[str]:
        connections = self._mcp_connections(request)
        if not connections:
            return []
        user_terms = self._terms(self._normalize(text))
        scored: List[Tuple[int, str]] = []
        for server_id, info in connections:
            descriptor = self._normalize(" ".join(self._flatten_text(info)))
            if not descriptor:
                descriptor = self._normalize(server_id)
            descriptor_terms = self._terms(descriptor)
            overlap = len(user_terms.intersection(descriptor_terms))
            explicit = 1 if self._normalize(server_id) in self._normalize(text) else 0
            score = overlap + explicit
            if score >= 2 or explicit:
                tool_id = server_id if server_id.startswith("server:mcp:") else f"server:mcp:{server_id}"
                scored.append((score, tool_id))
        scored.sort(key=lambda item: (-item[0], item[1]))
        limit = max(0, int(self.valves.max_selected_mcp_servers))
        return [tool_id for _, tool_id in scored[:limit]]

    def _available_local_tool_ids(
        self,
        body: Dict[str, Any],
        model: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> Set[str]:
        values: List[Any] = [
            body.get("tool_ids"),
            body.get("toolIds"),
            self._nested(body, ("metadata", "tool_ids")),
            self._nested(body, ("metadata", "toolIds")),
            self._nested(body, ("model", "meta", "toolIds")),
            self._nested(body, ("model", "meta", "tool_ids")),
            self._nested(model, ("meta", "toolIds")),
            self._nested(model, ("meta", "tool_ids")),
            self._nested(metadata, ("tool_ids",)),
            self._nested(metadata, ("toolIds",)),
        ]
        result: Set[str] = set()
        for value in values:
            result.update(self._string_list(value))
        if not bool(self.valves.strict_available_tools_only):
            result.update(tool_id for tool_id, _ in self.LOCAL_TOOL_RULES)
        return result

    def _mcp_connections(self, request: Any) -> List[Tuple[str, Any]]:
        config = self._nested(request, ("app", "state", "config"))
        connections = self._nested(config, ("TOOL_SERVER_CONNECTIONS",))
        if connections is None:
            connections = self._nested(config, ("tool_server_connections",))
        if isinstance(connections, dict):
            return [(str(key), value) for key, value in connections.items()]
        if isinstance(connections, list):
            output: List[Tuple[str, Any]] = []
            for item in connections:
                if isinstance(item, dict):
                    server_id = item.get("id") or item.get("server_id") or item.get("name")
                    if server_id:
                        output.append((str(server_id), item))
            return output
        return []

    def _conversation_text(self, body: Dict[str, Any]) -> str:
        messages = body.get("messages")
        if not isinstance(messages, list):
            return ""
        chunks: List[str] = []
        for message in messages[-6:]:
            if isinstance(message, dict):
                chunks.extend(self._flatten_text(message.get("content")))
        return "\n".join(chunk for chunk in chunks if chunk)

    def _flatten_text(self, value: Any) -> Iterable[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            chunks: List[str] = []
            for item in value.values():
                chunks.extend(self._flatten_text(item))
            return chunks
        if isinstance(value, list):
            chunks = []
            for item in value:
                chunks.extend(self._flatten_text(item))
            return chunks
        return [str(value)]

    def _normalize(self, text: str) -> str:
        text = text.replace("ß", "ss")
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"\s+", " ", text.lower()).strip()

    def _terms(self, text: str) -> Set[str]:
        return {term for term in re.findall(r"[a-z0-9_:-]{4,}", text) if term not in {"tool", "tools", "server", "openwebui"}}

    def _string_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value else []
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value if item]
        return []

    def _nested(self, value: Any, path: Sequence[str]) -> Any:
        current = value
        for part in path:
            if current is None:
                return None
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part, None)
        return current

    def _merge_unique(self, *groups: Sequence[str]) -> List[str]:
        seen: Set[str] = set()
        merged: List[str] = []
        for group in groups:
            for item in group:
                if item and item not in seen:
                    seen.add(item)
                    merged.append(item)
        return merged

    async def _emit(self, event_emitter: Any, description: str, done: bool) -> None:
        if event_emitter is None:
            return
        await event_emitter(
            {
                "type": "status",
                "data": {
                    "status": "complete" if done else "in_progress",
                    "level": "info",
                    "description": description,
                    "done": done,
                },
            }
        )
