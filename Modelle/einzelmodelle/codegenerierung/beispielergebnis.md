# Beispielergebnis und Arbeitsvorlage: Codegenerierung

## Zweck dieses Modells

Bestehende Muster erkennen, zielgenauen Code erzeugen und lokale Validierung oder Tests vorbereiten.

## Wiederverwendbarer Musterauftrag

> Aus einer Featurebeschreibung soll ein implementierbarer Patchplan mit Tests entstehen.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/implementierungsplan-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer UI-Mockups, Design-Screenshots, Formularzustaende oder Fehlanzeigen.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/implementierungsplan-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Der Plan muss Dateien, Schnittstellen, Testfaelle, Risiken und Rollback-Punkte nennen.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Codegenerierung. Verwende `beispielergebnis.md` und `beispiele/implementierungsplan-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
