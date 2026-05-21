# Beispielergebnis und Arbeitsvorlage: JSON-, CSV- und Log-Analyse

## Zweck dieses Modells

JSON, CSV, Logs und strukturierte Textdaten validieren, analysieren und in klare Befunde ueberfuehren.

## Wiederverwendbarer Musterauftrag

> Ein Logauszug und eine CSV sollen auf Fehler, Muster und Datenqualitaet geprueft werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/loganalyse-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision nur fuer Screenshot-Logs oder Tabellenbilder; verlange Rohtext, wenn Genauigkeit noetig ist.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/loganalyse-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Parsingstatus, Auffaelligkeiten, Beispiele, betroffene Felder und Repro-Schritte muessen enthalten sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell JSON-, CSV- und Log-Analyse. Verwende `beispielergebnis.md` und `beispiele/loganalyse-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
