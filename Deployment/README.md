# Offline OpenWebUI Deployment

Dieses Verzeichnis enthält lokale Vorlagen für einen offline nutzbaren OpenWebUI-Betrieb mit eigenem Jupyter-Server, persistenten Modellen, Tools, Skills und Artefakten.

## Compose-Varianten

- `docker-compose.workbench.yml`: Standardstart für OpenWebUI plus Workbench-Dashboard. Das Repository wird als `/workspace` in den Workbench-Container gemountet, damit Modell-Markdown-Dateien, Dist-Artefakte und Sync-Aktionen zentral verwaltet werden können. Das Workbench-Image enthält zusätzlich einen gebündelten Workspace-Snapshot inklusive `istqb-testfallgenerator`, `testprogrammierung` und generierten Dist-Artefakten; wenn `/workspace` beim Erststart noch keinen Modell-Workspace enthält, wird dieser Snapshot initialisiert.
- `docker-compose.shared-targets.yml`: Workbench-only-Start für eine bestehende gemeinsame WSL-/Portainer-Runtime. Diese Variante erstellt keinen OpenWebUI-, RAGFlow- oder Seafile-Container, sondern hängt die Workbench an `WORKBENCH_SHARED_DOCKER_NETWORK` und nutzt die vorhandenen Docker-DNS-Namen.
- `docker-compose.workbench-password-file.yml`: optionaler Override, der `WORKBENCH_AUTH_PASSWORD_HOST_FILE` read-only nach `WORKBENCH_AUTH_PASSWORD_FILE` in den Workbench-Container mountet.
- `docker-compose.openwebui-admin-token-file.yml`: optionaler Override, der `OPENWEBUI_ADMIN_TOKEN_HOST_FILE` read-only nach `OPENWEBUI_ADMIN_TOKEN_FILE` in den Workbench-Container mountet.
- `docker-compose.enterprise-ca.yml`: optionaler Override für Unternehmensnetze mit eigener Root-CA. Die CA wird in OpenWebUI und Workbench gemountet; der Workbench-Container aktualisiert den System-Truststore bei jedem Start.
- `docker-compose.shared-targets-enterprise-ca.yml`: optionaler CA-Override für `docker-compose.shared-targets.yml`. Diese Variante mountet die Root-CA nur in den Workbench-Container und erzeugt keine OpenWebUI-, RAGFlow- oder Seafile-Services.
- `docker-compose.top-secret.yml`: optionaler lokaler Override, der den Workbench-Container zusätzlich an das bestehende `top.secret`-Edge-Netz hängt und dort als `workbench` sowie `workbench.top.secret` verfügbar macht.
- `docker-compose.openwebui-offline.example.yml`: portable Offline-Beispielvorlage mit repo-relativen Mounts, named volumes und optional überschreibbaren OpenWebUI-/Jupyter-Images.
- `workbench.torvs-bw.env.example`: secretfreies Overlay für die produktive Übergabe mit OpenWebUI unter `https://lexi.torvs.bw`, RAGFlow unter `https://rag.torvs.bw` und Seafile unter `https://seafile.torvs.bw`.

Start der neuen Workbench-Umgebung:

