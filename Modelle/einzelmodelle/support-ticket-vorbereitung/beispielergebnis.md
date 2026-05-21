# Beispielergebnis und Arbeitsvorlage: Support-Ticket-Vorbereitung

## Zweck dieses Modells

Supportfaelle aus Symptomen, Screenshots, Logs und Nutzertexten in klare Tickets ueberfuehren.

## Wiederverwendbarer Musterauftrag

> Aus einem Chatverlauf und Screenshot soll ein eskalierbares Ticket entstehen.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/support-ticket-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer Fehlerscreenshots, Statusanzeigen, Dialoge oder betroffene UI-Elemente.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/support-ticket-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Ticket braucht Kurzbeschreibung, Impact, Repro, Environment, Anhaenge, Prioritaet und offene Fragen.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Support-Ticket-Vorbereitung. Verwende `beispielergebnis.md` und `beispiele/support-ticket-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
