# Offline OpenWebUI Deployment

Dieses Verzeichnis enthält lokale Vorlagen für einen offline nutzbaren OpenWebUI-Betrieb mit eigenem Jupyter-Server, persistenten Modellen, Tools, Skills und Artefakten.

## Zielbild

- OpenWebUI läuft ohne Internetzugriff.
- OpenWebUI nutzt die Standardfunktionen der Zielinstanz maximal: natives Tool Calling, Code Interpreter, Datei-/Knowledge-Kontext, Citations und Statusmeldungen, soweit die eingesetzte OpenWebUI-Version sie bereitstellt.
- Der lokale Offline-Addon-Stack `F:\offline-ai-stack\openwebui-offline-addons` stellt vorbereitete Caches, Playwright/Chromium, NLTK, Tiktoken und zusätzliche Python-Pakete bereit.
- Ein lokaler oder intern erreichbarer Jupyter-Server übernimmt kontrollierte Python-Ausführung.
- Modelle, Tools und Skills werden aus diesem Repository importiert.
- Erzeugte HTML-, PDF-, ZIP- und Datenartefakte landen in einem persistenten Volume.
- Nutzer können im Chat Ergebnisse anfordern und erhalten klare Datei-Hinweise oder Downloads, soweit die OpenWebUI-Instanz den Datei-Event bzw. den gemounteten Pfad bereitstellt.

## Wichtige Volumes

- `F:\OpenWebUI\Modelle\dist` nach `/app/backend/data/openwebui-import`
- `F:\OpenWebUI\Tools` nach `/app/backend/data/openwebui-tools`
- `F:\OpenWebUI\Artefakte\output` nach `/app/backend/data/offline_artifacts`
- `F:\offline-ai-stack\openwebui-offline-addons\cache` nach `/app/backend/data/cache`
- `F:\offline-ai-stack\openwebui-offline-addons\nltk_data` nach `/app/backend/data/nltk_data`
- `F:\offline-ai-stack\openwebui-offline-addons\python` nach `/app/backend/data/python`
- `F:\offline-ai-stack\openwebui-offline-addons\python\openwebui_offline_addons.pth` nach `/usr/local/lib/python3.11/site-packages/openwebui_offline_addons.pth`
- `F:\offline-ai-stack\openwebui-offline-addons\bin\start-offline.sh` nach `/app/backend/start-offline.sh`

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

- bevorzugt der lokale Playwright/Chromium-Cache aus `F:\offline-ai-stack\openwebui-offline-addons`
- danach Python-Paket `weasyprint`
- alternativ lokal installiertes `wkhtmltopdf`, nur wenn die Tool-Valve `allow_wkhtmltopdf` aktiviert wird

Ohne Konverter erzeugt das Tool weiterhin druckfertige HTML-Dateien, die manuell oder durch eine lokal bereitgestellte Pipeline in PDF umgewandelt werden können.
