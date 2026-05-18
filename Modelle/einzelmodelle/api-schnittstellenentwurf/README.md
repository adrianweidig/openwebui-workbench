# API- und Schnittstellenentwurf

## Zweck

Nutzer möchten eine API, Datenstruktur, Request/Response-Schemata oder Schnittstellendokumentation entwerfen.

**Dieses Modell soll ausgewählt werden,** wenn technische Schnittstellen geplant, beschrieben oder für Implementierung vorbereitet werden sollen.

## Quelle

Erzeugt aus `16_api-schnittstellenentwurf.md`.

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
