# Workbench Dashboard

🌐 Sprachen: [Deutsch](README.md) | [English](../docs/en/WORKBENCH_DASHBOARD.md)

`Workbench/dashboard` ist die lokale Verwaltungsoberfläche für dieses Repository. Der Service liest und schreibt direkt im gemounteten Repository-Volume und macht damit die Markdown-Dateien unter `Modelle/einzelmodelle/`, die Tool-Quellen unter `Tools/openwebui_ext/tools/` und die Skills unter `Tools/openwebui_ext/skills/` zur zentralen Quelle für Systemprompts, Mainprompts, Fachwissen, Beispiele, Tools und Modellpflege.

## Start lokal

```powershell
python -m Workbench.dashboard.server --host 127.0.0.1 --port 8088
```

Danach ist das Dashboard unter `http://127.0.0.1:8088` erreichbar.
Ohne expliziten `--host` bindet der Direktstart ebenfalls nur an `127.0.0.1`.
Wenn ein anderer Host wie `0.0.0.0` oder eine LAN-Adresse gesetzt wird, startet der Server nur mit gesetztem `WORKBENCH_AUTH_USERNAME` und `WORKBENCH_AUTH_PASSWORD` oder `WORKBENCH_AUTH_PASSWORD_FILE`.
Ungültige Runtime-Werte wie `WORKBENCH_PORT=abc`, `WORKBENCH_MAX_BODY_BYTES=abc`, `WORKBENCH_COMMAND_TIMEOUT_SECONDS=abc`, `OPENWEBUI_TLS_VERIFY=maybe`, `OPENWEBUI_BASE_URL=localhost:3000` oder ein nicht lesbarer `WORKBENCH_AUTH_PASSWORD_FILE` werden beim Direktstart als kurze Startup-Fehler ausgegeben; vorab prüft `python scripts/check_workbench_setup.py` dieselben Werte ohne Serverstart.
Wenn Host oder Port nicht gebunden werden können, etwa weil `8088` bereits belegt ist, endet der Direktstart ebenfalls mit einer kurzen Startup-Meldung statt einem Python-Traceback.

Optional schützt der Server alle Routen per HTTP Basic Auth:

```powershell
$env:WORKBENCH_AUTH_USERNAME="workbench"
$env:WORKBENCH_AUTH_PASSWORD=Read-Host "Workbench-Passwort"
python -m Workbench.dashboard.server --host 127.0.0.1 --port 8088
```

## Start mit Docker Compose

```powershell
python scripts/init_workbench_env.py
python scripts/init_workbench_env.py --check
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

Standardports:

- OpenWebUI: `http://localhost:3000`
- Workbench Dashboard: `http://localhost:8088`

Wenn OpenWebUI bereits außerhalb dieses Compose-Projekts läuft:

```powershell
$env:OPENWEBUI_BASE_URL="http://host.docker.internal:3000"
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build workbench
```

Für den API-Sync wird ein OpenWebUI-Admin-API-Key über `OPENWEBUI_ADMIN_TOKEN` oder `OPENWEBUI_ADMIN_TOKEN_FILE` erwartet. Der Token wird nicht in Antworten ausgegeben und gehört nicht ins Repository.

## Dashboard-Funktionen

- Modellpakete aus `Modelle/einzelmodelle/` anzeigen.
- Freigegebene Markdown-Dateien eines Modellpakets bearbeiten:
  - `systemprompt.md`
  - `mainprompt.md`
  - `fachwissen.md`
  - modellseitig definierte Beispielergebnis-Datei, zum Beispiel `beispielergebnis.md`, `beispielergebnis.html` oder `beispielergebnis.json`
  - `customgpt_infos.md`
  - `beispiele/*.md`
- Tool-Quellen unter `Tools/openwebui_ext/tools/*.py` bearbeiten.
- Skill-Markdown unter `Tools/openwebui_ext/skills/*.md` bearbeiten.
- Markdown-Dateien im Split-, Editor- oder Viewer-Modus lesen.
- Python-Tools mit Syntax-Highlighting in der Vorschau prüfen.
- Dunkles Standard-Theme nutzen und bei Bedarf lokal auf Light umschalten.
- Deutsch als Standardsprache nutzen und über die Sprachwahl oder `WORKBENCH_LOCALE=en` auf Englisch umschalten.
- Dist-Artefakte neu erzeugen.
- Import-Payload lokal prüfen.
- Tools, Filter, Skills, Knowledge und Modelle zur konfigurierten OpenWebUI-Instanz als Hintergrundjob synchronisieren.
- Zentrale Workspace-Verifikation starten.

OpenWebUI-Syncs blockieren die Dashboard-Oberfläche nicht. Ein laufender Sync wird wiederverwendet, wenn derselbe Import erneut ausgelöst wird; parallele Importprozesse werden dadurch vermieden.

## HTTPS und lokale Zertifikate

Wenn die Workbench OpenWebUI über eine lokale HTTPS-Adresse wie `https://openwebui.top.secret` erreicht, kann sie private Zertifikate explizit vertrauen oder für eine rein lokale Testinstanz die TLS-Prüfung deaktivieren:

```powershell
$env:OPENWEBUI_BASE_URL="https://openwebui.top.secret"
$env:OPENWEBUI_PUBLIC_URL="https://openwebui.top.secret"
$env:OPENWEBUI_CA_FILE="C:\Pfad\zur\local-ca.pem"
```

Nur für vertrauenswürdige lokale Endpunkte:

```powershell
$env:OPENWEBUI_TLS_VERIFY="false"
```

## Sicherheitsgrenzen

Das Dashboard ist für lokale Nutzung gedacht. Die Compose-Datei bindet es bewusst nur an `127.0.0.1`. Bei gesetztem `WORKBENCH_AUTH_USERNAME` und `WORKBENCH_AUTH_PASSWORD` oder `WORKBENCH_AUTH_PASSWORD_FILE` nutzt es HTTP Basic Auth. Der Direktstart blockiert Nicht-Loopback-Bindings ohne diese Auth-Konfiguration.
