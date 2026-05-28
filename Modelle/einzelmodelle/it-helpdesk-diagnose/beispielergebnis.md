# Beispielergebnis und Arbeitsvorlage: IT-Helpdesk-Diagnose

## Zweck dieses Modells

IT-Probleme aus Nutzerbeschreibung, Screenshots, Logs und Konfigurationen schnell triagieren.

## Wiederverwendbarer Musterauftrag

> Ein Nutzer meldet ein Problem mit Screenshot und wenigen Symptomen.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/helpdesk-diagnose-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für Fehlermasken, Taskleisten-/Tray-Zustände, Dialoge oder Netzwerksymbole.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/helpdesk-diagnose-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Antwort muss Sofortmaßnahmen, Rückfragen, Diagnosepfad und Eskalationskriterium enthalten.

## Copy/Paste-Starterprompt

```text
Nutze das Modell IT-Helpdesk-Diagnose. Verwende `beispielergebnis.md` und `beispiele/helpdesk-diagnose-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
