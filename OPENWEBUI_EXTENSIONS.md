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
Die öffentlichen Function-Exports aus `Tools/openwebui_ext/third_party/public_openwebui_functions/` werden produktiv ausschließlich als echte Filter unter `Tools/openwebui_ext/filters/` geführt. `auto_tool_selector.py` aktiviert passende lokale Tools und optional konfigurierte MCP-Server vor dem Modellaufruf, bleibt dabei aber offlinefähig und verzichtet auf externe LLM- oder Netzwerk-Fallbacks.

## Filter importieren

1. OpenWebUI als Administrator öffnen.
2. `Workspace > Functions > Import` wählen und `Tools/dist/openwebui-functions-import.json` importieren.
3. Falls der Function-Importdialog nicht verfügbar ist, `Workspace > Functions > Create Function` wählen und den Inhalt aus `Tools/openwebui_ext/filters/*.py` einzeln einfügen.
4. Speichern, Valves prüfen und Filter für Modelle aktivieren.

Der Filter `context_compressor_filter.py` zählt vor jedem Modellaufruf die geschätzten Kontexttokens. Sobald der konfigurierte Schwellwert erreicht ist, sendet er eine Statusmeldung, erzeugt eine kompakte Zusammenfassung älterer Chatteile und injiziert diese als Systemkontext in denselben Chatrequest. Einen neuen Chat legt der Filter bewusst nicht selbst an, weil OpenWebUI-Filter dafür keine stabile versionsübergreifende API garantieren; der robuste Default ist die Zusammenfassung im aktuellen Chatkontext.
Der Filter `auto_tool_selector.py` läuft als `inlet` vor dem Modellaufruf. Er ergänzt `body.tool_ids` heuristisch um passende bereits verfügbare lokale Tools wie `ask_user`, `parallel_tools`, `sub_agent`, `llm_council`, `visuals_toolkit_v4`, Jupyter, Artefakt-Tools und Validatoren. Optionale Public-/Netzwerktools werden nur gewählt, wenn sie tatsächlich im Modell-/Request-Kontext verfügbar sind.

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
- `parallel_tools.py`: bereits aktivierte OpenWebUI-Tools parallel ausführen.
- `sub_agent.py`: isolierte OpenWebUI-Subagenten mit Air-Gap-sicheren Defaults ausführen.
- `llm_council.py`: lokale Modellratsantworten über die OpenWebUI-API erzeugen.
- `visuals_toolkit_v4.py`: CDN-freie Text-, ASCII- und Visual-Hilfen als Ergänzung zu den lokalen Visual-Tools.
- `tool_skill_overlay_planner.py`: Modell-/Tool-/Skill-Overlays mit Redundanz und Fallbacks planen.
- `comfyui_workflow_inspector.py`: ComfyUI-Workflow-JSON lokal prüfen und Setup-Checklisten erzeugen.

## Filter-Katalog

- `context_compressor_filter.py`: modellübergreifender Kontextkomprimierer mit Token-Schätzung, Statusmeldung und automatischer Zusammenfassung älterer Chatanteile.
- `auto_tool_selector.py`: offlinefähiger inlet-Filter, der passende Tool-IDs vor dem Modellaufruf aktiviert.
- `markdown_normalizer.py`: output-Filter für Markdown-, Mermaid-, Tabellen- und Codeblock-Normalisierung.

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

