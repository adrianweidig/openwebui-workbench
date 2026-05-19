---
name: safe-mcp-openapi-import
description: Sicherheitsworkflow für Offline-MCP-, MCPO- und OpenAPI-Toolserver in OpenWebUI.
---

# Safe MCP OpenAPI Import

Nutze diesen Skill, wenn OpenWebUI mit MCP-Servern, MCPO-Proxies oder OpenAPI-Toolservern erweitert werden soll.

## Prüfschritte

1. Quelle, Lizenz und Betreiber klären.
2. Endpunkte und Methoden prüfen: read-only, write, admin, destructive.
3. OpenAPI-Schema lokal mit `openapi_schema_inspector` analysieren.
4. Netzwerkziel begrenzen: bevorzugt lokale Container, keine unkontrollierten internen Netze.
5. Secrets nur über OpenWebUI-Konfiguration, Valves oder Container-Secrets setzen.
6. Toolserver zunächst nur einem Testmodell und Admin-Gruppe zuordnen.

## Fallback

Wenn ein MCP/OpenAPI-Server nicht sicher geprüft werden kann, wird er nicht automatisch aktiviert. Stattdessen eine Skill-Anleitung oder eine manuelle Checkliste verwenden.

## Ergebnis

Liefere eine Importentscheidung: freigeben, eingeschränkt freigeben oder blockieren. Begründe mit Risiken, benötigten Umgebungsvariablen und Modellzuordnung.
