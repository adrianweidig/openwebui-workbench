# Workbench Dashboard

🌐 Sprachen: [Deutsch](WORKBENCH_DASHBOARD.md) | [English](en/WORKBENCH_DASHBOARD.md)

Das Dashboard ist der schnellste Weg, die OpenWebUI-Modellpakete in diesem Repository zu pflegen.

OpenWebUI bleibt die Chat- und Runtime-Instanz. Die Workbench läuft daneben als lokales Dashboard und bearbeitet die Dateien, aus denen Custom-GPT-ähnliche OpenWebUI-Modelle gebaut und synchronisiert werden.

## Start

```powershell
python scripts/init_workbench_env.py
python scripts/check_workbench_setup.py
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

Danach öffnen:

```text
http://localhost:8088
```

Die Standard-Compose-Datei startet genau einen Container: `workbench`.

Setze `OPENWEBUI_BASE_URL` in `.env` auf die OpenWebUI-Instanz, die der Container erreichen soll. Wenn OpenWebUI auf dem Host läuft, reicht bei Docker Desktop meist:

```env
OPENWEBUI_BASE_URL=http://host.docker.internal:3000
OPENWEBUI_PUBLIC_URL=http://localhost:3000
```

## Was bearbeitet wird

Im Dashboard pflegst du:

- `mainprompt.md`
- `fachwissen.md`
- `Golden_Example.*`
- Beispiele unter `beispiele/`
- das jeweilige `model.json`
- Tools unter `Tools/openwebui_ext/tools/`
- Filter unter `Tools/openwebui_ext/filters/`
- Skills unter `Tools/openwebui_ext/skills/`
- Promptvorlagen unter `Tools/openwebui_ext/prompts/`

Das Repository bleibt die Quelle der Wahrheit.

## Model Settings

Jedes Modell hat einen Tab **Einstellungen**. Dort passt du ein Modell an deine OpenWebUI-Umgebung an.

Typische Felder:

- `base_model_id`
- Name, Beschreibung und Tags
- Capabilities
- `toolIds`, `filterIds` und `skillIds`
- `params.temperature`
- `params.top_p`
- `params.stop`
- `params.function_calling`
- `params.reasoning_effort`
- `params.parallel_tool_calls`
- Raw JSON für Felder ohne Formularfeld

Nach dem Speichern Importartefakte neu erzeugen und den Import prüfen.

## Sync-Ablauf

1. Modelldateien oder Einstellungen ändern.
2. Speichern.
3. **Artefakte neu erzeugen** ausführen.
4. **Import prüfen** ausführen.
5. `OPENWEBUI_ADMIN_TOKEN` oder `OPENWEBUI_ADMIN_TOKEN_FILE` nur setzen, wenn ein echter API-Sync gewünscht ist.
6. **Zu OpenWebUI synchronisieren** ausführen.

Ohne Admin-Token bleibt die Workbench ein Editor und Artefaktgenerator.

## Modellstatus

Die Workbench kann lokale Modelldefinitionen mit OpenWebUI vergleichen.

Statuswerte:

- `identical`: lokale Felder und OpenWebUI-Felder passen zusammen
- `local_only`: Modell existiert nur im Repository
- `remote_only`: Modell existiert nur in OpenWebUI
- `conflict`: beide Seiten existieren, verwaltete Felder unterscheiden sich
- `remote_inactive`: OpenWebUI meldet das Modell als inaktiv oder gelöscht
- `read_error`: OpenWebUI konnte nicht sauber gelesen werden

Die Workbench zieht Remote-Modelle nicht destruktiv ins Repository. Remote-only-Modelle erscheinen als schreibgeschützte Snapshots.

## Sicherheit

- Compose bindet das Dashboard an `127.0.0.1`.
- Compose verlangt Dashboard-Authentifizierung.
- Tokens werden nur aus Umgebungsvariablen oder Token-Dateien gelesen.
- Schreibende API-Routen verlangen den Same-Origin-Header der Dashboard-UI.
- Dashboard-Aktionen führen feste Repository-Kommandos aus, keine frei eingegebenen Shell-Befehle.

## Validierung

```powershell
python scripts/verify_openwebui_workspace.py
python -m unittest discover Workbench.dashboard.tests
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml config
```
