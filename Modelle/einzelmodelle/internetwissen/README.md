# Internetwissen

Offline nutzbares OpenWebUI-Modell für allgemeines Wissen, Anleitungen, Recherchemethodik, Quellenkritik und Wissensstrukturierung.

## Zweck

`internetwissen` ist ein initiales, leichtgewichtiges Wissensmodell. Es bringt eine kompakte, selbst geschriebene KnowledgeBase direkt im Repository mit und benötigt keine externen GB-/TB-Daten.

## Geeignete Aufgaben

- allgemeine Erklärungen
- Schritt-für-Schritt-Anleitungen
- Recherchepläne
- Quellenkritik
- Vergleichstabellen
- FAQ, Glossare und Lernnotizen
- Einordnung von Aktualitätsgrenzen

## Nicht im Initialumfang

- keine Live-Websuche
- keine FineWeb- oder Common-Crawl-Daten
- keine Wikipedia-/Kiwix-Dumps
- kein externer Vektorindex
- keine automatische Webarchiv-Pipeline
- keine großen Datenartefakte im Git-Repository

## Vorgesehene Tools

Das Modell nutzt nur vorhandene Offline-Default-Bausteine und keine neuen Tools. Im Modellprofil sind kleine Hilfstools für Validierung, Repository-Kontext und Aufgabenplanung vorgesehen:

- `json_csv_text_validator`
- `repo_tree_analyzer`
- `parallel_task_planner`

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, Dateien unter `beispiele/` und Produktprofile unter `i18n/` werden beim API-Import als Knowledge für dieses Modell hinterlegt.

## Ausbau

Große Offline-Webkorpora wie FineWeb, FineWeb-Edu, Common Crawl, Wikipedia-/Kiwix-Dumps und externe lokale Retrieval-Indizes sind Roadmap-Themen. Sie werden nicht als Initialdaten in dieses Modellpaket aufgenommen.
