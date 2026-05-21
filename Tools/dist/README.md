# OpenWebUI Tools/Filter/Skills Offline-Paket

Dieses Verzeichnis ist der Copy/Paste- und Transportbereich für OpenWebUI-Tools, Filter und Skills.

## Enthalten

- `openwebui-tools-skills-offline.zip`: ZIP-Paket aus `Tools/jupyter`, `Tools/openwebui_ext`, `Tools/index.json`, `Tools/import_openwebui_workspace.py` und `Tools/README.md`.
- `openwebui-tools-offline-import.json`: direkt importierbares GUI-Bundle für alle Offline-Default-Tools.
- `openwebui-tools-import.json`: direkt importierbares GUI-Bundle inklusive optionaler Netzwerk-, Rich-UI- und lokaler Crawl-Tools.
- `openwebui-functions-import.json`: direkt importierbares GUI-Bundle für Functions/Filter.
- `openwebui-tool-registry.json`: maschinenlesbare Tool-Registry mit Importreihenfolge, Pfaden, Checksummen und öffentlichen Tool-Methoden.
- `openwebui-function-registry.json`: maschinenlesbare Function-/Filter-Registry mit Auto-Tool-Selector, Kontextkomprimierer und Markdown-Normalizer.

## Nutzung

1. ZIP in die Air-Gap-Umgebung kopieren.
2. Entpacken.
3. `openwebui-tools-offline-import.json` über `Workspace > Tools > Import` importieren.
4. `openwebui-functions-import.json` über `Workspace > Functions > Import` importieren.
5. `.md`-Dateien aus `openwebui_ext/skills/` über `Workspace > Skills` importieren.
6. Für den vollständigen API-Pfad `scripts/openwebui_workspace_config.yaml` nutzen; sie setzt Jupyter-, Artefakt-, Addon-, Tool- und Function-/Filter-Valves zentral.

Der empfohlene Offline-Stack bindet `F:\offline-ai-stack\openwebui-offline-addons` in OpenWebUI ein. Die Konfigurationsdatei setzt dafür `addons.*`, `environment.*` und die passenden `tool_valves.*`, sodass Tools lokale Python-Pakete, Tiktoken/NLTK-Caches und Playwright/Chromium ohne Laufzeitdownloads verwenden können. Filterwerte wie das Kontextbudget des `context_compressor_filter` liegen im Abschnitt `function_valves`.

Optionale Tools aus `openwebui-tools-import.json`, die nicht im Offline-Default liegen, müssen bewusst konfiguriert werden: `openui_generative_ui.py` benötigt ein lokal bereitgestelltes OpenUI-Browser-Bundle, `web_search_and_crawl.py` lokale/self-hosted SearXNG-/Crawl4AI-Endpunkte und `safe_http_fetcher.py`/`github_repo_inspector.py` sind keine Air-Gap-Defaults.
Alle Functions in `openwebui-functions-import.json` sind als OpenWebUI-Filter importierbar. `auto_tool_selector.py` ist ein offlinefähiger inlet-Filter und aktiviert nur Tool-IDs, die im Modell- oder Request-Kontext verfügbar sind.

## Reproduzierbare Erzeugung

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```

Für einen direkten API-Import in eine laufende OpenWebUI-Instanz:

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Ein lokaler Import-Probelauf ohne OpenWebUI-Aufruf ist mit `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.yaml` möglich.
