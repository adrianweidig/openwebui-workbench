# Beispielergebnis und Arbeitsvorlage: PromptForge

## Zweck dieses Modells

Erste Nutzerprompts nach Best Practices in direkt kopierbare, zielsystemspezifische Promptvorlagen optimieren.

## Wiederverwendbarer Musterauftrag

> Ein roher Nutzerprompt soll für ChatGPT, Custom GPT, OpenWebUI oder lokale LLMs verbessert werden.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/promptforge-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für Screenshots von Zieloberflaechen, Prompt-Buildern, Fehlermeldungen oder Beispielausgaben.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/promptforge-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Prompt muss Rolle, Ziel, Kontext, Quellen, Toolregeln, Ausgabeformat, Grenzen und Erfolgskriterien enthalten.

## Copy/Paste-Starterprompt

```text
Nutze das Modell PromptForge. Verwende `beispielergebnis.md` und `beispiele/promptforge-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
