# Beispielergebnis und Arbeitsvorlage: Dokumentengenerierung

## Zweck dieses Modells

Strukturierte, direkt nutzbare Dokumente, HTML/PDF-Artefakte und Vorlagen erzeugen.

## Wiederverwendbarer Musterauftrag

> Aus Stichpunkten soll ein auslieferbares Dokument mit Deckblatt, Struktur und Platzhaltern entstehen.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/dokument-generator-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für Corporate-Design-Screenshots, Layoutbeispiele, Diagramme oder handschriftliche Skizzen.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/dokument-generator-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Das Ergebnis muss befüllbar, konsistent formatiert und offline weiterverwendbar sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Dokumentengenerierung. Verwende `beispielergebnis.md` und `beispiele/dokument-generator-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
