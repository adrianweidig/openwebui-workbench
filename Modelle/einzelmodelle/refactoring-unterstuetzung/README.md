# Refactoring-Unterstützung

## Zweck

Nutzer möchten bestehenden Code lesbarer, modularer, sicherer oder wartbarer machen, ohne fachliches Verhalten unbeabsichtigt zu ändern.

**Dieses Modell soll ausgewählt werden,** wenn Code verbessert, vereinfacht oder neu strukturiert werden soll.

## Quelle

Erzeugt aus `15_refactoring-unterstuetzung.md`.

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
