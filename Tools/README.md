# Tools

Dieser Ordner enthält die operativ relevanten Tool-Artefakte.

## Unterstruktur

- `jupyter/`: Offline-Jupyter-Tool für OpenWebUI
- `openwebui_ext/`: zusätzliche direkt importierbare OpenWebUI-Tools, Skills, Doku und Tests
- `dist/`: portables Offline-Paket für Tools und Skills
- `index.json`: Tool-Index für die lokale Übersicht
- `import_openwebui_workspace.py`: API-Importer für Tools, Functions/Filter, Skills, Knowledge und Modelle

## Nutzung

Die produktive Tool-Datei für OpenWebUI liegt unter `jupyter/jupyter_tool.py`.

Weitere produktive Tools liegen unter `openwebui_ext/tools/`. Für den Offline-ChatGPT-ähnlichen Betrieb sind besonders wichtig:

- `jupyter/jupyter_tool.py`: kontrollierte Python-Ausführung über den lokalen Jupyter-Server.
- `openwebui_ext/tools/ask_user.py`: interaktive Rückfragen über OpenWebUI-Pop-ups stellen.
- `openwebui_ext/tools/offline_artifact_workbench.py`: HTML-, Präsentations-, PDF- und ZIP-Artefakte im erlaubten Artefaktverzeichnis erzeugen.
- `openwebui_ext/tools/json_csv_text_validator.py`: Daten vor Artefakterzeugung validieren.
- `openwebui_ext/tools/inline_visuals_toolkit_v3.py`: offline SVG-Charts, HTML-Dashboards und Mermaid-Blöcke erzeugen.
- `openwebui_ext/tools/parallel_task_planner.py`: komplexe Arbeit in sichere Parallelwellen und Subagent-Aufgaben zerlegen.
- `openwebui_ext/tools/parallel_tools.py`: bereits aktivierte OpenWebUI-Tools parallel ausführen.
- `openwebui_ext/tools/sub_agent.py`: direkte OpenWebUI-Subagenten mit Air-Gap-sicheren Builtin-Defaults ausführen.
- `openwebui_ext/tools/llm_council.py`: lokale Modellratsantworten über die OpenWebUI-API erzeugen.
- `openwebui_ext/tools/subagent_orchestrator.py`: Subagent-Roster, delegierbare Arbeitspakete und Ergebnis-Merges für agentische Workflows erzeugen.
- `openwebui_ext/tools/tool_skill_overlay_planner.py`: Tools und Skills redundant auf Modellprofile verteilen.
- `openwebui_ext/tools/comfyui_workflow_inspector.py`: ComfyUI-Workflows offline prüfen und Setup-Checklisten erzeugen.
- `openwebui_ext/tools/mediawiki_legacy_crawler.py`: interne alte MediaWiki-Server per API und Legacy-Login crawlen.
- `openwebui_ext/filters/auto_tool_selector.py`: passende lokale Tools und optional konfigurierte MCP-Server vor dem Modellaufruf aktivieren.
- `openwebui_ext/filters/markdown_normalizer.py`: Markdown-, Tabellen-, Mermaid- und Codeblock-Ausgaben nach dem Modellaufruf normalisieren.
- `openwebui_ext/filters/context_compressor_filter.py`: lange Chats vor dem Modellaufruf lokal komprimieren.

Optionale, nicht im Offline-Standard aktivierte Drittanbieter-Tools:

- `openwebui_ext/tools/openui_generative_ui.py`: Rich UI nur mit lokal bereitgestelltem OpenUI-Browser-Bundle.
- `openwebui_ext/tools/web_search_and_crawl.py`: lokale/self-hosted SearXNG-/Crawl4AI-Suche mit Public-Network-Guard.
- `openwebui_ext/tools/safe_http_fetcher.py` und `openwebui_ext/tools/github_repo_inspector.py`: bewusste Netzwerkprofile, nicht Air-Gap-Default.

Die Laufzeit-Abhängigkeiten der importierbaren Tools sind in `openwebui_ext/docs/offline-capability-map.md` dokumentiert. Dort ist festgehalten, welche Dateien nur die OpenWebUI-Tool-Laufzeit benötigen, welche optional lokale Renderer verwenden und welche bewusst nicht zum Air-Gap-Default gehören.

## API-Import

Der bevorzugte Weg ist der Generator mit anschließendem API-Import. Er schreibt zuerst die Registries, Modellprofile, ZIPs und Prüfübersichten und ruft danach den Importer auf:

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Die Konfigurationsdatei ist die zentrale Laufzeitquelle für den Import: `openwebui.base_url` muss von der Maschine erreichbar sein, auf der das Python-Skript läuft; `jupyter.url`, `artifacts.root`, `addons.*`, `tool_valves.*` und `function_valves.*` müssen aus Sicht des OpenWebUI-Backends sinnvoll sein, z. B. `http://jupyter:8888` oder `/app/backend/data/cache/ms-playwright`. Standardmäßig importiert der API-Importer alle importierbaren Tools aus dem Repo; `import.include_optional_network_tools: false` schränkt dies lokal auf die Offline-Default-Tools ein. Tools, Skills, modellbezogene Knowledge-Bases und Modelle werden dabei automatisch public gesetzt; Functions/Filter werden aktiv und global geschaltet.

`import_openwebui_workspace.py` bleibt als Fallback direkt ausführbar und nutzt dieselbe zentrale YAML. Es importiert Tools, setzt Tool-Valves, importiert Functions/Filter, setzt Function-/Filter-Valves, importiert Skills, lädt `mainprompt.md`, `fachwissen.md`, die modellseitig definierte Beispielergebnis-Datei und Dateien aus `beispiele/` je Modell als Knowledge hoch, importiert anschließend die Modellprofile inklusive eingebetteter Icons und erzwingt die Public-/Global-Sichtbarkeit über die OpenWebUI-API. Vor einem echten Import kann `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.yaml` die lokalen Payloads prüfen.
Tool-Updates und Tool-Valves werden zuerst über `/api/tools/...` ausgeführt und danach über `/api/v1/tools/...` versucht. Ein `We could not find what you're looking for` beim Valves-Schritt bedeutet in OpenWebUI normalerweise: Tool-ID noch nicht vorhanden, keine erkennbare `Valves`-Klasse im Tool oder eine ältere Instanz ohne diesen Endpunkt. Der Importer bricht dann nicht den gesamten Lauf ab, sondern meldet den übersprungenen Valves-Satz.
Es wird auch in `dist/openwebui-tools-skills-offline.zip` mit ausgeliefert.