```powershell
python scripts/init_workbench_env.py
python scripts/init_workbench_env.py --check
python scripts/check_workbench_setup.py
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

Für den Parallelbetrieb mit einem zweiten Agenten und bestehenden gemeinsamen Zielcontainern ist stattdessen die Shared-Targets-Variante vorgesehen:

```powershell
python scripts/init_workbench_env.py
$env:WORKBENCH_SHARED_DOCKER_NETWORK="ki_infra_seu_test"
$env:OPENWEBUI_BASE_URL="http://openwebui:8080"
$env:OPENWEBUI_PUBLIC_URL="https://openwebui.top.secret"
$env:RAGFLOW_BASE_URL="http://ragflow"
$env:SEAFILE_BASE_URL="http://seafile"
docker compose --env-file .env -f Deployment/docker-compose.shared-targets.yml up -d --build
```

Diese Variante erzeugt ausschließlich den agentenspezifischen Workbench-Container `openwebui-workbench` mit eigenem Host-Port `WORKBENCH_PORT` und nutzt das externe Netzwerk `WORKBENCH_SHARED_DOCKER_NETWORK`. Die Zielcontainer bleiben extern: OpenWebUI wird über `OPENWEBUI_BASE_URL`, RAGFlow über `RAGFLOW_BASE_URL` und Seafile über `SEAFILE_BASE_URL` adressiert. Der Workbench-Stack darf diese gemeinsamen Zielcontainer nicht neu erzeugen, ersetzen oder über eigene Volumes überschreiben. Setze `RAGFLOW_BASE_URL` auf den im gemeinsamen Stack wirklich lauschenden internen HTTP-Endpunkt; im lokalen `ki_infra_seu_test` ist das `http://ki-test-ragflow` beziehungsweise der Docker-DNS-Alias `http://ragflow`, nicht Port `9380`.
`OPENWEBUI_PUBLIC_URL` ist in dieser Variante bewusst Pflicht und muss auf die browserseitig erreichbare Adresse des gemeinsamen OpenWebUI-Zielcontainers zeigen, zum Beispiel den lokalen Edge-Host `https://openwebui.top.secret`. Nutze `http://localhost:3000` nur, wenn dieser Host-Port nachweislich auf denselben gemeinsamen OpenWebUI-Zielcontainer zeigt; ein alter separater Workbench-OpenWebUI-Container darf dadurch nicht als Zielsystem getarnt werden.

`scripts/init_workbench_env.py` erzeugt eine ignorierte lokale `.env` aus `Deployment/workbench.env.example` und füllt `WEBUI_SECRET_KEY` sowie `WORKBENCH_AUTH_PASSWORD` mit zufälligen lokalen Werten. Bestehende `.env`-Dateien werden ohne `--force` nicht überschrieben, und Secret-Werte werden nicht auf der Konsole ausgegeben. `WORKBENCH_AUTH_USERNAME` fällt sonst auf `workbench` zurück. Für Portainer oder Docker-Secrets kann statt `WORKBENCH_AUTH_PASSWORD` eine gemountete Datei über `WORKBENCH_AUTH_PASSWORD_FILE` genutzt werden. Compose und der Portainer-Wizard setzen `WORKBENCH_REQUIRE_AUTH=true`; der Dashboard-Container startet dann erst, wenn Benutzername und Passwort oder Passwortdatei wirksam konfiguriert sind.
`scripts/check_workbench_setup.py` ist der nicht-mutierende Setup-Doctor für Administratoren: Er prüft Python-Version, Env-Vorlage, lokale `.env`, Host-Portwerte, OpenWebUI-URLs, optionale Portainer-/RAGFlow-/Seafile-URLs, boolesche Flags, numerische Runtime-Grenzen, dateibasierte Runtime-Pfade, Compose-Datei und Docker-Verfügbarkeit, ohne Dienste zu starten oder Secret-Werte auszugeben. Mit `--probe-runtime` werden OpenWebUI und optional Portainer zusätzlich per HTTP geprüft; fehlendes Docker ist standardmäßig eine Warnung und kann mit `--require-docker` für Installationsabnahmen als Fehler gewertet werden.
Wenn Docker unter Windows nicht in der PATH liegt, aber `wsl.exe` verfügbar ist, meldet der Setup-Doctor diesen WSL-Pfad ausdrücklich. Führe `--require-docker`, `--run-compose-config` und die echten Compose-Starts dann in der WSL-Umgebung mit Docker aus.
Wenn der Aufruf aus Windows heraus trotzdem die WSL-Docker-Installation nutzen soll, kann der Docker-Befehl für nicht-mutierende Compose-Prüfungen explizit gesetzt werden:

```powershell
python scripts/check_workbench_setup.py --docker-command "wsl.exe -d Debian -- docker" --require-docker --run-compose-config
python scripts/verify_openwebui_workspace.py --include-docker-compose --docker-command "wsl.exe -d Debian -- docker"
```

Der Setup-Doctor führt bei explizitem `--docker-command` zusätzlich `docker compose version` aus. Ein deaktivierter `WSLService` oder ein nicht erreichbarer WSL-Docker-Pfad wird damit als Preflight-Fehler gemeldet, bevor Compose-Konfigurationen oder Containerstarts versucht werden.
Für Portainer-Hostpfade, die vom Windows-Generator nicht lokal gelesen werden können, kann dieselbe Prüfung bewusst als Hostpfad-Warnung laufen:

