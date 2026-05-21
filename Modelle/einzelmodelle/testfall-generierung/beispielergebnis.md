# Beispielergebnis und Arbeitsvorlage: Testfall-Generierung

## Zweck dieses Modells

Aus Anforderungen, Code, UI-Screenshots und Risiken konkrete Testfaelle und Akzeptanztests erzeugen.

## Wiederverwendbarer Musterauftrag

> Ein Feature soll mit funktionalen, negativen, UI- und Regressionstests abgesichert werden.

## Erwartetes Ergebnisartefakt

- Primaere Datei: `beispiele/testfallkatalog-vorlage.md`
- Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision fuer UI-Screenshots, Fehlzustaende, Formularlayouts und visuelle Akzeptanzkriterien.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/testfallkatalog-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

## Qualitaetslatte

Testfaelle brauchen Preconditions, Schritte, Testdaten, erwartetes Ergebnis und Prioritaet.

## Copy/Paste-Starterprompt

```text
Nutze das Modell Testfall-Generierung. Verwende `beispielergebnis.md` und `beispiele/testfallkatalog-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

Qualitaetskriterien:
[Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
```
