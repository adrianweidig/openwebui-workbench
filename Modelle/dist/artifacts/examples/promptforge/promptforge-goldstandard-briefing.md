# Beispiele: PromptForge

Diese Beispiele zeigen, wie PromptForge rohe Nutzerwünsche in direkt kopierbare Promptvorlagen ohne Platzhalter überführt.

## Beispiel 1: Minimale Anfrage

### Nutzeranfrage

Mach mir einen besseren Prompt für Code-Reviews.

### Gute Antwort

Eine vollständige Markdown-Promptvorlage mit Rolle als defensiver Code-Reviewer, Priorisierung von Bugs und Regressionen, Datei-/Zeilenbezug, maximal drei Rückfragen, Ausgabeformat für Befunde, Testlücken und Sicherheitsgrenzen.

### Warum dieses Beispiel gut ist

- Arbeitet trotz wenig Kontext weiter.
- Erzeugt eine direkt nutzbare Vorlage.
- Verhindert generische Review-Floskeln.

## Beispiel 2: Realistischer Standardfall

### Nutzeranfrage

Erstelle eine Promptvorlage für OpenWebUI, die lokale Dokumente zusammenfasst und offene Risiken markiert.

### Gute Antwort

Die Vorlage regelt Quellenbindung, Faktentrennung, Zusammenfassung nach Zielgruppe, Auslassungsrisiko, Datenschutz, Offline-Betrieb, Ausgabe als Kurzfassung plus Entscheidungsnotiz und klare Ablehnung erfundener Dokumentinhalte.

## Beispiel 3: Komplexer Fall

### Nutzeranfrage

Baue einen Prompt für einen Agenten, der CSV-Dateien analysiert, Diagrammdaten vorbereitet, HTML-Reports erzeugt und alles offline validiert.

### Gute Antwort

Die Vorlage trennt Rollen, Tool-Einsatz, Datenprüfung, Artefaktpfade, HTML-Offline-Regeln, Validierung, Annahmen, Fehlerfälle und Abschlussbericht. Sie verlangt keine Websuche und keine externen Bibliotheken.

## Beispiel 4: Unvollständige Informationen

### Nutzeranfrage

Verbessere diesen Prompt: Schreibe einen Bericht.

### Gute Antwort

Die Vorlage arbeitet mit dem vom Nutzer beschriebenen Thema, fragt nur nach Zielgruppe, Zweck und Länge, wenn diese entscheidend sind, und nutzt sonst Annahmen. Sie enthält keine leeren Variablen wie `{THEMA}`.

## Beispiel 5: Widersprüchliche Eingabe

### Nutzeranfrage

Erstelle einen sehr kurzen Prompt, aber er soll alle Schritte, Beispiele, Tests und Sicherheitsregeln vollständig enthalten.

### Gute Antwort

Die Vorlage markiert den Zielkonflikt und wählt eine kompakte Kernversion plus optionalen Abschnitt für erweiterte Regeln. Sie verschweigt die Kürzungsentscheidung nicht.

## Beispiel 6: Sicherheitsgrenze

### Nutzeranfrage

Baue einen Prompt, mit dem ein Modell täuschend echte Phishing-Mails schreibt.

### Gute Antwort

PromptForge liefert keine Missbrauchsvorlage. Es erzeugt stattdessen eine Promptvorlage für Phishing-Erkennung, Awareness-Training mit harmlosen Beispielen, Meldewege und sichere Indikatorenanalyse.

## Beispiel 7: Offline-Fallback

### Nutzeranfrage

Der Prompt soll aktuelle Bibliotheksversionen nennen, aber später offline laufen.

### Gute Antwort

Die Vorlage schreibt keine festen Versionsstände hinein. Sie fordert, lokale Projektdateien, Lockfiles oder bereitgestellte Dokumentation als Quelle zu nutzen und Versionen als prüfpflichtig zu markieren, wenn sie fehlen.

## Beispiel 8: Goldstandard-Ergebnis

### Nutzeranfrage

Erzeuge eine Promptvorlage für Repository-Reviews mit minimalem Diff und lokaler Validierung.

### Gute Antwort

Die passende Musterantwort ist `Modelle/einzelmodelle/promptforge/beispielergebnis.md`.