```powershell
python scripts/check_workbench_setup.py --allow-unverified-root-ca-path
python scripts/check_workbench_setup.py --allow-unverified-root-ca-path --allow-unverified-secret-file-path
```

Dieser Schalter ersetzt keine CA-Prüfung: lokal lesbare PEM-Dateien werden weiterhin validiert, und der Admin muss die Datei auf dem Docker-/Portainer-Host vor dem Stack-Start prüfen.
Der Secret-Dateipfad-Schalter gilt für `WORKBENCH_AUTH_PASSWORD_HOST_FILE` und `OPENWEBUI_ADMIN_TOKEN_HOST_FILE`: lokal lesbare Secret-Dateipfade werden als Datei geprüft, aber Secret-Dateiinhalte werden nicht gelesen oder ausgegeben.

Für lokale Docker-Compose-Starts ohne direkte Secret-Werte in `.env` können die dateibasierten Overrides getrennt zugeschaltet werden. So bleibt die Passwortdatei unabhängig vom optionalen OpenWebUI-Admin-Token nutzbar:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.workbench-password-file.yml up -d --build
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.openwebui-admin-token-file.yml up -d --build workbench
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.workbench-password-file.yml -f Deployment/docker-compose.openwebui-admin-token-file.yml up -d --build workbench
```

Bei Nutzung beider Dateien müssen in `.env` die jeweiligen Host- und Containerpfade gesetzt sein: `WORKBENCH_AUTH_PASSWORD_HOST_FILE` plus `WORKBENCH_AUTH_PASSWORD_FILE` beziehungsweise `OPENWEBUI_ADMIN_TOKEN_HOST_FILE` plus `OPENWEBUI_ADMIN_TOKEN_FILE`.
Der Setup-Doctor kann dieselbe Kombination vor dem Start nicht-mutierend rendern:

```powershell
python scripts/check_workbench_setup.py --require-docker --run-compose-config --compose-override Deployment/docker-compose.workbench-password-file.yml --compose-override Deployment/docker-compose.openwebui-admin-token-file.yml
```

Für Abnahmen nach einem Stack-Start kann der Setup-Doctor zusätzlich nicht-mutierende HTTP-Probes ausführen. Ohne `--require-runtime` sind nicht erreichbare Dienste Warnungen; mit `--require-runtime` werden sie zu Fehlern:

```powershell
python scripts/check_workbench_setup.py --probe-runtime --portainer-url https://portainer.top.secret
python scripts/check_workbench_setup.py --probe-runtime --require-runtime --portainer-url https://portainer.top.secret
```

Der Probe ruft keine Admin-APIs mit Token auf. OpenWebUI wird über `OPENWEBUI_PUBLIC_URL` geprüft, Portainer über `--portainer-url` oder `PORTAINER_URL` in der lokalen `.env`; der CLI-Wert hat Vorrang. HTTP 401/403 zählt als erreichbar, weil damit der Dienst antwortet und Auth verlangt. Der Portainer-Wizard kann `PORTAINER_URL` direkt in die generierte `workbench.env` schreiben, damit derselbe Wert für spätere Setup-Doctor-Abnahmen verfügbar ist.
Wenn der Probe bei einer privaten Edge-CA mit `CA cert does not include key usage extension` fehlschlägt, ist nicht die Workbench-URL das Problem, sondern die Root-CA. Erzeuge oder installiere eine Root-CA mit gültiger Key-Usage für CA-Zertifikate, insbesondere `keyCertSign`, und stelle sie über `OPENWEBUI_CA_FILE` oder `OPENWEBUI_CA_PATH` bereit. `OPENWEBUI_TLS_VERIFY=false` bleibt nur eine kurzlebige lokale Diagnoseoption.

Scharfe KI-Smoke-Tests laufen nicht gegen lokale Modelle. Wenn ein Administrator echte Modellinferenz prüfen will, werden die Provider-Keys nur für den gestarteten Prozess aus dem lokalen DPAPI-Store geladen:

```powershell
& C:\Users\adria\.codex\local-secrets\llm-providers\Invoke-WithLlmProviderEnv.ps1 -All -Command @('python','scripts/run_llm_provider_smoke.py','--require')
```

Der Smoke-Test verweigert lokale OpenWebUI-, Ollama-, `localhost`- und private Docker-Netz-Endpunkte. Er gibt nur Provider, Modell, Host, HTTP-Status und Antwortlänge aus; Secret-Werte werden weder gelesen noch geloggt. Für eine feste Auswahl setzt der Administrator `LLM_PROVIDER_SMOKE_PROVIDER` und `LLM_PROVIDER_SMOKE_MODEL` in der Prozessumgebung.

Die Compose-Datei enthält Healthchecks für OpenWebUI (`/health`) und Workbench (`/healthz`). Der Workbench-Healthcheck nutzt keine Auth-Daten und gibt nur einen minimalen Status zurück.
Die Workbench-Dashboard-Automation läuft standardmäßig alle 30 Minuten mit der nicht-mutierenden Aktion `check`. In Portainer kann der Administrator dies über `WORKBENCH_AUTOMATION_ENABLED`, `WORKBENCH_AUTOMATION_INTERVAL_MINUTES`, `WORKBENCH_AUTOMATION_ACTIONS` und `WORKBENCH_AUTOMATION_RUN_ON_START` anpassen. `sync-status` ist ebenfalls nicht-mutierend und kann automatisiert werden, wenn regelmäßige OpenWebUI-Statusvergleiche gewünscht sind. Schreibende Aktionen wie `generate`, `import-dry-run` oder `import-openwebui` sind nicht Teil des sicheren Defaults und sollten nur nach bewusster Admin-Entscheidung ergänzt werden; `pull-openwebui` bleibt eine manuelle Snapshot-Aktion, weil sie lokale Dateien schreibt.

In der Shared-Targets-Variante prüft der Workbench-Healthcheck nur das Dashboard selbst. Die Zielcontainer werden nicht kontrolliert oder neu gestartet; ihre Betriebsfähigkeit bleibt Aufgabe der gemeinsamen KI-Infra-/Portainer-Umgebung. Der Setup-Doctor validiert die konfigurierten Ziel-URLs syntaktisch; nicht-mutierende Reachability-Prüfungen der Zielcontainer laufen gezielt über WSL-/Container-Smokes im gemeinsamen Docker-Netz. Die Dashboard-Statusanzeige bleibt auf OpenWebUI und den Workbench-Zustand fokussiert.

## Admin-Smoke-Check

Nach dem Start:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml ps
```

