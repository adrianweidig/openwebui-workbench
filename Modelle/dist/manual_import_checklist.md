# OpenWebUI Import

## Enthaltene Artefakte

- `openwebui-models-import.json`: alle Modelle als direkt importierbare OpenWebUI-JSON-Datei
- `models_fallback_bundle.json`: Kompatibilitätskopie desselben Modellimports
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfad zum Jupyter-Tool
- `functions_fallback_bundle.json`: Filter-Metadaten für den Kontextkomprimierer
- `artifacts/icons/`: generische schwarz-weiße Profilicons für Modellbilder
- `artifacts/`: Kopien der Einzelartefakte für manuelle Übernahme
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur

## Direktimport

`openwebui-models-import.json` und die einzelnen `models/<modell-id>/model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportschema und sind für den GUI-Import gedacht.

## Manuelle Integration

1. In OpenWebUI entweder `openwebui-models-import.json` oder ein einzelnes `model.json` importieren.
2. Basismodell `coder` prüfen.
3. Optional `systemprompt.md`, `mainprompt.md` und `fachwissen.md` im Repository für Pflege oder lokale Knowledge-Nutzung heranziehen.
4. Web Search deaktiviert lassen, falls die Instanz Default-Werte überschreibt.
5. Vor dem Modellimport alle Tools aus `Tools/openwebui_ext/tools/*.py` und `Tools/jupyter/jupyter_tool.py` importieren, insbesondere Internet-Recherche, Subagent-Orchestrierung, Parallelplanung, Jupyter und Artefakttools.
6. `context_compressor_filter.py` vor dem Modellimport als OpenWebUI-Function/Filter importieren und bei allen Chat-Modellen aktiv lassen.
7. Skills aus `Tools/openwebui_ext/skills/*.md` importieren, falls die OpenWebUI-Instanz Skill-Importe unterstützt.
8. Danach `openwebui-models-import.json` importieren; Icons, Systemprompt, Mainprompt, Fachwissen und Tool-/Filter-Zuordnung sind in den Modellprofilen enthalten.
