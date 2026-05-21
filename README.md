# OpenWebUI Workspace

Dieses Repository verwaltet den lokalen Arbeitsbereich unter `F:\OpenWebUI`.

## Struktur

- `OpenWebUI Model Builder/`: nur Arbeitsanweisungen, Quellvorgaben und Generatorlogik
- `Problemfälle/`: fachliche Briefings, aus denen die Aufgabenmodelle erzeugt werden
- `Modelle/einzelmodelle/`: menschenlesbar sortierte, einzelne Modellpakete
- `Modelle/icons/`: generische schwarz-weiße SVG-/PNG-Profilicons für OpenWebUI-Modelle
- `Modelle/dist/`: Air-Gap-Handover-Ordner für Copy/Paste, ZIP und OpenWebUI-Importdateien
- `Tools/jupyter/`: produktiv nutzbares Jupyter-Tool mit Beispielkonfiguration
- `Tools/openwebui_ext/`: zusätzliche importierbare OpenWebUI-Tools, Skills, Doku und Tests
- `Artefakte/`: lokaler Ausgabe- und Übergabebereich für HTML, PDF, ZIP, Tabellen und Diagramme
- `Deployment/`: Offline-Container- und Volume-Vorlagen
- `Dokumentation/`: Betriebs- und Zielbilddokumentation
- `Weiteres/`: sonstige Referenzmaterialien

## Arbeitsweise

- `OpenWebUI Model Builder/` bleibt der Ausgangspunkt für Vorgaben und Regenerierung.
- Scharfe Artefakte liegen für den laufenden Betrieb unter `Modelle/` und `Tools/`.
- Laufzeitausgaben liegen unter `Artefakte/` und werden normalerweise nicht versioniert.
- Original-Briefings in `Problemfälle/` werden nicht destruktiv verändert.
- Builder-interne Sicherungen bleiben lokal unter `OpenWebUI Model Builder/.backup/`, werden ignoriert und nicht versioniert.
- Alte Generatorausgaben unter `OpenWebUI Model Builder/dist/` sind nicht kanonisch; produktive Artefakte liegen ausschließlich unter `Modelle/dist/` und `Tools/dist/`.
- Das Repository ist auf Offline-/Air-Gapped-Arbeit ausgelegt.

## OpenWebUI Direktnutzung

### Modelle per GUI

