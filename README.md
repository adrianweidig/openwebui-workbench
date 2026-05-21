# OpenWebUI Workspace

Dieses Repository verwaltet den lokalen Arbeitsbereich unter `E:\OpenWebUI`.

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
5. Falls die Instanz Paketdateien oder Knowledge-Dateien pro Modell erlaubt, `systemprompt.md`, `mainprompt.md` und `fachwissen.md` zusätzlich hinterlegen.
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

Für HTML-, PDF-, Präsentations- und ZIP-Ergebnisse zusätzlich `Tools/openwebui_ext/tools/offline_artifact_workbench.py` importieren und `OPENWEBUI_ARTIFACT_ROOT` auf ein persistentes OpenWebUI-Volume setzen.

Für visuelle Offline-Ausgaben, parallele Tool-/Subagent-Planung und robuste Modell-Overlays zusätzlich diese Tools importieren:

- `Tools/openwebui_ext/tools/inline_visuals_toolkit_v3.py`
- `Tools/openwebui_ext/tools/parallel_task_planner.py`
- `Tools/openwebui_ext/tools/tool_skill_overlay_planner.py`
- `Tools/openwebui_ext/tools/comfyui_workflow_inspector.py`

Die Tool-Registry und die Modell-Tool-Zuweisungen können reproduzierbar erzeugt und geprüft werden. Der Generator sortiert Tools, Filter und Modelle deterministisch und schließt lokale Cache-Dateien aus den ZIP-Paketen aus:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```

Der generierte Importplan liegt unter `Modelle/dist/openwebui-registration-plan.json` und erzwingt die Reihenfolge Tools, Filter, Skills, modellbezogene Knowledge-Dateien, Modelle.
Die Modellprofile werden dabei auf natives Offline-Tool-Calling, eingebettete Modellicons, use-case-spezifische `temperature`-/`top_p`-Werte, ein High-Reasoning-Systemprofil und eine verbindliche Tool-/Skill-Nutzungssektion normalisiert. Systemprompt, Mainprompt und Fachwissen sind im Sammelimport enthalten. `max_tokens` wird bewusst nicht gesetzt, damit die Zielinstanz ihre eigenen Kontext- und Antwortlimits verwenden kann. Nicht passende Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden ebenfalls nicht gesetzt.
Die Tool-Nutzungssektion erzwingt am Aufgabenanfang eine Tool-/Skill-Inventur und passende Tools, sobald Dateien, strukturierte Daten, Code, Artefakte, APIs, Docker-/OpenWebUI-Fehler, Visuals, Parallelplanung, Subagenten, Modellrat, Modell-/Tool-/Skill-Overlays, ComfyUI-Workflows oder Skill-Erstellung betroffen sind. Der Filter `auto_tool_selector` unterstützt diese Vorgabe, indem er passende verfügbare Tool-IDs vor dem Modellaufruf ergänzt; `markdown_normalizer` und `context_compressor_filter` bleiben ebenfalls standardmäßig als Filter verfügbar.
Die Datei `Modelle/dist/openwebui-model-params-summary.json` listet die Parameter je Modell explizit zur schnellen Kontrolle.

Für API-basierten Direktimport kann eine lokale Konfigurationsdatei genutzt werden. Dazu `scripts/openwebui_workspace_config.example.yaml` nach `scripts/openwebui_workspace_config.yaml` kopieren und dort die von der Import-Maschine erreichbare OpenWebUI-Adresse, den OpenWebUI-Admin-API-Key sowie die aus dem OpenWebUI-Container erreichbare Jupyter-Adresse und den Jupyter-Token eintragen. Die echte `openwebui_workspace_config.yaml` wird nicht versioniert.

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Alternativ können `OPENWEBUI_ADMIN_TOKEN`, `OPENWEBUI_BASE_URL` oder die CLI-Parameter `--token` und `--base-url` genutzt werden. Das direkte Importskript `Tools/import_openwebui_workspace.py` bleibt als Fallback nutzbar. Es importiert Tools, Functions/Filter, Skills, Modellprofile, eingebettete Icons, setzt die Jupyter-/Artefakt-Valves aus der Konfigurationsdatei und hängt `mainprompt.md` sowie `fachwissen.md` als Knowledge pro Modell an.
Ein Import-Probelauf ohne OpenWebUI-Aufruf ist mit `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.yaml` möglich.
Falls keine YAML-Datei genutzt werden soll, können lokale Defaults oben in `scripts/configure_openwebui_tool_models.py` bei `SCRIPT_OPENWEBUI_BASE_URL`, `SCRIPT_OPENWEBUI_ADMIN_TOKEN`, `SCRIPT_JUPYTER_URL`, `SCRIPT_JUPYTER_TOKEN`, `SCRIPT_JUPYTER_ALLOWED_WORKDIR` und `SCRIPT_ARTIFACT_ROOT` eingetragen werden. Dieser Weg ist für lokale Einmalimporte gedacht; für dauerhafte Arbeit bleibt die ignorierte YAML-Datei sauberer.

### Modelle per Volume oder Dateimount

Wenn der OpenWebUI-Container lokale Dateien per Volume lesen soll, ist `Modelle/dist/` der vorgesehene Handover-Ordner. Die primäre Importdatei ist `Modelle/dist/openwebui-models-import.json`.

Beispiel `docker run`:

```text
-v E:\OpenWebUI\Modelle\dist:/app/backend/data/openwebui-import
```

Beispiel `docker-compose.yml`:

```yaml
services:
  openwebui:
    volumes:
      - E:\OpenWebUI\Modelle\dist:/app/backend/data/openwebui-import
      - E:\OpenWebUI\Tools\jupyter:/app/backend/data/openwebui-tools/jupyter
      - E:\OpenWebUI\Artefakte\output:/app/backend/data/offline_artifacts
```

Hinweis: Der exakte Zielpfad im Container hängt von der eingesetzten `openwebui:latest`-Variante ab. Falls die Instanz keinen direkten Dateiscan für Modelle unterstützt, `Modelle/dist/openwebui-models-import.json` oder ein einzelnes `Modelle/einzelmodelle/<modell-id>/model.json` direkt über die GUI importieren.

### Jupyter-Tool in OpenWebUI

1. Tool-Datei aus `Tools/jupyter/jupyter_tool.py` verwenden.
2. Konfigurationswerte aus `Tools/jupyter/.env.example` oder `Tools/jupyter/jupyter_config.example.json` lokal setzen.
3. Benötigte Variablen:

```text
OPENWEBUI_JUPYTER_URL
OPENWEBUI_JUPYTER_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR
OPENWEBUI_ARTIFACT_ROOT
```

Bei Nutzung des API-Importers werden diese Werte aus `scripts/openwebui_workspace_config.yaml` als Tool-Valves für `air_gapped_jupyter_python` und `offline_artifact_workbench` gesetzt. Die Jupyter-URL muss aus Sicht des OpenWebUI-Backends erreichbar sein, etwa `http://jupyter:8888` im Docker-Netz.

## Wichtige Einstiege

- `OpenWebUI Model Builder/README.md`
- `Modelle/einzelmodelle/index.md`
- `Modelle/dist/README.md`
- `Tools/jupyter/README.md`
- `OPENWEBUI_EXTENSIONS.md`
- `Dokumentation/OFFLINE_CHATGPT_WORKBENCH.md`
- `Deployment/README.md`
