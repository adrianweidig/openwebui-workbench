# OpenWebUI Workspace

Dieses Repository verwaltet den lokalen Arbeitsbereich unter `E:\OpenWebUI`.

## Struktur

- `OpenWebUI Model Builder/`: nur Arbeitsanweisungen, Quellvorgaben, Generatorlogik und Builder-interne Hilfsbereiche
- `Problemfaelle/`: fachliche Briefings, aus denen die Aufgabenmodelle erzeugt werden
- `Modelle/einzelmodelle/`: menschenlesbar sortierte, einzelne Modellpakete
- `Modelle/dist/`: Air-Gap-Handover-Ordner fuer Copy/Paste, ZIP und Fallback-Importdateien
- `Tools/jupyter/`: produktiv nutzbares Jupyter-Tool mit Beispielkonfiguration
- `Weiteres/`: sonstige Referenzmaterialien

## Arbeitsweise

- `OpenWebUI Model Builder/` bleibt der Ausgangspunkt fuer Vorgaben und Regenerierung.
- Scharfe Artefakte liegen fuer den laufenden Betrieb unter `Modelle/` und `Tools/`.
- Original-Briefings in `Problemfaelle/` werden nicht destruktiv veraendert.
- Builder-interne Sicherungen bleiben unter `OpenWebUI Model Builder/.backup/`.
- Das Repository ist auf Offline-/Air-Gapped-Arbeit ausgelegt.

## OpenWebUI Direktnutzung

### Modelle per GUI

1. In OpenWebUI das gewuenschte Basismodell `coder` verfuegbar machen.
2. In `Modelle/einzelmodelle/<modell-id>/` das passende Paket waehlen.
3. In OpenWebUI ein neues Modell anlegen.
4. `systemprompt.md` als System Prompt uebernehmen.
5. Werte aus `model.json` fuer Name, Beschreibung, Parameter und Features uebernehmen.
6. Falls die Instanz Paketdateien oder Knowledge-Dateien pro Modell erlaubt, `mainprompt.md` und `fachwissen.md` ebenfalls hinterlegen.
7. Das Jupyter-Tool nur dann zuordnen, wenn es im Modellprofil genannt ist.

### Modelle per Volume oder Dateimount

Wenn der OpenWebUI-Container lokale Dateien per Volume lesen soll, ist `Modelle/dist/` der vorgesehene Handover-Ordner.

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

Hinweis: Der exakte Zielpfad im Container haengt von der eingesetzten `openwebui:latest`-Variante ab. Falls die Instanz keinen direkten Dateiscan fuer Modelle unterstuetzt, die Dateien aus `Modelle/dist/` oder `Modelle/einzelmodelle/` manuell in der GUI uebernehmen.

### Jupyter-Tool in OpenWebUI

1. Tool-Datei aus `Tools/jupyter/jupyter_tool.py` verwenden.
2. Konfigurationswerte aus `Tools/jupyter/.env.example` oder `Tools/jupyter/jupyter_config.example.json` lokal setzen.
3. Benoetigte Variablen:

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