1. In OpenWebUI das gewünschte Basismodell `coder` verfügbar machen.
2. In `Modelle/einzelmodelle/<modell-id>/` das passende Paket wählen.
3. Entweder das einzelne `model.json` importieren oder ein neues Modell anlegen.
4. Jedes `model.json` ist ein direkt importierbares OpenWebUI-JSON-Array mit genau einem Modellobjekt.
5. Falls die Instanz Paketdateien oder Knowledge-Dateien pro Modell erlaubt, `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und Dateien aus `beispiele/` zusätzlich hinterlegen.
6. Optional ein schlichtes Profilicon aus `Modelle/icons/generic/` oder aus dem Handover unter `Modelle/dist/artifacts/icons/generic/` zuweisen.
7. Das Jupyter-Tool nur dann zuordnen, wenn es im Modellprofil genannt ist.

### Zusätzliche Tools und Skills

Die Erweiterungen unter `Tools/openwebui_ext/` sind direkt für OpenWebUI vorbereitet:

- `Tools/dist/openwebui-tools-offline-import.json` über `Workspace > Tools > Import` importieren.
- `Tools/dist/openwebui-functions-import.json` über `Workspace > Functions > Import` importieren; alle aktivierten Functions sind echte Filter.
- Optional mit Netzwerk-/Rich-UI-/lokalen Crawl-Tools: `Tools/dist/openwebui-tools-import.json` über `Workspace > Tools > Import` importieren.
- Einzelne `.py`-Dateien aus `Tools/openwebui_ext/tools/` nur als Fallback über `Workspace > Tools > Create Tool` einfügen.
- `.md`-Dateien aus `Tools/openwebui_ext/skills/` über `Workspace > Skills > Import` importieren.
- Details, Sicherheitsgrenzen und Testbefehle stehen in `OPENWEBUI_EXTENSIONS.md`.

Für HTML-, PDF-, Präsentations- und ZIP-Ergebnisse zusätzlich `Tools/openwebui_ext/tools/offline_artifact_workbench.py` importieren; beim API-Import wird der persistente Artefaktpfad zentral über `scripts/openwebui_workspace_config.yaml` als Tool-Valve gesetzt.

Für visuelle Offline-Ausgaben, parallele Tool-/Subagent-Planung und robuste Modell-Overlays zusätzlich diese Tools importieren:

- `Tools/openwebui_ext/tools/inline_visuals_toolkit_v3.py`
- `Tools/openwebui_ext/tools/parallel_task_planner.py`
- `Tools/openwebui_ext/tools/tool_skill_overlay_planner.py`
- `Tools/openwebui_ext/tools/comfyui_workflow_inspector.py`

OpenWebUI-Standardfunktionen dürfen ausdrücklich genutzt werden: Datei-/Knowledge-Kontext, Citations, Statusmeldungen, Code Interpreter, natives Tool Calling und alle Builtins, die die jeweilige OpenWebUI-Version bereitstellt. Zusätzlich ist der lokale Stack `F:\offline-ai-stack\openwebui-offline-addons` als Offline-Laufzeit vorgesehen; er stellt Caches, Tiktoken, NLTK, Playwright/Chromium und zusätzliche Python-Pakete für Tools und Filter bereit.

Zusätzlich zu den Problemfallmodellen gibt es zwei Querschnittsmodelle:

- `Allgemein`: Fallbackmodell für freie oder gemischte Nutzerprobleme, die nicht eindeutig zu einem Spezialmodell passen; nutzt das Basismodell `coder` mit allen importierbaren Tools und allen Standardfiltern.
- `PromptForge`: arbeitet wie der Custom GPT `PromptForge` aus `adrianweidig/custom-gpts` und erzeugt vollständige Markdown-Promptvorlagen für ChatGPT, Custom GPTs, OpenWebUI, lokale LLMs und API-Workflows.
- `n8n Workflow Architect`: arbeitet wie der Custom GPT `n8n Workflow Architect` und erstellt oder prüft importierbare n8n-Workflow-JSONs.
- `OpenWebUI Model Builder`: arbeitet wie der Custom GPT `OpenWebUI Model Builder` und erzeugt vollständige OpenWebUI-Modellpakete.
- `Mistral Vision Workbench`: nutzt die Mistral-Medium-VL-Fähigkeit für Screenshots, UI-Tests, Folien, Diagramme, Scans, Dokumentbilder und visuelle Artefakt-QA.

Das Modell `Präsentationserstellung` ist an den Custom GPT `Präsentationscreator` angeglichen. Standardziel ist eine hochwertige, animierte und interaktive Browser-Keynote als `präsentation.html`; PDF/PPTX sind nur noch Fallbacks oder explizite Sonderwünsche.
Alle Chat-Modelle aktivieren `meta.capabilities.vision` und enthalten eine Vision-/UI-Bildanalyse-Sektion. Vision wird genutzt, wenn die Zielinstanz Bildinhalte wirklich an Mistral weitergibt; andernfalls greifen OCR-/Datei-/Beschreibungspfad und lokale Offline-Tools. Jedes Modell hat `beispielergebnis.md` und mindestens ein wiederverwendbares Beispiel unter `beispiele/`; der Präsentationscreator liefert zusätzlich `praesentation-premium-demo.html` mit Navigation, Dark Mode, Hover-Toolbar und Offline-CSS.

Die Tool-Registry und die Modell-Tool-Zuweisungen können reproduzierbar erzeugt und geprüft werden. Der Generator sortiert Tools, Filter und Modelle deterministisch und schließt lokale Cache-Dateien aus den ZIP-Paketen aus:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```

