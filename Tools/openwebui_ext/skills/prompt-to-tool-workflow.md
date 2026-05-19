---
name: prompt-to-tool-workflow
description: Umwandlung von Nutzerzielen in passende OpenWebUI-Tool- und Skill-Workflows mit Sicherheitsprüfung und Ergebnisvalidierung.
---

# Prompt To Tool Workflow

## Zielklärung
- Bestimme Ziel, Eingaben, gewünschtes Ergebnis, Risiko und notwendige Tools.
- Stelle maximal drei Rückfragen, wenn Pflichtinformationen fehlen.
- Arbeite mit klar gekennzeichneten Annahmen weiter, wenn das Risiko gering ist.

## Auswahl
- Nutze Skills für Arbeitsweise, Qualitätsregeln und wiederkehrende Denkprozesse.
- Nutze Tools nur für notwendige Berechnung, Validierung, API-Abfrage oder strukturierte Analyse.
- Bevorzuge das kleinste Tool mit ausreichenden Sicherheitsgrenzen.

## Ausführung
- Reihenfolge: Validieren, analysieren, ausführen, Ergebnis prüfen, zusammenfassen.
- Tool-Ergebnisse kritisch bewerten und bei Widersprüchen kennzeichnen.
- Keine Secrets aus Tool-Eingaben oder Ergebnissen wiedergeben.

## Ergebnis
- Nenne verwendete Skills und Tools.
- Liefere Ergebnis, Annahmen, Risiken und nächste konkrete Schritte.
