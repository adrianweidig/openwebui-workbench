# OpenWebUI Workspace

Dieses Repository verwaltet den lokalen Arbeitsbereich unter `E:\OpenWebUI`.

## Struktur

- `OpenWebUI Model Builder/`: nur Arbeitsanweisungen, Quellvorgaben, Generatorlogik und Builder-interne Hilfsbereiche
- `Problemfälle/`: fachliche Briefings, aus denen die Aufgabenmodelle erzeugt werden
- `Modelle/einzelmodelle/`: menschenlesbar sortierte, einzelne Modellpakete
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
- Builder-interne Sicherungen bleiben unter `OpenWebUI Model Builder/.backup/`.
- Das Repository ist auf Offline-/Air-Gapped-Arbeit ausgelegt.

## OpenWebUI Direktnutzung

### Modelle per GUI

1. In OpenWebUI das gewünschte Basismodell `coder` verfügbar machen.
2. In `Modelle/einzelmodelle/<modell-id>/` das passende Paket wählen.
3. Entweder das einzelne `model.json` importieren oder ein neues Modell anlegen.
4. Jedes `model.json` ist ein direkt importierbares OpenWebUI-JSON-Array mit genau einem Modellobjekt.
5. Falls die Instanz Paketdateien oder Knowledge-Dateien pro Modell erlaubt, `systemprompt.md`, `mainprompt.md` und `fachwissen.md` zusätzlich hinterlegen.
6. Das Jupyter-Tool nur dann zuordnen, wenn es im Modellprofil genannt ist.

### Zusätzliche Tools und Skills

Die Erweiterungen unter `Tools/openwebui_ext/` sind direkt für OpenWebUI vorbereitet:

- `.py`-Dateien aus `Tools/openwebui_ext/tools/` über `Workspace > Tools > Create Tool` importieren.
- `.md`-Dateien aus `Tools/openwebui_ext/skills/` über `Workspace > Skills > Import` importieren.
- Details, Sicherheitsgrenzen und Testbefehle stehen in `OPENWEBUI_EXTENSIONS.md`.

Für HTML-, PDF-, Präsentations- und ZIP-Ergebnisse zusätzlich `Tools/openwebui_ext/tools/offline_artifact_workbench.py` importieren und `OPENWEBUI_ARTIFACT_ROOT` auf ein persistentes OpenWebUI-Volume setzen.

Für visuelle Offline-Ausgaben, parallele Tool-/Subagent-Planung und robuste Modell-Overlays zusätzlich diese Tools importieren:

- `Tools/openwebui_ext/tools/inline_visuals_toolkit_v3.py`
- `Tools/openwebui_ext/tools/parallel_task_planner.py`
- `Tools/openwebui_ext/tools/tool_skill_overlay_planner.py`
- `Tools/openwebui_ext/tools/comfyui_workflow_inspector.py`

Die Tool-Registry und die Modell-Tool-Zuweisungen können reproduzierbar erzeugt und geprüft werden:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```

Der generierte Importplan liegt unter `Modelle/dist/openwebui-registration-plan.json` und erzwingt die Reihenfolge Tools, Skills, Modelle.

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

## Wichtige Einstiege

- `OpenWebUI Model Builder/README.md`
- `Modelle/einzelmodelle/index.md`
- `Modelle/dist/README.md`
- `Tools/jupyter/README.md`
- `OPENWEBUI_EXTENSIONS.md`
- `Dokumentation/OFFLINE_CHATGPT_WORKBENCH.md`
- `Deployment/README.md`
