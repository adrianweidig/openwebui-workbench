# E-Mail- und Kommunikationsassistenz

## Zweck

Nutzer möchten professionelle E-Mails, Antworten, interne Nachrichten, Zusammenfassungen oder Kommunikationsvarianten formulieren.

## Quelle

Erzeugt aus `23_email-kommunikationsassistenz.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: optional_disabled

## Dateien

- `model.json`: direkt importierbare OpenWebUI-JSON-Datei im Exportschema, als Array mit genau einem Modellobjekt
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