Der generierte Importplan liegt unter `Modelle/dist/openwebui-registration-plan.json` und erzwingt die Reihenfolge Tools, Tool-Publication, Tool-Valves, Functions/Filter, Function-/Filter-Globalisierung, Function-/Filter-Valves, Skills, Skill-Publication, modellbezogene Knowledge-Dateien, Knowledge-Publication, Modelle und Modell-Publication.
Die Modellprofile werden dabei auf natives Offline-Tool-Calling, OpenWebUI-Builtin-Nutzung, Vision-Fähigkeit, eingebettete Modellicons, use-case-spezifische `temperature`-/`top_p`-Werte und einen kurzen Bootstrap-Systemprompt normalisiert. Dieser Systemprompt bleibt bewusst knapp und verpflichtet jedes Modell, vor der Antwort `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und Dateien aus `beispiele/` als Knowledge zu laden, zu analysieren und für Rolle, Scope, Ausgabeformat, Tool-Nutzung und Qualitätsmaßstab anzuwenden. `max_tokens` wird bewusst nicht gesetzt, damit die Zielinstanz ihre eigenen Kontext- und Antwortlimits verwenden kann. Nicht passende Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden ebenfalls nicht gesetzt; High Reasoning wird für lokale Mistral-Medium-128B-Instanzen über die kurze Systemanweisung, Tool-Planung und Ergebnisvalidierung erzwungen.
Die Tool-Nutzungssektion erzwingt am Aufgabenanfang eine Tool-/Skill-Inventur und passende Tools, sobald Dateien, strukturierte Daten, Code, Artefakte, APIs, Docker-/OpenWebUI-Fehler, Visuals, Parallelplanung oder Subagenten betroffen sind. Die konkrete Tool-Syntax und die use-case-spezifischen Arbeitsmuster liegen in `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, `beispiele/` und den importierten Skills; der kurze Systemprompt verweist nur auf diese Pflicht. Der Filter `auto_tool_selector` unterstützt diese Vorgabe, indem er passende verfügbare Tool-IDs vor dem Modellaufruf ergänzt; `markdown_normalizer` und `context_compressor_filter` bleiben ebenfalls standardmäßig als Filter verfügbar. `context_compressor_filter` normalisiert zusätzlich 0-Output-Token-Requests und kürzt übergroße Einzelprompts vor dem Modellaufruf unter das sichere Kontextbudget.
Die Datei `Modelle/dist/openwebui-model-params-summary.json` listet die Parameter je Modell explizit zur schnellen Kontrolle.

Für den API-basierten Direktimport ist `scripts/openwebui_workspace_config.yaml` die zentrale Laufzeitkonfiguration. Dazu `scripts/openwebui_workspace_config.example.yaml` kopieren und dort die von der Import-Maschine erreichbare OpenWebUI-Root-Adresse, den OpenWebUI-Admin-API-Key, Auth-Header/Scheme, die aus dem OpenWebUI-Backend erreichbare Jupyter-Adresse, Backend-Pfade, Addon-Pfade, Tool-Valves und Function-/Filter-Valves eintragen. Die OpenWebUI-Adresse soll auf die WebUI-Root zeigen, z. B. `http://127.0.0.1:3000`, nicht auf `/api` oder `/api/v1`. Die echte `openwebui_workspace_config.yaml` wird nicht versioniert. Der API-Importer importiert standardmäßig alle importierbaren Tools aus dem Repo; `import.include_optional_network_tools: false` reduziert den Import auf den Offline-Default-Satz.

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Das direkte Importskript `Tools/import_openwebui_workspace.py` bleibt als Fallback nutzbar und liest dieselbe zentrale Konfigurationsdatei. CLI-Parameter wie `--token`, `--base-url` oder `--jupyter-url` sind nur für bewusste Einmal-Overrides gedacht. Der Importer importiert Tools, Functions/Filter, Skills, Modellprofile, eingebettete Icons, setzt Tool- und Function-Valves aus der Konfiguration, hängt `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` sowie Dateien aus `beispiele/` als Knowledge pro Modell an, veröffentlicht Tools/Skills/Knowledge/Modelle automatisch mit Public-Read-Grants und setzt alle Functions/Filter aktiv sowie global.
Für Tools nutzt der Importer zuerst die aktuellen OpenWebUI-Endpunkte unter `/api/tools/...` und fällt danach auf `/api/v1/tools/...` zurück. Falls OpenWebUI beim Schritt Tool-Valves mit `We could not find what you're looking for` antwortet, ist entweder das Tool noch nicht importiert oder die Instanz erkennt keine `Valves`-Schema-Klasse am Tool. `air_gapped_jupyter_python` exportiert deshalb `Valves` und `Tools.Valves`; nach einem Pull und erneutem Import sollte der Valves-Schritt für dieses Tool nicht mehr an der Schema-Erkennung scheitern.
Ein Import-Probelauf ohne OpenWebUI-Aufruf ist mit `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.yaml` möglich.

