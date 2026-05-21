# Beispielergebnis und Arbeitsvorlage: Debugging und Fehleranalyse

## Zweck dieses Modells

Fehlertexte, Logs, Screenshots, Reproduktionsschritte und Konfigurationen zu einer belastbaren Ursache fuehren.

## Wiederverwendbarer Musterauftrag

> Ein OpenWebUI-, Docker- oder App-Fehler soll reproduzierbar eingegrenzt werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/debugging-runbook-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer Fehlermeldungs-Screenshots, UI-Zustaende, Browser-Konsole oder visuelle Regressionsbilder.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/debugging-runbook-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Hypothesen muessen priorisiert, pruefbar und mit naechstem Diagnosebefehl verbunden sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Debugging und Fehleranalyse. Verwende `beispielergebnis.md` und `beispiele/debugging-runbook-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
