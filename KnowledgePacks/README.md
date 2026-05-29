# KnowledgePacks

KnowledgePacks sind optionale, versionierte Offline-Wissenspakete für Modelle der Workbench. Sie ergänzen kleine repo-interne Knowledge-Dateien, ersetzen aber keine Live-Websuche.

## Regeln

- Gesamtbudget für `KnowledgePacks/` und optional versionierte `Deployment/images/`: maximal 10 GiB.
- Keine ungeprüften Dumps, keine ungeklärten Copyright-Inhalte, keine personenbezogenen Daten.
- Jedes echte Pack braucht ein Manifest mit Lizenz, Snapshot-Datum, Größenangaben, SHA256-Prüfsummen und Update-Methode.
- Externe URLs sind nur Provenienz-Metadaten, keine Runtime-Abhängigkeiten.
- Downloads oder Updates erfolgen nur durch explizite Maintainer-Schritte, nie während Modellantworten.
- Kleine Markdown-/JSON-Dateien können normal in Git liegen; große Dateien gehören in Git LFS oder Release-Artefakte.

## Struktur

| Pfad | Zweck |
|---|---|
| `index.json` | Übersicht über bekannte KnowledgePack-Familien |
| `internetwissen/` | optionale Offline-Wissenspakete für das Modell `internetwissen` |
| `internetwissen/schema/knowledgepack.schema.json` | Manifest-Schema |
| `internetwissen/manifest.example.json` | Beispielmanifest ohne echte Datenartefakte |
| `internetwissen/packs/` | Ablage für lokale Pack-Dateien, zunächst leer |

## Prüfung

```powershell
python scripts/check_offline_data_budget.py
python scripts/validate_knowledgepacks.py
python scripts/verify_openwebui_workspace.py
```
