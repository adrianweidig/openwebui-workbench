# Übersetzung und Lokalisierung

## Zweck

Nutzer möchten Texte übersetzen, vereinfachen, lokalisieren oder sprachlich an Zielgruppen anpassen.

## Quelle

Erzeugt aus `24_uebersetzung-lokalisierung.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: optional

## Dateien

- `model.json`: direkt importierbare OpenWebUI-JSON-Datei im Exportschema, als Array mit genau einem Modellobjekt
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
