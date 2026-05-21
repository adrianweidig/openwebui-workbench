# OpenWebUI Import

## Enthaltene Artefakte

- `openwebui-models-import.json`: alle Modelle als direkt importierbare OpenWebUI-JSON-Datei
- `models_fallback_bundle.json`: Kompatibilitätskopie desselben Modellimports
- `Tools/dist/openwebui-tools-offline-import.json`: direkt importierbares GUI-Bundle für alle Offline-Default-Tools
- `Tools/dist/openwebui-tools-import.json`: direkt importierbares GUI-Bundle inklusive optionaler Netzwerk-, Rich-UI- und lokaler Crawl-Tools
- `Tools/dist/openwebui-functions-import.json`: direkt importierbares GUI-Bundle für Functions/Filter
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfade zum Jupyter-Tool sowie zu den Offline-Visual-, Parallel-, Overlay- und ComfyUI-Prüftools
- `functions_fallback_bundle.json`: Filter-Metadaten für den Kontextkomprimierer
- `openwebui-registration-plan.json`: Reihenfolge für Tool-, Filter-, Skill- und Modellimport sowie Native-Function-Calling-Empfehlung
- `openwebui-model-params-summary.json`: explizite Prüfübersicht für `max_tokens`, Temperature, Runtime-Keys, eingebettete Icons und Tool-Zuordnung je Modell
- `artifacts/`: Kopien der Einzelartefakte für manuelle Übernahme
- `artifacts/icons/`: generische schwarz-weiße SVG-/PNG-Profilicons mit weißem Hintergrund
- `artifacts/icons/openwebui-generic-icons.json`: Icon-Katalog mit vorgeschlagener Modellzuordnung
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur
- `artifacts/models/offline-workbench-agent.model.json`: Sammelmodell für ChatGPT-ähnliche Offline-Nutzung mit Jupyter- und Artefakt-Workflow

## Direktimport

`openwebui-models-import.json` und die einzelnen `models/<modell-id>/model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportschema und sind für den GUI-Import gedacht.

Die Chat-Modelle nutzen 256k `max_tokens`, use-case-abhängige `temperature`, natives Tool-Calling, eingebettete Modellicons und ein High-Reasoning-Systemprofil. Systemprompt, Mainprompt und Fachwissen sind im jeweiligen `params.system` enthalten. Der Standardworkflow ist offline; öffentliche Netzwerktools werden nicht zugewiesen. Nicht passende Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden bewusst nicht gesetzt, damit die Profile mit Mistral Medium 3.5 128B kompatibel bleiben.

## Manuelle Integration

1. In OpenWebUI `Tools/dist/openwebui-tools-offline-import.json` über `Workspace > Tools > Import` importieren.
2. `Tools/dist/openwebui-functions-import.json` über `Workspace > Functions > Import` importieren.
3. Optional Skills aus `Tools/openwebui_ext/skills/*.md` importieren.
4. In OpenWebUI entweder `openwebui-models-import.json` oder ein einzelnes `model.json` importieren.
5. Basismodell `coder` prüfen.
6. Optional `systemprompt.md`, `mainprompt.md` und `fachwissen.md` im Repository für Pflege oder lokale Knowledge-Nutzung heranziehen.
7. Web Search deaktiviert lassen, falls die Instanz Default-Werte überschreibt.
8. Die Chat-Modelle enthalten bereits Tool-/Filter-Zuordnung, eingebettete Icons, Systemprompt, Mainprompt, Fachwissen, `meta.capabilities.builtin_tools: true` und `params.function_calling: "native"`.
