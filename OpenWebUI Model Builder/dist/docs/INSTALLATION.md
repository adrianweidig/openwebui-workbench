# Installation

## Voraussetzungen

- Lokale oder interne `openwebui:latest`-Instanz
- Basismodell-ID in OpenWebUI: `coder`
- Kein Internetzugriff erforderlich
- Optional: lokal oder intern erreichbarer Jupyter Server für `air_gapped_jupyter_python`

## Modelle einrichten

1. Einzelimport: `models/<modell-id>/model.json` in OpenWebUI importieren. Jede Datei ist ein JSON-Array mit genau einem Modellobjekt im OpenWebUI-Exportschema.
2. Sammelimport: alternativ `openwebui-import/openwebui-models-import.json` importieren.
3. Nach dem Import prüfen, dass als Basismodell `coder` gesetzt ist.
4. Optional die Paketdateien `systemprompt.md`, `mainprompt.md` und `fachwissen.md` zur menschlichen Wartung oder als zusätzliche lokale Referenz hinterlegen.
5. Web Search deaktiviert lassen, falls die Zielinstanz nach dem Import abweichende Defaults setzt.
6. Das Jupyter-Tool nur den Modellen zuordnen, die es fachlich benötigen.

## Tool einrichten

1. `tools/jupyter/jupyter_tool.py` in OpenWebUI als Tool importieren oder nach lokaler Tool-Konvention eintragen.
2. Konfigurationswerte als Umgebungsvariablen oder Tool-Valves setzen.
3. Keine echten Tokens in Modellprofile, Prompts oder Dokumentation schreiben.
4. Statische Validierung ausführen.

## Import-Bundle

`openwebui-import/openwebui-models-import.json` ist die primäre Modell-Importdatei. `openwebui-import/openwebui-offline-artifacts.zip` enthält dieselben Artefakte zusätzlich als Transportpaket für Air-Gap-Umgebungen.
