"""
title: Workbench Required File Context Filter
type: filter
description: Injects Workbench model required files as protected full-context system block and attaches their OpenWebUI file IDs to every request.
version: 1.0.0
license: MIT
security: Offline-only filter. It does not call networks, execute tools, call an LLM or read files at request time.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Filter:
    """OpenWebUI filter that injects required Workbench model files."""

    REQUIRED_CONTEXT_MARKER = "## Workbench-Pflichtdateien"

    class Valves(BaseModel):
        priority: int = Field(850, description="Filter execution order. Must run before context compression.")
        emit_status: bool = Field(True, description="Emit a short warning status when model metadata is missing.")

    def __init__(self) -> None:
        self.valves = self.Valves()
        self.toggle = False

    async def inlet(
        self,
        body: Dict[str, Any],
        __event_emitter__: Any = None,
        __user__: Optional[Dict[str, Any]] = None,
        __model__: Optional[Dict[str, Any]] = None,
        __metadata__: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        meta = self._model_meta(body, __model__, __metadata__)
        file_context = meta.get("workbenchFileContext") if isinstance(meta, dict) else None
        if not isinstance(file_context, dict):
            self._write_debug(body, "missing workbenchFileContext metadata")
            await self._emit(__event_emitter__, "Workbench-Pflichtdateien nicht injiziert: Modell-Metadaten fehlen.")
            return body

        required_files = file_context.get("requiredFiles")
        if not isinstance(required_files, list) or not required_files:
            self._write_debug(body, "workbenchFileContext.requiredFiles empty")
            return body

        self._attach_uploaded_files(body, file_context.get("uploadedFiles"))
        context_block = self._required_context_block(required_files)
        if not context_block:
            self._write_debug(body, "requiredFiles had no inline content")
            return body

        messages = body.setdefault("messages", [])
        if not isinstance(messages, list):
            self._write_debug(body, "body.messages is not a list")
            return body

        if not self._has_required_context_message(messages):
            messages.insert(0, {"role": "system", "content": context_block})
        self._write_debug(body, "required file context injected")
        return body

    def _model_meta(
        self,
        body: Dict[str, Any],
        model: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        for candidate in [
            model,
            body.get("model") if isinstance(body.get("model"), dict) else None,
            metadata.get("model") if isinstance(metadata, dict) and isinstance(metadata.get("model"), dict) else None,
        ]:
            if isinstance(candidate, dict) and isinstance(candidate.get("meta"), dict):
                return candidate["meta"]
            info = candidate.get("info") if isinstance(candidate, dict) else None
            if isinstance(info, dict) and isinstance(info.get("meta"), dict):
                return info["meta"]
        return {}

    def _attach_uploaded_files(self, body: Dict[str, Any], uploaded_files: Any) -> None:
        if not isinstance(uploaded_files, list):
            return
        files = body.setdefault("files", [])
        if not isinstance(files, list):
            return
        existing = {
            (item.get("type"), item.get("id"))
            for item in files
            if isinstance(item, dict)
        }
        for uploaded in uploaded_files:
            if not isinstance(uploaded, dict):
                continue
            file_id = uploaded.get("fileId") or uploaded.get("id")
            if not file_id:
                continue
            file_ref = {"type": "file", "id": str(file_id)}
            if ("file", str(file_id)) not in existing:
                files.append(file_ref)
                existing.add(("file", str(file_id)))

    def _required_context_block(self, required_files: List[Any]) -> str:
        sections = [
            self.REQUIRED_CONTEXT_MARKER,
            "",
            "Die folgenden Inhalte sind vollständiger Pflichtkontext für dieses Modell. "
            "Sie wurden aus den angehängten Workbench-Files übernommen und sind nicht optionales RAG-Wissen.",
        ]
        appended = 0
        for item in required_files:
            if not isinstance(item, dict):
                continue
            filename = str(item.get("filename") or item.get("path") or "").strip()
            content = item.get("content")
            if not filename or not isinstance(content, str) or not content.strip():
                continue
            sections.extend(["", f"### Datei: {filename}", content.strip()])
            appended += 1
        return "\n".join(sections).strip() if appended else ""

    def _has_required_context_message(self, messages: List[Any]) -> bool:
        return any(
            isinstance(message, dict)
            and message.get("role") == "system"
            and self.REQUIRED_CONTEXT_MARKER in str(message.get("content", ""))
            for message in messages
        )

    def _write_debug(self, body: Dict[str, Any], status: str) -> None:
        metadata = body.setdefault("metadata", {})
        if isinstance(metadata, dict):
            metadata["workbench_required_file_context_filter"] = {"status": status}

    async def _emit(self, event_emitter: Any, description: str) -> None:
        if event_emitter is None or not bool(self.valves.emit_status):
            return
        try:
            await event_emitter(
                {
                    "type": "status",
                    "data": {"description": description, "done": True, "hidden": False},
                }
            )
        except Exception:
            return
