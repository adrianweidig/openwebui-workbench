# Anforderungsanalyse und Lastenheft

## Zweck

Nutzer möchten Anforderungen aus Beschreibungen, Gesprächen oder Dokumenten strukturieren, klären und in Lastenheft-/Pflichtenheft-nahe Form bringen.

**Dieses Modell soll ausgewählt werden,** wenn unklare Wünsche in Anforderungen, Akzeptanzkriterien, Risiken und Rückfragen überführt werden sollen.

## Quelle

Erzeugt aus `19_anforderungsanalyse-lastenheft.md`.

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
