---
name: offline-use-case-router
description: Ordnet beliebige Nutzeranfragen passenden Offline-Tools, Skills, Modellprofilen und Fallbacks zu.
---

# Offline Use Case Router

Nutze diesen Skill als erste Orientierung für neue oder unklare Aufgaben in der Offline-Workbench.

## Routing

- Daten, JSON, CSV, Logs: `json_csv_text_validator`, danach Jupyter oder Artefakt-Workbench.
- Code, Repository, Review: `repo_tree_analyzer`, `code-review-deep`, `repository-maintenance`.
- API, OpenAPI, Integration: `openapi_schema_inspector`, `api-integration-debugging`.
- Docker/OpenWebUI-Betrieb: `docker_compose_triage`, `docker-openwebui-troubleshooting`.
- Recherche mit Quellen: `research-grounding`; offline nur mit bereitgestellten Quellen oder Knowledge Base.
- Visuals, Diagramme, Dashboards: `inline_visuals_toolkit_v3`, `visual-toolkit-v3-offline`.
- Medien/ComfyUI: `comfyui_workflow_inspector`, `offline-creative-media-workflows`.
- Komplexe Arbeit: `parallel_task_planner`, `parallel-tools-subagents`.
- Modell-/Tool-Zuordnung: `tool_skill_overlay_planner`, `model-tool-skill-overlays`.

## Verhalten

Wähle den kleinsten ausreichenden Tool-Satz. Wenn ein Tool fehlt, nenne den nächsten Fallback und arbeite mit Skills oder Checklisten weiter.
