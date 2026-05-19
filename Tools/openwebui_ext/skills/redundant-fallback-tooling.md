---
name: redundant-fallback-tooling
description: Erstellt Fallback-Ketten für gleiche Use Cases, damit Ausfälle einzelner Tools oder Dienste nicht den Workflow brechen.
---

# Redundant Fallback Tooling

Nutze diesen Skill, wenn ein Use Case gefahrlos über mehrere Tools, Skills oder manuelle Verfahren abgedeckt werden soll.

## Fallback-Schichten

1. Primäres Tool: direkt, schnell, gut strukturiert.
2. Sekundäres Tool: anderer Implementierungsweg oder geringere Abhängigkeit.
3. Skill-Anleitung: Modell kann strukturiert weiterarbeiten, auch wenn kein Tool verfügbar ist.
4. Jupyter oder Artefakt-Workbench: lokale Ausführung oder Datei-Erzeugung, wenn passend.
5. Manuelle Checkliste: minimaler, auditierbarer Weg ohne Automatisierung.

## Bewertungsregeln

- Offline-fähig schlägt API-Key-Pflicht, wenn die Umgebung air-gapped ist.
- Read-only schlägt write, wenn nur Analyse nötig ist.
- Kleine, klar begrenzte Tools schlagen monolithische Tools bei kritischem Betrieb.
- Zwei Tools mit gleicher Funktion sind sinnvoll, wenn sie unterschiedliche Fehlerbilder haben.

## Ausgabe

Liefere pro Use Case eine Fallback-Kette mit Auslöser für den Wechsel, Risiko, benötigter Konfiguration und erwarteter Ergebnisform.
