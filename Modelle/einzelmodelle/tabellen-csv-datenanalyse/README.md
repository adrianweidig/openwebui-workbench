# Tabellen- und CSV-Datenanalyse

## Zweck

Nutzer möchten CSV-, XLSX- oder tabellarische Daten offline untersuchen, bereinigen, aggregieren, visualisieren und interpretieren.

**Dieses Modell soll ausgewählt werden,** wenn strukturierte Daten analysiert oder in Erkenntnisse, Tabellen, Diagramme oder Reports überführt werden sollen.

## Quelle

Erzeugt aus `07_tabellen-csv-datenanalyse.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: required

## Dateien

- `model.json`: generisches Modellprofil
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Die JSON-Struktur ist eine Fallback-Struktur, weil lokal kein Referenzexport der Zielinstanz vorhanden war.
