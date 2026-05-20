# Offline Capability Map

Diese Matrix ordnet typische OpenWebUI-Use-Cases auf lokale Tools, Skills und Fallbacks. Ziel ist nicht ein einzelnes Monster-Tool, sondern überlagerbare Fähigkeiten, die pro Modellprofil gefahrlos aktiviert werden können.

## Grundregeln

- Native Tool Calling für toolfähige Modelle nutzen.
- Kritische Use Cases mindestens doppelt abdecken: Tool plus Skill oder Tool plus Jupyter/Checkliste.
- Riskante Tools nicht global aktivieren.
- Externe APIs und Dienste nur als optionale lokale Profile, nie als Air-Gap-Default.
- Schreibende Tools pro Modell und Nutzergruppe begrenzen.

## Use-Case-Abdeckung

| Use Case | Primär | Fallback | Skill |
| --- | --- | --- | --- |
| JSON/CSV/Text prüfen | `json_csv_text_validator.py` | Jupyter | `data-cleaning-analysis` |
| Artefakte erzeugen | `offline_artifact_workbench.py` | Jupyter/HTML manuell | `offline-artifact-production` |
| Visuals/Charts/Dashboards | `inline_visuals_toolkit_v3.py` | Mermaid/Texttabelle | `visual-toolkit-v3-offline` |
| ComfyUI-Bild/Audio/Video vorbereiten | `comfyui_workflow_inspector.py` | Prompt-/Parameter-Checkliste | `offline-creative-media-workflows` |
| Parallelisierung/Subagents | `parallel_task_planner.py` | manuelle Wellenplanung | `parallel-tools-subagents` |
| Modell-Tool-Zuordnung | `tool_skill_overlay_planner.py` | Markdown-Matrix | `model-tool-skill-overlays` |
| Redundante Fallbacks | `tool_skill_overlay_planner.py` | manuelle Checkliste | `redundant-fallback-tooling` |
| OpenAPI prüfen | `openapi_schema_inspector.py` | Schemaauszug in Chat | `api-integration-debugging` |
| MCP/OpenAPI sicher importieren | `openapi_schema_inspector.py` | Importentscheidung manuell | `safe-mcp-openapi-import` |
| Docker/OpenWebUI triagieren | `docker_compose_triage.py` | Logauszug im Chat | `docker-openwebui-troubleshooting` |
| Repository-Struktur prüfen | `repo_tree_analyzer.py` | Dateibaum im Chat | `repository-maintenance` |
| Skills erzeugen | `markdown_skill_builder.py` | Skill-Template manuell | `openwebui-tool-authoring` |

## Empfohlene Modellprofile

### Offline Workbench Agent

- Tools: Jupyter, Artefakt-Workbench, Validator, Inline Visuals, Parallel Planner, Overlay Planner.
- Skills: `offline-use-case-router`, `redundant-fallback-tooling`, `native-tool-calling-rollout`.
- Zweck: breite Alltagsabdeckung mit lokalen Fallbacks.

### Visual Media Agent

- Tools: Inline Visuals, ComfyUI Workflow Inspector, Artefakt-Workbench.
- Skills: `visual-toolkit-v3-offline`, `offline-creative-media-workflows`.
- Zweck: Visuals, Präsentationen, Bild-/Audio-/Video-Vorbereitung.

### Integration Agent

- Tools: OpenAPI Inspector, Docker Compose Triage.
- Skills: `safe-mcp-openapi-import`, `api-integration-debugging`, `docker-openwebui-troubleshooting`.
- Zweck: lokale Schnittstellen und Toolserver sicher anbinden.

### Review Agent

- Tools: Repo Tree Analyzer, JSON/CSV/Text Validator.
- Skills: `code-review-deep`, `repository-maintenance`, `secure-tool-usage`.
- Zweck: Code-, Struktur- und Änderungsprüfung.

## Nicht als Default aktivieren

- Tools mit Shell-, Dateischreib-, Deployment- oder Admin-API-Zugriff.
- Drittanbieter-Plugins mit Same-Origin-Iframe-Anforderung, Remote-CDNs oder unklarer CSP, solange kein lokaler Review abgeschlossen ist.
- Externe API-Tools mit Tokenpflicht in einer Air-Gap-Umgebung.
- `safe_http_fetcher.py` und `github_repo_inspector.py` nur in separaten, bewusst nicht-air-gapped Profilen importieren; sie sind kein Offline-Default und keinem Modell zugewiesen.
