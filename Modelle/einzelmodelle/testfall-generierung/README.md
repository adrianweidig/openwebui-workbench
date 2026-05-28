# Testfall-Generierung

## Zweck

Nutzer möchten aus Anforderungen oder Code sinnvolle Unit-, Integrations-, Regression- oder Akzeptanztests ableiten.

## Quelle

Erzeugt aus `13_testfall-generierung.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: enabled

## Dateien

- `model.json`: direkt importierbare OpenWebUI-JSON-Datei im Exportschema, als Array mit genau einem Modellobjekt
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln
- `beispielergebnis.md`: Goldstandard für risikobasierte Testfallkataloge
- `beispiele/testfall-generierung-goldstandard-briefing.md`: Few-Shot-Beispiele für negative Tests, Grenzfälle, Offline-Fixtures und sichere Testdaten

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
