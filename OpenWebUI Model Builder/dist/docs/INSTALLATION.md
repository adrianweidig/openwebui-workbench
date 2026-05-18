# Installation

## Voraussetzungen

- Lokale oder interne `openwebui:latest`-Instanz
- Basismodell-ID in OpenWebUI: `coder`
- Kein Internetzugriff erforderlich
- Optional: lokal oder intern erreichbarer Jupyter Server fuer `air_gapped_jupyter_python`

## Modelle einrichten

1. In OpenWebUI ein neues Workspace-/Aufgabenmodell anlegen.
2. Als Basismodell `coder` auswaehlen.
3. Inhalt aus `models/<modell-id>/systemprompt.md` als Systemprompt eintragen.
4. `mainprompt.md` und `fachwissen.md` als lokale Modell-/Knowledge-Dateien oder zusammen mit dem Systemprompt nach lokaler OpenWebUI-Konvention hinterlegen.
5. Parameter aus `models/<modell-id>/model.json` uebernehmen.
6. Web Search deaktiviert lassen.
7. Jupyter-Tool nur den Modellen zuordnen, deren `model.json` das Tool listet.

## Tool einrichten

1. `tools/jupyter/jupyter_tool.py` in OpenWebUI als Tool importieren oder nach lokaler Tool-Konvention eintragen.
2. Konfigurationswerte als Umgebungsvariablen oder Tool-Valves setzen.
3. Keine echten Tokens in Modellprofile, Prompts oder Dokumentation schreiben.
4. Statische Validierung ausfuehren.

## Import-Bundle

`openwebui-import/openwebui-offline-artifacts.zip` enthaelt die erzeugten Artefakte. Da kein lokaler OpenWebUI-Referenzexport vorhanden war, ist das Bundle nicht als garantiert feldgenauer Direktimport zu verstehen.
