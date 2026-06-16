# OpenWebUI Extensions

Dieses Repository enthält zusätzliche OpenWebUI-Erweiterungen unter `Tools/openwebui_ext/`. Sie ergänzen die vorhandenen Modelle und das bestehende Jupyter-Tool um praktische, einzeln importierbare Tools, Filter, Skills und Promptvorlagen.

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

Der Filter `context_compressor_filter.py` zählt vor jedem Modellaufruf die geschätzten Kontexttokens. Sobald der konfigurierte Schwellwert erreicht ist, sendet er eine Statusmeldung, erzeugt eine kompakte Zusammenfassung älterer Chatteile und injiziert diese als Systemkontext in denselben Chatrequest. Zusätzlich entfernt er 0-Ausgabewerte wie `max_tokens: 0` oder `num_predict: 0` und setzt bei weiter übergroßen Requests einen harten Context Budget Guard ein, der Systemnachrichten schützt, die jüngste Nutzeranweisung priorisiert und sehr große Einzelprompts struktur-aware kürzt. Einen neuen Chat legt der Filter bewusst nicht selbst an, weil OpenWebUI-Filter dafür keine stabile versionsübergreifende API garantieren; der robuste Default ist die Zusammenfassung im aktuellen Chatkontext.
Der Filter `auto_tool_selector.py` läuft als `inlet` vor dem Modellaufruf. Er ergänzt `body.tool_ids` heuristisch um passende bereits verfügbare lokale Tools wie `ask_user`, `parallel_tools`, `sub_agent`, `llm_council`, `visuals_toolkit_v4`, Jupyter, Artefakt-Tools und Validatoren. Optionale Public-/Netzwerktools werden nur gewählt, wenn sie tatsächlich im Modell-/Request-Kontext verfügbar sind.

## Skills importieren

1. `Workspace > Skills > Import` öffnen.
2. Eine Datei aus `Tools/openwebui_ext/skills/*.md` auswählen.
3. Name, Beschreibung und Zugriff prüfen.
4. Skill per `$skill-name` im Chat nutzen oder an ein Modell binden.

## Promptvorlagen importieren

1. Bevorzugt den API-Importer oder `Tools/dist/openwebui-prompts-import.json` verwenden.
2. Als Fallback `Workspace > Prompts` öffnen und eine Vorlage aus `Tools/openwebui_ext/prompts/*.md` manuell anlegen.
3. `command`, Name, Inhalt, Tags und Zugriff prüfen.
4. Promptvorlagen sind eigenständige OpenWebUI-Prompts; sie werden nicht als Modell-Knowledge importiert.

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

- `context_compressor_filter.py`: modellübergreifender Kontextkomprimierer mit Token-Schätzung, Statusmeldung, automatischer Zusammenfassung älterer Chatanteile, 0-Output-Token-Normalisierung und hartem Budget-Guard für übergroße Einzelprompts.
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

## Zentrale Konfiguration, Valves und Secrets

Secrets gehören nie in Git. Für den API-Import ist `scripts/openwebui_workspace_config.yaml` die zentrale lokale Konfigurationsdatei; sie wird ignoriert und bleibt auf der Zielmaschine. Dokumentations- und Beispielwerte müssen Platzhalter bleiben.

Die Datei bündelt die von der Import-Maschine erreichbare OpenWebUI-Adresse, den Admin-API-Key, backend-sichtbare Artefakt- und Addon-Pfade, Jupyter-Zugangsdaten, `tool_valves` und `function_valves`. Der Importer setzt daraus unter anderem die Valves für `air_gapped_jupyter_python`, `offline_artifact_workbench` und den `context_compressor_filter`. CLI-Parameter sind nur für bewusste Einmal-Overrides gedacht.

Beim API-Import werden die importierten Tools, Skills, Promptvorlagen, modellbezogenen Knowledge-Bases und Modelle automatisch mit Public-Read-Grants veröffentlicht. Functions und Filter werden nach Create/Update aktiviert und global geschaltet, damit sie ohne manuelle Nacharbeit für alle passenden Modelle greifen.

Der Offline-Addon-Stack `F:\offline-ai-stack\openwebui-offline-addons` kann als lokale OpenWebUI-Erweiterung eingebunden werden. Im Container werden seine Bestandteile über `/app/backend/data/cache`, `/app/backend/data/python`, `/app/backend/data/nltk_data` und `/app/backend/data/cache/ms-playwright` bereitgestellt und in der zentralen YAML abgebildet. Tools und Filter sollen außerdem OpenWebUI-Standardfunktionen wie Datei-/Knowledge-Kontext, Citations, Statusmeldungen, Code Interpreter, native Tool Calls und Builtins nutzen, wenn die Zielinstanz sie anbietet.

## Tests

Zentrale lokale Prüfung:

```powershell
python scripts/verify_openwebui_workspace.py
```

Einzeldiagnose:

```powershell
python -m compileall -q scripts Tools
python scripts/validate_openwebui_extensions.py
python scripts/configure_openwebui_tool_models.py --check
python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.example.yaml
python -m unittest discover Tools.openwebui_ext.tests
```

## Tool- und Modellregistrierung

