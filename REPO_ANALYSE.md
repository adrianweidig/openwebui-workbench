# Repo-Analyse

## Stand

Analysebasis ist der OpenWebUI-Workbench-Arbeitsbaum nach der Workspace-Strukturierung. Diese Datei ist eine Momentaufnahme; die zentrale Einstiegspunkt-Dokumentation ist `README.md`.

Aktueller Abgleich vom 2026-05-31: Für laufende Arbeit sind `README.md`, `TESTING.md`, `docs/ARCHITECTURE.md`, `docs/WORKBENCH_DASHBOARD.md`, `docs/LANGUAGE_PAIRS.md` und `AGENTS.md` maßgeblich. Die Dateizahlen unten bleiben als historische Orientierung erhalten und sind kein Live-Inventar.

## Beobachtungen

- Das Repository ist ein OpenWebUI-Workspace für offline nutzbare Modellpakete, Tools, Filter, Skills und Handover-Artefakte.
- `Problemfälle/` enthält die fachlichen Briefings.
- `Modelle/einzelmodelle/` enthält die menschenlesbaren Modellpakete.
- `Modelle/dist/` und `Tools/dist/` enthalten bewusst versionierte Übergabe- und ZIP-Artefakte.
- `Tools/openwebui_ext/` enthält importierbare OpenWebUI-Erweiterungen inklusive lokaler Tests.
- `Artefakte/output/` und `Artefakte/temp/` sind lokale Laufzeitbereiche und sollen außer `.gitkeep` nicht versioniert werden.

## Historischer Dateibestand

Die folgenden Zahlen stammen aus der ursprünglichen Analyse, schließen `.git/` aus und dienen nur zur Orientierung.

| Bereich | Dateien | Unterordner | Größe in Byte |
|---|---:|---:|---:|
| `Artefakte` | 4 | 2 | 1241 |
| `Deployment` | 3 | 0 | 6082 |
| `Dokumentation` | 1 | 0 | 4431 |
| `Modelle` | 352 | 103 | 2705414 |
| `OpenWebUI Model Builder` | 7 | 1 | 1472783 |
| `Problemfälle` | 27 | 0 | 190405 |
| `scripts` | 4 | 0 | 146161 |
| `Tools` | 83 | 11 | 2813109 |
| `Weiteres` | 1 | 0 | 169 |

## Bewertung

- Die operative Struktur ist klar getrennt: Briefings, Einzelmodelle, Dist-Artefakte, Tools und Deployment-Vorlagen.
- Identische Modell-JSONs in `Modelle/einzelmodelle/` und `Modelle/dist/artifacts/models/` sind gewollte Handover-Duplikate.
- Es gibt kein klassisches Paketmanifest; die Qualitätsprüfung läuft über die vorhandenen Python-Skripte und Unittests.
- Die zentrale `README.md` bündelt Nutzung, Validierung, Importwege und Verweise auf Spezialdokumente.
- Wiederkehrende Prüfpunkte liegen inzwischen im zentralen Verify-Runner: Dokumentations-Sprachpaare, Secret-Hygiene, Extension-Validierung, Generator-/ZIP-Drift, Import-Dry-Run, Unit-Tests und JSON-Validierung.

## Offene operative Punkte

- Lizenz- und Copyright-Angaben sollten vor externer oder kommerziell relevanter Veröffentlichung menschlich beziehungsweise rechtlich geprüft werden.
- Bei Änderungen an Modell-, Tool-, Filter-, Dashboard- oder Deployment-Logik muss mindestens `python scripts/verify_openwebui_workspace.py` erneut laufen. Bei Compose-Änderungen zusätzlich `python scripts/verify_openwebui_workspace.py --include-docker-compose`, wenn Docker verfügbar ist.
