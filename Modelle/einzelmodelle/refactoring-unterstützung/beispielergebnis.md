# Beispielergebnis und Arbeitsvorlage: Refactoring-Unterstützung

## Zweck dieses Modells

Refactoring-Ziele, Codebereiche, Risiken, Tests und schrittweise Umsetzung strukturieren.

## Wiederverwendbarer Musterauftrag

> Ein Modul soll ohne Verhaltensbruch schrittweise umgebaut werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/refactoring-plan-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für UI-Verhaltensvergleiche, Architekturskizzen oder visuelle Regressionen.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/refactoring-plan-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Plan braucht Scope, Nicht-Ziele, Reihenfolge, Tests, Rollback und Akzeptanzkriterien.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Refactoring-Unterstützung. Verwende `beispielergebnis.md` und `beispiele/refactoring-plan-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
