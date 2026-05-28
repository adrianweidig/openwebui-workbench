# Beispielergebnis und Arbeitsvorlage: Dokumentenanalyse

## Zweck dieses Modells

Dokumente, Scans, PDFs und strukturierte Inhalte quellenorientiert analysieren.

## Wiederverwendbarer Musterauftrag

> Ein Vertrag, Bericht oder Scan soll mit Kernaussagen, Risiken und Belegstellen analysiert werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/dokumentenanalyse-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für gescannte Seiten, Fotos, Stempel, Tabellenbilder oder visuelle Markierungen.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/dokumentenanalyse-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Kernaussagen, Belege, Unsicherheiten und extrahierte Daten müssen getrennt bleiben.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Dokumentenanalyse. Verwende `beispielergebnis.md` und `beispiele/dokumentenanalyse-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
