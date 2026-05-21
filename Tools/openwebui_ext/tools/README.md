# OpenWebUI Tools

Dieses Verzeichnis enthält direkt importierbare OpenWebUI-Workspace-Tools als einzelne Python-Dateien. Jede Datei enthält eine `Tools`-Klasse, typisierte `async`-Methoden und eine kurze Sicherheitsnotiz im Metadaten-Docstring.

## Enthaltene Tools

- `safe_http_fetcher.py`: begrenzte HTTP-GET/HEAD-Abfragen für öffentliche URLs mit SSRF-Schutz.
- `openapi_schema_inspector.py`: lokale Analyse eingefügter OpenAPI-JSON-Schemas.
- `json_csv_text_validator.py`: Validierung und Zusammenfassung von JSON, CSV und Text.
- `github_repo_inspector.py`: read-only GitHub-Repository-Metadatenprüfung.
- `ask_user.py`: Interaktive OpenWebUI-Pop-up-Rückfragen ohne externe Dienste.
- `docker_compose_triage.py`: Analyse eingefügter Docker-Compose- und Fehlertexte.
- `repo_tree_analyzer.py`: Analyse eingefügter Repository-Dateibäume ohne Dateisystemzugriff.
- `markdown_skill_builder.py`: Erstellung importierbarer OpenWebUI-Skill-Markdown-Dateien.
- `offline_artifact_workbench.py`: Offline-Erzeugung von HTML-Dokumenten, HTML-Präsentationen, optionalen PDFs und ZIP-Paketen.
- `inline_visuals_toolkit_v3.py`: Offline-SVG-Charts, HTML-Dashboards, Mermaid-Blöcke und Visual-Briefs ohne externe Assets.
- `parallel_task_planner.py`: Dependency-sichere Parallelwellen, Subagent-Arbeitspakete und Ergebnis-Konsolidierung.
- `parallel_tools.py`: Drittanbieter-Tool für parallele Ausführung bereits aktivierter OpenWebUI-Tools.
- `sub_agent.py`: Drittanbieter-Tool für isolierte OpenWebUI-Subagenten mit Air-Gap-sicheren Defaults.
- `llm_council.py`: Lokaler Modellrat über die OpenWebUI-API ohne öffentliche Fallback-APIs.
- `tool_skill_overlay_planner.py`: Modellbezogene Tool-/Skill-Overlays, Redundanz und Fallback-Abdeckung.
- `comfyui_workflow_inspector.py`: Lokale ComfyUI-Workflow-Inspection und Offline-Setup-Checklisten.
- `visuals_toolkit_v4.py`: Drittanbieter-Visuals mit CDN-freiem Text-/ASCII-Default.
- `openui_generative_ui.py`: Optionales Rich-UI-Tool für lokal bereitgestellte OpenUI-Browser-Bundles; kein Offline-Default.
- `web_search_and_crawl.py`: Optionales lokales/self-hosted SearXNG-/Crawl4AI-Tool mit Air-Gap-Allowlist; kein Offline-Default.

## Import

In OpenWebUI als Administrator `Workspace > Tools > Import` öffnen und bevorzugt `Tools/dist/openwebui-tools-offline-import.json` importieren. Für einzelne Tools kann alternativ `Workspace > Tools > Create Tool` genutzt werden; dann den Inhalt der jeweiligen `.py`-Datei einfügen, speichern und anschließend gezielt für Modelle aktivieren.

## Sicherheitsgrenzen

Tools führen serverseitig Python aus. Vor Produktiveinsatz Code erneut prüfen, Zugriff nur vertrauenswürdigen Administratoren geben und Valves ohne echte Secrets versionieren.
