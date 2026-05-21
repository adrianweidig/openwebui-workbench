# OpenWebUI Extensions

Dieses Repository enthält zusätzliche OpenWebUI-Erweiterungen unter `Tools/openwebui_ext/`. Sie ergänzen die vorhandenen Modelle und das bestehende Jupyter-Tool um praktische, einzeln importierbare Tools, Filter und Skills.

## Tools importieren

1. OpenWebUI als Administrator öffnen.
2. `Workspace > Tools > Import` wählen.
3. Für den Offline-Standard `Tools/dist/openwebui-tools-offline-import.json` importieren. Dieses Bundle enthält nur Tools mit Air-Gap-sicheren Defaults.
4. Falls optionale Tools bewusst erlaubt sind, stattdessen `Tools/dist/openwebui-tools-import.json` importieren. Darin liegen zusätzlich Public-Network-/Rich-UI-Tools, die lokale Endpunkte oder statische Assets benötigen.
5. Speichern, Valves prüfen und Tools gezielt für passende Modelle aktivieren.

Fallback für einzelne Tools: `Workspace > Tools > Create Tool` öffnen und den Inhalt einer Datei aus `Tools/openwebui_ext/tools/*.py` oder `Tools/jupyter/jupyter_tool.py` einfügen.

Tools führen serverseitig Python aus. Nur vertrauenswürdige Administratoren sollten Tools importieren oder ändern.

Die öffentlichen Tool-Exports aus `Tools/openwebui_ext/third_party/public_openwebui_tools/` wurden nicht roh als Default übernommen. Produktive Kopien liegen unter `Tools/openwebui_ext/tools/` und wurden für Air-Gap-Betrieb angepasst: keine öffentlichen API-Fallbacks, keine öffentlichen CDN-Defaults im Offline-Standard und Public-Web-Crawling nur mit lokaler/private Host-Allowlist.

## Filter importieren

1. OpenWebUI als Administrator öffnen.
2. `Workspace > Functions > Import` wählen und `Tools/dist/openwebui-functions-import.json` importieren.
3. Falls der Function-Importdialog nicht verfügbar ist, `Workspace > Functions > Create Function` wählen und den Inhalt aus `Tools/openwebui_ext/filters/context_compressor_filter.py` einfügen.
4. Speichern, Valves prüfen und Filter für Modelle aktivieren.

Der Filter `context_compressor_filter.py` zählt vor jedem Modellaufruf die geschätzten Kontexttokens. Sobald der konfigurierte Schwellwert erreicht ist, sendet er eine Statusmeldung, erzeugt eine kompakte Zusammenfassung älterer Chatteile und injiziert diese als Systemkontext in denselben Chatrequest. Einen neuen Chat legt der Filter bewusst nicht selbst an, weil OpenWebUI-Filter dafür keine stabile versionsübergreifende API garantieren; der robuste Default ist die Zusammenfassung im aktuellen Chatkontext.

## Skills importieren

1. `Workspace > Skills > Import` öffnen.
2. Eine Datei aus `Tools/openwebui_ext/skills/*.md` auswählen.
3. Name, Beschreibung und Zugriff prüfen.
4. Skill per `$skill-name` im Chat nutzen oder an ein Modell binden.

## Tool-Katalog

