# Beispielergebnis und Arbeitsvorlage: Compliance- und Richtlinienprüfung

## Zweck dieses Modells

Richtlinien, Nachweise, Kontrollen und Abweichungen nachvollziehbar prüfen.

## Wiederverwendbarer Musterauftrag

> Ein Prozess oder Dokumentensatz soll gegen interne Richtlinien bewertet werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/compliance-pruefbericht-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für gescannte Nachweise, UI-Screenshots von Einstellungen oder Kontroll-Dashboards.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/compliance-pruefbericht-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Jede Abweichung braucht Quelle, Risiko, Empfehlung, Verantwortlichkeit und Nachweisstatus.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Compliance- und Richtlinienprüfung. Verwende `beispielergebnis.md` und `beispiele/compliance-pruefbericht-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
