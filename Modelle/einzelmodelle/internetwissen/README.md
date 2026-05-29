# Internetwissen

Offline nutzbares OpenWebUI-Modell für allgemeines Wissen, Anleitungen, Recherchemethodik, Quellenkritik, Aktualitätsgrenzen und Wissensstrukturierung.

## Zweck

`internetwissen` ist integriert und bewusst leichtgewichtig. Es bringt eine kompakte, selbst geschriebene KnowledgeBase direkt im Repository mit und benötigt keine externen GB-/TB-Daten.

## Geeignete Aufgaben

- allgemeine Erklärungen
- Schritt-für-Schritt-Anleitungen
- Recherchepläne
- Quellenkritik
- Vergleichstabellen
- FAQ, Glossare und Lernnotizen
- Einordnung von Aktualitätsgrenzen
- lokale Auswertung bereitgestellter Quellen

## Offline-Grenzen

- keine Live-Websuche
- keine FineWeb- oder Common-Crawl-Daten
- keine Wikipedia-/Kiwix-Dumps
- kein externer Vektorindex
- keine automatische Webarchiv-Pipeline
- keine großen Datenartefakte im Initialpaket
- keine aktuellen Fakten ohne bereitgestellte Quelle, lokale Datei oder validiertes KnowledgePack

## Vorgesehene Tools

Das Modell nutzt nur vorhandene Offline-Default-Bausteine und keine öffentlichen Netzwerktools. Im Modellprofil sind Hilfstools für Rückfragen, Validierung, Repository-Kontext, Aufgabenplanung und Offline-Artefakte vorgesehen:

- `ask_user`
- `json_csv_text_validator`
- `repo_tree_analyzer`
- `parallel_task_planner`
- `offline_artifact_workbench`
- `inline_visuals_toolkit_v3`

Nicht im Offline-Profil: `safe_http_fetcher`, `github_repo_inspector`, `web_search_and_crawl`, `openui_generative_ui`, `mediawiki_legacy_crawler`.

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, Dateien unter `beispiele/` und Produktprofile unter `i18n/` werden beim API-Import als Knowledge für dieses Modell hinterlegt.

## KnowledgePacks

Optionale größere Wissensdaten laufen über `KnowledgePacks/` und die zentrale Offline-Datenpolicy. Sie brauchen Manifest, Lizenz, Snapshot-Datum, Größenangaben, SHA256-Prüfsummen und bleiben zusammen mit optionalen Offline-Image-Artefakten auf maximal 10 GiB begrenzt.

## Ausbau

Große Offline-Webkorpora wie FineWeb, FineWeb-Edu, Common Crawl, Wikipedia-/Kiwix-Dumps und externe lokale Retrieval-Indizes sind spätere, optionale Roadmap-Themen. Sie werden nicht als Initialdaten in dieses Modellpaket aufgenommen und dürfen keine Runtime-Websuche einführen.
