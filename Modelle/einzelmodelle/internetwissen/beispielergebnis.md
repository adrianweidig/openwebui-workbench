# Beispielergebnis und Arbeitsvorlage: Internetwissen

## Zweck dieses Modells

Offline-Wissensfragen, Quellenkritik, Aktualitätsgrenzen und Recherchepläne strukturiert bearbeiten, ohne Live-Webzugriff vorzutäuschen.

## Wiederverwendbarer Musterauftrag

> Ein Nutzer will ein zeitabhängiges oder quellennahes Thema verstehen und braucht eine belastbare Offline-Einordnung mit Prüffragen.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/internetwissen-rechercheplan-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision nur für sichtbare Quellen-Screenshots, Tabellen oder Webseitenausschnitte; markiere alles Nicht-Sichtbare als unbestätigt.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/internetwissen-rechercheplan-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Antworten trennen bekannte Fakten, Nutzerangaben, Annahmen, Aktualitätsrisiken, Quellenarten, Prüffragen und nächsten Recherchepfad.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Internetwissen. Verwende `beispielergebnis.md` und `beispiele/internetwissen-rechercheplan-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
