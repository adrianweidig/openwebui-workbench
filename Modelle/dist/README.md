# OpenWebUI Import

## Enthaltene Artefakte

- `openwebui-models-import.json`: alle Modelle als direkt importierbare OpenWebUI-JSON-Datei
- `models_fallback_bundle.json`: Kompatibilitätskopie desselben Modellimports
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfade zum Jupyter-Tool sowie zu den Offline-Visual-, Parallel-, Overlay- und ComfyUI-Prüftools
- `functions_fallback_bundle.json`: Filter-Metadaten für den Kontextkomprimierer
- `openwebui-registration-plan.json`: Reihenfolge für Tool-, Filter-, Skill- und Modellimport sowie Native-Function-Calling-Empfehlung
- `openwebui-model-params-summary.json`: explizite Prüfübersicht für Runtime-Keys, eingebettete Icons und Tool-Zuordnung je Modell
- `artifacts/`: Kopien der Einzelartefakte für manuelle Übernahme
- `artifacts/icons/`: generische schwarz-weiße SVG-/PNG-Profilicons mit weißem Hintergrund
- `artifacts/icons/openwebui-generic-icons.json`: Icon-Katalog mit vorgeschlagener Modellzuordnung
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur
- `artifacts/models/offline-workbench-agent.model.json`: Sammelmodell für ChatGPT-ähnliche Offline-Nutzung mit Jupyter- und Artefakt-Workflow

## Direktimport

`openwebui-models-import.json` und die einzelnen `models/<modell-id>/model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportschema und sind für den GUI-Import gedacht.

Die Chat-Modelle nutzen natives Tool-Calling, eingebettete Modellicons und ein High-Reasoning-Systemprofil. Systemprompt, Mainprompt und Fachwissen sind im jeweiligen `params.system` enthalten. Der Standardworkflow ist offline; öffentliche Netzwerktools werden nicht zugewiesen. Feste Laufzeitparameter wie `max_tokens`, `temperature`, `top_p`, `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden bewusst nicht gesetzt, damit die Zielinstanz ihre eigenen Defaults verwenden kann.

## Manuelle Integration

1. In OpenWebUI entweder `openwebui-models-import.json` oder ein einzelnes `model.json` importieren.
2. Basismodell `coder` prüfen.
3. Optional `systemprompt.md`, `mainprompt.md` und `fachwissen.md` im Repository für Pflege oder lokale Knowledge-Nutzung heranziehen.
4. Web Search deaktiviert lassen, falls die Instanz Default-Werte überschreibt.
5. Vor dem Modellimport nur die Offline-Tools aus `openwebui-registration-plan.json` unter `tools_first` importieren; dazu gehören Subagent-Orchestrierung, Parallelplanung, Jupyter und Artefakttools.
6. Danach `openwebui-models-import.json` importieren. Die Chat-Modelle enthalten bereits Tool-/Filter-Zuordnung, eingebettete Icons, Systemprompt, Mainprompt, Fachwissen, `meta.capabilities.builtin_tools: true` und `params.function_calling: "native"`.
