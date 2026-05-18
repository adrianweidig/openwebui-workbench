# OpenWebUI Import

## Enthaltene Artefakte

- `models_fallback_bundle.json`: alle Modellprofile in einer generischen Bundle-Datei
- `tools_fallback_bundle.json`: Tool-Metadaten und Pfad zum Jupyter-Tool
- `artifacts/`: Kopien der Einzelartefakte fuer manuelle Uebernahme
- `openwebui-offline-artifacts.zip`: ZIP der erzeugten Struktur

## Direktimport

Ein feldgenauer Direktimport kann nicht garantiert werden, weil lokal kein Referenzexport aus der Zielinstanz vorhanden war. Verwende die JSON-Dateien als strukturierte Vorlage oder passe sie an einen realen Export aus `openwebui:latest` an.

## Manuelle Integration

1. Modell in OpenWebUI anlegen.
2. Basismodell `coder` auswaehlen.
3. Systemprompt uebernehmen.
4. `mainprompt.md` und `fachwissen.md` nach lokaler OpenWebUI-Konvention hinterlegen.
5. Parameter und Capabilities aus `model.json` setzen.
6. Web Search deaktiviert lassen.
7. Jupyter-Tool nur bei zugeordneten Modellen aktivieren.
