# Prozess- und Workflow-Dokumentation

## Zweck

Nutzer möchten Abläufe, SOPs, Verantwortlichkeiten, Prozessschritte oder Entscheidungspunkte dokumentieren oder verbessern.

**Dieses Modell soll ausgewählt werden,** wenn ein Prozess verständlich beschrieben, standardisiert oder in eine Arbeitsanweisung überführt werden soll.

## Quelle

Erzeugt aus `22_prozess-workflow-dokumentation.md`.

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
