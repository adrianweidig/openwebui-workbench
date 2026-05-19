"""
title: Repository Tree Analyzer
description: Analyze a pasted repository tree or file list without server-side filesystem reads.
version: 1.0.0
license: MIT
security: Uses only text supplied by the user. It does not open paths, read files, call networks or run commands.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, List

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


class Tools:
    """OpenWebUI toolkit for pasted repository tree analysis."""

    class Valves(BaseModel):
        max_input_chars: int = Field(120000, description="Maximum pasted tree length.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def analyze_tree(self, tree_text: str, __event_emitter__: Any = None) -> str:
        """
        Analyze a pasted file tree and suggest missing repository hygiene files.
        :param tree_text: Pasted output from a file tree, rg --files or similar.
        """
        if len(tree_text) > int(self.valves.max_input_chars):
            return "Fehler: Eingabe ist zu groß."
        await self._emit(__event_emitter__, "Analysiere Repository-Baum", False)
        paths = [self._clean(line) for line in tree_text.splitlines() if self._clean(line)]
        suffixes = Counter(self._suffix(path) for path in paths if self._suffix(path))
        names = {path.lower().replace("\\", "/").split("/")[-1] for path in paths}
        dirs = {path.lower().replace("\\", "/").split("/")[0] for path in paths if "/" in path.replace("\\", "/")}
        gaps: List[str] = []
        for required in ["readme.md", "license", "security.md", ".gitignore"]:
            if required not in names:
                gaps.append(f"`{required}` nicht erkannt.")
        if not any(name.startswith("test_") or name in {"tests", "pytest.ini"} for name in names | dirs):
            gaps.append("Keine klare Teststruktur erkannt.")
        if not any("openwebui" in path.lower() and "tools" in path.lower() for path in paths):
            gaps.append("Keine offensichtliche OpenWebUI-Toolstruktur erkannt.")
        await self._emit(__event_emitter__, "Repository-Baum analysiert", True)
        lines = [
            "# Repository-Baum-Analyse",
            f"- Einträge: {len(paths)}",
            f"- Top-Level-Ordner: {', '.join(sorted(dirs)[:20]) if dirs else 'keine erkannt'}",
            "",
            "## Häufige Dateitypen",
        ]
        lines.extend(f"- `.{suffix}`: {count}" for suffix, count in suffixes.most_common(12))
        lines.extend(["", "## Lücken", *(f"- {gap}" for gap in gaps or ["Keine offensichtlichen Hygiene-Lücken erkannt."])])
        lines.extend(["", "## Empfohlene OpenWebUI-Erweiterungsstruktur", "- `Tools/openwebui_ext/tools/` für importierbare `.py`-Tools", "- `Tools/openwebui_ext/skills/` für importierbare `.md`-Skills", "- `Tools/openwebui_ext/docs/` für Import-, Sicherheits- und Betriebshinweise", "- `Artefakte/` für offline erzeugte Ergebnisse", "- `scripts/validate_openwebui_extensions.py` für lokale Prüfung"])
        return "\n".join(lines)

    def _clean(self, line: str) -> str:
        return re.sub(r"^[\s|`+\\-]+", "", line).strip()

    def _suffix(self, path: str) -> str:
        name = path.replace("\\", "/").rsplit("/", 1)[-1]
        if "." not in name or name.startswith("."):
            return ""
        return name.rsplit(".", 1)[-1].lower()

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
