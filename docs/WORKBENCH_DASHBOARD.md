# Workbench Dashboard

Das Workbench Dashboard macht dieses Repository zur aktiven Verwaltungsoberfläche für eine OpenWebUI-Instanz. OpenWebUI bleibt der Chat- und Runtime-Container; die Workbench läuft daneben als zweiter Container und verwaltet die Quellen, aus denen Tools, Filter, Skills, Knowledge und Modellprofile erzeugt und synchronisiert werden.

## Zielbild

```text
Browser
  |-- http://localhost:3000  -> OpenWebUI
  `-- http://localhost:8088  -> Workbench Dashboard

Docker Compose
  |-- openwebui  -> /app/backend/data
  `-- workbench  -> /workspace  (dieses Repository als Volume)
```

Die bearbeitbare Quelle bleibt das Repository:

- `Modelle/einzelmodelle/<modell>/systemprompt.md`
- `Modelle/einzelmodelle/<modell>/mainprompt.md`
- `Modelle/einzelmodelle/<modell>/fachwissen.md`
- `Modelle/einzelmodelle/<modell>/beispielergebnis.md`
- `Modelle/einzelmodelle/<modell>/beispiele/*.md`
- `Tools/openwebui_ext/tools/*.py`
- `Tools/openwebui_ext/skills/*.md`
- `Tools/dist/`
- `Modelle/dist/`

## Compose-Start

```powershell
Copy-Item Deployment/workbench.env.example .env
notepad .env
docker compose -f Deployment/docker-compose.workbench.yml up -d --build
```

Danach:

- OpenWebUI: `http://localhost:3000`
- Workbench: `http://localhost:8088`

Die OpenWebUI-Image-Referenz folgt der offiziellen Docker-Dokumentation und nutzt `ghcr.io/open-webui/open-webui:main` als Default.

## Lokale `top.secret`-Adresse

Wenn auf der Maschine bereits der lokale `top.secret`-Edge-Proxy läuft, kann die Workbench ohne Port über `https://workbench.top.secret` erreichbar gemacht werden:

```powershell
docker compose -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.top-secret.yml up -d --build workbench
```

Voraussetzungen außerhalb dieses Repositorys:

- Windows-Hostsfile: `127.0.0.1 workbench.top.secret`, optional per `powershell -ExecutionPolicy Bypass -File Deployment/enable-workbench-top-secret.ps1`
- Edge-Netzwerk: `ki_infra_seu_test` oder per `TOPSECRET_EDGE_NETWORK` gesetzt
- Nginx-Route im Edge-Proxy nach `http://workbench:8088`

Der Nginx-Server-Block dafür liegt als Vorlage unter [`../Deployment/top-secret-nginx.workbench.conf`](../Deployment/top-secret-nginx.workbench.conf). Die Adresse ist für lokale Nutzung gedacht; das Dashboard hat keine eigene Authentifizierung.

## Nur Workbench zu vorhandener OpenWebUI-Instanz starten

Wenn OpenWebUI schon als anderer Container oder Hostprozess läuft:

```powershell
$env:OPENWEBUI_BASE_URL="http://host.docker.internal:3000"
$env:OPENWEBUI_PUBLIC_URL="http://localhost:3000"
docker compose -f Deployment/docker-compose.workbench.yml up -d --build workbench
```

Unter Linux kann statt `host.docker.internal` auch eine konkrete Host-IP verwendet werden. Die Compose-Datei enthält zusätzlich `host-gateway`, damit `host.docker.internal` in aktuellen Docker-Installationen funktioniert.

## Arbeitsablauf

1. Modell im Dashboard auswählen.
2. `systemprompt.md`, `mainprompt.md`, `fachwissen.md` oder Beispiele direkt im Markdown-Editor ändern und im Viewer prüfen.
3. Datei speichern.
4. Optional Tools unter `Tools/openwebui_ext/tools/*.py` oder Skills unter `Tools/openwebui_ext/skills/*.md` im Dashboard bearbeiten. Python-Tools werden in der Vorschau mit Syntax-Highlighting angezeigt.
5. `Artefakte neu erzeugen` ausführen.
6. `Import prüfen` ausführen.
7. Mit gesetztem `OPENWEBUI_ADMIN_TOKEN` `Zu OpenWebUI synchronisieren` ausführen.

Der Sync verwendet die vorhandenen Skripte:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.example.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --base-url <OPENWEBUI_BASE_URL> --token <OPENWEBUI_ADMIN_TOKEN>
```

## Konfiguration

| Variable | Zweck |
|---|---|
| `OPENWEBUI_BASE_URL` | URL, die der Workbench-Container zur OpenWebUI-API nutzt. Im Compose-Stack `http://openwebui:8080`. |
| `OPENWEBUI_PUBLIC_URL` | Browser-Link im Dashboard, meist `http://localhost:3000`. |
| `OPENWEBUI_TLS_VERIFY` | `true` prüft HTTPS-Zertifikate. Für vertrauenswürdige lokale Self-Signed-Endpunkte kann `false` gesetzt werden. |
| `OPENWEBUI_CA_FILE` | Optionaler CA-Bundle-Pfad für private lokale OpenWebUI-Zertifikate. |
| `OPENWEBUI_CA_PATH` | Optionales CA-Verzeichnis für private lokale OpenWebUI-Zertifikate. |
| `OPENWEBUI_ADMIN_TOKEN` | Admin-API-Key für echte Synchronisierung. Nicht nötig für Lesen, Bearbeiten, Generieren oder Dry-Run. |
| `OPENWEBUI_ADMIN_TOKEN_FILE` | Alternativer Pfad zu einer Token-Datei im Container. |
| `WEBUI_SECRET_KEY` | Stabiler lokaler OpenWebUI-Secret-Key, damit Sessions nach Container-Neustarts erhalten bleiben. |
| `WORKBENCH_ALLOW_WRITE` | `true` erlaubt Markdown-Schreibzugriff. |
| `WORKBENCH_COMMAND_TIMEOUT_SECONDS` | Timeout für Generator-, Import- und Verify-Aktionen. |

## Sicherheit

- Das Dashboard ist in der Compose-Datei nur an `127.0.0.1` gebunden.
- Es hat keine eigene Authentifizierung.
- Dark Mode ist der Standard; die Theme-Auswahl bleibt lokal im Browser gespeichert.
- API-Token werden nur über Umgebung oder Token-Datei gelesen und in Aktionsausgaben redigiert.
- Für HTTPS zu OpenWebUI wird Zertifikatsprüfung standardmäßig beibehalten. Eine deaktivierte Prüfung ist nur für lokale, vertrauenswürdige Testendpunkte vorgesehen.
- Es werden keine frei eingegebenen Shell-Befehle ausgeführt; Dashboard-Aktionen sind fest verdrahtete Repository-Kommandos.
- Markdown-Schreibzugriff ist auf freigegebene Dateien innerhalb eines Modellpakets begrenzt.
- Tool- und Skill-Schreibzugriff ist auf existierende Dateien unter `Tools/openwebui_ext/tools/*.py` und `Tools/openwebui_ext/skills/*.md` begrenzt.

## Validierung

```powershell
python scripts/verify_openwebui_workspace.py
python -m unittest discover Workbench.dashboard.tests
docker compose -f Deployment/docker-compose.workbench.yml config
```

Die Docker-Prüfung ist optional und erfordert eine lokale Docker-Installation.