Erwartung:

- `openwebui` läuft und wird nach der Startphase als healthy angezeigt.
- `workbench` läuft und wird nach der Startphase als healthy angezeigt.
- OpenWebUI ist lokal unter `http://localhost:3000` erreichbar.
- Die Workbench ist lokal unter `http://localhost:8088` erreichbar und fragt nach HTTP-Basic-Auth.

Wenn ein Dienst nicht healthy wird:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml logs --tail=100 openwebui
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml logs --tail=100 workbench
```

Führe zusätzlich die nicht-mutierende Repository-Prüfung aus:

```powershell
python scripts/check_workbench_setup.py --require-docker
python scripts/verify_openwebui_workspace.py --include-docker-compose
```

## Unternehmensnetz mit eigener Root-CA

Für OpenWebUI-Instanzen hinter internen HTTPS-Zertifikaten muss der Workbench-Container die Unternehmens-CA kennen. Lege in `.env` den Host-Pfad so ab, wie Docker oder Portainer ihn sieht:

```env
WORKBENCH_ENTERPRISE_CA_HOST_FILE=/opt/company-ca/root-ca.pem
WORKBENCH_CA_BUNDLE=/certs/company-root-ca.pem
OPENWEBUI_CA_FILE=/certs/company-root-ca.pem
OPENWEBUI_TLS_VERIFY=true
```

Start mit CA-Override:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.enterprise-ca.yml up -d --build
```

