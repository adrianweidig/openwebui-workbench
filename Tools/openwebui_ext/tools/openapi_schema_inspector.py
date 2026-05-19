"""
title: OpenAPI Schema Inspector
description: Analyze pasted OpenAPI JSON and summarize endpoints, parameters and security hints without making API calls.
version: 1.0.0
license: MIT
security: This tool parses user-provided text only. It does not call APIs, process tokens, access files or execute shell commands.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    class BaseModel:
        pass

    def Field(default: Any = None, description: str = "") -> Any:
        return default


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


class Tools:
    """OpenWebUI toolkit for local OpenAPI schema review."""

    class Valves(BaseModel):
        max_input_chars: int = Field(250000, description="Maximum OpenAPI text length.")
        max_endpoints: int = Field(80, description="Maximum endpoints included in the result.")

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def inspect_openapi_json(self, schema_json: str, __event_emitter__: Any = None) -> str:
        """
        Inspect an OpenAPI JSON schema supplied as text.
        :param schema_json: JSON document containing an OpenAPI 3.x or Swagger 2.0 schema.
        """
        if len(schema_json) > int(self.valves.max_input_chars):
            return "Fehler: Schema ist zu groß für die konfigurierte Analysegrenze."
        await self._emit(__event_emitter__, "Analysiere OpenAPI-Schema", False)
        try:
            schema = json.loads(schema_json)
        except json.JSONDecodeError as exc:
            return f"Fehler: Ungültiges JSON bei Zeile {exc.lineno}, Spalte {exc.colno}: {exc.msg}"
        if not isinstance(schema, dict):
            return "Fehler: Das OpenAPI-Schema muss ein JSON-Objekt sein."

        title = self._text(schema.get("info", {}).get("title", "Unbenannt"))
        version = self._text(schema.get("info", {}).get("version", "unbekannt"))
        paths = schema.get("paths", {})
        security_schemes = schema.get("components", {}).get("securitySchemes", {}) or schema.get("securityDefinitions", {})
        endpoints = self._collect_endpoints(paths)
        risks = self._risks(schema, endpoints, security_schemes)
        await self._emit(__event_emitter__, "OpenAPI-Analyse abgeschlossen", True)

        lines = [
            "# OpenAPI-Analyse",
            f"- Titel: {title}",
            f"- Version: {version}",
            f"- OpenAPI/Swagger: {self._text(schema.get('openapi', schema.get('swagger', 'nicht angegeben')))}",
            f"- Endpunkte erkannt: {len(endpoints)}",
            f"- Security-Schemes: {', '.join(security_schemes.keys()) if security_schemes else 'keine'}",
            "",
            "## Endpunkte",
        ]
        for endpoint in endpoints[: int(self.valves.max_endpoints)]:
            lines.append(f"- `{endpoint['method'].upper()} {endpoint['path']}`: {endpoint['summary']}")
            if endpoint["params"]:
                lines.append(f"  Parameter: {', '.join(endpoint['params'][:12])}")
            if endpoint["auth"]:
                lines.append(f"  Auth-Hinweis: {endpoint['auth']}")
        if len(endpoints) > int(self.valves.max_endpoints):
            lines.append(f"- ... {len(endpoints) - int(self.valves.max_endpoints)} weitere Endpunkte gekürzt")
        lines.extend(["", "## Risiken und Lücken"])
        lines.extend(f"- {risk}" for risk in risks) if risks else lines.append("- Keine offensichtlichen strukturellen Risiken erkannt.")
        lines.extend(["", "## Tooling-Empfehlung", "- Erst nur lesende Endpunkte anbinden.", "- Authentifizierung über Valves oder OAuth-Injektion konfigurieren; Tokens nie in Prompts oder Logs ausgeben.", "- Für schreibende Endpunkte explizite Bestätigung, Eingabevalidierung und Audit-Logging vorsehen."])
        return "\n".join(lines)

    def _collect_endpoints(self, paths: Any) -> List[Dict[str, Any]]:
        endpoints: List[Dict[str, Any]] = []
        if not isinstance(paths, dict):
            return endpoints
        for path, operations in paths.items():
            if not isinstance(operations, dict):
                continue
            for method, operation in operations.items():
                if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                    continue
                params = []
                for param in operation.get("parameters", []):
                    if isinstance(param, dict):
                        params.append(self._text(param.get("name", "unnamed")) + ":" + self._text(param.get("in", "unknown")))
                auth = "operation security gesetzt" if operation.get("security") else ""
                endpoints.append({"path": self._text(path), "method": method, "summary": self._text(operation.get("summary") or operation.get("operationId") or "ohne Kurzbeschreibung"), "params": params, "auth": auth})
        return endpoints

    def _risks(self, schema: Dict[str, Any], endpoints: List[Dict[str, Any]], security_schemes: Dict[str, Any]) -> List[str]:
        risks: List[str] = []
        if not schema.get("servers") and not schema.get("host"):
            risks.append("Keine Server- oder Host-Angabe vorhanden.")
        if not security_schemes:
            risks.append("Keine zentralen Security-Schemes definiert.")
        for endpoint in endpoints:
            if endpoint["method"].lower() in {"post", "put", "patch", "delete"} and not endpoint["auth"]:
                risks.append(f"Schreibender Endpunkt ohne operationale Security-Angabe: {endpoint['method'].upper()} {endpoint['path']}")
        if any(re.search(r"(token|password|secret|api[_-]?key)", p, re.I) for e in endpoints for p in e["params"]):
            risks.append("Parameter mit potentiell sensiblen Namen erkannt; Ausgabe und Logging redigieren.")
        return risks[:25]

    def _text(self, value: Any) -> str:
        return str(value).replace("\n", " ").strip()[:300]

    async def _emit(self, emitter: Any, description: str, done: bool) -> None:
        if emitter:
            await emitter({"type": "status", "data": {"description": description, "done": done}})