Die reproduzierbare Tool-/Modellkonfiguration wird über `scripts/configure_openwebui_tool_models.py` erzeugt:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```

Das Skript arbeitet in dieser Reihenfolge:

1. Tool-Dateien aus `Tools/jupyter/` und `Tools/openwebui_ext/tools/` entdecken und importierbar prüfen.
2. Filter-Dateien aus `Tools/openwebui_ext/filters/` entdecken und importierbar prüfen.
3. Promptvorlagen aus `Tools/openwebui_ext/prompts/` entdecken und importierbar prüfen.
4. `Tools/dist/openwebui-tools-offline-import.json`, `Tools/dist/openwebui-tools-import.json`, `Tools/dist/openwebui-functions-import.json`, `Tools/dist/openwebui-prompts-import.json`, `Tools/index.json`, die Registries und die Fallback-Bundles erzeugen.
5. Chat-Modelle in `Modelle/einzelmodelle/*/model.json` konfigurieren.
6. Kombinierte Modellimporte und Einzelartefakte unter `Modelle/dist/` neu schreiben.
7. Optional Offline-ZIP-Pakete neu bauen.

Chat-Modelle erhalten im Spezialmodell-Standard nur Offline-Default-Tools in `meta.toolIds`; das Fallbackmodell `Allgemein` erhält bewusst alle importierbaren Tools. Zusätzlich setzt der Generator `base_model_id` auf das ausgewählte OpenWebUI-Basismodell, standardmäßig `coder`; derselbe Wert ist in der Workbench-GUI im Sync-Bereich, per CLI mit `--base-model-id <modell-id>` oder per Environment `WORKBENCH_BASE_MODEL_ID` änderbar. Außerdem setzt der Generator `meta.filterIds`, `meta.defaultFilterIds`, `meta.capabilities.builtin_tools: true`, `meta.capabilities.vision: true`, `meta.primaryToolIds`, `meta.recommendedSkillIds`, `meta.requiredFileContextFiles`, `meta.exampleKnowledgeFiles`, `meta.workbenchFileContext`, `params.function_calling: "native"`, `params.reasoning_effort: "high"`, `params.temperature: 0.7`, `params.top_p: 0.95`, `params.parallel_tool_calls: true`, eingebettete PNG-Icons in `meta.profile_image_url` und einen kurzen deterministischen Systemprompt. Dieser Systemprompt verweist verbindlich auf `mainprompt.md`, `fachwissen.md` und `Golden_Example.<ext>`; die drei Dateien werden nicht als optionales RAG-Wissen behandelt. Weitere Beispiele aus `beispiele/`, Legacy-Artefakte `beispielergebnis.*` und i18n-Profile bleiben fokussiertes Knowledge/RAG-Material. `params.max_tokens` wird nicht gesetzt, damit OpenWebUI und der jeweilige Modellserver ihre eigenen Kontext- und Antwortlimits verwenden. Öffentliche Netzwerktools werden im Offline-Standard nicht zugewiesen, stehen aber im Modell `Allgemein` für bewusst freigegebene Instanzen zur Verfügung. Embedding- und Reranker-Modelle werden anhand von Modell-ID, Name, Base Model, Tags und Capabilities ausgeschlossen; falls solche Modelle später ergänzt werden, entfernt das Skript dort Tool-, Filter- und Function-Calling-Zuweisungen.

Der API-basierte Import kann direkt über den Generator ausgeführt werden:

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Die Konfigurationsdatei enthält die von der ausführenden Maschine erreichbare OpenWebUI-Adresse und den Admin-API-Key sowie die aus Sicht des OpenWebUI-Backends erreichbare Jupyter-Adresse, den Jupyter-Token, das Artefakt-Volume, die `addons.*`-Pfade, generische `tool_valves`, `function_valves` und zentrale dokumentierte Environment-Namen. Die echte `scripts/openwebui_workspace_config.yaml` ist per `.gitignore` ausgeschlossen; nur die Beispiel-Datei wird versioniert. `import.include_optional_network_tools: true` ist der Standard, damit der API-Importer alle importierbaren Repo-Tools anlegt; für einen strikten Minimalimport kann der Wert lokal auf `false` gesetzt werden.

Der Generator validiert zuerst alle lokalen Artefakte und startet danach `Tools/import_openwebui_workspace.py`. Der Importer importiert beziehungsweise aktualisiert Tools, setzt Tool-Valves, importiert Functions/Filter, setzt Function-/Filter-Valves, importiert Skills und Promptvorlagen und anschließend Modelle. Standardmäßig lädt er pro Modell `mainprompt.md`, `fachwissen.md` und `Golden_Example.<ext>` als echte OpenWebUI-Files hoch, speichert die resultierenden File-IDs in `meta.workbenchFileContext.uploadedFiles` und importiert erst danach das Modellprofil. Die Knowledge Collection wird nur aus `meta.exampleKnowledgeFiles` gebaut, also aus `beispiele/**`, optionalen Legacy-Dateien `beispielergebnis.*` und primären i18n-Profilen. Ein lokaler Payload-Check ohne OpenWebUI-Aufruf ist mit `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.yaml` oder direkt mit `python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.yaml` möglich.

## Wartung

Vor Produktiveinsatz externe Tools und neue eigene Tools erneut prüfen. Änderungen an Tool-Dateien sollten immer mit Importtest, Annotationstest und Secret-Scan validiert werden.

## Offline Capability Map

Für die modellbezogene Zuordnung und Fallback-Abdeckung liegt eine Matrix unter `Tools/openwebui_ext/docs/offline-capability-map.md`. Sie beschreibt, welche Tools und Skills pro Use Case kombiniert werden sollten und welche Drittanbieter-/Same-Origin-/API-Tools nicht als Default aktiviert werden.
