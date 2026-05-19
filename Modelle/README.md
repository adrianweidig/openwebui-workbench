# Modelle

Dieser Ordner enthält die operativ relevanten Modellartefakte.

## Unterstruktur

- `einzelmodelle/`: menschenlesbar sortierte Modellpakete mit importierbarem `model.json`, `systemprompt.md`, `mainprompt.md`, `fachwissen.md` und `README.md`
- `dist/`: Air-Gap-Handover für Copy/Paste, ZIP und OpenWebUI-Import

## Nutzung

- Für inhaltliche Prüfung und manuelle Bearbeitung `einzelmodelle/` verwenden.
- Für Transport in die Zielumgebung oder gebündelte Übergabe `dist/` verwenden.
- Für die ChatGPT-ähnliche Offline-Gesamterfahrung zuerst `einzelmodelle/offline-workbench-agent/model.json` importieren und mit Jupyter- sowie Artefakt-Tools koppeln.
