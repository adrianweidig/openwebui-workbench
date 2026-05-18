# Workspace Uebersicht

## Ziel

`E:\OpenWebUI` dient als gemeinsames Arbeitsverzeichnis fuer:

- OpenWebUI-Modellbau
- Problemfall-Sammlung
- lokale Tool-Entwicklung
- spaetere manuelle Erweiterungen

## Aktueller Bestand

- Der Builder-Bereich ist der am weitesten ausgebaute Teil.
- `Problemfaelle/` enthaelt die fachlichen Briefings.
- `Modelle/`, `Tools/` und `Weiteres/` sind aktuell strukturell vorhanden, aber noch nicht fachlich ausgebaut.

## Empfohlene Nutzung

1. Neue Problemfaelle zuerst unter `Problemfaelle/` als Briefing anlegen.
2. Modellpakete ueber den Builder regenerieren.
3. Nur stabile, bewusst versionierbare Artefakte einchecken.
4. Lokale Cache-Dateien und Backup-Snapshots nicht committen.

## Git-Konvention

- Root des Git-Repositories ist `E:\OpenWebUI`.
- Generierte OpenWebUI-Artefakte unter `OpenWebUI Model Builder/dist/` sind Teil des versionierten Outputs.
- Builder-Backups unter `OpenWebUI Model Builder/.backup/` bleiben lokal.
