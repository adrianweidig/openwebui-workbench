# Beispielergebnis und Arbeitsvorlage: E-Mail- und Kommunikationsassistenz

## Zweck dieses Modells

E-Mails, Antworten, Eskalationen und Kommunikationsvorlagen praezise und adressatengerecht formulieren.

## Wiederverwendbarer Musterauftrag

> Aus Kontext, Ziel und Tonalitaet soll eine sendefertige Antwort entstehen.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/email-antwort-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer E-Mail-Screenshots, Ticketmasken oder visuelle Kontextinformationen; maskiere sensible Daten.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/email-antwort-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Ton, Ziel, Aktion, Frist, Anhaenge und Risiken muessen explizit passen.

## Copy/Paste-Starterprompt

```text
Nutze das Modell E-Mail- und Kommunikationsassistenz. Verwende `beispielergebnis.md` und `beispiele/email-antwort-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
