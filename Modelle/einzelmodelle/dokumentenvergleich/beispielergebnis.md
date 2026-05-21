# Beispielergebnis und Arbeitsvorlage: Dokumentenvergleich

## Zweck dieses Modells

Dokumentversionen, Textvarianten, Tabellen und Scans nachvollziehbar vergleichen.

## Wiederverwendbarer Musterauftrag

> Zwei Versionen eines Dokuments sollen mit inhaltlichen und strukturellen Unterschieden verglichen werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/dokumentenvergleich-matrix-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer gescannte Versionen, markierte PDFs, Layoutabweichungen oder Screenshotvergleiche.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/dokumentenvergleich-matrix-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Unterschiede muessen nach Relevanz, Quelle, Risiko und empfohlener Aktion sortiert sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Dokumentenvergleich. Verwende `beispielergebnis.md` und `beispiele/dokumentenvergleich-matrix-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
