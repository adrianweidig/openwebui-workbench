# Meeting-Protokoll-Auswertung

## Zweck

Nutzer möchten aus Notizen oder Transkripten Entscheidungen, Aufgaben, Verantwortlichkeiten, Fristen und offene Fragen extrahieren.

**Dieses Modell soll ausgewählt werden,** wenn ein Meeting nachbereitet oder in Aktionslisten überführt werden soll.

## Quelle

Erzeugt aus `18_meeting-protokoll-auswertung.md`.

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