Chat-Modelle erhalten im Spezialmodell-Standard nur Offline-Default-Tools in `meta.toolIds`; das Fallbackmodell `Allgemein` erhält bewusst alle importierbaren Tools. Zusätzlich setzt der Generator `meta.filterIds`, `meta.defaultFilterIds`, `meta.capabilities.builtin_tools: true`, `meta.primaryToolIds`, `meta.recommendedSkillIds`, `meta.requiredKnowledgeFiles`, `params.function_calling: "native"`, use-case-spezifische `params.temperature`-/`params.top_p`-Werte, eingebettete SVG-Icons in `meta.profile_image_url`, ein High-Reasoning-Systemprofil, ein CustomGPT-Qualitätsprofil, explizite Tool-Aufrufmuster, den Markdown-Formatierungshinweis und eine verbindliche Tool-/Skill-Nutzungssektion inklusive Systemprompt, Mainprompt und Fachwissen. Diese Sektion nennt pro Modell primäre Tools und passende Skills aus der Offline-Capability-Map, erzwingt am Aufgabenanfang eine Tool-/Skill-Inventur und verpflichtet das Modell, bei passenden Auslösern vor der finalen Antwort ein geeignetes freigegebenes Tool zu nutzen. Die expliziten Tool-Aufrufmuster nennen konkrete Methoden für lokale Mistral-Medium-128B-Instanzen, unter anderem `parallel_task_planner.build_parallel_execution_plan(...)`, `parallel_tools.run_tools_parallel(...)`, `sub_agent.run_sub_agent(...)`, `sub_agent.run_parallel_sub_agents(...)`, `air_gapped_jupyter_python.run_python(...)`, `json_csv_text_validator.validate_json(...)`, `offline_artifact_workbench.create_slide_deck(...)`, `openapi_schema_inspector.inspect_openapi_json(...)`, `docker_compose_triage.analyze_error_text(...)` und `tool_skill_overlay_planner.build_overlay_matrix(...)`. Das CustomGPT-Qualitätsprofil erzwingt klare Rolle, Scope, Knowledge-Nutzung, Erfolgskriterien, Sicherheitsgrenzen, maximal drei Rückfragen und einen finalen Selbstcheck. `params.max_tokens` wird nicht gesetzt, damit OpenWebUI und der jeweilige Modellserver ihre eigenen Kontext- und Antwortlimits verwenden. Nicht passende Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden ebenfalls nicht gesetzt; High Reasoning wird über die Systemanweisung, Tool-Planung und Ergebnisvalidierung erzwungen. Öffentliche Netzwerktools werden im Offline-Standard nicht zugewiesen, stehen aber im Modell `Allgemein` für bewusst freigegebene Instanzen zur Verfügung. Embedding- und Reranker-Modelle werden anhand von Modell-ID, Name, Base Model, Tags und Capabilities ausgeschlossen; falls solche Modelle später ergänzt werden, entfernt das Skript dort Tool-, Filter- und Function-Calling-Zuweisungen.

Der API-basierte Import kann direkt über den Generator ausgeführt werden:

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Die Konfigurationsdatei enthält die von der ausführenden Maschine erreichbare OpenWebUI-Adresse und den Admin-API-Key sowie die aus Sicht des OpenWebUI-Backends erreichbare Jupyter-Adresse, den Jupyter-Token und das Artefakt-Volume. Die echte `scripts/openwebui_workspace_config.yaml` ist per `.gitignore` ausgeschlossen; nur die Beispiel-Datei wird versioniert. `import.include_optional_network_tools: true` ist der Standard, damit der API-Importer alle importierbaren Repo-Tools anlegt; für einen strikten Minimalimport kann der Wert lokal auf `false` gesetzt werden.
Alternativ können dieselben Werte für lokale Einmalimporte oben in `scripts/configure_openwebui_tool_models.py` in den `SCRIPT_*`-Konstanten oder als CLI-Parameter wie `--jupyter-url`, `--jupyter-token` und `--artifact-root` gesetzt werden.

Der Generator validiert zuerst alle lokalen Artefakte und startet danach `Tools/import_openwebui_workspace.py`. Der Importer importiert beziehungsweise aktualisiert Tools, Functions/Filter, Skills und Modelle. Standardmäßig lädt er zusätzlich `mainprompt.md` und `fachwissen.md` jedes Modellpakets als Knowledge-Basis hoch, verknüpft diese Knowledge im jeweiligen Modellprofil und setzt die Tool-Valves für `air_gapped_jupyter_python` sowie `offline_artifact_workbench`. Ein lokaler Payload-Check ohne OpenWebUI-Aufruf ist mit `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.yaml` oder direkt mit `python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.yaml` möglich.

## Wartung

Vor Produktiveinsatz externe Tools und neue eigene Tools erneut prüfen. Änderungen an Tool-Dateien sollten immer mit Importtest, Annotationstest und Secret-Scan validiert werden.

## Offline Capability Map

Für die modellbezogene Zuordnung und Fallback-Abdeckung liegt eine Matrix unter `Tools/openwebui_ext/docs/offline-capability-map.md`. Sie beschreibt, welche Tools und Skills pro Use Case kombiniert werden sollten und welche Drittanbieter-/Same-Origin-/API-Tools nicht als Default aktiviert werden.
