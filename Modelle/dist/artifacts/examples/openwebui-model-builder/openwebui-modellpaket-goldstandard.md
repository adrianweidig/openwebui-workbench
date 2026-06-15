# Beispiele: OpenWebUI Model Builder

## Beispiel 1: Minimale Anfrage

### Nutzeranfrage

Erstelle ein Modell für Support-Ticket-Vorbereitung.

### Gute Antwort

Das Modellpaket nutzt ein aufgabenorientiertes `model.json`, kurzen deterministischen Systemprompt, `mainprompt.md`, `fachwissen.md`, `Golden_Example.<ext>` als Pflichtdateien, sinnvolle Promptvorschläge, optionale Beispiele unter `beispiele/`, deaktivierte Websuche und klare Sicherheitsgrenzen.

## Beispiel 2: Realistischer Standardfall

### Nutzeranfrage

Baue ein OpenWebUI-Modell für interne Dokumentenanalyse mit hochgeladenen PDFs, aber ohne Internet.

### Gute Antwort

Das Paket aktiviert File Upload und File Context, deaktiviert Web Search, beschreibt Quellenbindung, Auslassungsrisiko, Datenschutz und Antwortformat. Tool-IDs werden nicht erfunden.

## Beispiel 3: Komplexer Fall

### Nutzeranfrage

Erzeuge ein Modellpaket für CSV-Analyse mit Code Interpreter, JSON-Validierung und Importcheck.

### Gute Antwort

Das Paket trennt Capabilities, Default Features, Knowledge-Dateien, empfohlene Tools, Testdaten und Validierung. `model.json` bleibt importierbar und secret-frei.

## Beispiel 4: Unvollständige Informationen

### Nutzeranfrage

Ich brauche ein Modell für Compliance.

### Gute Antwort

Der Builder fragt höchstens nach Regelwerk, Zielgruppe und Ausgabeformat. Wenn keine Antwort vorliegt, erstellt er ein generisches Prüfmodell mit prüfpflichtigen Normangaben und ohne erfundene Rechtsquellen.

## Beispiel 5: Widersprüchliche Eingabe

### Nutzeranfrage

Das Modell soll offline laufen, aber immer aktuelle Webquellen automatisch recherchieren.

### Gute Antwort

Der Builder markiert den Konflikt und erzeugt eine Offline-Variante mit lokaler Knowledge-Nutzung sowie eine optionale Online-Variante, die Web Search nur bewusst aktiviert.

## Beispiel 6: Sicherheitsgrenze

### Nutzeranfrage

Baue ein Modell, das Login-Daten aus Supportchats sammelt.

### Gute Antwort

Der Builder lehnt Credential-Abgriff ab und erstellt stattdessen ein Modell für Secret-Erkennung, Maskierung, Rotationsempfehlung und sichere Ticket-Eskalation.

## Beispiel 7: Offline-Fallback

### Nutzeranfrage

Verwende unsere Tools und Skills, aber ich kenne die IDs nicht.

### Gute Antwort

Das Paket dokumentiert Tool- und Skill-Zuordnung als Import-Nacharbeit und erfindet keine IDs. Es nutzt leere Listen oder repo-bekannte IDs nur, wenn sie aus bereitgestellten Dateien stammen.

## Beispiel 8: Goldstandard-Ergebnis

### Nutzeranfrage

Erstelle ein vollständiges OpenWebUI-Aufgabenmodell für Support-Ticket-Vorbereitung.

### Gute Antwort

Die passende Musterantwort ist `Modelle/einzelmodelle/openwebui-model-builder/beispielergebnis.md`.
