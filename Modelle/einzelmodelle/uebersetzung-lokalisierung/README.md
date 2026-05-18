# Übersetzung und Lokalisierung

## Zweck

Nutzer möchten Texte übersetzen, vereinfachen, lokalisieren oder sprachlich an Zielgruppen anpassen.

**Dieses Modell soll ausgewählt werden,** wenn vorhandene Inhalte sprachlich übertragen oder kulturell/terminologisch angepasst werden sollen.

## Quelle

Erzeugt aus `24_uebersetzung-lokalisierung.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: optional

## Dateien

- `model.json`: generisches Modellprofil
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Die JSON-Struktur ist eine Fallback-Struktur, weil lokal kein Referenzexport der Zielinstanz vorhanden war.
