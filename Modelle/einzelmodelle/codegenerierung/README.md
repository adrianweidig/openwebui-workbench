# Codegenerierung

## Zweck

Nutzer möchten aus einer Beschreibung lauffähigen, verständlichen und wartbaren Code erzeugen.

## Quelle

Erzeugt aus `09_codegenerierung.md`.

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
- `beispielergebnis.py`: ausführbares Offline-Goldstandardartefakt mit Standardbibliothek, Eingabevalidierung, Markdown-Ausgabe und Selbsttest
- `beispiele/codegenerierung-goldstandard-briefing.md`: Few-Shot-Beispiele für minimale, komplexe, widersprüchliche und sicherheitskritische Aufträge

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
