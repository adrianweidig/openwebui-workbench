# Testfall-Generierung

## Zweck

Nutzer möchten aus Anforderungen oder Code sinnvolle Unit-, Integrations-, Regression- oder Akzeptanztests ableiten.

**Dieses Modell soll ausgewählt werden,** wenn Testspezifikation, Testdaten oder Testcode benötigt werden.

## Quelle

Erzeugt aus `13_testfall-generierung.md`.

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
