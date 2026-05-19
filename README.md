# OpenWebUI Workspace

Dieses Repository verwaltet den lokalen Arbeitsbereich unter `E:\OpenWebUI`.

## Struktur

- `OpenWebUI Model Builder/`: nur Arbeitsanweisungen, Quellvorgaben, Generatorlogik und Builder-interne Hilfsbereiche
- `Problemfälle/`: fachliche Briefings, aus denen die Aufgabenmodelle erzeugt werden
- `Modelle/einzelmodelle/`: menschenlesbar sortierte, einzelne Modellpakete
- `Modelle/dist/`: Air-Gap-Handover-Ordner für Copy/Paste, ZIP und OpenWebUI-Importdateien
- `Tools/jupyter/`: produktiv nutzbares Jupyter-Tool mit Beispielkonfiguration
- `Weiteres/`: sonstige Referenzmaterialien

## Arbeitsweise

- `OpenWebUI Model Builder/` bleibt der Ausgangspunkt für Vorgaben und Regenerierung.
- Scharfe Artefakte liegen für den laufenden Betrieb unter `Modelle/` und `Tools/`.
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
7. Das Jupyter-Tool nur dann zuordnen, wenn es im Modellprofil genannt ist.

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
```

## Wichtige Einstiege

- `OpenWebUI Model Builder/README.md`
- `Modelle/einzelmodelle/index.md`
- `Modelle/dist/README.md`
- `Tools/jupyter/README.md`
