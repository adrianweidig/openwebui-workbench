# Workbench Dashboard

🌐 Sprachen: [Deutsch](WORKBENCH_DASHBOARD.md) | [English](en/WORKBENCH_DASHBOARD.md)

Das Workbench Dashboard macht dieses Repository zur aktiven Verwaltungsoberfläche für eine OpenWebUI-Instanz. OpenWebUI bleibt der Chat- und Runtime-Container; die Workbench läuft daneben als zweiter Container und verwaltet die Quellen, aus denen Tools, Functions/Filter, Skills, Promptvorlagen, Knowledge und Modellprofile erzeugt und synchronisiert werden.

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
- modellseitig definierte Beispielergebnis-Dateien wie `beispielergebnis.md`, `beispielergebnis.html` oder `beispielergebnis.json`
- freigegebene Beispiele unter `Modelle/einzelmodelle/<modell>/beispiele/`
- `Tools/openwebui_ext/tools/*.py`
- `Tools/openwebui_ext/filters/*.py`
- `Tools/openwebui_ext/skills/*.md`
- `Tools/openwebui_ext/prompts/*.md`
- `Tools/dist/`
- `Modelle/dist/`

## Compose-Start

```powershell
python scripts/init_workbench_env.py
python scripts/init_workbench_env.py --check
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

Der Init-Befehl erzeugt eine lokale, ignorierte `.env` aus `Deployment/workbench.env.example`, setzt zufällige Werte für `WEBUI_SECRET_KEY` und `WORKBENCH_AUTH_PASSWORD` und gibt diese Werte nicht auf der Konsole aus. Bestehende `.env`-Dateien werden ohne `--force` nicht überschrieben.

Die lokale `.env` muss für Compose/Portainer `WORKBENCH_REQUIRE_AUTH=true` sowie `WORKBENCH_AUTH_PASSWORD` oder eine gemountete `WORKBENCH_AUTH_PASSWORD_FILE` setzen. Ohne wirksame Authentifizierung beendet der Dashboard-Container den Start mit einer klaren Fehlermeldung; mit gesetztem Passwort schützt das Dashboard alle Routen per HTTP Basic Auth. `WORKBENCH_AUTH_USERNAME` ist optional und nutzt standardmäßig `workbench`.

Danach:

- OpenWebUI: `http://localhost:3000`
- Workbench: `http://localhost:8088`

Die OpenWebUI-Image-Referenz folgt der offiziellen Docker-Dokumentation und nutzt `ghcr.io/open-webui/open-webui:main` als Default.
Die Compose-Datei definiert Healthchecks für OpenWebUI und Workbench. Der Workbench-Healthcheck ruft `http://127.0.0.1:8088/healthz` im Container auf; dieser Endpunkt gibt nur einen minimalen Status zurück und benötigt keine Authentifizierung.

Kurzer Smoke-Check nach dem Start:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml ps
```

Beide Services sollten nach ihrer Startphase als healthy erscheinen. Falls nicht, zuerst die Service-Logs und danach `python scripts/verify_openwebui_workspace.py --include-docker-compose` prüfen.

## Lokale `top.secret`-Adresse

Wenn auf der Maschine bereits der lokale `top.secret`-Edge-Proxy läuft, kann die Workbench über `https://workbench.top.secret` erreichbar gemacht werden. Falls der lokale Edge nicht auf Host-Port 443 veröffentlicht ist, muss der veröffentlichte HTTPS-Port in der URL ergänzt werden, zum Beispiel `https://workbench.top.secret:25443`.

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.top-secret.yml up -d --build workbench
```

Voraussetzungen außerhalb dieses Repositorys:

- Windows-Hostsfile: `127.0.0.1 workbench.top.secret`, optional per `powershell -ExecutionPolicy Bypass -File Deployment/enable-workbench-top-secret.ps1`
- Edge-Netzwerk: `ki_infra_seu_test` oder per `TOPSECRET_EDGE_NETWORK` gesetzt
- Nginx-Route im Edge-Proxy nach `http://workbench:8088`

Der Nginx-Server-Block dafür liegt als Vorlage unter [`../Deployment/top-secret-nginx.workbench.conf`](../Deployment/top-secret-nginx.workbench.conf). Die Adresse ist für lokale Nutzung gedacht; vor der Nutzung über diese Adresse sollten `WORKBENCH_AUTH_USERNAME` und `WORKBENCH_AUTH_PASSWORD` oder `WORKBENCH_AUTH_PASSWORD_FILE` gesetzt sein.

## Nur Workbench zu vorhandener OpenWebUI-Instanz starten

Wenn OpenWebUI schon als anderer Container oder Hostprozess läuft:

```powershell
$env:OPENWEBUI_BASE_URL="http://host.docker.internal:3000"
$env:OPENWEBUI_PUBLIC_URL="http://localhost:3000"
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build workbench
```

Unter Linux kann statt `host.docker.internal` auch eine konkrete Host-IP verwendet werden. Die Compose-Datei enthält zusätzlich `host-gateway`, damit `host.docker.internal` in aktuellen Docker-Installationen funktioniert.

## Arbeitsablauf

1. Modell im Dashboard auswählen.
2. `systemprompt.md`, `mainprompt.md`, `fachwissen.md` oder Beispiele direkt im Markdown-Editor ändern und im Viewer prüfen.
3. Datei speichern.
4. Optional Tools, Functions/Filter, Skills oder Promptvorlagen im Ressourcenbereich bearbeiten. Lokale Dateien können dort entfernt werden; mit Admin-Token können ausgewählte Ressourcen zusätzlich aus OpenWebUI gelöscht werden.
5. `Artefakte neu erzeugen` ausführen.
6. `Import prüfen` ausführen.
7. Im Sync-Bereich bei Bedarf `Basismodelle laden` nutzen, das gewünschte OpenWebUI-Basismodell auswählen und mit gesetztem `OPENWEBUI_ADMIN_TOKEN` oder `OPENWEBUI_ADMIN_TOKEN_FILE` `Zu OpenWebUI synchronisieren` ausführen. Dieser Sync importiert alle Workbench-Modelle sowie Tools, Functions/Filter, Skills, Promptvorlagen, Pflichtdateien und Knowledge.
8. `Modellstatus vergleichen` ausführen, um die verwalteten Modellfelder der Workbench mit OpenWebUI zu vergleichen.
9. `OpenWebUI-Snapshot aktualisieren` ausführen, wenn OpenWebUI-only-Modelle in der Workbench sichtbar werden sollen.

Der echte OpenWebUI-Sync läuft im Dashboard als Hintergrundjob. Die Oberfläche bleibt währenddessen bedienbar; ein zweiter Sync-Klick startet keinen parallelen Import, sondern zeigt den laufenden Job weiter an.

## Bidirektionale Modellprüfung

Die Workbench bleibt die Schreibquelle für die versionierten Modellpakete unter `Modelle/einzelmodelle/`. Der bestehende API-Import spiegelt diese Pakete nach OpenWebUI. Für die Gegenrichtung gibt es bewusst keinen automatischen destruktiven Pull: `scripts/sync_openwebui_models.py` liest OpenWebUI über die API, vergleicht die verwalteten Felder `id`, `name`, `base_model_id`, `params` und die bekannten Workbench-`meta`-Schlüssel mit dem lokalen Modellstand und schreibt bei Bedarf einen prüfbaren Snapshot unter `Artefakte/openwebui_sync/`.

Die Statuswerte sind:

- `identical`: Workbench und OpenWebUI sind in den verwalteten Feldern gleich.
- `local_only`: Das Modell existiert nur lokal; ein Workbench-zu-OpenWebUI-Import kann es erzeugen.
- `remote_only`: Das Modell existiert nur in OpenWebUI; es wird als schreibgeschützter Snapshot in der Modellliste sichtbar.
- `conflict`: Beide Seiten enthalten denselben Modell-ID-Eintrag, aber verwaltete Werte unterscheiden sich. Keine Seite wird automatisch überschrieben.
- `remote_inactive`: OpenWebUI meldet das Modell als inaktiv; die Workbench übernimmt daraus keine Löschung.
- `read_error`: Eine Seite konnte nicht sauber gelesen werden.

CLI-Prüfung ohne lokale Schreibwirkung:

```powershell
python scripts/sync_openwebui_models.py --base-url https://openwebui.top.secret --token-file /run/secrets/openwebui-admin-token --ca-file /certs/top-secret-edge-root-ca.pem
```

CLI-Snapshot für die Workbench-Sicht:

```powershell
python scripts/sync_openwebui_models.py --base-url https://openwebui.top.secret --token-file /run/secrets/openwebui-admin-token --ca-file /certs/top-secret-edge-root-ca.pem --write-snapshot
```

Nach `--write-snapshot` liest das Dashboard `Artefakte/openwebui_sync/status.json`. Remote-only-Modelle erscheinen in der Modellliste mit dem Status `nur OpenWebUI`; der Editor bleibt für diese Einträge schreibgeschützt, damit keine lokale Modellquelle erfunden oder überschrieben wird.

Manuelle End-to-End-Prüfung:

1. Ausgangszustand mit `Modellstatus vergleichen` prüfen.
2. Neues lokales Modellpaket unter `Modelle/einzelmodelle/` anlegen oder ein bestehendes Modell ändern.
3. `Artefakte neu erzeugen`, `Import prüfen` und danach `Zu OpenWebUI synchronisieren` ausführen.
4. In OpenWebUI prüfen, ob der neue oder geänderte Eintrag sichtbar ist.
5. In OpenWebUI ein Testmodell direkt anlegen oder ein bestehendes Testmodell ändern.
6. `OpenWebUI-Snapshot aktualisieren` ausführen.
7. In der Workbench prüfen, ob das OpenWebUI-only-Modell oder der Konfliktstatus sichtbar ist.
8. Einen Konflikt erzeugen, indem dieselbe Modell-ID lokal und remote unterschiedlich geändert wird; `Modellstatus vergleichen` muss `conflict` melden und beide Seiten dürfen nicht automatisch überschrieben werden.
9. Ein Modell in OpenWebUI deaktivieren oder entfernen; der nächste Snapshot muss dies als `remote_inactive` oder `local_only` sichtbar machen, ohne lokale Dateien zu löschen.

## Automation

Beim normalen Dashboard-Start richtet die Workbench eine interne Automation ein. Der sichere Default ist ein nicht-mutierender Workspace-Check alle 30 Minuten (`WORKBENCH_AUTOMATION_ACTIONS=check`). Dadurch werden Status-, Generator-, JSON- und Unit-Test-Drift regelmäßig sichtbar, ohne Modelle oder OpenWebUI automatisch zu verändern.

Schreibende Automationsaktionen sind bewusst opt-in: `generate`, `import-dry-run` oder `import-openwebui` dürfen nur in `WORKBENCH_AUTOMATION_ACTIONS` ergänzt werden, wenn der Administrator die Schreib- beziehungsweise API-Wirkung akzeptiert und passende Tokens/Konfigurationen gesetzt hat. `sync-status` ist nicht-mutierend und kann bei Bedarf automatisiert werden; `pull-openwebui` schreibt lokale Snapshots und bleibt deshalb eine bewusste manuelle Aktion. Der Scheduler nutzt dieselben Job-Locks wie die manuelle UI; ein bereits laufender gleicher Job wird nicht parallel neu gestartet.

