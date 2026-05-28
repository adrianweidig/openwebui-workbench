# Beispielergebnis und Arbeitsvorlage: Informationsextraktion

## Zweck dieses Modells

Informationen aus Texten, Tabellen, Logs, Dokumenten und Bildern in ein definiertes Schema extrahieren.

## Wiederverwendbarer Musterauftrag

> Aus gemischten Quellen soll valides JSON mit Belegen und Unsicherheiten entstehen.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/extraktionsschema-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für Formularfotos, Tabellenbilder, Scans, Etiketten oder UI-Datenmasken.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/extraktionsschema-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Jedes Feld braucht Quelle, Normalisierung, Unsicherheit und Validierungsregel.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Informationsextraktion. Verwende `beispielergebnis.md` und `beispiele/extraktionsschema-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
