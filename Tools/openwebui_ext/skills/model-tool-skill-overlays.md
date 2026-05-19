---
name: model-tool-skill-overlays
description: Plant robuste Modellprofile mit überlagerbaren Tools, Skills, Redundanz und Native-Tool-Calling-Regeln.
---

# Model Tool Skill Overlays

Nutze diesen Skill, wenn OpenWebUI-Modelle mit Tools und Skills so ausgestattet werden sollen, dass Fähigkeiten redundant, austauschbar und offline betreibbar bleiben.

## Prinzipien

- Ein Modellprofil erhält nur die Tools, die es für seinen Zweck regelmäßig braucht.
- Jeder kritische Use Case bekommt mindestens zwei Pfade: Tool, Skill, Knowledge Base, Jupyter oder manuelle Checkliste.
- Riskante Tools werden nicht global aktiviert, sondern rollen- und modellbezogen.
- Native Tool Calling ist der Zielmodus. Prompt-basierte Tool-Fallbacks nur als dokumentierte Übergangslösung nutzen.
- Skills dürfen Tools erklären und stabilisieren, ersetzen aber keine Sicherheitsprüfung für serverseitigen Python-Code.

## Arbeitsweise

1. Sammle Modelle, vorhandene Tools, Skills und Use Cases als JSON.
2. Nutze `tool_skill_overlay_planner.build_overlay_matrix` für die Modellzuordnung.
3. Nutze `tool_skill_overlay_planner.compare_capability_coverage`, um Lücken zu finden.
4. Nutze `tool_skill_overlay_planner.suggest_fallback_stack`, um primäre und sekundäre Pfade je Use Case zu definieren.
5. Dokumentiere pro Modell: aktive Tools, aktive Skills, bewusst nicht aktive riskante Tools und manuellen Fallback.

## Ergebnis

Das Ergebnis ist eine Matrix, die Admins in OpenWebUI unter `Workspace > Models` nachvollziehbar abbilden können.
