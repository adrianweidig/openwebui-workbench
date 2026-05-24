# FAQ

## Ist dieses Repository eine Web-App?

Nein. Es ist ein portabler OpenWebUI-Workbench-Arbeitsbereich mit Modellpaketen, Tools, Filtern, Skills, Importartefakten, Deployment-Vorlagen und Prüfskripten.

## Welcher Befehl prüft den aktuellen Stand?

```powershell
python scripts/verify_openwebui_workspace.py
```

Dieser Befehl ist nicht-mutierend und für Pull Requests sowie lokale Wartung der wichtigste Smoke-Check.

## Warum gibt es kein Paketmanager-Lockfile?

Das Repository hat aktuell kein Projektmanifest und keine klassische App-Build-Pipeline. Die Basisprüfung nutzt Python-Standardbibliothek, lokale Skripte und Unit-Tests. Optionale Pakete erweitern einzelne OpenWebUI-nahe Tests, sind aber nicht für die schnelle Basisprüfung erforderlich.

## Warum sind Dateien in `Modelle/einzelmodelle/` und `Modelle/dist/artifacts/` ähnlich oder identisch?

Das ist gewollt. `Modelle/einzelmodelle/` ist die menschenlesbare Pflegeablage. `Modelle/dist/` ist der kanonische Handover-Bereich für Import, Copy/Paste, ZIP und Air-Gap-Transfer.

## Wann muss ich Dist-Artefakte neu erzeugen?

Wenn Tool-, Filter-, Skill- oder Modellartefakte bewusst geändert wurden:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/verify_openwebui_workspace.py
```

## Was bedeutet `Änderungen erkannt: True` im Generator-Check?

Der aktuelle Dist- oder Modellzustand ist nicht synchron mit den Generatorregeln. In diesem Fall Generator mit `--write --check --rebuild-zips` ausführen, Diff prüfen und danach erneut verifizieren.

## Warum wird ein Test übersprungen?

In Minimalumgebungen können optionale Pakete wie `pydantic` fehlen. Dann werden OpenWebUI-nahe GUI-Schema-Tests übersprungen, während die strukturellen Importtests weiterlaufen.

## Warum schlägt die Docker-Prüfung fehl oder wird übersprungen?

`python scripts/verify_openwebui_workspace.py --include-docker-compose` benötigt lokal verfügbares Docker. Ohne Docker bleibt die Python-/Artefaktvalidierung trotzdem aussagekräftig.

## Wo gehören echte Tokens hin?

In keine versionierte Datei. Für API-Importe wird lokal `scripts/openwebui_workspace_config.yaml` aus `scripts/openwebui_workspace_config.example.yaml` erstellt. Diese echte Datei ist ignoriert.

## Welche OpenWebUI-Adresse gehört in die Importkonfiguration?

`openwebui.base_url` soll auf die WebUI-Root zeigen, zum Beispiel `http://127.0.0.1:3000`, nicht auf `/api` oder `/api/v1`.

## Was bedeutet `We could not find what you're looking for` beim Tool-Valves-Schritt?

Typische Ursachen sind: das Tool wurde noch nicht importiert, die OpenWebUI-Instanz erkennt keine `Valves`-Schema-Klasse am Tool oder die Version stellt den Valves-Endpunkt nicht bereit. Der Importer meldet den übersprungenen Valves-Satz und führt den restlichen Import weiter.

## Sind öffentliche Netzwerktools im Offline-Standard aktiv?

Nein. Der Offline-Standard nutzt Air-Gap-taugliche Defaults. Netzwerk- oder Rich-UI-Tools sind optional und müssen bewusst importiert, konfiguriert und geprüft werden.

## Wo finde ich Drittanbieterhinweise?

In `THIRD_PARTY_NOTICES.md`. Dort sind geprüfte Quellen, Entscheidungen und übernommene Tool-Exports dokumentiert.
