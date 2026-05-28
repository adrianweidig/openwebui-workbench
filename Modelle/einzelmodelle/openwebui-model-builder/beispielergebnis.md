# Beispielergebnis und Arbeitsvorlage: OpenWebUI Model Builder

## Zweck dieses Modells

Vollständige OpenWebUI-Modellpakete mit Prompt, Wissen, Tools, Skills, Icons, Importplan und QA erzeugen.

## Wiederverwendbarer Musterauftrag

> Aus einer Modellidee soll ein importierbares OpenWebUI-Modellpaket entstehen.

## Erwartetes Ergebnisartefakt

- Primäre Datei: `beispiele/modellpaket-vorlage.md`
- Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
- Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

## Vision- und Screenshot-Nutzung

Nutze Vision für Icon-/UI-Screenshots, Custom-GPT-Referenzen oder Modellprofil-Mockups.

## Tool-first-Ablauf

1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
4. Ergebnis in der Vorlage unter `beispiele/modellpaket-vorlage.md` strukturieren.
5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

## Qualitätslatte

Paket muss model.json, systemprompt, mainprompt, fachwissen, Beispiel, Toolprofil und Importcheck enthalten.

## Copy/Paste-Starterprompt

```text
Nutze das Modell OpenWebUI Model Builder. Verwende `beispielergebnis.md` und `beispiele/modellpaket-vorlage.md` als Vorlage.

Ziel:
[Was soll am Ende konkret vorliegen?]

Eingaben:
[Dateien, Text, Screenshots, Daten, Constraints]

Gewuenschtes Ergebnisformat:
[Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

Qualitätskriterien:
[Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
```
