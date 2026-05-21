# Beispielergebnis und Arbeitsvorlage: n8n Workflow Architect

## Zweck dieses Modells

Importierbare n8n-Workflows planen, validieren und mit Test- sowie Sicherheitshinweisen ausgeben.

## Wiederverwendbarer Musterauftrag

> Ein Integrationsziel soll in einen pruefbaren n8n-Workflow mit Nodes, Credentials und Fehlerpfad ueberfuehrt werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/n8n-workflow-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer n8n-Canvas-Screenshots, Node-Konfigurationen oder Fehleranzeigen.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/n8n-workflow-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Workflow, Trigger, Datenvertrag, Fehlerbehandlung, Secrets und Testfaelle muessen konsistent sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell n8n Workflow Architect. Verwende `beispielergebnis.md` und `beispiele/n8n-workflow-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
