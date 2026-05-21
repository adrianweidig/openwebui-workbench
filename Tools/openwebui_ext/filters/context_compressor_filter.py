"""
title: Context Compressor Filter
type: filter
description: Counts chat-context tokens before model calls, normalizes zero output-token requests and keeps oversized prompts inside a safe context budget.
version: 1.1.0
license: MIT
security: Offline-only filter. It does not call networks, write files, execute commands or store chat content outside the current request payload.
"""

from __future__ import annotations

import copy
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
    HARD_GUARD_MARKER = "[Automatische Kontextkürzung]"
    NOTICE = (
        "ich komprimiere nun den chatkontext indem ich eine zusammenfassung der bisherigen "
        "konversation erzeuge; diese zusammenfassung wird für diesen einen chatkontext gemerkt "
        "und automatisch weiterverwendet."
    )
    HARD_GUARD_NOTICE = (
        "Der folgende Kontext wurde automatisch gekürzt; Details außerhalb der "
        "Zusammenfassung sind nicht zuverlässig verfügbar."
    )
    ZERO_OUTPUT_TOKEN_KEYS = {
        "max_tokens",
        "max_completion_tokens",
        "max_new_tokens",
        "num_predict",
        "n_predict",
    }

    class Valves(BaseModel):
        priority: int = Field(900, description="Filter execution order. Higher values run after most filters.")
        default_context_window_tokens: int = Field(131072, description="Fallback context window when the model does not expose one.")
        reserved_output_tokens: int = Field(4096, description="Output-token reserve kept free in the context budget.")
        safety_margin_tokens: int = Field(2048, description="Additional token margin to avoid provider-side off-by-one context failures.")
        trigger_ratio: float = Field(0.82, description="Compress older chat turns when estimated tokens reach this share of the context window.")
        target_ratio_after_compression: float = Field(0.55, description="Target budget for normal older-turn compression.")
        keep_recent_messages: int = Field(8, description="Recent non-system messages to keep, trimming individual oversized messages if needed.")
        min_messages_before_compression: int = Field(12, description="Minimum message count before normal older-turn compression.")
        summary_max_tokens: int = Field(3500, description="Maximum estimated tokens for generated heuristic summaries.")
        hard_guard_enabled: bool = Field(True, description="Apply a final hard budget guard when the request still exceeds the safe input budget.")
        hard_guard_recent_messages: int = Field(6, description="Recent non-system messages considered by the hard guard.")
        hard_guard_min_message_tokens: int = Field(180, description="Minimum token budget for a retained but aggressively summarized message.")
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
        normalized_zero_paths = self._remove_zero_output_token_values(body)
        messages = body.get("messages")
        if not isinstance(messages, list):
            self._write_metadata(
                body,
                token_count=0,
                context_window=self._context_window_tokens(body, __model__),
                compressed=False,
                normalized_zero_output_tokens=bool(normalized_zero_paths),
                removed_zero_output_token_paths=normalized_zero_paths,
            )
            return body

        context_window = self._context_window_tokens(body, __model__)
        input_budget = self._effective_input_budget(context_window)
        total_tokens = self._messages_tokens(messages)
        new_tokens = total_tokens
        compressed = False
        hard_guard_applied = False
        summary_tokens: Optional[int] = None
        threshold = max(1, int(context_window * float(self.valves.trigger_ratio)))

        if total_tokens >= threshold and len(messages) >= int(self.valves.min_messages_before_compression):
            if self.valves.emit_status:
                await self._emit(__event_emitter__, self.NOTICE, done=False)
            compressed_messages, summary_tokens = self._compress_messages(messages, total_tokens, context_window, input_budget)
            if compressed_messages is not None:
                body["messages"] = compressed_messages
                messages = compressed_messages
                new_tokens = self._messages_tokens(messages)
                compressed = True
                if self.valves.emit_status:
                    await self._emit(
                        __event_emitter__,
                        f"Kontextkomprimierung abgeschlossen: ca. {total_tokens} -> {new_tokens} Tokens.",
                        done=True,
                    )
            elif self.valves.emit_status:
                await self._emit(
                    __event_emitter__,
                    "Kontextkomprimierung übersprungen: Es gibt noch keinen älteren komprimierbaren Chatanteil.",
                    done=True,
                )

        if bool(self.valves.hard_guard_enabled) and new_tokens > input_budget:
            if self.valves.emit_status:
                await self._emit(
                    __event_emitter__,
                    f"Context Budget Guard aktiv: ca. {new_tokens} Tokens überschreiten das sichere Eingabebudget {input_budget}.",
                    done=False,
                )
            guarded_messages = self._hard_guard_messages(messages, new_tokens, context_window, input_budget)
            body["messages"] = guarded_messages
            new_tokens = self._messages_tokens(guarded_messages)
            hard_guard_applied = True
            compressed = True
            if self.valves.emit_status:
                await self._emit(
                    __event_emitter__,
                    f"Context Budget Guard abgeschlossen: ca. {total_tokens} -> {new_tokens} Tokens.",
                    done=True,
                )

        self._write_metadata(
            body,
            new_tokens,
            context_window,
            compressed=compressed,
            original_tokens=total_tokens,
            summary_tokens=summary_tokens,
            hard_guard_applied=hard_guard_applied,
            normalized_zero_output_tokens=bool(normalized_zero_paths),
            removed_zero_output_token_paths=normalized_zero_paths,
            input_budget=input_budget,
        )
        return body

    def _compress_messages(
        self,
        messages: List[Dict[str, Any]],
        total_tokens: int,
        context_window: int,
        input_budget: int,
    ) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        system_messages, existing_summaries, conversational = self._split_messages(messages)
        if len(conversational) <= 1:
            return None, 0

        keep_recent = max(1, int(self.valves.keep_recent_messages))
        if len(conversational) <= keep_recent:
            keep_recent = max(1, min(len(conversational) - 1, keep_recent // 2 or 1))

        older = conversational[:-keep_recent]
        recent = conversational[-keep_recent:]
        if not older:
            return None, 0

        target_tokens = max(1000, int(min(context_window, input_budget) * float(self.valves.target_ratio_after_compression)))
        summary_token_budget = min(
            int(self.valves.summary_max_tokens),
            max(500, target_tokens - self._messages_tokens(system_messages + recent)),
        )
        summary = self._build_summary(existing_summaries, older, total_tokens, context_window, summary_token_budget)
        summary_message = {"role": "system", "content": summary}
        output = list(system_messages)
        if bool(self.valves.inject_notice_message):
            output.append({"role": "assistant", "content": self.NOTICE})
        output.append(summary_message)
        output.extend(recent)
        return output, self._estimate_tokens(summary)

    def _hard_guard_messages(
        self,
        messages: List[Dict[str, Any]],
        total_tokens: int,
        context_window: int,
        input_budget: int,
    ) -> List[Dict[str, Any]]:
        system_messages, existing_summaries, conversational = self._split_messages(messages)
        output = list(system_messages)
        output.append(
            {
                "role": "system",
                "content": "\n".join(
                    [
                        self.SUMMARY_MARKER,
                        self.HARD_GUARD_MARKER,
                        self.HARD_GUARD_NOTICE,
                        f"Ursprüngliche Schätzung: ca. {total_tokens} Tokens.",
                        f"Sicheres Eingabebudget: ca. {input_budget} von {context_window} Kontexttokens.",
                    ]
                ),
            }
        )

        remaining_budget = max(0, input_budget - self._messages_tokens(output))
        keep_recent = max(1, min(int(self.valves.hard_guard_recent_messages), len(conversational)))
        older = conversational[:-keep_recent]
        recent = conversational[-keep_recent:] if keep_recent else conversational

        if older and remaining_budget > int(self.valves.hard_guard_min_message_tokens):
            summary_budget = min(
                int(self.valves.summary_max_tokens),
                max(int(self.valves.hard_guard_min_message_tokens), remaining_budget // 4),
            )
            older_summary = self._build_summary(existing_summaries, older, total_tokens, context_window, summary_budget)
            output.append({"role": "system", "content": older_summary})

        for index, message in enumerate(recent):
            used = self._messages_tokens(output)
            remaining = max(0, input_budget - used)
            remaining_messages = max(1, len(recent) - index)
            per_message_budget = max(int(self.valves.hard_guard_min_message_tokens), remaining // remaining_messages)
            output.append(self._fit_message_to_budget(message, per_message_budget, is_last=(index == len(recent) - 1)))

        return self._tighten_to_budget(output, input_budget)

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

    def _fit_message_to_budget(self, message: Dict[str, Any], token_budget: int, is_last: bool = False) -> Dict[str, Any]:
        token_budget = max(int(self.valves.hard_guard_min_message_tokens), int(token_budget))
        if self._estimate_tokens(self._message_text(message)) <= token_budget:
            return copy.deepcopy(message)
        role = str(message.get("role", "unknown"))
        summary = self._build_aggressive_message_summary(self._message_text(message), role, token_budget, is_last=is_last)
        fitted = copy.deepcopy(message)
        fitted["content"] = summary
        metadata = fitted.setdefault("metadata", {})
        if isinstance(metadata, dict):
            metadata["context_compressor_filter"] = {
                "trimmed": True,
                "original_estimated_tokens": self._estimate_tokens(self._message_text(message)),
                "target_token_budget": token_budget,
            }
        return fitted

    def _build_aggressive_message_summary(self, text: str, role: str, token_budget: int, is_last: bool = False) -> str:
        max_chars = max(600, int(token_budget * float(self.valves.approximate_chars_per_token)))
        important = self._important_lines(text, max_chars=max(500, max_chars // 3))
        structure = self._structure_hints(text)
        start_chars = max(180, max_chars // 4)
        end_chars = max(180, max_chars // 4)
        lines = [
            self.SUMMARY_MARKER,
            self.HARD_GUARD_MARKER,
            self.HARD_GUARD_NOTICE,
            f"Rolle: {role}. Ursprüngliche Schätzung: ca. {self._estimate_tokens(text)} Tokens.",
            "Diese Nachricht wurde heuristisch verdichtet; ausgelassene Details gelten als unbekannt.",
            "",
            "## Strukturhinweise",
            structure or "- Keine eindeutigen Strukturhinweise erkannt.",
            "",
            "## Anfang",
            self._truncate_multiline(text, start_chars),
        ]
        if important:
            lines.extend(["", "## Relevante Zeilen", important])
        lines.extend(["", "## Ende", self._truncate_multiline(text[-max(0, end_chars * 2) :], end_chars)])
        if is_last:
            lines.extend(["", "## Priorität", "Diese Nachricht war die jüngste Nutzer- oder Toolnachricht und hat Vorrang vor älteren komprimierten Inhalten."])
        return self._truncate("\n".join(lines), max_chars)

    def _tighten_to_budget(self, messages: List[Dict[str, Any]], input_budget: int) -> List[Dict[str, Any]]:
        if self._messages_tokens(messages) <= input_budget:
            return messages
        tightened: List[Dict[str, Any]] = []
        for message in messages:
            role = str(message.get("role", ""))
            content = self._message_text(message)
            if role == "system" and self.HARD_GUARD_MARKER not in content:
                tightened.append(message)
                continue
            remaining_messages = max(1, len(messages) - len(tightened))
            remaining_budget = max(int(self.valves.hard_guard_min_message_tokens), (input_budget - self._messages_tokens(tightened)) // remaining_messages)
            tightened.append(self._fit_message_to_budget(message, remaining_budget))
        return tightened

    def _split_messages(self, messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
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
        return system_messages, existing_summaries, conversational

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

    def _effective_input_budget(self, context_window: int) -> int:
        reserved = max(0, int(self.valves.reserved_output_tokens))
        safety = max(0, int(self.valves.safety_margin_tokens))
        if context_window <= reserved + safety + 256:
            return max(256, int(context_window * 0.8))
        return max(256, context_window - reserved - safety)

    def _messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        return sum(self._estimate_tokens(self._message_text(message)) + 6 for message in messages if isinstance(message, dict))

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        chars_per_token = max(1.0, float(self.valves.approximate_chars_per_token))
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

    def _structure_hints(self, text: str) -> str:
        hints: List[str] = []
        stripped = text.lstrip()
        if stripped.startswith("{") or stripped.startswith("["):
            keys = self._unique_matches(r'"([^"\n]{1,80})"\s*:', text, 18)
            hints.append("JSON-ähnlicher Inhalt" + (f"; sichtbare Schlüssel: {', '.join(keys)}" if keys else ""))
        lines = [line for line in text.splitlines() if line.strip()]
        if lines and any(separator in lines[0] for separator in [",", ";", "\t", "|"]):
            hints.append(f"Tabellen-/CSV-Header: {self._truncate(lines[0], 260)}")
        paths = self._unique_matches(r"(?:[A-Za-z]:\\|/)[^\s\"'<>|]{3,}", text, 12)
        if paths:
            hints.append("Pfade: " + ", ".join(paths))
        code_symbols = self._unique_matches(r"\b(?:def|class|function|async\s+def)\s+([A-Za-z_][A-Za-z0-9_]*)", text, 18)
        if code_symbols:
            hints.append("Code-Symbole: " + ", ".join(code_symbols))
        return "\n".join(f"- {hint}" for hint in hints)

    def _important_lines(self, text: str, max_chars: int) -> str:
        patterns = re.compile(
            r"(?i)(error|exception|traceback|failed|fatal|warn|context length|max_tokens|num_predict|token|"
            r"\bTODO\b|\bFIXME\b|^\s*(def|class|function|async\s+def|import|from|SELECT|CREATE|INSERT|UPDATE|DELETE)\b|"
            r"\.py\b|\.json\b|\.yaml\b|\.yml\b|docker|compose|openwebui)"
        )
        selected: List[str] = []
        for line in text.splitlines():
            compact = line.strip()
            if compact and patterns.search(compact):
                selected.append(self._truncate(compact, 360))
            if len("\n".join(selected)) >= max_chars:
                break
        return self._truncate_multiline("\n".join(selected), max_chars) if selected else ""

    def _unique_matches(self, pattern: str, text: str, limit: int) -> List[str]:
        seen = set()
        values: List[str] = []
        for match in re.finditer(pattern, text):
            value = match.group(1) if match.groups() else match.group(0)
            value = self._truncate(str(value).strip(), 120)
            if value and value not in seen:
                seen.add(value)
                values.append(value)
            if len(values) >= limit:
                break
        return values

    def _truncate(self, text: str, max_chars: int) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= max_chars:
            return compact
        return compact[: max(0, max_chars - 20)].rstrip() + " ... [gekürzt]"

    def _truncate_multiline(self, text: str, max_chars: int) -> str:
        compact = text.strip()
        if len(compact) <= max_chars:
            return compact
        return compact[: max(0, max_chars - 20)].rstrip() + "\n... [gekürzt]"

    def _remove_zero_output_token_values(self, body: Dict[str, Any]) -> List[str]:
        removed: List[str] = []

        def is_zero(value: Any) -> bool:
            return value == 0 or value == 0.0 or (isinstance(value, str) and value.strip() == "0")

        def visit(value: Any, path: str) -> None:
            if isinstance(value, dict):
                for key in list(value.keys()):
                    nested_path = f"{path}.{key}" if path else str(key)
                    if str(key) in self.ZERO_OUTPUT_TOKEN_KEYS and is_zero(value.get(key)):
                        del value[key]
                        removed.append(nested_path)
                        continue
                    if str(key) == "messages":
                        continue
                    visit(value.get(key), nested_path)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    visit(item, f"{path}[{index}]")

        visit(body, "body")
        return removed

    def _write_metadata(
        self,
        body: Dict[str, Any],
        token_count: int,
        context_window: int,
        compressed: bool,
        original_tokens: Optional[int] = None,
        summary_tokens: Optional[int] = None,
        hard_guard_applied: bool = False,
        normalized_zero_output_tokens: bool = False,
        removed_zero_output_token_paths: Optional[List[str]] = None,
        input_budget: Optional[int] = None,
    ) -> None:
        metadata = body.setdefault("metadata", {})
        if not isinstance(metadata, dict):
            return
        metadata["context_compressor_filter"] = {
            "compressed": compressed,
            "hard_guard_applied": hard_guard_applied,
            "normalized_zero_output_tokens": normalized_zero_output_tokens,
            "removed_zero_output_token_paths": removed_zero_output_token_paths or [],
            "estimated_tokens": token_count,
            "estimated_tokens_after": token_count,
            "original_estimated_tokens": original_tokens,
            "summary_estimated_tokens": summary_tokens,
            "context_window_tokens": context_window,
            "effective_input_budget_tokens": input_budget if input_budget is not None else self._effective_input_budget(context_window),
            "reserved_output_tokens": int(self.valves.reserved_output_tokens),
            "safety_margin_tokens": int(self.valves.safety_margin_tokens),
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
