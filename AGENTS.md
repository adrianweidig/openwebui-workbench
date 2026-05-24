# OpenWebUI Workbench Agentenanweisungen

## Projektüberblick

Dieses Repository ist ein portabler OpenWebUI-Workbench-Arbeitsbereich für Modellpakete, Tools, Filter, Skills, Importartefakte und Deployment-Vorlagen. Es ist keine klassische Web-App und hat aktuell kein Paketmanager-Lockfile. Änderungen sollen die direkte OpenWebUI-Nutzbarkeit erhalten.

## Wichtige Verzeichnisse

- `OpenWebUI Model Builder/`: Vorgaben, Generatorlogik und Builder-Arbeitsbereich.
- `Problemfälle/`: fachliche Briefings; nicht destruktiv bearbeiten.
- `Modelle/einzelmodelle/`: menschenlesbare Modellpakete.
- `Modelle/dist/`: kanonische Air-Gap-Handover-Artefakte.
- `Tools/jupyter/`: produktives Jupyter-Tool.
- `Tools/openwebui_ext/`: importierbare Tools, Filter, Skills, Doku und Tests.
- `Tools/dist/`: gebündelte Tool-/Skill-Artefakte.
- `Artefakte/output/` und `Artefakte/temp/`: lokale Laufzeitausgaben, normalerweise nicht versioniert.
- `Deployment/`: Offline-Compose- und Volume-Vorlagen.

## Standardbefehle

Installationsbefehl: keiner, solange kein Projektmanifest ergänzt wird.

Validierung:

```powershell
python scripts/validate_openwebui_extensions.py
python scripts/configure_openwebui_tool_models.py --check
python -m unittest discover Tools.openwebui_ext.tests
```

Artefakte bewusst neu erzeugen:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
```

API-Import nur nach ausdrücklichem Auftrag und mit lokal gesetztem Token:

```powershell
$env:OPENWEBUI_ADMIN_TOKEN="YOUR_OPEN_WEBUI_API_KEY"
python Tools/import_openwebui_workspace.py --base-url http://localhost:3000
```

## Coding-Konventionen

- Bestehende Python-Tool-Struktur beibehalten: importierbare `Tools`-Klassen, async Tool-Methoden, Typannotationen.
- OpenWebUI-Filter als `Filter`-Klassen mit passenden Hooks halten.
- Keine neuen externen Abhängigkeiten ohne konkreten Prüf- oder Laufzeitnutzen.
- Kein globales Formatieren und keine breitflächigen Refactors.
- JSON-Artefakte mit UTF-8 und stabiler Sortierung/Formatierung des Generators pflegen.

## Dokumentationskonventionen

- `README.md` ist der zentrale Einstieg.
- Spezialdokumente behalten, wenn sie operative Details liefern; aus der README darauf verlinken.
- Deutsche Fließtexte mit echten UTF-8-Umlauten schreiben.
- Technische Aussagen nur dokumentieren, wenn die Dateien oder Skripte im aktuellen Stand existieren.
- Drittanbieter-Quellen und Übernahmen in `THIRD_PARTY_NOTICES.md` dokumentieren.

## Git-Regeln

- Vor Änderungen `git status --short --branch` prüfen.
- Bei `dubious ownership` keine globale Git-Konfiguration ändern; für Prüfungen `git -c safe.directory=E:/OpenWebUI ...` nutzen.
- Keine destruktiven Git-Befehle ohne ausdrückliche Freigabe.
- Pull, Push, Merge, Rebase und Konfliktlösung nicht automatisch ausführen, außer der Nutzer beauftragt ausdrücklich Repository-Synchronisation oder Veröffentlichung.
- Bestehende Nutzer- oder Fremdänderungen nicht überschreiben.

## Sicherheitsgrenzen

- Keine Secrets, Tokens, Passwörter oder echten Zugangsdaten in Dateien schreiben.
- `.env`, lokale YAML-Konfigurationen und Tokens bleiben lokal und werden ignoriert.
- Keine produktiven OpenWebUI-, Jupyter-, Docker- oder API-Aktionen ohne klaren Auftrag.
- Netzwerktools sind nicht Teil des Air-Gap-Defaults und dürfen nicht still aktiviert werden.
- Unsichere oder nicht referenzierte Dateien nicht löschen, sondern im Abschlussbericht markieren.

## Datei-Löschungen

- Sicher löschbar sind nur lokale Caches wie `__pycache__/`, `.pytest_cache/` oder eindeutig temporäre Dateien.
- Modell-Duplikate zwischen `Modelle/einzelmodelle/` und `Modelle/dist/artifacts/` sind gewollt.
- Dist-ZIP- und Importdateien sind Handover-Artefakte und nicht ohne Regenerierung zu löschen.
- Original-Briefings in `Problemfälle/` bleiben erhalten.

## Definition of Done

- Relevante Checks wurden ausgeführt oder die Grenze wurde begründet.
- `git diff` wurde geprüft.
- README, AGENTS und Lizenzangaben sind konsistent.
- Keine Secrets wurden hinzugefügt.
- Keine Funktionalität wurde absichtlich verändert.
- Unsichere Punkte sind im Abschlussbericht als prüfpflichtig markiert.
