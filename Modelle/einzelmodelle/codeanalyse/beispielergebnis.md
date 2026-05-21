# Beispielergebnis und Arbeitsvorlage: Codeanalyse

## Zweck dieses Modells

Codebasen, Abhaengigkeiten, Kontrollfluesse, Risiken und technische Ursachen strukturiert analysieren.

## Wiederverwendbarer Musterauftrag

> Eine unklare Codebasis soll mit Architektur, Hotspots und Hypothesen verstanden werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/codeanalyse-bericht-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer Architektur-Screenshots, UI-Flows oder Diagramme, die Codeverhalten erklaeren.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/codeanalyse-bericht-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Trenne belegte Fakten aus Code/Tool-Ausgaben von Hypothesen und empfohlenen Messungen.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Codeanalyse. Verwende `beispielergebnis.md` und `beispiele/codeanalyse-bericht-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
