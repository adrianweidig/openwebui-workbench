# Code-Dokumentation

## Zweck

Nutzer möchten vorhandenen oder neuen Code verständlich dokumentieren: README, API-Doku, Funktionskommentare, Architekturhinweise.

**Dieses Modell soll ausgewählt werden,** wenn Codewissen für Nutzer, Entwickler oder Betrieb verständlich dokumentiert werden soll.

## Quelle

Erzeugt aus `14_code-dokumentation.md`.

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
