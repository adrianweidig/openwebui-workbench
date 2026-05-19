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
- `openwebui_ext/tools/offline_artifact_workbench.py`: HTML-, Präsentations-, PDF- und ZIP-Artefakte im erlaubten Artefaktverzeichnis erzeugen.
- `openwebui_ext/tools/json_csv_text_validator.py`: Daten vor Artefakterzeugung validieren.
- `openwebui_ext/tools/inline_visuals_toolkit_v3.py`: offline SVG-Charts, HTML-Dashboards und Mermaid-Blöcke erzeugen.
- `openwebui_ext/tools/parallel_task_planner.py`: komplexe Arbeit in sichere Parallelwellen und Subagent-Aufgaben zerlegen.
- `openwebui_ext/tools/tool_skill_overlay_planner.py`: Tools und Skills redundant auf Modellprofile verteilen.
- `openwebui_ext/tools/comfyui_workflow_inspector.py`: ComfyUI-Workflows offline prüfen und Setup-Checklisten erzeugen.
- `openwebui_ext/tools/mediawiki_legacy_crawler.py`: interne alte MediaWiki-Server per API und Legacy-Login crawlen.
