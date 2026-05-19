---
name: parallel-tools-subagents
description: Zerlegt komplexe Aufgaben in sichere parallele Tool-Wellen und Subagent-Arbeitspakete.
---

# Parallel Tools und Subagents

Nutze diesen Skill für komplexe Aufgaben, die in unabhängige Recherche-, Analyse-, Implementierungs-, Prüf- oder Dokumentationsstränge aufgeteilt werden können.

## Arbeitsweise

1. Zerlege die Aufgabe in konkrete Arbeitspakete mit eindeutigem Ergebnis.
2. Markiere Abhängigkeiten explizit. Nur Aufgaben ohne gemeinsame Schreibziele oder Zustandsabhängigkeiten dürfen in dieselbe Welle.
3. Ordne pro Arbeitspaket Tool, Skill oder Subagent-Modell zu.
4. Nutze `parallel_task_planner.build_parallel_execution_plan`, um Wellen zu planen.
5. Nutze `parallel_task_planner.split_for_subagents`, wenn Workspace-Modelle mit Spezialwissen, Knowledge Bases oder eigenen Tool-Sets vorhanden sind.
6. Führe Ergebnisse mit `parallel_task_planner.merge_parallel_results` zusammen.

## Sicherheitsregeln

- Schreibende Tools, Deployment, Git, Shell, Dateiumbenennung und Datenbankänderungen nicht blind parallel ausführen.
- Externe oder langlaufende Tools immer mit Timeout und Besitzer planen.
- Jeder Subagent liefert Quelle, Status, Ergebnis, Risiken und geänderte Dateien oder Artefakte.
- Bei widersprüchlichen Resultaten nicht mitteln, sondern Konflikt offen benennen und eine Entscheidungsgrundlage liefern.

## Ergebnisformat

Gib einen Parallelplan mit Wellen, Akteuren, erwarteten Ergebnissen, Fallbacks und klarer Sequenz für abhängige Schritte aus.
