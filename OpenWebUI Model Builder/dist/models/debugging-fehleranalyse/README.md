# Debugging und Fehleranalyse

## Zweck

Nutzer möchten Fehler, Exceptions, Stacktraces, unerwartetes Verhalten oder kaputte Skripte systematisch analysieren.

**Dieses Modell soll ausgewählt werden,** wenn ein konkreter Fehler behoben oder eine Ursache eingegrenzt werden soll.

## Quelle

Erzeugt aus `12_debugging-fehleranalyse.md`.

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
