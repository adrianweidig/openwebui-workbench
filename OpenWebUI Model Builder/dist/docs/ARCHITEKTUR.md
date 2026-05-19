# Architektur

## Zielbild

Die erzeugte Struktur stellt offline nutzbare OpenWebUI-Aufgabenmodelle bereit. Jedes Modell ist ein Preset über dem Basismodell `coder` und enthält eigene Promptdateien, Fachwissen, ein direkt importierbares OpenWebUI-`model.json` und Sicherheitsregeln.

## Quellen

- Primäre lokale Quelle: `OpenWebUI Model Builder`
- Konkrete Problemfallquelle: `Problemfälle`
- Kein Internet, keine externen APIs, keine externen Knowledge Bases

## Bestandteile

- `models/`: je Problemfall ein Modellpaket mit importierbarem `model.json`, `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, `README.md`
- `tools/jupyter/`: OpenWebUI-kompatibles Python-Tool für lokalen oder internen Jupyter Server
- `openwebui-import/`: OpenWebUI-Importdateien und manuelle Importhinweise
- `docs/`: Betriebs-, Installations- und Validierungsdokumentation
- `tests/`: lokale Prüfroutinen ohne Internet
- `reports/`: Inventar, Matrix, Validierungsbericht und offene Punkte

## Modellanzahl

Erzeugt wurden 25 Modelle aus vorhandenen detaillierten Problemfall-Briefings.

## Importschema

Die `model.json`-Dateien und `openwebui-models-import.json` folgen dem lokal geprüften OpenWebUI-Export-/Importschema. Grundlage sind importierbare Referenzdateien aus der lokalen Umgebung. Unsicher bleibt nur, welche Containerpfade und optionalen Tool-Verknüpfungen eine konkrete `openwebui:latest`-Instanz zusätzlich erwartet.
