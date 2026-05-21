# Beispielergebnis und Arbeitsvorlage: Übersetzung und Lokalisierung

## Zweck dieses Modells

Texte, UI-Kopien, Dokumente und Lokalisierungsfragen zielgruppen- und kontextgerecht uebertragen.

## Wiederverwendbarer Musterauftrag

> UI-Texte und Screenshots sollen fuer eine Zielregion lokalisiert werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/lokalisierungsauftrag-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer UI-Screenshots, Kontext, abgeschnittene Texte oder Layoutprobleme nach Uebersetzung.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/lokalisierungsauftrag-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Ergebnis braucht Zielvariante, Tonalitaet, Platzhalter, Laengenrisiken und QA-Hinweise.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Übersetzung und Lokalisierung. Verwende `beispielergebnis.md` und `beispiele/lokalisierungsauftrag-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
