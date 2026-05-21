# OpenWebUI Import

## Enthaltene Artefakte

- `openwebui-models-import.json`: alle Modelle als direkt importierbare OpenWebUI-JSON-Datei
- `models_fallback_bundle.json`: Kompatibilitätskopie desselben Modellimports
- `Tools/dist/openwebui-tools-offline-import.json`: direkt importierbares GUI-Bundle für alle Offline-Default-Tools
- `Tools/dist/openwebui-tools-import.json`: direkt importierbares GUI-Bundle inklusive optionaler Netzwerk-, Rich-UI- und lokaler Crawl-Tools
- `Tools/dist/openwebui-functions-import.json`: direkt importierbares GUI-Bundle für Functions/Filter
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfad zum Jupyter-Tool
- `functions_fallback_bundle.json`: Filter-Metadaten für den Kontextkomprimierer
- `openwebui-model-params-summary.json`: Prüfübersicht für Modellparameter und Tool-Zuordnung je Modell
- `artifacts/icons/`: generische schwarz-weiße Profilicons für Modellbilder
- `artifacts/`: Kopien der Einzelartefakte für manuelle Übernahme
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur

## Direktimport

`openwebui-models-import.json` und die einzelnen `models/<modell-id>/model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportschema und sind für den GUI-Import gedacht.

## Manuelle Integration

1. `Tools/dist/openwebui-tools-offline-import.json` über `Workspace > Tools > Import` importieren.
2. `Tools/dist/openwebui-functions-import.json` über `Workspace > Functions > Import` importieren.
3. Skills aus `Tools/openwebui_ext/skills/*.md` importieren, falls die OpenWebUI-Instanz Skill-Importe unterstützt.
4. Danach in OpenWebUI entweder `openwebui-models-import.json` oder ein einzelnes `model.json` importieren.
5. Basismodell `coder` prüfen.
6. Optional `systemprompt.md`, `mainprompt.md` und `fachwissen.md` im Repository für Pflege oder lokale Knowledge-Nutzung heranziehen.
7. Web Search deaktiviert lassen, falls die Instanz Default-Werte überschreibt.
8. Icons, Systemprompt, Mainprompt, Fachwissen und Tool-/Filter-Zuordnung sind in den Modellprofilen enthalten.
