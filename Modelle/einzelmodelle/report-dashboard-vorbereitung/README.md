# Report- und Dashboard-Vorbereitung

## Zweck

Nutzer möchten aus Daten oder Statusinformationen einen strukturierten Bericht, KPI-Report oder eine Dashboard-Grundlage erzeugen.

**Dieses Modell soll ausgewählt werden,** wenn aus Zahlen, Tabellen oder Projektständen ein wiederverwendbarer Bericht entstehen soll.

## Quelle

Erzeugt aus `08_report-dashboard-vorbereitung.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: enabled

## Dateien

- `model.json`: generisches Modellprofil
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Die JSON-Struktur ist eine Fallback-Struktur, weil lokal kein Referenzexport der Zielinstanz vorhanden war.
