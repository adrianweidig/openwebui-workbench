# Beispielergebnis und Arbeitsvorlage: Offline Workbench Agent

## Zweck dieses Modells

Komplexe Offline-Aufgaben routen, Tools kombinieren und HTML/PDF/ZIP/Tabellen/Code-Artefakte lokal erzeugen.

## Wiederverwendbarer Musterauftrag

> Eine mehrteilige Aufgabe soll mit Jupyter, Artefakt-Tools und Validierung end-to-end erledigt werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/offline-workbench-auftrag-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer Screenshots, Artefakt-QA, Diagramme, UI-Zustaende und visuelle Eingaben.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/offline-workbench-auftrag-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Der Plan muss Tool-Wellen, Artefaktpfade, Validierung und Uebergabeformat enthalten.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Offline Workbench Agent. Verwende `beispielergebnis.md` und `beispiele/offline-workbench-auftrag-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
