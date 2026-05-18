# Codeanalyse

## Zweck

Nutzer möchten bestehenden Code verstehen, Abhängigkeiten erkennen, Risiken finden oder Architektur und Datenflüsse erklären lassen.

**Dieses Modell soll ausgewählt werden,** wenn vorhandener Code gelesen, erklärt, strukturiert oder bewertet werden soll.

## Quelle

Erzeugt aus `10_codeanalyse.md`.

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
