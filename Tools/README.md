# Tools

Dieser Ordner enthält die operativ relevanten Tool-Artefakte.

## Unterstruktur

- `jupyter/`: Offline-Jupyter-Tool für OpenWebUI
- `openwebui_ext/`: zusätzliche direkt importierbare OpenWebUI-Tools, Skills, Doku und Tests
- `dist/`: portables Offline-Paket für Tools und Skills
- `index.json`: Tool-Index für die lokale Übersicht

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

Optionale, nicht im Offline-Standard aktivierte Drittanbieter-Tools:

- `openwebui_ext/tools/openui_generative_ui.py`: Rich UI nur mit lokal bereitgestelltem OpenUI-Browser-Bundle.
- `openwebui_ext/tools/web_search_and_crawl.py`: lokale/self-hosted SearXNG-/Crawl4AI-Suche mit Public-Network-Guard.
- `openwebui_ext/tools/safe_http_fetcher.py` und `openwebui_ext/tools/github_repo_inspector.py`: bewusste Netzwerkprofile, nicht Air-Gap-Default.
