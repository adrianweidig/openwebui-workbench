# OpenWebUI Import

## Enthaltene Artefakte

- `openwebui-models-import.json`: alle Modelle als direkt importierbare OpenWebUI-JSON-Datei
- `models_fallback_bundle.json`: Kompatibilitätskopie desselben Modellimports
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfade zum Jupyter-Tool sowie zu den Offline-Visual-, Parallel-, Overlay- und ComfyUI-Prüftools
- `functions_fallback_bundle.json`: Filter-Metadaten für den Kontextkomprimierer
- `openwebui-registration-plan.json`: Reihenfolge für Tool-, Filter-, Skill- und Modellimport sowie Native-Function-Calling-Empfehlung
- `artifacts/`: Kopien der Einzelartefakte für manuelle Übernahme
- `artifacts/icons/`: generische schwarz-weiße SVG-/PNG-Profilicons mit weißem Hintergrund
- `artifacts/icons/openwebui-generic-icons.json`: Icon-Katalog mit vorgeschlagener Modellzuordnung
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur
- `artifacts/models/offline-workbench-agent.model.json`: Sammelmodell für ChatGPT-ähnliche Offline-Nutzung mit Jupyter- und Artefakt-Workflow

## Direktimport

`openwebui-models-import.json` und die einzelnen `models/<modell-id>/model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportschema und sind für den GUI-Import gedacht.

Die Chat-Modelle nutzen 256k `max_tokens`, use-case-abhängige `temperature`, natives Tool-Calling, eingebettete Modellicons und ein High-Reasoning-Systemprofil. Systemprompt, Mainprompt und Fachwissen sind im jeweiligen `params.system` enthalten. Nicht passende Runtime-Parameter wie `reasoning_effort`, `num_ctx`, `top_k` und `seed` werden bewusst nicht gesetzt, damit die Profile mit Mistral Medium 3.5 128B kompatibel bleiben.

## Manuelle Integration

1. In OpenWebUI entweder `openwebui-models-import.json` oder ein einzelnes `model.json` importieren.
2. Basismodell `coder` prüfen.
3. Optional `systemprompt.md`, `mainprompt.md` und `fachwissen.md` im Repository für Pflege oder lokale Knowledge-Nutzung heranziehen.
4. Web Search deaktiviert lassen, falls die Instanz Default-Werte überschreibt.
5. Vor dem Modellimport Tools, Filter und Skills gemäß `openwebui-registration-plan.json` importieren; dazu gehören Internet-Recherche, Subagent-Orchestrierung, Parallelplanung, Jupyter und Artefakttools.
6. Danach `openwebui-models-import.json` importieren. Die Chat-Modelle enthalten bereits Tool-/Filter-Zuordnung, eingebettete Icons, Systemprompt, Mainprompt, Fachwissen, `meta.capabilities.builtin_tools: true` und `params.function_calling: "native"`.