Start im Shared-Targets-Betrieb mit bestehendem OpenWebUI, RAGFlow und Seafile:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.shared-targets.yml -f Deployment/docker-compose.shared-targets-enterprise-ca.yml up -d --build
```

Für `*.top.secret` in der lokalen WSL-Testumgebung ist der Host-Pfad typischerweise `/mnt/docker_data/test/edge/certs/top-secret-edge-root-ca.pem`. Die CA-Datei muss eine gültige CA-Key-Usage enthalten, insbesondere `Certificate Sign` und `CRL Sign`; ungültige lokale Test-CAs müssen an der Edge-Erzeugungsquelle neu erstellt werden.

Der Workbench-Container installiert `ca-certificates` im Image und führt beim Start immer `update-ca-certificates` aus. Wenn `WORKBENCH_CA_BUNDLE` gesetzt ist, wird die gemountete PEM-Datei vorab geprüft: fehlende Dateien, Private Keys und Nicht-PEM-Inhalte führen zu einem klaren Startfehler. Secrets, Tokens und Private Keys gehören nicht in diese CA-Datei.
Der Setup-Doctor prüft `WORKBENCH_ENTERPRISE_CA_HOST_FILE` schon vor dem Compose-Start als Hostdatei: fehlende Dateien, Private Keys und Nicht-PEM-Inhalte werden als Installationsfehler gemeldet.

Der Portainer-Wizard prüft den Root-CA-Pfad ebenfalls lokal, wenn die Datei vom ausführenden System aus lesbar ist. Wenn du den Wizard unter Windows ausführst, der CA-Pfad aber nur auf dem Docker-/Portainer-Host existiert, prüfe die PEM-Datei vorher administrativ und starte den Wizard mit `-AllowUnverifiedRootCaPath`. Der generierte Stack mountet den Pfad dann unverändert als `WORKBENCH_ENTERPRISE_CA_HOST_FILE`; Containerstart und Setup-Doctor auf dem Zielhost prüfen die Datei anschließend erneut. Für die Windows-seitige Preflight-Prüfung derselben generierten Env-Datei nutze zusätzlich `python scripts/check_workbench_setup.py --allow-unverified-root-ca-path`.

Bei einem bereits vorhandenen OpenWebUI über HTTPS setzt du zusätzlich:

```env
OPENWEBUI_BASE_URL=https://openwebui.intern
OPENWEBUI_PUBLIC_URL=https://openwebui.intern
```

`OPENWEBUI_TLS_VERIFY=false` bleibt nur eine Diagnoseoption für kurzlebige lokale Tests. Für Unternehmensbetrieb ist die gemountete Root-CA der vorgesehene Weg.

## Portainer-Wizard

Für Portainer oder schnelle Erstinstallation erzeugt der interaktive Assistent eine Stack-Compose-Datei und eine passende Env-Datei:

```powershell
powershell -ExecutionPolicy Bypass -File Deployment/configure-workbench-enterprise.ps1
```

Der Assistent fragt ab:

- ob OpenWebUI im Stack mitgestartet oder eine vorhandene Instanz genutzt wird
- die interne und öffentliche OpenWebUI-URL
- optional die Portainer-URL für spätere Runtime-Probes ohne Token
- den Docker-/Portainer-sichtbaren Repository-Pfad
- den Docker-Netzwerknamen und ob ein vorhandenes externes Netzwerk genutzt werden soll
- optional den Root-CA-Pfad
- Dashboard-Login, optionalen Hostpfad zu einer Workbench-Passwortdatei, optionalen OpenWebUI-Admin-Token und optionalen Hostpfad zu einer Token-Datei

Ausgabe:

- `Deployment/generated/portainer-compose.yml`
- `Deployment/generated/workbench.env`

`Deployment/generated/` ist ignoriert. Die generierte Compose-Datei kann in Portainer eingefügt werden; die Werte aus `workbench.env` gehören in die Stack-Umgebung. Pfade müssen so angegeben sein, wie der Docker-Host oder Portainer-Agent sie sieht, nicht zwingend wie Windows sie anzeigt. Für Portainer nutzt der Assistent standardmäßig das veröffentlichte Image `ghcr.io/adrianweidig/openwebui-workbench/workbench-dashboard:latest`, weil Portainer nicht aus deinem lokalen Repository-Kontext bauen muss. Die lokalen Override-Dateien `docker-compose.workbench-password-file.yml` und `docker-compose.openwebui-admin-token-file.yml` sind für den normalen Docker-Compose-Pfad gedacht; der Portainer-Wizard erzeugt die entsprechenden Mounts direkt in seiner Stack-Datei.
Die generierte Workbench-Service-Definition setzt `WORKBENCH_REQUIRE_AUTH=true` und akzeptiert entweder `WORKBENCH_AUTH_PASSWORD` oder eine gemountete `WORKBENCH_AUTH_PASSWORD_FILE`. Wenn das Passwort im Assistenten leer bleibt und keine Passwortdatei gemountet wird, muss einer dieser Werte vor dem Stack-Start in Portainer gesetzt werden.
Die generierte Portainer-Compose-Datei enthält Healthchecks für die gebündelte OpenWebUI-Instanz (`/health`) und das Workbench-Dashboard (`/healthz`), damit Portainer den Startzustand direkt als healthy oder unhealthy anzeigen kann.
Die OpenWebUI-URL-Felder werden als vollständige `http`- oder `https`-URLs ohne eingebettete Zugangsdaten validiert, bevor sie in `workbench.env` geschrieben werden.
Eine optional gesetzte `PORTAINER_URL` wird als vollständige `http`- oder `https`-URL ohne eingebettete Zugangsdaten validiert und nur in `workbench.env` gespeichert. Sie dient dem hostseitigen Setup-Doctor für Reachability-Prüfungen und wird nicht als Token oder Secret behandelt.
Wenn das Workbench-Passwort oder der OpenWebUI-Admin-Token als Docker-/Portainer-Secret oder Bind-Datei gemountet wird, kann der Assistent einen Hostpfad abfragen und ihn read-only in den Workbench-Container einhängen. Für das Dashboard-Passwort setzt er `WORKBENCH_AUTH_PASSWORD_HOST_FILE` auf den Docker-/Portainer-sichtbaren Hostpfad und `WORKBENCH_AUTH_PASSWORD_FILE` standardmäßig auf `/run/secrets/workbench-auth-password`. Für den Admin-Token setzt er `OPENWEBUI_ADMIN_TOKEN_HOST_FILE` und `OPENWEBUI_ADMIN_TOKEN_FILE` standardmäßig auf `/run/secrets/openwebui-admin-token`. Der Assistent liest oder schreibt keine Secret-Dateiinhalte. Wenn der Hostpfad nur auf dem Docker-/Portainer-Host existiert und vom ausführenden Windows-System nicht lesbar ist, prüfe die Datei administrativ und starte den Assistenten mit `-AllowUnverifiedSecretFilePath`. Für eine Windows-seitige Preflight-Prüfung der generierten Env-Datei nutze entsprechend `python scripts/check_workbench_setup.py --allow-unverified-secret-file-path`; lokal lesbare Secret-Dateipfade werden dabei als Datei geprüft, aber nicht ausgelesen.
Wenn Workbench und OpenWebUI in ein bereits vorhandenes gemeinsames Docker-Netz sollen, etwa für eine bestehende OpenWebUI-, Reverse-Proxy- oder Portainer-Umgebung, im Assistenten den vorhandenen Netzwerknamen angeben und das externe Netzwerk bestätigen. Dann erzeugt der Stack das Netzwerk nicht selbst, sondern bindet beide Services über `external: true` an `WORKBENCH_DOCKER_NETWORK`. Ohne diese Auswahl legt der generierte Stack ein eigenes Bridge-Netz mit diesem Namen an.

Wenn der lokale `top.secret`-Edge-Proxy aktiv ist:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.top-secret.yml up -d --build workbench
```

