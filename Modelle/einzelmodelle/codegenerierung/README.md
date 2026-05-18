# Codegenerierung

## Zweck

Nutzer möchten aus einer Beschreibung lauffähigen, verständlichen und wartbaren Code erzeugen.

**Dieses Modell soll ausgewählt werden,** wenn neuer Code, Skripte, Funktionen, APIs, Automatisierungen oder Prototypen erstellt werden sollen.

## Quelle

Erzeugt aus `09_codegenerierung.md`.

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