Ein manueller Lauf bleibt unabhängig vom Intervall möglich:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8088/api/automation/run -Headers @{ "X-Workbench-Request" = "same-origin" }
```

Bei aktivierter Basic Auth muss der Request zusätzlich die Dashboard-Zugangsdaten enthalten. Im Dashboard selbst bleiben die Aktionskarten unter `Sync` der bevorzugte manuelle Weg.

Der Sync verwendet die vorhandenen Skripte:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.example.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --base-url <OPENWEBUI_BASE_URL> --token <OPENWEBUI_ADMIN_TOKEN>
python scripts/sync_openwebui_models.py --base-url <OPENWEBUI_BASE_URL> --token-file <OPENWEBUI_ADMIN_TOKEN_FILE> --write-snapshot
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
| `OPENWEBUI_ADMIN_TOKEN_HOST_FILE` | Hostpfad für generierte Portainer-Stacks oder den optionalen Compose-Override `docker-compose.openwebui-admin-token-file.yml`, der read-only nach `OPENWEBUI_ADMIN_TOKEN_FILE` gemountet wird. |
| `WEBUI_SECRET_KEY` | Stabiler lokaler OpenWebUI-Secret-Key, damit Sessions nach Container-Neustarts erhalten bleiben. |
| `WORKBENCH_AUTH_USERNAME` | Benutzername für die HTTP-Basic-Auth des Dashboards. Standard in Compose: `workbench`. |
| `WORKBENCH_REQUIRE_AUTH` | `true` verlangt wirksame Dashboard-Authentifizierung beim Start. Compose/Portainer setzen dies standardmäßig. |
| `WORKBENCH_AUTH_PASSWORD` | Passwort für die HTTP-Basic-Auth des Dashboards. Alternative zu `WORKBENCH_AUTH_PASSWORD_FILE`; nicht committen. |
| `WORKBENCH_AUTH_PASSWORD_FILE` | Alternativer Pfad zu einer Passwortdatei im Container. |
| `WORKBENCH_AUTH_PASSWORD_HOST_FILE` | Hostpfad für generierte Portainer-Stacks oder den optionalen Compose-Override `docker-compose.workbench-password-file.yml`, der read-only nach `WORKBENCH_AUTH_PASSWORD_FILE` gemountet wird. |
| `WORKBENCH_ALLOW_WRITE` | `true` erlaubt Markdown-Schreibzugriff. |
| `WORKBENCH_COMMAND_TIMEOUT_SECONDS` | Timeout für Generator-, Dry-Run- und Verify-Aktionen. |
| `WORKBENCH_IMPORT_TIMEOUT_SECONDS` | Prozess-Timeout für den Hintergrund-Sync nach OpenWebUI. Standard: 1800 Sekunden, damit ein seltener Clean-Import nicht vom Dashboard abgebrochen wird. |
| `WORKBENCH_IMPORT_HTTP_TIMEOUT_SECONDS` | HTTP-Timeout pro OpenWebUI-API-Request während des Imports. Standard: 600 Sekunden. |
| `WORKBENCH_AUTOMATION_ENABLED` | Aktiviert die Dashboard-Automation. Standard: `true`. |
| `WORKBENCH_AUTOMATION_INTERVAL_MINUTES` | Intervall der Dashboard-Automation. Standard: `30`, erlaubter Bereich: `5` bis `1440`. |
| `WORKBENCH_AUTOMATION_ACTIONS` | Kommagetrennte Aktionen für automatische Läufe. Standard: `check`; erlaubte Werte: `check`, `generate`, `import-dry-run`, `import-openwebui`, `sync-status`. |
| `WORKBENCH_AUTOMATION_RUN_ON_START` | `true` startet den ersten Automationslauf sofort beim Dashboard-Start. Standard: `false`, damit Starts ruhig bleiben. |
| `WORKBENCH_LOCALE` | Standard-Locale des Dashboards, aktuell `de` oder `en`. Unbekannte Werte fallen auf Deutsch zurück. |

## Internationalisierung

Das Dashboard startet auf Deutsch und kann über die Sprachwahl oben rechts auf Englisch umgestellt werden. Die Auswahl wird lokal im Browser als `workbench-locale` gespeichert. Ohne manuelle Auswahl nutzt das Dashboard `WORKBENCH_LOCALE`, Browser-/HTTP-Sprache und System-Locale; wenn keine unterstützte Sprache ermittelt wird, bleibt Deutsch der Fallback.

UI-Texte liegen unter `Workbench/dashboard/static/locales/`. Server- und API-Meldungen liegen in `Workbench/dashboard/i18n.py`. Neue Sprachen müssen dieselben Schlüssel wie `de.json` bereitstellen und in den unterstützten Locales ergänzt werden.

## Sicherheit

- Das Dashboard ist in der Compose-Datei nur an `127.0.0.1` gebunden.
- Wenn `WORKBENCH_AUTH_USERNAME` und ein Passwort oder eine Passwortdatei gesetzt sind, schützt das Dashboard alle Routen per HTTP Basic Auth.
- Bei `WORKBENCH_REQUIRE_AUTH=true` startet das Dashboard ohne diese Auth-Konfiguration nicht.
- Ohne beide Auth-Variablen bleibt nur der Loopback-Entwicklerstart möglich; Nicht-Loopback-Bindings wie `0.0.0.0` werden beim Direktstart blockiert.
- Dark Mode ist der Standard; die Theme-Auswahl bleibt lokal im Browser gespeichert.
- API-Token werden nur über Umgebung oder Token-Datei gelesen und in Aktionsausgaben redigiert.
- Für HTTPS zu OpenWebUI wird Zertifikatsprüfung standardmäßig beibehalten. Eine deaktivierte Prüfung ist nur für lokale, vertrauenswürdige Testendpunkte vorgesehen.
- Es werden keine frei eingegebenen Shell-Befehle ausgeführt; Dashboard-Aktionen sind fest verdrahtete Repository-Kommandos.
- Schreibende API-Routen (`POST`, `PUT`, `DELETE`) verlangen zusätzlich den Header `X-Workbench-Request: same-origin`; die Dashboard-UI setzt ihn automatisch.
- Dashboard-Antworten setzen restriktive Browser-Security-Header wie `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options` und `Referrer-Policy`.
- Markdown-Schreibzugriff ist auf freigegebene Dateien innerhalb eines Modellpakets begrenzt.
- Tool- und Skill-Schreibzugriff ist auf existierende Dateien unter `Tools/openwebui_ext/tools/*.py` und `Tools/openwebui_ext/skills/*.md` begrenzt.

## Validierung

```powershell
python scripts/verify_openwebui_workspace.py
python -m unittest discover Workbench.dashboard.tests
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml config
```

Die Docker-Prüfung ist optional und erfordert eine lokale Docker-Installation. Wenn Docker nur in WSL verfügbar ist, kann der Setup-Doctor den Pfad nicht-mutierend prüfen:

```powershell
python scripts/check_workbench_setup.py --docker-command "wsl.exe -d Debian -- docker" --require-docker
```

Dieser Preflight führt `docker compose version` aus und meldet einen deaktivierten `WSLService` oder nicht erreichbaren WSL-Docker-Pfad, ohne Container zu starten.
