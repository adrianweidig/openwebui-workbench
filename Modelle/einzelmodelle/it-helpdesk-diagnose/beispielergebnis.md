# Beispielergebnis und Arbeitsvorlage: IT-Helpdesk-Diagnose

## Zweck dieses Modells

IT-Probleme aus Nutzerbeschreibung, Screenshots, Logs und Konfigurationen schnell triagieren.

## Wiederverwendbarer Musterauftrag

> Ein Nutzer meldet ein Problem mit Screenshot und wenigen Symptomen.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/helpdesk-diagnose-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer Fehlermasken, Taskleisten-/Tray-Zustaende, Dialoge oder Netzwerksymbole.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/helpdesk-diagnose-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Antwort muss Sofortmassnahmen, Rueckfragen, Diagnosepfad und Eskalationskriterium enthalten.

## Copy/Paste-Starterprompt

```text
Nutze das Modell IT-Helpdesk-Diagnose. Verwende `beispielergebnis.md` und `beispiele/helpdesk-diagnose-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
