# Support-Ticket-Vorbereitung

## Zweck

Nutzer möchten unstrukturierte Supportanfragen in klare Tickets mit Kategorie, Priorität, Zusammenfassung, Rückfragen und Eskalationshinweisen umwandeln.

**Dieses Modell soll ausgewählt werden,** wenn Supportfälle strukturiert, priorisiert oder für 1st-/2nd-Level vorbereitet werden sollen.

## Quelle

Erzeugt aus `20_support-ticket-vorbereitung.md`.

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
