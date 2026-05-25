# Beispielergebnis und Arbeitsvorlage: E-Mail- und Kommunikationsassistenz

## Zweck dieses Modells

E-Mails, Antworten, Eskalationen und Kommunikationsvorlagen präzise und adressatengerecht formulieren.

## Wiederverwendbarer Musterauftrag

> Aus Kontext, Ziel und Tonalität soll eine sendefertige Antwort entstehen.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/email-antwort-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für E-Mail-Screenshots, Ticketmasken oder visuelle Kontextinformationen; maskiere sensible Daten.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/email-antwort-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Ton, Ziel, Aktion, Frist, Anhänge und Risiken müssen explizit passen.

## Copy/Paste-Starterprompt

```text
Nutze das Modell E-Mail- und Kommunikationsassistenz. Verwende `beispielergebnis.md` und `beispiele/email-antwort-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
