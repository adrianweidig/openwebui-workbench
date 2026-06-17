# OpenWebUI Workbench

Sprachen: [English](README.md) | [Deutsch](README.de.md)

![OpenWebUI Workbench Hero](docs/assets/openwebui-workbench-hero.png)

[![CI](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/ci.yml)
[![CodeQL](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/codeql.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/codeql.yml)
[![Dependency Review](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/dependency-review.yml)
[![Security Scorecard](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/security-scorecard.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/security-scorecard.yml)
[![Release Artifact](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/release-artifact.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/release-artifact.yml)
[![Docker](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/docker-workbench-dashboard.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/docker-workbench-dashboard.yml)
[![License](https://img.shields.io/github/license/adrianweidig/openwebui-workbench)](LICENSE)

OpenWebUI Workbench ist eine Sammlung fertiger Custom-GPT-ähnlicher Modelle für OpenWebUI.

Die Idee ist einfach: Nutzer wählen ein Aufgabenmodell, beschreiben ihr Problem und bekommen direkt eine starke erste Antwort. Sie müssen nicht erst lange mit einem leeren Basismodell über Rolle, Format, Fachwissen und Vorgehen diskutieren. Jedes Modell bringt die Dinge mit, die in der Praxis den Unterschied machen: Fachwissen, Hauptprompt, Systemprompt, Beispiele, passende Tools, Filter, Skills und Model Settings.

Die enthaltenen Prompts und Wissensdateien wurden mit GPT-5.5 Pro erzeugt und geschärft, damit dieses Verhalten lokal in OpenWebUI nutzbar ist, auch in privaten oder Air-Gap-Umgebungen.

## Was Du Bekommst

- Aufgabenmodelle für Code-Review, Debugging, Dokumentanalyse, Dokumenterstellung, n8n-Workflows, Testfälle, Präsentationen, Datenanalyse, Lokalisierung, Support-Tickets und mehr.
- Pro Modell eine editierbare `model.json` mit `base_model_id`, Name, Tags, Fähigkeiten, Tools, Filtern, Skills und Laufzeitparametern wie `temperature`, `top_p`, `reasoning_effort` und `parallel_tool_calls`.
- `mainprompt.md`, `fachwissen.md` und `Golden_Example.*` als verpflichtender Modellkontext beim API-Import.
- Importierbare OpenWebUI-Artefakte unter `Modelle/dist/` und `Tools/dist/`.
- Ein lokales Workbench-Dashboard zum Bearbeiten von Modell-Dateien, Model Settings, Tools, Filtern, Skills, Prompt-Templates und Importartefakten.
- Offline-freundliche Defaults. Netzwerkfähige Tools existieren, sind aber nicht Teil des sicheren Standardimports.

## Schnellstart

Voraussetzungen:

- Docker mit Docker Compose
- Python 3.10 oder neuer
- ein OpenWebUI-Basismodell unter der Modell-ID, die Du nutzen willst. Repository-Default ist `coder`; zeige diese ID auf Dein bevorzugtes lokales Modell oder ändere sie pro Modell im Dashboard.

Workbench-Dashboard starten:

```powershell
python scripts/init_workbench_env.py
python scripts/check_workbench_setup.py
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

Öffnen:

- Workbench: `http://localhost:8088`
- OpenWebUI: die URL aus Deiner `.env`, meist `http://localhost:3000`

`Deployment/docker-compose.workbench.yml` startet genau einen Container: das Workbench-Dashboard. Es startet und ersetzt keinen OpenWebUI-Server. Setze `OPENWEBUI_BASE_URL` auf die OpenWebUI-Instanz, die Du bereits nutzt.

## Modell Importieren

1. Workbench-Dashboard öffnen.
2. Modell unter `Modelle/einzelmodelle/` auswählen.
3. Tab **Model Settings** öffnen.
4. `base_model_id` auf Dein lokales OpenWebUI-Modell setzen, zum Beispiel `coder`, `mistral-medium-3.5-128b` oder eine andere Modell-ID aus Deiner Instanz.
5. Bei Bedarf Temperature, `top_p`, Tools, Filter, Skills, Tags oder Fähigkeiten anpassen.
6. Speichern und Importartefakte neu erzeugen.
7. Über die Dashboard-Sync-Aktion importieren oder `Modelle/dist/openwebui-models-import.json` manuell in OpenWebUI nutzen.

Der API-Import ist der beste Weg. Er lädt Prompt- und Wissensdateien als echte OpenWebUI-Dateien hoch und hält Modellprofil, Tools, Filter, Skills und Knowledge-Verknüpfung zusammen.

## Täglicher Ablauf

Nutze die Workbench als kleine Steuerzentrale für OpenWebUI-Modellpakete:

- Prompts und Fachwissen als Markdown bearbeiten
- pro Modell die `model.json` abstimmen
- Importartefakte neu erzeugen
- Import trocken prüfen
- lokale Modelle mit OpenWebUI vergleichen
- Modelle, Tools, Filter, Skills und Prompt-Templates synchronisieren, wenn ein Admin-Token gesetzt ist

Das Repository bleibt die Quelle der Wahrheit. OpenWebUI ist die Laufzeitumgebung.

## Repository-Struktur

| Pfad | Zweck |
|---|---|
| `Modelle/einzelmodelle/` | Menschenlesbare Modellpakete |
| `Modelle/dist/` | Generierte OpenWebUI-Modellimporte |
| `Tools/openwebui_ext/` | Tools, Filter, Skills, Prompt-Templates, Doku und Tests |
| `Tools/dist/` | Generierte Tool-, Function-, Skill- und Prompt-Importe |
| `Workbench/dashboard/` | Lokales Dashboard-Backend und statische UI |
| `Deployment/docker-compose.workbench.yml` | Ein-Container-Deployment für die Workbench |
| `scripts/verify_openwebui_workspace.py` | Zentrale nicht-mutierende Prüfung |

## Lokal Prüfen

```powershell
python scripts/verify_openwebui_workspace.py
python scripts/check_security_hygiene.py --include-bandit
```

Diese Checks kompilieren Python-Dateien, prüfen OpenWebUI-Erweiterungen, validieren generierte Artefakte, führen Import-Dry-Runs aus, suchen nach secret-ähnlichen Werten und starten die Unit-Tests.

## Sicherheits-Defaults

- Es werden keine Secrets committed.
- Das Dashboard bindet in Compose an `127.0.0.1`.
- Dashboard-Auth ist im Compose-Pfad Pflicht.
- OpenWebUI-Admin-Tokens kommen nur aus Umgebungsvariablen oder Token-Dateien.
- Schreibende Sync-Aktionen brauchen explizite Konfiguration.
- GitHub prüft CI, CodeQL, Dependency Review, OpenSSF Scorecard, Docker-Build und Release-Artefakte.

Sensible Befunde bitte privat melden; siehe [`SECURITY.md`](SECURITY.md).

## Weitere Doku

- [`Deployment/README.md`](Deployment/README.md): einfache Deployment-Hinweise
- [`docs/WORKBENCH_DASHBOARD.md`](docs/WORKBENCH_DASHBOARD.md): Dashboard-Nutzung
- [`OPENWEBUI_EXTENSIONS.md`](OPENWEBUI_EXTENSIONS.md): Tools, Filter, Skills und Importdetails
- [`TESTING.md`](TESTING.md): Prüfkommandos
- [`README.md`](README.md): englische GitHub-README

## Lizenz

Apache License 2.0. Siehe [`LICENSE`](LICENSE). Drittanbieter-Hinweise stehen in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
