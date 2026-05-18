# Dokumentenzusammenfassung

## Zweck

Nutzer möchten lange Dokumente, Protokolle, Berichte oder Richtlinien schnell in verständliche Kurzfassungen, Executive Summaries oder Stichpunktlisten überführen.

**Dieses Modell soll ausgewählt werden,** wenn das Hauptziel Verdichtung und verständliche Aufbereitung eines vorhandenen Textes ist.

## Quelle

Erzeugt aus `02_dokumentenzusammenfassung.md`.

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
