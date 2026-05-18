# Architektur

## Zielbild

Die erzeugte Struktur stellt offline nutzbare OpenWebUI-Aufgabenmodelle bereit. Jedes Modell ist ein Preset ueber dem Basismodell `coder` und enthaelt eigene Promptdateien, Fachwissen, Modellprofil und Sicherheitsregeln.

## Quellen

- Primaere lokale Quelle: `OpenWebUI Model Builder`
- Konkrete Problemfallquelle: `Problemfälle`
- Kein Internet, keine externen APIs, keine externen Knowledge Bases

## Bestandteile

- `models/`: je Problemfall ein Modellpaket mit `model.json`, `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, `README.md`
- `tools/jupyter/`: OpenWebUI-kompatibles Python-Tool fuer lokalen oder internen Jupyter Server
- `openwebui-import/`: generische Fallback-Bundles und manuelle Importhinweise
- `docs/`: Betriebs-, Installations- und Validierungsdokumentation
- `tests/`: lokale Pruefroutinen ohne Internet
- `reports/`: Inventar, Matrix, Validierungsbericht und offene Punkte

## Modellanzahl

Erzeugt wurden 25 Modelle aus vorhandenen detaillierten Problemfall-Briefings.

## Importunsicherheit

Lokal liegt kein OpenWebUI-Referenzexport der Zielinstanz vor. Deshalb sind `model.json` und Import-Bundles als robuste Fallback-Struktur dokumentiert und muessen gegen einen Export der konkreten `openwebui:latest`-Instanz abgeglichen werden.
