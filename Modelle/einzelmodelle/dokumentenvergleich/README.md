# Dokumentenvergleich

## Zweck

Nutzer möchten zwei oder mehrere Dokumente, Versionen, Angebote, Vertragsentwürfe, Spezifikationen oder Richtlinien vergleichen.

**Dieses Modell soll ausgewählt werden,** wenn Unterschiede, Überschneidungen, Änderungen oder Konflikte zwischen Dokumenten sichtbar gemacht werden sollen.

## Quelle

Erzeugt aus `03_dokumentenvergleich.md`.

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
