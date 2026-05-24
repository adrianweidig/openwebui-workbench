# Workspace Übersicht

## Ziel

`E:\openwebui-workbench` dient auf dieser Maschine als gemeinsames Arbeitsverzeichnis für:

- OpenWebUI-Modellbau
- Problemfall-Sammlung
- lokale Tool-Entwicklung
- spätere manuelle Erweiterungen

## Aktueller Bestand

- `OpenWebUI Model Builder/` ist der Ausgangspunkt für Vorgaben und Regenerierung.
- `Problemfälle/` enthält die fachlichen Briefings.
- `Modelle/einzelmodelle/` enthält die menschenlesbar sortierten Modellpakete.
- `Modelle/dist/` ist der Air-Gap-Copy/Paste-Bereich.
- `Tools/jupyter/` enthält das produktive Offline-Jupyter-Tool.

## Empfohlene Nutzung

1. Neue Problemfälle zuerst unter `Problemfälle/` als Briefing anlegen.
2. Modellpakete über den Builder regenerieren.
3. Scharfe Artefakte aus dem Builder unter `Modelle/` und `Tools/` für Menschen und Betrieb bereitstellen.
4. Lokale Cache-Dateien und Backup-Snapshots nicht committen.

## Git-Konvention

- Root des Git-Repositories ist `E:\openwebui-workbench`.
- Builder-Quellen bleiben unter `OpenWebUI Model Builder/`.
- Operative Modelle liegen unter `Modelle/`.
- Operative Tools liegen unter `Tools/`.
- Builder-Backups unter `OpenWebUI Model Builder/.backup/` bleiben lokal.
