# Refactoring-Unterstützung

## Zweck

Nutzer möchten bestehenden Code lesbarer, modularer, sicherer oder wartbarer machen, ohne fachliches Verhalten unbeabsichtigt zu ändern.

## Quelle

Erzeugt aus `15_refactoring-unterstützung.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: enabled

## Dateien

- `model.json`: direkt importierbare OpenWebUI-JSON-Datei im Exportschema, als Array mit genau einem Modellobjekt
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln
- `beispielergebnis.md`: Goldstandard für verhaltenswahrende Refactoring-Pläne
- `beispiele/refactoring-goldstandard-briefing.md`: Few-Shot-Beispiele für Invarianten, Charakterisierungstests, Rollback und Scope-Grenzen

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
