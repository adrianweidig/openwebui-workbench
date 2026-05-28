# Offline OpenWebUI Deployment

Dieses Verzeichnis enthält lokale Vorlagen für einen offline nutzbaren OpenWebUI-Betrieb mit eigenem Jupyter-Server, persistenten Modellen, Tools, Skills und Artefakten.

## Compose-Varianten

- `docker-compose.workbench.yml`: Standardstart für OpenWebUI plus Workbench-Dashboard. Das Repository wird als `/workspace` in den Workbench-Container gemountet, damit Modell-Markdown-Dateien, Dist-Artefakte und Sync-Aktionen zentral verwaltet werden können.
- `docker-compose.enterprise-ca.yml`: optionaler Override für Unternehmensnetze mit eigener Root-CA. Die CA wird in OpenWebUI und Workbench gemountet; der Workbench-Container aktualisiert den System-Truststore bei jedem Start.
- `docker-compose.top-secret.yml`: optionaler lokaler Override, der den Workbench-Container zusätzlich an das bestehende `top.secret`-Edge-Netz hängt und dort als `workbench` sowie `workbench.top.secret` verfügbar macht.
- `docker-compose.openwebui-offline.example.yml`: portable Offline-Beispielvorlage mit repo-relativen Mounts, named volumes und optional überschreibbaren OpenWebUI-/Jupyter-Images.

Start der neuen Workbench-Umgebung:

```powershell
Copy-Item Deployment/workbench.env.example .env
docker compose -f Deployment/docker-compose.workbench.yml up -d --build
```

Setze in der lokalen `.env` `WORKBENCH_AUTH_USERNAME` und `WORKBENCH_AUTH_PASSWORD` oder `WORKBENCH_AUTH_PASSWORD_FILE`, wenn das Dashboard nicht nur in einer kurzlebigen lokalen Entwicklersitzung läuft.

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
docker compose -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.enterprise-ca.yml up -d --build
```

Der Workbench-Container installiert `ca-certificates` im Image und führt beim Start immer `update-ca-certificates` aus. Wenn `WORKBENCH_CA_BUNDLE` gesetzt ist, wird die gemountete PEM-Datei vorab geprüft: fehlende Dateien, Private Keys und Nicht-PEM-Inhalte führen zu einem klaren Startfehler. Secrets, Tokens und Private Keys gehören nicht in diese CA-Datei.

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
- den Docker-/Portainer-sichtbaren Repository-Pfad
- optional den Root-CA-Pfad
- Dashboard-Login und optionalen OpenWebUI-Admin-Token

Ausgabe:

- `Deployment/generated/portainer-compose.yml`
- `Deployment/generated/workbench.env`

`Deployment/generated/` ist ignoriert. Die generierte Compose-Datei kann in Portainer eingefügt werden; die Werte aus `workbench.env` gehören in die Stack-Umgebung. Pfade müssen so angegeben sein, wie der Docker-Host oder Portainer-Agent sie sieht, nicht zwingend wie Windows sie anzeigt. Für Portainer nutzt der Assistent standardmäßig das veröffentlichte Image `ghcr.io/adrianweidig/openwebui-workbench/workbench-dashboard:latest`, weil Portainer nicht aus deinem lokalen Repository-Kontext bauen muss.

Wenn der lokale `top.secret`-Edge-Proxy aktiv ist:

```powershell
docker compose -f Deployment/docker-compose.workbench.yml -f Deployment/docker-compose.top-secret.yml up -d --build workbench
```

Der Edge-Proxy benötigt zusätzlich einen Host `workbench.top.secret`, eine Nginx-Route nach `http://workbench:8088` und einen lokalen Windows-Hosts-Eintrag `127.0.0.1 workbench.top.secret`. Die passende Nginx-Server-Block-Vorlage liegt in [`top-secret-nginx.workbench.conf`](top-secret-nginx.workbench.conf).

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
