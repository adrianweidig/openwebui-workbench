# E-Mail- und Kommunikationsassistenz

## Zweck

Nutzer möchten professionelle E-Mails, Antworten, interne Nachrichten, Zusammenfassungen oder Kommunikationsvarianten formulieren.

**Dieses Modell soll ausgewählt werden,** wenn der Schwerpunkt auf klarer, passender und zielgruppengerechter Kommunikation liegt.

## Quelle

Erzeugt aus `23_email-kommunikationsassistenz.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: optional_disabled

## Dateien

- `model.json`: generisches Modellprofil
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Die JSON-Struktur ist eine Fallback-Struktur, weil lokal kein Referenzexport der Zielinstanz vorhanden war.
