# OpenWebUI Tools/Filter/Skills Offline-Paket

Dieses Verzeichnis ist der Copy/Paste- und Transportbereich für OpenWebUI-Tools, Filter und Skills.

## Enthalten

- `openwebui-tools-skills-offline.zip`: ZIP-Paket aus `Tools/jupyter`, `Tools/openwebui_ext`, `Tools/index.json` und `Tools/README.md`.
- `openwebui-tool-registry.json`: maschinenlesbare Tool-Registry mit Importreihenfolge, Pfaden, Checksummen und öffentlichen Tool-Methoden.
- `openwebui-function-registry.json`: maschinenlesbare Function-/Filter-Registry mit dem Kontextkomprimierer.

## Nutzung

1. ZIP in die Air-Gap-Umgebung kopieren.
2. Entpacken.
3. `.py`-Dateien aus `openwebui_ext/tools/` über `Workspace > Tools` importieren.
4. `.py`-Dateien aus `openwebui_ext/filters/` über `Workspace > Functions` als Filter importieren.
5. `.md`-Dateien aus `openwebui_ext/skills/` über `Workspace > Skills` importieren.
6. Jupyter-, Artefakt- und Filter-Valves lokal setzen.

## Reproduzierbare Erzeugung

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```
