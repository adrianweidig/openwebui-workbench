# Informationsextraktion

## Zweck

Nutzer möchten aus unstrukturierten Dokumenten strukturierte Informationen wie Namen, Daten, Fristen, Beträge, Aufgaben, Risiken oder Entitäten extrahieren.

**Dieses Modell soll ausgewählt werden,** wenn aus Texten maschinenlesbare Tabellen, Listen oder JSON-Strukturen entstehen sollen.

## Quelle

Erzeugt aus `04_informationsextraktion.md`.

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
