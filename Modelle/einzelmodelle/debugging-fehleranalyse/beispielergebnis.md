# Beispielergebnis und Arbeitsvorlage: Debugging und Fehleranalyse

## Zweck dieses Modells

Fehlertexte, Logs, Screenshots, Reproduktionsschritte und Konfigurationen zu einer belastbaren Ursache führen.

## Wiederverwendbarer Musterauftrag

> Ein OpenWebUI-, Docker- oder App-Fehler soll reproduzierbar eingegrenzt werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/debugging-runbook-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für Fehlermeldungs-Screenshots, UI-Zustände, Browser-Konsole oder visuelle Regressionsbilder.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/debugging-runbook-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Hypothesen müssen priorisiert, prüfbar und mit nächstem Diagnosebefehl verbunden sein.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Debugging und Fehleranalyse. Verwende `beispielergebnis.md` und `beispiele/debugging-runbook-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
