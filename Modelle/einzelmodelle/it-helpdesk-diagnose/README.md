# IT-Helpdesk-Diagnose

## Zweck

Nutzer möchten IT-Probleme anhand von Symptomen, Logs und Systeminformationen strukturiert eingrenzen.

**Dieses Modell soll ausgewählt werden,** wenn ein Diagnosebaum, erste Prüfungen oder Eskalationsvorbereitung benötigt werden.

## Quelle

Erzeugt aus `21_it-helpdesk-diagnose.md`.

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
