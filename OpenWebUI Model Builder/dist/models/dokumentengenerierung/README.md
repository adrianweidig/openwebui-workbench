# Dokumentengenerierung

## Zweck

Nutzer möchten aus Stichpunkten, Gesprächsnotizen, Tabellen oder Vorgaben professionelle Dokumente erzeugen.

**Dieses Modell soll ausgewählt werden,** wenn ein neues Dokument erstellt werden soll: Bericht, Konzept, SOP, Vorlage, Angebotstext, Projektdokumentation oder Arbeitsanweisung.

## Quelle

Erzeugt aus `05_dokumentengenerierung.md`.

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
