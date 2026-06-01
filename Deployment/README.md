# Offline OpenWebUI Deployment

Dieses Verzeichnis enthält lokale Vorlagen für einen offline nutzbaren OpenWebUI-Betrieb mit eigenem Jupyter-Server, persistenten Modellen, Tools, Skills und Artefakten.

## Compose-Varianten

- `docker-compose.workbench.yml`: Standardstart für OpenWebUI plus Workbench-Dashboard. Das Repository wird als `/workspace` in den Workbench-Container gemountet, damit Modell-Markdown-Dateien, Dist-Artefakte und Sync-Aktionen zentral verwaltet werden können.
- `docker-compose.enterprise-ca.yml`: optionaler Override für Unternehmensnetze mit eigener Root-CA. Die CA wird in OpenWebUI und Workbench gemountet; der Workbench-Container aktualisiert den System-Truststore bei jedem Start.
- `docker-compose.top-secret.yml`: optionaler lokaler Override, der den Workbench-Container zusätzlich an das bestehende `top.secret`-Edge-Netz hängt und dort als `workbench` sowie `workbench.top.secret` verfügbar macht.
- `docker-compose.openwebui-offline.example.yml`: portable Offline-Beispielvorlage mit repo-relativen Mounts, named volumes und optional überschreibbaren OpenWebUI-/Jupyter-Images.

Start der neuen Workbench-Umgebung:

```powershell
python scripts/init_workbench_env.py
python scripts/init_workbench_env.py --check
python scripts/check_workbench_setup.py
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

`scripts/init_workbench_env.py` erzeugt eine ignorierte lokale `.env` aus `Deployment/workbench.env.example` und füllt `WEBUI_SECRET_KEY` sowie `WORKBENCH_AUTH_PASSWORD` mit zufälligen lokalen Werten. Bestehende `.env`-Dateien werden ohne `--force` nicht überschrieben, und Secret-Werte werden nicht auf der Konsole ausgegeben. `WORKBENCH_AUTH_USERNAME` fällt sonst auf `workbench` zurück. Die Compose-Datei startet das Dashboard nicht ohne Passwort, damit die Workbench immer über HTTP Basic Auth erreichbar ist.
`scripts/check_workbench_setup.py` ist der nicht-mutierende Setup-Doctor für Administratoren: Er prüft Python-Version, Env-Vorlage, lokale `.env`, Host-Portwerte, OpenWebUI-URLs, boolesche Flags, numerische Runtime-Grenzen, dateibasierte Runtime-Pfade, Compose-Datei und Docker-Verfügbarkeit, ohne Dienste zu starten oder Secret-Werte auszugeben. Fehlendes Docker ist standardmäßig eine Warnung; mit `--require-docker` wird es für Installationsabnahmen als Fehler gewertet.
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
```

Dieser Schalter ersetzt keine CA-Prüfung: lokal lesbare PEM-Dateien werden weiterhin validiert, und der Admin muss die Datei auf dem Docker-/Portainer-Host vor dem Stack-Start prüfen.

Für Abnahmen nach einem Stack-Start kann der Setup-Doctor zusätzlich nicht-mutierende HTTP-Probes ausführen. Ohne `--require-runtime` sind nicht erreichbare Dienste Warnungen; mit `--require-runtime` werden sie zu Fehlern:

```powershell
python scripts/check_workbench_setup.py --probe-runtime --portainer-url https://portainer.top.secret
python scripts/check_workbench_setup.py --probe-runtime --require-runtime --portainer-url https://portainer.top.secret
```

Der Probe ruft keine Admin-APIs mit Token auf. OpenWebUI wird über `OPENWEBUI_PUBLIC_URL` geprüft, Portainer über `--portainer-url` oder `PORTAINER_URL` in der lokalen `.env`; der CLI-Wert hat Vorrang. HTTP 401/403 zählt als erreichbar, weil damit der Dienst antwortet und Auth verlangt. Der Portainer-Wizard kann `PORTAINER_URL` direkt in die generierte `workbench.env` schreiben, damit derselbe Wert für spätere Setup-Doctor-Abnahmen verfügbar ist.

Die Compose-Datei enthält Healthchecks für OpenWebUI (`/health`) und Workbench (`/healthz`). Der Workbench-Healthcheck nutzt keine Auth-Daten und gibt nur einen minimalen Status zurück.
Die Workbench-Dashboard-Automation läuft standardmäßig alle 30 Minuten mit der nicht-mutierenden Aktion `check`. In Portainer kann der Administrator dies über `WORKBENCH_AUTOMATION_ENABLED`, `WORKBENCH_AUTOMATION_INTERVAL_MINUTES`, `WORKBENCH_AUTOMATION_ACTIONS` und `WORKBENCH_AUTOMATION_RUN_ON_START` anpassen. Schreibende Aktionen wie `generate`, `import-dry-run` oder `import-openwebui` sind nicht Teil des sicheren Defaults und sollten nur nach bewusster Admin-Entscheidung ergänzt werden.

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
- Dashboard-Login und optionalen OpenWebUI-Admin-Token

Ausgabe:

- `Deployment/generated/portainer-compose.yml`
- `Deployment/generated/workbench.env`

`Deployment/generated/` ist ignoriert. Die generierte Compose-Datei kann in Portainer eingefügt werden; die Werte aus `workbench.env` gehören in die Stack-Umgebung. Pfade müssen so angegeben sein, wie der Docker-Host oder Portainer-Agent sie sieht, nicht zwingend wie Windows sie anzeigt. Für Portainer nutzt der Assistent standardmäßig das veröffentlichte Image `ghcr.io/adrianweidig/openwebui-workbench/workbench-dashboard:latest`, weil Portainer nicht aus deinem lokalen Repository-Kontext bauen muss.
Die generierte Workbench-Service-Definition verlangt `WORKBENCH_AUTH_PASSWORD`; wenn der Wert im Assistenten leer bleibt, muss er vor dem Stack-Start in Portainer gesetzt werden.
Eine optional gesetzte `PORTAINER_URL` wird als vollständige `http`- oder `https`-URL ohne eingebettete Zugangsdaten validiert und nur in `workbench.env` gespeichert. Sie dient dem hostseitigen Setup-Doctor für Reachability-Prüfungen und wird nicht als Token oder Secret behandelt.
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