- `safe_http_fetcher.py`: optionales Netzwerktool für HTTP-GET/HEAD-Prüfung mit SSRF-Schutz; nicht Teil des Offline-Standardimports.
- `openapi_schema_inspector.py`: OpenAPI-JSON lokal auswerten.
- `json_csv_text_validator.py`: JSON, CSV und Text validieren.
- `github_repo_inspector.py`: optionales Netzwerktool für GitHub-Repositories read-only; nicht Teil des Offline-Standardimports.
- `docker_compose_triage.py`: Docker-Compose- und OpenWebUI-Fehlertexte analysieren.
- `repo_tree_analyzer.py`: eingefügte Repository-Bäume auswerten.
- `markdown_skill_builder.py`: OpenWebUI-Skill-Markdown erzeugen.
- `mediawiki_legacy_crawler.py`: interne MediaWiki-Instanzen per API crawlen, inklusive Legacy-Username/Passwort-Login über Valves.
- `offline_artifact_workbench.py`: offline HTML-, Präsentations-, PDF- und ZIP-Artefakte erzeugen.
- `inline_visuals_toolkit_v3.py`: offline SVG-Charts, HTML-Dashboards, Mermaid-Blöcke und Visual-Briefs erzeugen.
- `parallel_task_planner.py`: komplexe Arbeit in sichere Parallelwellen und Subagent-Arbeitspakete zerlegen.
- `subagent_orchestrator.py`: Subagent-Roster, Delegationsprompts und Ergebnis-Merges erzeugen.
- `tool_skill_overlay_planner.py`: Modell-/Tool-/Skill-Overlays mit Redundanz und Fallbacks planen.
- `comfyui_workflow_inspector.py`: ComfyUI-Workflow-JSON lokal prüfen und Setup-Checklisten erzeugen.

## Filter-Katalog

- `context_compressor_filter.py`: modellübergreifender Kontextkomprimierer mit Token-Schätzung, Statusmeldung und automatischer Zusammenfassung älterer Chatanteile.

## Skill-Katalog

- `secure-tool-usage`: sichere Tool-Auswahl und Secret-Handling.
- `openwebui-tool-authoring`: Erstellung importierbarer Python-Tools.
- `repository-maintenance`: strukturierte Repo-Wartung.
- `code-review-deep`: gründlicher Code-Review.
- `api-integration-debugging`: API-, Auth- und OpenAPI-Diagnose.
- `docker-openwebui-troubleshooting`: Docker/OpenWebUI-Fehleranalyse.
- `research-grounding`: quellenbasierte Recherche.
- `data-cleaning-analysis`: Datenvalidierung und Bereinigung.
- `prompt-to-tool-workflow`: Ziel in Tool-/Skill-Workflow übersetzen.
- `offline-artifact-production`: Workflow für offline erzeugte HTML-, PDF-, Präsentations- und Download-Artefakte.
- `visual-toolkit-v3-offline`: Visuals, SVG, Mermaid, Dashboards und ComfyUI-Fallbacks.
- `parallel-tools-subagents`: Parallelisierung und Subagent-Aufteilung.
- `model-tool-skill-overlays`: robuste modellbezogene Tool-/Skill-Überlagerung.
- `redundant-fallback-tooling`: Fallback-Ketten für gleiche Use Cases.
- `offline-creative-media-workflows`: lokale Bild-, Audio-, Video- und Präsentations-Workflows.
- `offline-use-case-router`: Routing neuer Aufgaben auf passende Offline-Tools und Skills.
- `safe-mcp-openapi-import`: sichere MCP-/OpenAPI-Toolserver-Prüfung.
- `native-tool-calling-rollout`: Native-Tool-Calling-Rollout und Abnahmetests.

## Valves, API-Keys und Secrets

Secrets gehören nie in Git. Tool-Konfigurationen wie GitHub-Token werden in OpenWebUI-Valves oder über sichere OAuth-Injektion gesetzt. Dokumentations- und Beispielwerte müssen Platzhalter bleiben.

Für Artefakte kann `OPENWEBUI_ARTIFACT_ROOT` gesetzt werden. Dieser Pfad sollte als persistentes Volume in den OpenWebUI-Container eingebunden werden, damit erzeugte Dateien nach Neustarts erhalten bleiben.

## Tests

Lokale Prüfung:

```powershell
python scripts/validate_openwebui_extensions.py
python -m unittest Tools.openwebui_ext.tests.test_openwebui_tools_importable
python scripts/configure_openwebui_tool_models.py --check
python -m unittest Tools.openwebui_ext.tests.test_openwebui_filters_importable
```

## Tool- und Modellregistrierung

