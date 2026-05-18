# Workspace Uebersicht

## Ziel

`E:\OpenWebUI` dient als gemeinsames Arbeitsverzeichnis fuer:

- OpenWebUI-Modellbau
- Problemfall-Sammlung
- lokale Tool-Entwicklung
- spaetere manuelle Erweiterungen

## Aktueller Bestand

- `OpenWebUI Model Builder/` ist der Ausgangspunkt fuer Vorgaben und Regenerierung.
- `Problemfaelle/` enthaelt die fachlichen Briefings.
- `Modelle/einzelmodelle/` enthaelt die menschenlesbar sortierten Modellpakete.
- `Modelle/dist/` ist der Air-Gap-Copy/Paste-Bereich.
- `Tools/jupyter/` enthaelt das produktive Offline-Jupyter-Tool.

## Empfohlene Nutzung

1. Neue Problemfaelle zuerst unter `Problemfaelle/` als Briefing anlegen.
2. Modellpakete ueber den Builder regenerieren.
3. Scharfe Artefakte aus dem Builder unter `Modelle/` und `Tools/` fuer Menschen und Betrieb bereitstellen.
4. Lokale Cache-Dateien und Backup-Snapshots nicht committen.

## Git-Konvention

- Root des Git-Repositories ist `E:\OpenWebUI`.
- Builder-Quellen bleiben unter `OpenWebUI Model Builder/`.
- Operative Modelle liegen unter `Modelle/`.
- Operative Tools liegen unter `Tools/`.
- Builder-Backups unter `OpenWebUI Model Builder/.backup/` bleiben lokal.
