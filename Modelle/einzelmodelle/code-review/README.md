# Code-Review

## Zweck

Nutzer möchten Code systematisch gegen Qualität, Lesbarkeit, Sicherheit, Fehlerbehandlung, Performance und Wartbarkeit prüfen.

**Dieses Modell soll ausgewählt werden,** wenn eine Review-Ausgabe mit Findings, Prioritäten und konkreten Verbesserungsvorschlägen benötigt wird.

## Quelle

Erzeugt aus `11_code-review.md`.

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