Der Edge-Proxy benötigt zusätzlich einen Host `workbench.top.secret`, eine Nginx-Route nach `http://workbench:8088` und einen lokalen Windows-Hosts-Eintrag `127.0.0.1 workbench.top.secret`. Die passende Nginx-Server-Block-Vorlage liegt in [`top-secret-nginx.workbench.conf`](top-secret-nginx.workbench.conf). Wenn der lokale Edge HTTPS nicht auf Host-Port 443 veröffentlicht, die URL mit veröffentlichtem Port öffnen, zum Beispiel `https://workbench.top.secret:25443`.

Der Windows-Hosts-Eintrag kann mit Administratorrechten idempotent gesetzt werden:

```powershell
powershell -ExecutionPolicy Bypass -File Deployment/enable-workbench-top-secret.ps1
```

Weitere Details stehen in [`../docs/WORKBENCH_DASHBOARD.md`](../docs/WORKBENCH_DASHBOARD.md).

## Zielbild

- OpenWebUI läuft ohne Internetzugriff.
- OpenWebUI nutzt die Standardfunktionen der Zielinstanz maximal: natives Tool Calling, Code Interpreter, Datei-/Knowledge-Kontext, Citations und Statusmeldungen, soweit die eingesetzte OpenWebUI-Version sie bereitstellt.
- Optionale Offline-Addon-Bundles können vorbereitete Caches, Playwright/Chromium, NLTK, Tiktoken und zusätzliche Python-Pakete bereitstellen; die Standard-Compose-Datei startet auch ohne diese Inhalte.
- Ein lokaler oder intern erreichbarer Jupyter-Server übernimmt kontrollierte Python-Ausführung.
- Modelle, Tools und Skills werden aus diesem Repository importiert.
- Erzeugte HTML-, PDF-, ZIP- und Datenartefakte landen in einem persistenten Volume.
- Nutzer können im Chat Ergebnisse anfordern und erhalten klare Datei-Hinweise oder Downloads, soweit die OpenWebUI-Instanz den Datei-Event bzw. den gemounteten Pfad bereitstellt.

