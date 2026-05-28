# Tabellen- und CSV-Datenanalyse

## Zweck

Nutzer möchten CSV-, XLSX- oder tabellarische Daten offline untersuchen, bereinigen, aggregieren, visualisieren und interpretieren.

## Quelle

Erzeugt aus `07_tabellen-csv-datenanalyse.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: required

## Dateien

- `model.json`: direkt importierbare OpenWebUI-JSON-Datei im Exportschema, als Array mit genau einem Modellobjekt
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln
- `beispielergebnis.py`: ausführbares Offline-Goldstandardartefakt für CSV-Profiling mit Standardbibliothek
- `beispiele/tabellen-csv-datenanalyse-goldstandard-briefing.md`: Few-Shot-Beispiele für Profiling, Datenqualität und Reproduzierbarkeit

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
