# Report- und Dashboard-Vorbereitung

## Zweck

Nutzer möchten aus Daten oder Statusinformationen einen strukturierten Bericht, KPI-Report oder eine Dashboard-Grundlage erzeugen.

## Quelle

Erzeugt aus `08_report-dashboard-vorbereitung.md`.

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
- `beispielergebnis.html`: offline lauffähiger Dashboard-Goldstandard ohne externe Ressourcen
- `beispiele/dashboard-goldstandard-briefing.md`: Few-Shot-Beispiele für KPI-Definition, Datenqualität und Dashboard-Storyline

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
