# n8n Workflow Architect

OpenWebUI-Modellumsetzung des Custom GPT `n8n Workflow Architect` aus `adrianweidig/custom-gpts`.

## Zweck

Erstellt, prüft und verbessert n8n-Workflows mit Fokus auf importierbares Workflow-JSON, Hosting-Modell, Credentials, Expressions, Sicherheit und Testbarkeit.

## Referenz

Quelle: `https://github.com/adrianweidig/custom-gpts/tree/main/N8N-Generator`

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.json`, `beispiele/` und `i18n/` werden beim API-Import als Knowledge für dieses Modell hinterlegt.

## Beispielergebnis

Das primäre Goldstandard-Beispiel ist `beispielergebnis.json`. Dieses Modell soll importierbare n8n-Workflow-JSONs erzeugen; deshalb darf eine Markdown-Datei das eigentliche Zielartefakt nicht ersetzen. Ergänzende Markdown-Dateien unter `beispiele/` erklären die Musterfälle und Sicherheitsgrenzen.
