# Test- und Prüfmodell

Dieses Repository ist ein OpenWebUI-Workspace mit Python-Skripten, importierbaren OpenWebUI-Tools, Filtern, Skills, Modellpaketen und generierten Importartefakten. Es gibt kein Paketmanager-Lockfile und keine klassische App-Build-Pipeline. Die lokale Qualitätssicherung läuft deshalb über Python-Standardbibliothek, Repository-Skripte und nicht-mutierende Generatorprüfungen.

## Voraussetzungen

- Python 3.10 oder neuer.
- Keine Installation von Projektabhängigkeiten für die schnelle Basisprüfung.
- Optional: `pydantic`, `fastapi`, `aiohttp`, `requests` und `starlette`, wenn OpenWebUI-nahe GUI-Schema-Importtests ohne Skip laufen sollen.
- Optional: Docker, wenn die Compose-Beispielkonfiguration zusätzlich geprüft werden soll.
- Keine echten OpenWebUI-Admin-Tokens, Jupyter-Tokens oder Produktivdienste für die Basisprüfung.

## Empfohlene Codex-Reihenfolge

1. Arbeitsbaum prüfen:

   ```powershell
   git -c safe.directory=<repo-pfad> -c core.quotePath=false status --short --branch
   ```

2. Zentrale schnelle Prüfung ausführen:

   ```powershell
   python scripts/verify_openwebui_workspace.py
   ```

3. Wenn Docker lokal verfügbar ist, Compose-Beispiele inklusive optionalem `top.secret`-Override zusätzlich prüfen:

   ```powershell
   python scripts/verify_openwebui_workspace.py --include-docker-compose
   ```

4. Wenn Tool-, Filter-, Skill- oder Modellartefakte bewusst geändert wurden, Dist-Artefakte neu erzeugen und danach erneut prüfen:

   ```powershell
   python scripts/generate_model_i18n_profiles.py
   python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
   python scripts/verify_openwebui_workspace.py
   ```

## Einzelbefehle für Diagnose

```powershell
python -m compileall -q scripts Tools Workbench
python scripts/generate_model_i18n_profiles.py
python scripts/validate_openwebui_extensions.py
python scripts/configure_openwebui_tool_models.py --check
python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.example.yaml
python -m unittest discover Tools.openwebui_ext.tests
python -m unittest discover Workbench.dashboard.tests
```

JSON-Artefakte werden durch `scripts/verify_openwebui_workspace.py` mitgeprüft. Der Generator-Check muss ohne neue Änderungen enden (`Änderungen erkannt: False`), sonst sind Dist-Artefakte nicht synchron.

## Internationalisierung prüfen

Das Dashboard muss Deutsch als Fallback und Englisch als Alternativsprache unterstützen. Die Produktkomponenten der Modelle müssen zusätzlich die direkt integrierten Locales `de`, `en`, `es`, `fr`, `pt-BR`, `it`, `nl`, `pl`, `tr`, `ja` und `zh-Hans` enthalten. Die relevanten Tests liegen in `Workbench.dashboard.tests` und `Tools.openwebui_ext.tests`; sie prüfen Locale-Normalisierung, `Accept-Language`-Auswertung, englische Auth-Fehlermeldungen, Produkt-i18n-Metadaten und Unicode-Modell-IDs. Für eine manuelle Prüfung:

```powershell
$env:WORKBENCH_LOCALE="en"
python scripts/generate_model_i18n_profiles.py
python -m Workbench.dashboard.server --host 127.0.0.1 --port 8088
```

Danach im Browser zwischen Deutsch und Englisch wechseln und prüfen, dass Umlaute in Modellnamen, Dateiinhalten und Vorschauen erhalten bleiben.

## Externe Dienste und Secrets

Die Basisprüfung darf keine produktiven Dienste aufrufen. Für API-Importe wird `scripts/openwebui_workspace_config.yaml` lokal aus `scripts/openwebui_workspace_config.example.yaml` erstellt und bleibt durch `.gitignore` unversioniert. Echte Werte wie `OPENWEBUI_ADMIN_TOKEN`, Jupyter-Tokens, lokale Hostnamen und Volume-Pfade gehören nur in diese lokale Datei oder in die Zielumgebung.

## Typische Befunde

- `pydantic is not available`: Der GUI-Schema-Test wird in Minimalumgebungen übersprungen; die strukturellen Importtests laufen weiter.
- `docker ist in dieser Umgebung nicht verfügbar`: Die Compose-Prüfung ist optional und betrifft nicht die Python-/Artefaktvalidierung.
- `Änderungen erkannt: True` im Generator-Check: `python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips` ausführen, Diff prüfen und danach erneut verifizieren.
- Fehler in `validate_openwebui_extensions.py`: Tool-/Filter-Datei auf Syntax, `Tools`-/`Filter`-Klasse, async Hooks, Typannotationen oder riskante Muster prüfen.
