# Beispielergebnis und Arbeitsvorlage: Mistral Vision Workbench

## Zweck dieses Modells

Bilder, Screenshots, UI-Zustände, Folien, Diagramme, Scans und visuelle Artefakte multimodal analysieren.

## Wiederverwendbarer Musterauftrag

> Ein UI-Screenshot oder eine HTML-Praesentation soll visuell geprüft und verbessert werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/vision-ui-qa-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Vision ist der Hauptpfad: sichtbare Fakten extrahieren, Unsicherheiten markieren und lokale Tools für Reproduktion oder Artefakte nutzen.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/vision-ui-qa-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Findings müssen sichtbar belegbar, priorisiert und mit konkretem Fix sowie Akzeptanzkriterium versehen sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Mistral Vision Workbench. Verwende `beispielergebnis.md` und `beispiele/vision-ui-qa-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