## Wichtige Volumes

- `<OPENWEBUI_WORKSPACE>\Modelle\dist` nach `/app/backend/data/openwebui-import`
- `<OPENWEBUI_WORKSPACE>\Tools` nach `/app/backend/data/openwebui-tools`
- `<OPENWEBUI_WORKSPACE>\Artefakte\output` nach `/app/backend/data/offline_artifacts`
- Named volume `openwebui-cache` nach `/app/backend/data/cache`; darf leer sein, wenn keine Offline-Caches vorhanden sind
- Named volume `openwebui-python-addons` nach `/app/backend/data/python`; darf leer sein, wenn keine zusätzlichen Python-Pakete vorhanden sind
- Lokale Addon-Pfade nur über einen eigenen, ignorierten Compose-Override einbinden, wenn die Dateien auf der Zielmaschine wirklich existieren

## Zentrale Import-Konfiguration

Für den reproduzierbaren Remote-Import ist die lokale Datei `scripts/openwebui_workspace_config.yaml` maßgeblich. Dort wird `openwebui.base_url` auf die von der Import-Maschine erreichbare Adresse gesetzt, während `jupyter.url`, `artifacts.root`, `addons.*`, `tool_valves.*` und `function_valves.*` die aus dem OpenWebUI-Backend erreichbaren Adressen und Pfade enthalten. Der Importbefehl setzt daraus die passenden Tool- und Function-/Filter-Valves:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Diese Namen sind in der zentralen YAML dokumentiert und werden vom Importer in OpenWebUI-Valves gemappt, soweit die jeweilige Function oder das jeweilige Tool Valves anbietet:

```text
OPENWEBUI_JUPYTER_URL
OPENWEBUI_JUPYTER_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR
OPENWEBUI_ARTIFACT_ROOT
OPENWEBUI_OFFLINE_ADDONS_ROOT
OPENWEBUI_OFFLINE_ADDONS_PYTHON_PATH
NLTK_DATA
HF_HOME
SENTENCE_TRANSFORMERS_HOME
TIKTOKEN_CACHE_DIR
WHISPER_MODEL_DIR
PLAYWRIGHT_BROWSERS_PATH
```

## PDF-Konvertierung

Für direkte PDF-Erzeugung muss im OpenWebUI-Container oder in der Tool-Laufzeit lokal ein Konverter vorhanden sein:

- bevorzugt ein lokal eingebundener Playwright/Chromium-Cache aus einem vorhandenen Addon-Bundle
- danach Python-Paket `weasyprint`
- alternativ lokal installiertes `wkhtmltopdf`, nur wenn die Tool-Valve `allow_wkhtmltopdf` aktiviert wird

Ohne Konverter erzeugt das Tool weiterhin druckfertige HTML-Dateien, die manuell oder durch eine lokal bereitgestellte Pipeline in PDF umgewandelt werden können.
