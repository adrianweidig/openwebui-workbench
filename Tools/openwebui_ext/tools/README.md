# OpenWebUI Tools

Dieses Verzeichnis enthält direkt importierbare OpenWebUI-Workspace-Tools als einzelne Python-Dateien. Jede Datei enthält eine `Tools`-Klasse, typisierte `async`-Methoden und eine kurze Sicherheitsnotiz im Metadaten-Docstring.

## Enthaltene Tools

- `safe_http_fetcher.py`: begrenzte HTTP-GET/HEAD-Abfragen für öffentliche URLs mit SSRF-Schutz.
- `openapi_schema_inspector.py`: lokale Analyse eingefügter OpenAPI-JSON-Schemas.
- `json_csv_text_validator.py`: Validierung und Zusammenfassung von JSON, CSV und Text.
- `github_repo_inspector.py`: read-only GitHub-Repository-Metadatenprüfung.
- `docker_compose_triage.py`: Analyse eingefügter Docker-Compose- und Fehlertexte.
- `repo_tree_analyzer.py`: Analyse eingefügter Repository-Dateibäume ohne Dateisystemzugriff.
- `markdown_skill_builder.py`: Erstellung importierbarer OpenWebUI-Skill-Markdown-Dateien.
- `offline_artifact_workbench.py`: Offline-Erzeugung von HTML-Dokumenten, HTML-Präsentationen, optionalen PDFs und ZIP-Paketen.
- `inline_visuals_toolkit_v3.py`: Offline-SVG-Charts, HTML-Dashboards, Mermaid-Blöcke und Visual-Briefs ohne externe Assets.
- `parallel_task_planner.py`: Dependency-sichere Parallelwellen, Subagent-Arbeitspakete und Ergebnis-Konsolidierung.
- `tool_skill_overlay_planner.py`: Modellbezogene Tool-/Skill-Overlays, Redundanz und Fallback-Abdeckung.
- `comfyui_workflow_inspector.py`: Lokale ComfyUI-Workflow-Inspection und Offline-Setup-Checklisten.

## Import

In OpenWebUI als Administrator `Workspace > Tools > Create Tool` öffnen, den Inhalt einer `.py`-Datei einfügen, speichern und anschließend gezielt für Modelle aktivieren.

## Sicherheitsgrenzen

Tools führen serverseitig Python aus. Vor Produktiveinsatz Code erneut prüfen, Zugriff nur vertrauenswürdigen Administratoren geben und Valves ohne echte Secrets versionieren.
