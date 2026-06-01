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
   python scripts/check_workbench_setup.py
   python scripts/verify_openwebui_workspace.py
   ```

3. Wenn Docker lokal verfügbar ist, Compose-Beispiele inklusive optionalem Enterprise-CA- und `top.secret`-Override zusätzlich prüfen:

   ```powershell
   python scripts/check_workbench_setup.py --require-docker --run-compose-config
   python scripts/verify_openwebui_workspace.py --include-docker-compose
   ```

   In GitHub Actions läuft derselbe Compose-Config-Pfad als separater CI-Job. Es werden nur Compose-Dateien gerendert, keine Container gestartet. Der optionale Verify-Pfad rendert neben Standard-, Shared-Targets-, Enterprise-CA- und `top.secret`-Varianten auch die separaten Passwortdatei- und OpenWebUI-Admin-Token-Datei-Overrides sowie deren kombinierte Nutzung.
   Auf Windows-Hosts ohne Docker in der PATH, aber mit verfügbarer WSL, weisen Setup-Doctor und Verify-Runner auf den WSL-Pfad hin. Die Compose-Prüfungen sollen dann aus der WSL-Umgebung laufen, die Docker bereitstellt.
   Für nicht-mutierende Prüfungen aus Windows heraus kann der Docker-Befehl explizit gesetzt werden:

   ```powershell
   python scripts/check_workbench_setup.py --docker-command "wsl.exe -d Debian -- docker" --require-docker --run-compose-config
   python scripts/verify_openwebui_workspace.py --include-docker-compose --docker-command "wsl.exe -d Debian -- docker"
   ```

   Der Setup-Doctor führt bei explizitem `--docker-command` vorab `docker compose version` aus. Ein deaktivierter `WSLService` oder ein nicht nutzbarer WSL-Docker-Pfad wird dadurch als Preflight-Fehler sichtbar, ohne Container zu starten.
   Zusätzliche lokale Compose-Overrides können für denselben Preflight wiederholbar angegeben werden:

   ```powershell
   python scripts/check_workbench_setup.py --require-docker --run-compose-config --compose-override Deployment/docker-compose.workbench-password-file.yml --compose-override Deployment/docker-compose.openwebui-admin-token-file.yml
   ```

   Bei Compose-Overrides mit `${VAR:?Meldung}` prüft der Setup-Doctor die benötigten Variablen vor `docker compose config`, damit fehlende Secret-Dateipfade als gezielte Preflight-Meldung statt als nachgelagerter Compose-Fehler erscheinen.

4. Wenn Tool-, Filter-, Skill- oder Modellartefakte bewusst geändert wurden, Dist-Artefakte neu erzeugen und danach erneut prüfen:

   ```powershell
   python scripts/generate_model_i18n_profiles.py
   python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
   python scripts/verify_openwebui_workspace.py
   ```

## Einzelbefehle für Diagnose

```powershell
python -m compileall -q scripts Tools Workbench
python scripts/check_workbench_setup.py
python scripts/check_doc_language_pairs.py
python scripts/check_security_hygiene.py
python scripts/generate_model_i18n_profiles.py
python scripts/validate_openwebui_extensions.py
python scripts/configure_openwebui_tool_models.py --check
python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.example.yaml
python -m unittest discover Tools.openwebui_ext.tests
python -m unittest discover Workbench.dashboard.tests
```

JSON-Artefakte werden durch `scripts/verify_openwebui_workspace.py` mitgeprüft. Der Generator-Check muss ohne neue Änderungen enden (`Änderungen erkannt: False`), sonst sind Dist-Artefakte nicht synchron.

Die Unit-Tests unter `Tools.openwebui_ext.tests` enthalten zusätzlich leichte Workflow-Hygiene-Prüfungen für sicher benannte Release-Artefakte. Die Dashboard-Tests prüfen neben API- und Schreibpfaden auch die Browser-Security-Header der lokalen Workbench-Oberfläche, die 30-Minuten-Dashboard-Automation mit manuellem Trigger und kurze Startup-Fehler für ungültige numerische, boolesche, URL-basierte oder dateibasierte Dashboard-Env-Werte, erzwungene Dashboard-Authentifizierung sowie für belegte Dashboard-Ports.

Der Setup-Doctor ist nicht-mutierend und prüft zusätzlich, ob `OPENWEBUI_PORT` und `WORKBENCH_PORT` gültige, unterschiedliche Host-Ports ergeben, ob `OPENWEBUI_BASE_URL`, `OPENWEBUI_PUBLIC_URL` sowie optional gesetzte `PORTAINER_URL`, `RAGFLOW_BASE_URL` und `SEAFILE_BASE_URL` vollständige `http`- oder `https`-URLs ohne eingebettete Zugangsdaten sind, ob boolesche Flags wie `OPENWEBUI_TLS_VERIFY` und `WORKBENCH_REQUIRE_AUTH` explizite Wahr/Falsch-Werte enthalten, ob Timeout-/Größenwerte und `WORKBENCH_AUTOMATION_INTERVAL_MINUTES` gültige Ganzzahlen sind, ob Automationsaktionen aus der erlaubten Liste stammen und ob dateibasierte Runtime-Pfade plausibel sind. Mit `--probe-runtime` prüft der Setup-Doctor OpenWebUI und optional Portainer per HTTP, ohne Tokens zu nutzen oder Dienste zu verändern. `WORKBENCH_ENTERPRISE_CA_HOST_FILE` wird als lokale Hostdatei und PEM-Zertifikat geprüft; mit `--allow-unverified-root-ca-path` darf ein nicht lokal sichtbarer Docker-/Portainer-Hostpfad als Warnung durchlaufen, während lokal lesbare PEM-Dateien weiterhin validiert werden. `WORKBENCH_AUTH_PASSWORD_HOST_FILE` und `OPENWEBUI_ADMIN_TOKEN_HOST_FILE` werden als lokale Hostdateien geprüft; mit `--allow-unverified-secret-file-path` darf ein nicht lokal sichtbarer Docker-/Portainer-Hostpfad als Warnung durchlaufen, ohne Secret-Dateiinhalte zu lesen oder auszugeben. Container-only Secret- oder CA-Pfade werden als Warnung markiert, wenn sie hostseitig nicht sichtbar sind. Fehlende Werte nutzen die Compose-Defaults.

Mit `--probe-runtime` führt der Setup-Doctor zusätzlich nicht-mutierende HTTP-Probes aus. OpenWebUI wird über `OPENWEBUI_PUBLIC_URL` geprüft; Portainer wird nur geprüft, wenn `--portainer-url`, die Prozessumgebung `PORTAINER_URL` oder `PORTAINER_URL` in der lokalen `.env` gesetzt ist. Der CLI-Wert hat Vorrang vor `.env`. Der Probe nutzt keine Tokens, behandelt HTTP 401/403 als erreichbaren Auth-Endpunkt und wird mit `--require-runtime` abnahmehart.

## Security-Hygiene prüfen

Der Standard-Verify-Lauf enthält `scripts/check_security_hygiene.py`. Der Check betrachtet versionierte und nicht ignorierte Textdateien, meldet nur Pfad, Zeile und Befundart und gibt verdächtige Werte absichtlich nicht aus.

```powershell
python scripts/check_security_hygiene.py
python scripts/check_security_hygiene.py --include-bandit
```

`--include-bandit` ist optional und läuft nur, wenn Bandit lokal installiert ist. Es wird keine neue Pflichtabhängigkeit eingeführt.

## Dokumentations-Sprachpaare prüfen

Kanonische deutsch/englische Dokumentationspaare sind in [`docs/LANGUAGE_PAIRS.md`](docs/LANGUAGE_PAIRS.md) beschrieben und werden durch `scripts/check_doc_language_pairs.py` geprüft. Der Check stellt sicher, dass erwartete Paare vorhanden sind und sichtbare Sprachlinks besitzen.

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
