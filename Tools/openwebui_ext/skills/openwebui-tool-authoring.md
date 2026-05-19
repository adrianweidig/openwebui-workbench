---
name: openwebui-tool-authoring
description: Erstellung importierbarer OpenWebUI-Python-Tools mit Valves, async-Methoden, Event-Emitter und Security Review.
---

# OpenWebUI Tool Authoring

## Ziel
Erstelle OpenWebUI-Tools als einzelne Python-Dateien, die direkt in `Workspace > Tools` importiert werden können.

## Aufbau
- Top-Level-Docstring mit `title`, `description`, `version`, `license` und Sicherheitsnotiz.
- Eine Klasse `Tools`.
- Optionale innere Klasse `Valves(BaseModel)` für Admin-Konfiguration.
- Optionale `UserValves(BaseModel)` nur für harmlose nutzerspezifische Einstellungen.
- Öffentliche Tool-Methoden als `async def` mit vollständigen Typannotationen.

## Implementierung
- Nutze Standardbibliothek bevorzugt vor Zusatzabhängigkeiten.
- Begrenze Eingaben, Ausgaben, Timeouts und Redirects.
- Redigiere Secrets in Fehlern, Headern, Logs und Ergebnissen.
- Verwende `__event_emitter__` für `status` und bei externen Quellen optional `citation`.
- Führe keine Shell-Kommandos aus und öffne keine beliebigen Dateien.

## Tests und Review
- Importiere jede Tool-Datei isoliert.
- Prüfe `Tools`-Klasse, öffentliche Methoden, Typannotationen und Syntax.
- Suche riskante Muster wie Shell-Aufrufe, dynamische Codeausführung, unbeschränkte Netzwerk- oder Dateizugriffe.
- Dokumentiere Valves, Grenzen und bekannte Fehlermodi.
