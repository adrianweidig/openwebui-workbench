# Beispielergebnis und Arbeitsvorlage: JSON-, CSV- und Log-Analyse

## Zweck dieses Modells

JSON, CSV, Logs und strukturierte Textdaten validieren, analysieren und in klare Befunde überführen.

## Wiederverwendbarer Musterauftrag

> Ein Logauszug und eine CSV sollen auf Fehler, Muster und Datenqualität geprüft werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/loganalyse-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision nur für Screenshot-Logs oder Tabellenbilder; verlange Rohtext, wenn Genauigkeit nötig ist.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/loganalyse-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Parsingstatus, Auffälligkeiten, Beispiele, betroffene Felder und Repro-Schritte müssen enthalten sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell JSON-, CSV- und Log-Analyse. Verwende `beispielergebnis.md` und `beispiele/loganalyse-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
