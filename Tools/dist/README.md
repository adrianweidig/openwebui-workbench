# OpenWebUI Tools/Filter/Skills Offline-Paket

Dieses Verzeichnis ist der Copy/Paste- und Transportbereich für OpenWebUI-Tools, Filter und Skills.

## Enthalten

- `openwebui-tools-skills-offline.zip`: ZIP-Paket aus `Tools/jupyter`, `Tools/openwebui_ext`, `Tools/index.json` und `Tools/README.md`.
- `openwebui-tools-offline-import.json`: direkt importierbares GUI-Bundle für alle Offline-Default-Tools.
- `openwebui-tools-import.json`: direkt importierbares GUI-Bundle inklusive optionaler Netzwerk-, Rich-UI- und lokaler Crawl-Tools.
- `openwebui-functions-import.json`: direkt importierbares GUI-Bundle für Functions/Filter.
- `openwebui-tool-registry.json`: maschinenlesbare Tool-Registry mit Importreihenfolge, Pfaden, Checksummen und öffentlichen Tool-Methoden.
- `openwebui-function-registry.json`: maschinenlesbare Function-/Filter-Registry mit dem Kontextkomprimierer.

## Nutzung

1. ZIP in die Air-Gap-Umgebung kopieren.
2. Entpacken.
3. `openwebui-tools-offline-import.json` über `Workspace > Tools > Import` importieren.
4. `openwebui-functions-import.json` über `Workspace > Functions > Import` importieren.
5. `.md`-Dateien aus `openwebui_ext/skills/` über `Workspace > Skills` importieren.
6. Jupyter-, Artefakt- und Filter-Valves lokal setzen.

Optionale Tools aus `openwebui-tools-import.json`, die nicht im Offline-Default liegen, müssen bewusst konfiguriert werden: `openui_generative_ui.py` benötigt ein lokal bereitgestelltes OpenUI-Browser-Bundle, `web_search_and_crawl.py` lokale/self-hosted SearXNG-/Crawl4AI-Endpunkte und `safe_http_fetcher.py`/`github_repo_inspector.py` sind keine Air-Gap-Defaults.

## Reproduzierbare Erzeugung

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```