Die reproduzierbare Tool-/Modellkonfiguration wird über `scripts/configure_openwebui_tool_models.py` erzeugt:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```

Das Skript arbeitet in dieser Reihenfolge:

1. Tool-Dateien aus `Tools/jupyter/` und `Tools/openwebui_ext/tools/` entdecken und importierbar prüfen.
2. Filter-Dateien aus `Tools/openwebui_ext/filters/` entdecken und importierbar prüfen.
3. `Tools/dist/openwebui-tools-offline-import.json`, `Tools/dist/openwebui-tools-import.json`, `Tools/dist/openwebui-functions-import.json`, `Tools/index.json`, die Registries und die Fallback-Bundles erzeugen.
4. Chat-Modelle in `Modelle/einzelmodelle/*/model.json` konfigurieren.
5. Kombinierte Modellimporte und Einzelartefakte unter `Modelle/dist/` neu schreiben.
6. Optional Offline-ZIP-Pakete neu bauen.

Chat-Modelle erhalten nur Offline-Default-Tools in `meta.toolIds`, außerdem `meta.filterIds`, `meta.defaultFilterIds`, `meta.capabilities.builtin_tools: true`, `meta.primaryToolIds`, `meta.recommendedSkillIds`, `meta.requiredKnowledgeFiles`, `params.function_calling: "native"`, use-case-spezifische `params.temperature`-/`params.top_p`-Werte, eingebettete SVG-Icons in `meta.profile_image_url`, ein High-Reasoning-Systemprofil und eine verbindliche Tool-/Skill-Nutzungssektion inklusive Systemprompt, Mainprompt und Fachwissen. Diese Sektion nennt pro Modell primäre Tools und passende Skills aus der Offline-Capability-Map, erzwingt am Aufgabenanfang eine Tool-/Skill-Inventur und verpflichtet das Modell, bei passenden Auslösern vor der finalen Antwort ein geeignetes freigegebenes Tool zu nutzen. `params.max_tokens` wird nicht gesetzt, damit OpenWebUI und der jeweilige Modellserver ihre eigenen Kontext- und Antwortlimits verwenden. Nicht passende Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden ebenfalls nicht gesetzt. Öffentliche Netzwerktools werden im Offline-Standard nicht zugewiesen. Embedding- und Reranker-Modelle werden anhand von Modell-ID, Name, Base Model, Tags und Capabilities ausgeschlossen; falls solche Modelle später ergänzt werden, entfernt das Skript dort Tool-, Filter- und Function-Calling-Zuweisungen.

Der API-basierte Import kann direkt über den Generator ausgeführt werden:

```powershell
$env:OPENWEBUI_ADMIN_TOKEN="YOUR_OPEN_WEBUI_API_KEY"
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --base-url http://localhost:3000
```

Der Generator validiert zuerst alle lokalen Artefakte und startet danach `Tools/import_openwebui_workspace.py`. Der Importer importiert beziehungsweise aktualisiert Tools, Functions/Filter, Skills und Modelle. Standardmäßig lädt er zusätzlich `mainprompt.md` und `fachwissen.md` jedes Modellpakets als Knowledge-Basis hoch und verknüpft diese Knowledge im jeweiligen Modellprofil. Ein lokaler Payload-Check ohne OpenWebUI-Aufruf ist mit `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run` oder direkt mit `python Tools/import_openwebui_workspace.py --dry-run` möglich.

## Wartung

Vor Produktiveinsatz externe Tools und neue eigene Tools erneut prüfen. Änderungen an Tool-Dateien sollten immer mit Importtest, Annotationstest und Secret-Scan validiert werden.

## Offline Capability Map

Für die modellbezogene Zuordnung und Fallback-Abdeckung liegt eine Matrix unter `Tools/openwebui_ext/docs/offline-capability-map.md`. Sie beschreibt, welche Tools und Skills pro Use Case kombiniert werden sollten und welche Drittanbieter-/Same-Origin-/API-Tools nicht als Default aktiviert werden.
