# Architektur

🌐 Sprachen: [Deutsch](ARCHITECTURE.md) | [English](en/ARCHITECTURE.md)

Dieses Repository ist ein portabler OpenWebUI-Workbench-Arbeitsbereich. Es enthält keine laufende Anwendung, sondern kuratierte Quellen, Generatorlogik, importierbare Artefakte und lokale Validierung.

## Komponenten

```mermaid
flowchart LR
  Briefings["Problemfälle<br/>fachliche Briefings"] --> Builder["OpenWebUI Model Builder<br/>Regeln und Generatorlogik"]
  Builder --> Models["Modelle/einzelmodelle<br/>menschenlesbare Modellpakete"]
  Models --> Dist["Modelle/dist<br/>Importe, ZIPs, Handover"]
  Tools["Tools/openwebui_ext<br/>Tools, Filter, Skills, Prompts"] --> ToolDist["Tools/dist<br/>OpenWebUI-Bundles"]
  Jupyter["Tools/jupyter<br/>Jupyter-Tool"] --> ToolDist
  ToolDist --> Importer["Tools/import_openwebui_workspace.py<br/>API-Import"]
  Dist --> Importer
  Config["scripts/openwebui_workspace_config.yaml<br/>lokale, ignorierte Zielkonfiguration"] --> Importer
  Importer --> OpenWebUI["OpenWebUI-Zielinstanz"]
  Artifacts["Artefakte/output<br/>lokale Laufzeitausgaben"] <--> OpenWebUI
```

## Hauptbereiche

| Bereich | Aufgabe |
|---|---|
| `Problemfälle/` | Fachliche Ausgangspunkte für Modellpakete |
| `OpenWebUI Model Builder/` | Builder-Regeln und Generator-Arbeitsbereich |
| `Modelle/einzelmodelle/` | Primäre, menschenlesbare Modellablage |
| `Modelle/dist/` | Kanonische Übergabe- und Importartefakte |
| `Tools/jupyter/` | Kontrollierte Python-Ausführung über Jupyter |
| `Tools/openwebui_ext/` | OpenWebUI-Tools, Filter, Skills, Promptvorlagen, Doku und Tests |
| `Tools/dist/` | Importierbare Tool-, Skill-, Prompt- und Function-Bundles |
| `scripts/` | Generator-, Validierungs- und Beispielkonfigurationsskripte |
| `Deployment/` | Offline-Compose- und Volume-Vorlagen |
| `Artefakte/` | Lokale Laufzeit- und Übergabedateien, normalerweise nicht versioniert |

## Generierungs- und Importfluss

1. Fachliche Anforderungen werden in `Problemfälle/` beschrieben.
2. Modellpakete werden in `Modelle/einzelmodelle/` gepflegt.
3. Tools, Filter, Skills und Promptvorlagen werden unter `Tools/openwebui_ext/` gepflegt.
4. `scripts/configure_openwebui_tool_models.py` prüft und normalisiert Tool-, Filter-, Prompt- und Modellzuordnungen.
5. Der Generator schreibt Registries, Importdateien, Zusammenfassungen und ZIPs in `Modelle/dist/` und `Tools/dist/`.
6. `Tools/import_openwebui_workspace.py` kann diese Artefakte mit einer lokalen YAML-Konfiguration in eine OpenWebUI-Zielinstanz importieren.

## Wartungsgrenzen großer Dateien

Einige Dateien bleiben groß, weil OpenWebUI importierbare Einzeldateien oder kompakte Handover-Artefakte erwartet. Neue Logik soll trotzdem an klaren Grenzen landen:

| Datei | Rolle | Änderungsregel |
|---|---|---|
| `scripts/configure_openwebui_tool_models.py` | Orchestriert Tool-, Filter-, Modell- und Dist-Generierung | Neue wiederverwendbare Prüf- oder Manifestlogik in kleine Hilfsmodule unter `scripts/` auslagern |
| `scripts/dist_zip_manifest.py` | Vergleicht erwartete Dist-ZIP-Quellen mit ZIP-Inhalten | ZIP-/Drift-Prüfung hier halten, nicht im Generator duplizieren |
| `Tools/openwebui_ext/tools/sub_agent.py` | Importierbares OpenWebUI-Tool mit direkter Runtime-Anbindung | Öffentliche Tool-Klasse stabil halten; nur interne, risikoarme Helfer extrahieren |
| `Tools/openwebui_ext/tools/web_search_and_crawl.py` | Optionales Netzwerkprofil für Suche und Crawling | Netzwerkgrenzen und optionale Abhängigkeiten lokal halten; kein Air-Gap-Default |

Bei Refactors zählt die Importoberfläche stärker als Dateigröße: `Tools`-/`Filter`-Klassen, Modell-JSON-Formate, Registry-Schemas und Dist-Dateinamen dürfen nicht nebenbei brechen.

## Validierung

Der zentrale Verify-Runner ist `scripts/verify_openwebui_workspace.py`. Er führt aus:

- Python-Syntax-Compile für `scripts` und `Tools`
- Dokumentations-Sprachpaar- und Security-Hygiene-Checks
- strukturelle Validierung von OpenWebUI-Tools, Filtern, Skills und Promptvorlagen
- Generator-Check ohne Schreiboperation
- API-Import-Dry-Run mit Beispielkonfiguration
- Unit-Tests unter `Tools.openwebui_ext.tests`
- JSON-Validierung aller JSON-Dateien im Repository

## Sicherheitsgrenzen

- Echte OpenWebUI-Admin-Tokens, Jupyter-Tokens und lokale Zielkonfigurationen werden nicht versioniert.
- Netzwerkfähige Tools sind nicht Teil des Offline-Standardimports.
- Tools laufen in OpenWebUI serverseitig; Zielinstanzen müssen Valves, Dateisystem-Mounts und Admin-Rechte selbst absichern.
- `Artefakte/output/` und `Artefakte/temp/` sind lokale Laufzeitbereiche und werden außer `.gitkeep` ignoriert.

## Erweiterungspunkte

- Neue Problemfälle: `Problemfälle/`
- Neue Modellpakete: `Modelle/einzelmodelle/<modell-id>/`
- Neue OpenWebUI-Tools: `Tools/openwebui_ext/tools/`
- Neue Filter: `Tools/openwebui_ext/filters/`
- Neue Skills: `Tools/openwebui_ext/skills/`
- Neue Promptvorlagen: `Tools/openwebui_ext/prompts/`
- Neue Tests: `Tools/openwebui_ext/tests/`

Nach Änderungen an diesen Bereichen sollte mindestens `python scripts/verify_openwebui_workspace.py` laufen.
