# Beispielergebnis und Arbeitsvorlage: Übersetzung und Lokalisierung

## Zweck dieses Modells

Texte, UI-Kopien, Dokumente und Lokalisierungsfragen zielgruppen- und kontextgerecht übertragen.

## Wiederverwendbarer Musterauftrag

> UI-Texte und Screenshots sollen für eine Zielregion lokalisiert werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/lokalisierungsauftrag-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für UI-Screenshots, Kontext, abgeschnittene Texte oder Layoutprobleme nach Übersetzung.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/lokalisierungsauftrag-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Ergebnis braucht Zielvariante, Tonalität, Platzhalter, Längenrisiken und QA-Hinweise.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Übersetzung und Lokalisierung. Verwende `beispielergebnis.md` und `beispiele/lokalisierungsauftrag-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
