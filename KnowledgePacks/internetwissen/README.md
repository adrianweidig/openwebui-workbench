# Internetwissen KnowledgePacks

Dieser Bereich ist für optionale Offline-Wissenspakete des Modells `internetwissen` vorbereitet. Das initiale Modell funktioniert ohne diese Pakete.

## Initialer Stand

- Keine großen Datenbestände sind enthalten.
- `packs/` bleibt leer, bis lizenzklare Quellen, Snapshot-Prozess und Prüfsummen vorliegen.
- Das Beispielmanifest zeigt nur die Struktur und wird nicht als echtes Datenpaket importiert.

## Anforderungen an echte Packs

Ein echtes KnowledgePack muss:

- im 10-GiB-Gesamtbudget bleiben,
- ein Manifest nach `schema/knowledgepack.schema.json` besitzen,
- jede Datei mit Größe und SHA256-Prüfsumme aufführen,
- Lizenz und Provenienz dokumentieren,
- das Snapshot-Datum nennen,
- klar zwischen initialem Bestandteil und optionaler Erweiterung unterscheiden,
- ohne Runtime-Download nutzbar sein.

## Nicht enthalten

- FineWeb- oder Common-Crawl-Daten,
- Wikipedia-, Wikimedia- oder Kiwix-Dumps,
- externe Vektorindizes,
- automatische Webarchiv-Pipelines,
- Daten mit ungeklärter Lizenz.