### Modelle per Volume oder Dateimount

Wenn der OpenWebUI-Container lokale Dateien per Volume lesen soll, ist `Modelle/dist/` der vorgesehene Handover-Ordner. Die primäre Importdatei ist `Modelle/dist/openwebui-models-import.json`.

Beispiel `docker run`:

```text
-v F:\OpenWebUI\Modelle\dist:/app/backend/data/openwebui-import
```

Beispiel `docker-compose.yml`:

```yaml
services:
  openwebui:
    volumes:
      - F:\OpenWebUI\Modelle\dist:/app/backend/data/openwebui-import
      - F:\OpenWebUI\Tools\jupyter:/app/backend/data/openwebui-tools/jupyter
      - F:\OpenWebUI\Artefakte\output:/app/backend/data/offline_artifacts
      - F:\offline-ai-stack\openwebui-offline-addons\cache:/app/backend/data/cache
      - F:\offline-ai-stack\openwebui-offline-addons\nltk_data:/app/backend/data/nltk_data
      - F:\offline-ai-stack\openwebui-offline-addons\python:/app/backend/data/python
```

Hinweis: Der exakte Zielpfad im Container hängt von der eingesetzten `openwebui:latest`-Variante ab. Falls die Instanz keinen direkten Dateiscan für Modelle unterstützt, `Modelle/dist/openwebui-models-import.json` oder ein einzelnes `Modelle/einzelmodelle/<modell-id>/model.json` direkt über die GUI importieren.

### Jupyter-Tool in OpenWebUI

1. Tool-Datei aus `Tools/jupyter/jupyter_tool.py` verwenden.
2. Für den Repo-Import die Werte in `scripts/openwebui_workspace_config.yaml` unter `jupyter`, `tool_valves.air_gapped_jupyter_python` und `tool_valves.offline_artifact_workbench` setzen.
3. Die folgenden Valve-/Umgebungsnamen sind dort zentral dokumentiert:

```text
OPENWEBUI_JUPYTER_URL
OPENWEBUI_JUPYTER_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR
OPENWEBUI_ARTIFACT_ROOT
OPENWEBUI_OFFLINE_ADDONS_ROOT
OPENWEBUI_OFFLINE_ADDONS_PYTHON_PATH
NLTK_DATA
TIKTOKEN_CACHE_DIR
PLAYWRIGHT_BROWSERS_PATH
```

Bei Nutzung des API-Importers werden diese Werte aus `scripts/openwebui_workspace_config.yaml` als Tool-Valves für `air_gapped_jupyter_python` und `offline_artifact_workbench` gesetzt. Function-/Filter-Valves wie das Kontextbudget des `context_compressor_filter` liegen im Abschnitt `function_valves`. Die Jupyter-URL und die Addon-Pfade müssen aus Sicht des OpenWebUI-Backends erreichbar sein, etwa `http://jupyter:8888` und `/app/backend/data/cache/ms-playwright` im Docker-Netz.
Wenn dieser Schritt auf einer OpenWebUI-Version ohne Tool-Valves-Endpunkt übersprungen wird, läuft der Import weiter; dann müssen die Jupyter-Valves einmalig über die OpenWebUI-Tool-Oberfläche oder über eine neuere OpenWebUI-Version gesetzt werden.

## Wichtige Einstiege

- `OpenWebUI Model Builder/README.md`
- `Modelle/einzelmodelle/index.md`
- `Modelle/dist/README.md`
- `Tools/jupyter/README.md`
- `OPENWEBUI_EXTENSIONS.md`
- `Dokumentation/OFFLINE_CHATGPT_WORKBENCH.md`
- `Deployment/README.md`
