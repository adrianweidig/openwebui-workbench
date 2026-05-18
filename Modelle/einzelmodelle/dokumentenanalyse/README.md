# Dokumentenanalyse

## Zweck

Nutzer haben ein oder mehrere Dokumente und möchten Inhalte, Struktur, Risiken, offene Punkte, Widersprüche oder Entscheidungsgrundlagen verstehen.

**Dieses Modell soll ausgewählt werden,** wenn ein vorhandenes Dokument analysiert, bewertet, strukturiert oder geprüft werden soll, ohne daraus primär ein neues Dokument zu erzeugen.

## Quelle

Erzeugt aus `01_dokumentenanalyse.md`.

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
