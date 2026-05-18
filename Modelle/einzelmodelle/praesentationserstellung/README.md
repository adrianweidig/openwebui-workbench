# Präsentationserstellung

## Zweck

Nutzer möchten aus Informationen, Dokumenten oder Stichpunkten eine Präsentationsstruktur oder direkt eine PPTX-Datei erzeugen.

**Dieses Modell soll ausgewählt werden,** wenn eine Folienstruktur, Management-Präsentation, Schulung, Pitch, Projektstatus oder Ergebnispräsentation benötigt wird.

## Quelle

Erzeugt aus `06_praesentationserstellung.md`.

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
