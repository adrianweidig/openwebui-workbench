# JSON-, CSV- und Log-Analyse

## Zweck

Nutzer möchten strukturierte Dateien, Logs, Fehlermuster, Events oder Datenströme offline untersuchen und auswerten.

**Dieses Modell soll ausgewählt werden,** wenn technische oder operative Rohdaten analysiert werden müssen.

## Quelle

Erzeugt aus `17_json-csv-log-analyse.md`.

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
