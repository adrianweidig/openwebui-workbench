# OpenWebUI Import

## Enthaltene Artefakte

- `openwebui-models-import.json`: alle Modelle als direkt importierbare OpenWebUI-JSON-Datei
- `models_fallback_bundle.json`: Kompatibilitätskopie desselben Modellimports
- `Tools/dist/openwebui-tools-offline-import.json`: direkt importierbares GUI-Bundle für alle Offline-Default-Tools
- `Tools/dist/openwebui-tools-import.json`: direkt importierbares GUI-Bundle inklusive optionaler Netzwerk-, Rich-UI- und lokaler Crawl-Tools
- `Tools/dist/openwebui-functions-import.json`: direkt importierbares GUI-Bundle für Functions/Filter
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfade zum Jupyter-Tool sowie zu den Offline-Visual-, Parallel-, Overlay- und ComfyUI-Prüftools
- `functions_fallback_bundle.json`: Filter-Metadaten für den Kontextkomprimierer
- `openwebui-registration-plan.json`: Reihenfolge für Tool-, Public-Access-, Tool-Valve-, Filter-, Global-Function-, Function-Valve-, Skill-, Knowledge- und Modellimport sowie Native-Function-Calling-Empfehlung
- `openwebui-model-params-summary.json`: explizite Prüfübersicht für `temperature`, `top_p`, Runtime-Keys, Tool-Pflichtprofil, eingebettete Icons und Tool-Zuordnung je Modell
- `artifacts/`: Kopien der Einzelartefakte für manuelle Übernahme
- `artifacts/icons/`: generische schwarz-weiße SVG-/PNG-Profilicons mit weißem Hintergrund
- `artifacts/icons/openwebui-generic-icons.json`: Icon-Katalog mit vorgeschlagener Modellzuordnung
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur
- `artifacts/models/offline-workbench-agent.model.json`: Sammelmodell für ChatGPT-ähnliche Offline-Nutzung mit Jupyter- und Artefakt-Workflow
- `artifacts/models/allgemein.model.json`: allgemeines Fallbackmodell für freie oder gemischte Nutzerprobleme mit allen Offline-Tools und Standardfiltern
- `artifacts/models/promptforge.model.json`: Prompt-Optimierungsmodell mit kuratiertem Prompting-Best-Practice-Fachwissen
- `artifacts/models/n8n-workflow-architect.model.json`: Custom-GPT-nahe n8n-Workflow-Erstellung und -Prüfung
- `artifacts/models/openwebui-model-builder.model.json`: Custom-GPT-nahe Erstellung vollständiger OpenWebUI-Modellpakete
- `artifacts/models/mistral-vision-workbench.model.json`: Vision- und UI-QA-Modell für Screenshots, Folien, Scans, Diagramme und visuelle Artefakte
- `artifacts/models/präsentationserstellung.model.json`: Custom-GPT-nahe Browser-Keynote-Erstellung als `präsentation.html`
- `artifacts/examples/`: pro Modell nutzbare Beispielvorlagen und Rich-Artefakte, darunter `präsentationserstellung/praesentation-premium-demo.html`

## Direktimport

`openwebui-models-import.json` und die einzelnen `models/<modell-id>/model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportschema und sind für den GUI-Import gedacht. Für den vollständigen Import inklusive Tools, Functions/Filter, Skills, Tool-Valves, Function-/Filter-Valves, modellbezogener Knowledge-Bases, Public-Access für Tools/Skills/Knowledge/Modelle und globaler Functions/Filter ist der API-Import über `scripts/configure_openwebui_tool_models.py --import-openwebui --config scripts/openwebui_workspace_config.yaml` vorgesehen. Die zentrale YAML enthält OpenWebUI-Adresse, Admin-Token, Jupyter, Backend-Pfade, Addon-Pfade, `tool_valves` und `function_valves`.

Die Chat-Modelle nutzen natives Tool-Calling, OpenWebUI-Standardfunktionen und Builtins, Vision-Fähigkeit, use-case-spezifische `temperature`-/`top_p`-Werte, eingebettete Modellicons, profilbezogene Skills über `meta.skillIds` und einen kurzen Bootstrap-Systemprompt mit Tool-/Skill-Inventur. Der Systemprompt enthält bewusst keine langen Fachregeln mehr; er verpflichtet das Modell stattdessen, `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und Dateien aus `beispiele/` vor der Antwort als Knowledge zu laden, zu analysieren und aktiv anzuwenden. Der API-Importer lädt diese Dateien je Modell als OpenWebUI-Knowledge hoch und verknüpft sie in `meta.knowledge`; die passenden Skills werden vorher importiert und anschließend am Modell verankert. Parallelisierung, Subagenten und Vision-gestützte UI-/Artefaktprüfung sind bei komplexen mehrteiligen Aufgaben weiterhin der Standardweg. Der Stack `F:\offline-ai-stack\openwebui-offline-addons` ist als lokale Laufzeit für Caches, Tiktoken, NLTK, Playwright/Chromium und zusätzliche Python-Pakete vorgesehen. Der Standardworkflow ist offline; öffentliche Netzwerktools werden nicht zugewiesen. `max_tokens` wird bewusst nicht gesetzt, damit die Zielinstanz ihre eigenen Kontext- und Antwortlimits verwenden kann. Nicht passende Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden ebenfalls nicht gesetzt.

## Manuelle Integration

1. In OpenWebUI `Tools/dist/openwebui-tools-offline-import.json` über `Workspace > Tools > Import` importieren.
2. `Tools/dist/openwebui-functions-import.json` über `Workspace > Functions > Import` importieren.
3. Skills aus `Tools/openwebui_ext/skills/*.md` importieren, bevor Modellprofile geladen werden.
4. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und passende Dateien aus `beispiele/` je Modell als Knowledge bereitstellen, falls nicht der API-Importer genutzt wird.
5. In OpenWebUI entweder `openwebui-models-import.json` oder ein einzelnes `model.json` importieren.
6. Basismodell `coder` prüfen.
7. Optional `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und `beispiele/` im Repository für Pflege oder lokale Knowledge-Nutzung heranziehen.
8. Web Search deaktiviert lassen, falls die Instanz Default-Werte überschreibt.
9. Die Chat-Modelle enthalten bereits Tool-/Filter-Zuordnung, Skill-Zuordnung über `meta.skillIds`, eingebettete Icons, kurzen Bootstrap-Systemprompt, `meta.capabilities.builtin_tools: true`, Builtin-/Addon-Nutzungshinweise und `params.function_calling: "native"`; Mainprompt, Fachwissen und Beispielwissen werden als Knowledge verknüpft.
