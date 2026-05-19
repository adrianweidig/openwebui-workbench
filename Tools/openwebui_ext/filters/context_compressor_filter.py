"""
title: Context Compressor Filter
type: filter
description: Counts chat-context tokens before model calls and compresses older messages when the configured context window is nearly exhausted.
version: 1.0.0
license: MIT
security: Offline-only filter. It does not call networks, write files, execute commands or store chat content outside the current request payload.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Filter:
    """OpenWebUI filter that keeps long chats inside a usable context budget."""

    SUMMARY_MARKER = "[Automatische Kontextkomprimierung]"
    NOTICE = (
        "ich komprimiere nun den chatkontext indem ich eine zusammenfassung der bisherigen "
        "konversation erzeuge; diese zusammenfassung wird für diesen einen chatkontext gemerkt "
        "und automatisch weiterverwendet."
    )

    class Valves(BaseModel):
        priority: int = Field(900, description="Filter execution order. Higher values run after most filters.")
        default_context_window_tokens: int = Field(128000, description="Fallback context window when the model does not expose one.")
        trigger_ratio: float = Field(0.82, description="Compress when estimated tokens reach this share of the context window.")
        target_ratio_after_compression: float = Field(0.55, description="Target budget for the compressed payload.")
        keep_recent_messages: int = Field(8, description="Recent non-system messages to keep verbatim.")
        min_messages_before_compression: int = Field(12, description="Minimum message count before compressing older turns.")
        summary_max_tokens: int = Field(3500, description="Maximum estimated tokens for the generated summary.")
        approximate_chars_per_token: float = Field(4.0, description="Fallback character-to-token estimate used offline.")
        emit_status: bool = Field(True, description="Emit visible status updates in the WebUI while compressing.")
        inject_notice_message: bool = Field(True, description="Inject a short assistant notice into the model context.")

    def __init__(self) -> None:
        self.valves = self.Valves()
        self.toggle = True

    async def inlet(
        self,
        body: Dict[str, Any],
        __event_emitter__: Any = None,
        __user__: Optional[Dict[str, Any]] = None,
        __model__: Optional[Dict[str, Any]] = None,
        __metadata__: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compress older chat turns before the request is sent to the model."""
        messages = body.get("messages")
        if not isinstance(messages, list):
            return body

        context_window = self._context_window_tokens(body, __model__)
        total_tokens = self._messages_tokens(messages)
        threshold = max(1, int(context_window * float(self.valves.trigger_ratio)))
        if total_tokens < threshold or len(messages) < int(self.valves.min_messages_before_compression):
            self._write_metadata(body, total_tokens, context_window, compressed=False)
            return body

        if self.valves.emit_status:
            await self._emit(__event_emitter__, self.NOTICE, done=False)

        compressed_messages, summary_tokens = self._compress_messages(messages, total_tokens, context_window)
        if compressed_messages is None:
            self._write_metadata(body, total_tokens, context_window, compressed=False)
            if self.valves.emit_status:
                await self._emit(__event_emitter__, "Kontextkomprimierung übersprungen: Es gibt noch keinen älteren komprimierbaren Chatanteil.", done=True)
            return body

        body["messages"] = compressed_messages
        new_tokens = self._messages_tokens(compressed_messages)
        self._write_metadata(
            body,
            new_tokens,
            context_window,
            compressed=True,
            original_tokens=total_tokens,
            summary_tokens=summary_tokens,
        )
        if self.valves.emit_status:
            await self._emit(
                __event_emitter__,
                f"Kontextkomprimierung abgeschlossen: ca. {total_tokens} -> {new_tokens} Tokens.",
                done=True,
            )
        return body

    def _compress_messages(
        self,
        messages: List[Dict[str, Any]],
        total_tokens: int,
        context_window: int,
    ) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        system_messages: List[Dict[str, Any]] = []
        existing_summaries: List[Dict[str, Any]] = []
        conversational: List[Dict[str, Any]] = []

        for message in messages:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role", "user"))
            content = self._message_text(message)
            if role == "system" and self.SUMMARY_MARKER in content:
                existing_summaries.append(message)
            elif role == "system":
                system_messages.append(message)
            else:
                conversational.append(message)

        if len(conversational) <= 1:
            return None, 0

        keep_recent = max(1, int(self.valves.keep_recent_messages))
        if len(conversational) <= keep_recent:
            keep_recent = max(1, min(len(conversational) - 1, keep_recent // 2 or 1))

        older = conversational[:-keep_recent]
        recent = conversational[-keep_recent:]
        if not older:
            return None, 0

        target_tokens = max(1000, int(context_window * float(self.valves.target_ratio_after_compression)))
        summary_token_budget = min(int(self.valves.summary_max_tokens), max(500, target_tokens - self._messages_tokens(system_messages + recent)))
        summary = self._build_summary(existing_summaries, older, total_tokens, context_window, summary_token_budget)
        summary_message = {"role": "system", "content": summary}
        output = list(system_messages)
        if bool(self.valves.inject_notice_message):
            output.append({"role": "assistant", "content": self.NOTICE})
        output.append(summary_message)
        output.extend(recent)
        return output, self._estimate_tokens(summary)

    def _build_summary(
        self,
        existing_summaries: List[Dict[str, Any]],
        older_messages: List[Dict[str, Any]],
        total_tokens: int,
        context_window: int,
        summary_token_budget: int,
    ) -> str:
        max_chars = max(1200, int(summary_token_budget * float(self.valves.approximate_chars_per_token)))
        per_message_chars = max(220, min(900, max_chars // max(1, len(older_messages) + len(existing_summaries))))
        lines = [
            self.SUMMARY_MARKER,
            "",
            "Diese automatisch erzeugte Zusammenfassung ersetzt ältere Chatnachrichten in diesem Request.",
            f"Ursprüngliche Schätzung: ca. {total_tokens} Tokens bei Kontextfenster {context_window}.",
            "",
            "## Bisherige Zusammenfassung",
        ]

        if existing_summaries:
            for summary in existing_summaries[-2:]:
                lines.append(self._truncate(self._message_text(summary), per_message_chars))
        else:
            lines.append("- Keine frühere automatische Zusammenfassung vorhanden.")

        lines.extend(["", "## Komprimierte ältere Nachrichten"])
        for index, message in enumerate(older_messages, start=1):
            role = str(message.get("role", "unknown"))
            text = self._truncate(self._message_text(message), per_message_chars)
            lines.append(f"- Turn {index} ({role}): {text}")

        lines.extend(
            [
                "",
                "## Fortsetzungsregeln",
                "- Behandle diese Zusammenfassung als Gedächtnis des bisherigen Chats.",
                "- Nutze die nachfolgenden jüngsten Nachrichten als detailreichste Quelle.",
                "- Erfinde keine Details, die nicht in Zusammenfassung oder aktuellen Nachrichten stehen.",
            ]
        )
        summary = "\n".join(lines)
        return self._truncate(summary, max_chars)

    def _context_window_tokens(self, body: Dict[str, Any], model: Optional[Dict[str, Any]]) -> int:
        candidates: List[int] = []
        for source in [model, body]:
            for value in self._walk_context_values(source):
                if isinstance(value, int) and value > 0:
                    candidates.append(value)
                elif isinstance(value, str) and value.isdigit():
                    candidates.append(int(value))
        if candidates:
            return max(candidates)
        return int(self.valves.default_context_window_tokens)

    def _walk_context_values(self, value: Any) -> Iterable[Any]:
        context_keys = {
            "context_length",
            "max_context_length",
            "context_window",
            "max_context_window",
            "num_ctx",
            "n_ctx",
            "num_context",
            "model_context_length",
            "model_context_window",
        }
        if isinstance(value, dict):
            for key, nested in value.items():
                if str(key).lower() in context_keys:
                    yield nested
                elif isinstance(nested, (dict, list)):
                    yield from self._walk_context_values(nested)
        elif isinstance(value, list):
            for item in value:
                yield from self._walk_context_values(item)

    def _messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        return sum(self._estimate_tokens(self._message_text(message)) + 6 for message in messages if isinstance(message, dict))

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        chars_per_token = max(1.0, float(self.valves.approximate_chars_per_token))
        # Extra term accounts for punctuation-heavy code, JSON and CSV where char/4 underestimates.
        dense_segments = len(re.findall(r"[{}\[\](),.:;=<>/\\|_-]", text))
        return int(math.ceil(len(text) / chars_per_token) + math.ceil(dense_segments / 12))

    def _message_text(self, message: Dict[str, Any]) -> str:
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, dict):
                    if isinstance(item.get("text"), str):
                        parts.append(item["text"])
                    elif item.get("type"):
                        parts.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return str(content)

    def _truncate(self, text: str, max_chars: int) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= max_chars:
            return compact
        return compact[: max(0, max_chars - 20)].rstrip() + " ... [gekürzt]"

    def _write_metadata(
        self,
        body: Dict[str, Any],
        token_count: int,
        context_window: int,
        compressed: bool,
        original_tokens: Optional[int] = None,
        summary_tokens: Optional[int] = None,
    ) -> None:
        metadata = body.setdefault("metadata", {})
        if not isinstance(metadata, dict):
            return
        metadata["context_compressor_filter"] = {
            "compressed": compressed,
            "estimated_tokens": token_count,
            "original_estimated_tokens": original_tokens,
            "summary_estimated_tokens": summary_tokens,
            "context_window_tokens": context_window,
            "trigger_ratio": float(self.valves.trigger_ratio),
        }

    async def _emit(self, event_emitter: Any, description: str, done: bool) -> None:
        if event_emitter is None:
            return
        try:
            await event_emitter(
                {
                    "type": "status",
                    "data": {"description": description, "done": done, "hidden": False},
                }
            )
        except Exception:
            return
