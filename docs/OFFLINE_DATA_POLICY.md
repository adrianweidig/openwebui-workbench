# Offline-Datenpolicy

Diese Policy regelt, wie die Workbench mit lokalen Wissensdaten, KnowledgePacks und optionalen Offline-Image-Artefakten umgeht. Der Offline-Default benötigt keine Live-Websuche und lädt zur Laufzeit keine Daten aus dem Internet nach.

## Grundsätze

- Kleine KnowledgeBase-Dateien bleiben direkt im jeweiligen Modellpaket, zum Beispiel `mainprompt.md`, `fachwissen.md`, `beispielergebnis.*` und Dateien unter `beispiele/`.
- Größere Datenbestände werden als KnowledgePacks geführt.
- KnowledgePacks und optional versionierte Offline-Image-Artefakte dürfen zusammen maximal 10 GiB belegen.
- Externe URLs in Manifesten sind Provenienz-Metadaten. Sie sind keine Runtime-Abhängigkeit.
- Produktive Tokens, private URLs, personenbezogene Daten und ungeklärte Fremdinhalte dürfen nicht in KnowledgePacks landen.
- Downloads oder Updates dürfen nur über explizit dafür gestartete Wartungsschritte erfolgen, nicht während Modellantworten, Imports oder normalem Workbench-Betrieb.

## KnowledgePack-Anforderungen

Jedes KnowledgePack braucht ein Manifest mit:

- eindeutiger ID,
- Titel und Version,
- Zielmodellen,
- Lizenzangaben,
- Snapshot-Datum,
- Offline-Runtime-Aussage,
- Artefaktliste mit Pfad, Medientyp, Sprache, Größe und SHA256-Prüfsumme,
- Quelle oder Quellenart,
- Update-Anleitung oder Update-Methode.

Das Manifestformat liegt unter [`KnowledgePacks/internetwissen/schema/knowledgepack.schema.json`](../KnowledgePacks/internetwissen/schema/knowledgepack.schema.json). Ein Beispiel liegt unter [`KnowledgePacks/internetwissen/manifest.example.json`](../KnowledgePacks/internetwissen/manifest.example.json).

## Größenbudget

Das Standardbudget beträgt:

```text
10 GiB = 10.737.418.240 Bytes
```

Der Check [`scripts/check_offline_data_budget.py`](../scripts/check_offline_data_budget.py) zählt Dateien unter:

- `KnowledgePacks/`
- `Deployment/images/`

Wenn das Budget überschritten wird, schlägt der Verify-Runner fehl und nennt die größten Dateien.

## Validierung

Der Check [`scripts/validate_knowledgepacks.py`](../scripts/validate_knowledgepacks.py) prüft:

- Manifest-Pflichtfelder,
- Schema-Kennung,
- Zielmodell-Liste,
- Offline-Runtime-Flag,
- Artefaktfelder,
- Pfade innerhalb des KnowledgePack-Verzeichnisses,
- Größe und SHA256-Prüfsumme für echte Manifeste.

`manifest.example.json` darf ohne echte Datenartefakte im Repository liegen. Echte Manifestdateien müssen dagegen auf vorhandene Dateien mit korrekter Größe und Prüfsumme zeigen.

## Git und Release-Artefakte

Kleine Markdown- und JSON-Dateien bleiben direkt versionierbar. Große Wissensdateien, Dumps, Archive oder Datenbanken gehören nur nach Maintainer-Entscheidung in Git LFS oder in Release-Artefakte.

Vorbereitete LFS-Muster stehen in `.gitattributes`. Eine LFS-Migration wird nicht automatisch erzwungen.

## Initialer Umfang von `internetwissen`

Das Modell `internetwissen` bleibt im Initialumfang kompakt:

- keine FineWeb- oder Common-Crawl-Daten,
- keine Wikipedia-, Wikimedia- oder Kiwix-Dumps,
- kein externer Vektorindex,
- keine automatische Webarchiv-Pipeline,
- keine Runtime-Websuche.

Optionale KnowledgePacks können später ergänzt werden, wenn Lizenz, Snapshot, Hashes, Größenbudget und Update-Prozess geklärt sind.
