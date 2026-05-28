# Informationsextraktion

## Zweck

Nutzer möchten aus unstrukturierten Dokumenten strukturierte Informationen wie Namen, Daten, Fristen, Beträge, Aufgaben, Risiken oder Entitäten extrahieren.

## Quelle

Erzeugt aus `04_informationsextraktion.md`.

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
- `beispielergebnis.json`: valides JSON-Goldstandardergebnis mit Belegen, Normalisierung und Unsicherheiten
- `beispiele/informationsextraktion-goldstandard-briefing.md`: Few-Shot-Beispiele für Schemaextraktion und Datenschutzgrenzen

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
