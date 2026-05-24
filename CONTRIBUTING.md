# Contributing

Danke für dein Interesse an der OpenWebUI Workbench. Beiträge sind willkommen, wenn sie die direkte OpenWebUI-Nutzbarkeit, Offline-Fähigkeit, Dokumentation, Validierung oder Wartbarkeit verbessern.

## Geeignete Beiträge

- neue oder präzisere Problemfall-Briefings unter `Problemfälle/`
- Verbesserungen an Modellpaketen unter `Modelle/einzelmodelle/`
- sichere OpenWebUI-Tools, Filter oder Skills unter `Tools/openwebui_ext/`
- Tests für Tools, Filter, Importlogik und Generatorverhalten
- Dokumentationskorrekturen für Import, Deployment, Valves, Fehlerbilder oder Offline-Betrieb
- kleine Repository-Hygiene-Verbesserungen ohne Formatierungswelle

## Lokale Einrichtung

Für die Basisprüfung ist keine Paketinstallation nötig. Benötigt wird Python 3.10 oder neuer.

```powershell
git clone https://github.com/adrianweidig/openwebui-workbench.git
cd openwebui-workbench
python scripts/verify_openwebui_workspace.py
```

Optionale Python-Pakete wie `pydantic`, `fastapi`, `aiohttp`, `requests` und `starlette` können OpenWebUI-nahe Schema-Tests erweitern. Docker ist nur für die optionale Compose-Prüfung relevant.

## Entwicklungsregeln

- Bestehende Inhalte nicht destruktiv überschreiben.
- `Problemfälle/` als fachliche Quelle behandeln und nicht beiläufig umformulieren.
- Operative Modellartefakte unter `Modelle/` und Toolartefakte unter `Tools/` pflegen.
- `Modelle/dist/` und `Tools/dist/` sind kanonische Handover-Artefakte und dürfen nur bewusst regeneriert werden.
- Keine Secrets, Tokens, API-Keys oder produktiven Zugangsdaten committen.
- Keine öffentlichen Netzwerk-Defaults in Offline-Tools einbauen.
- Neue externe Quellen oder übernommene Tool-Exports in `THIRD_PARTY_NOTICES.md` dokumentieren.

## Tests und Validierung

Vor jedem Pull Request mindestens ausführen:

```powershell
python scripts/verify_openwebui_workspace.py
```

Für gezielte Diagnose:

```powershell
python -m compileall -q scripts Tools
python scripts/validate_openwebui_extensions.py
python scripts/configure_openwebui_tool_models.py --check
python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.example.yaml
python -m unittest discover Tools.openwebui_ext.tests
```

Wenn Tool-, Filter-, Skill- oder Modellartefakte geändert wurden:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/verify_openwebui_workspace.py
```

Wenn Docker verfügbar ist:

```powershell
python scripts/verify_openwebui_workspace.py --include-docker-compose
```

## Pull Requests

Ein guter Pull Request enthält:

- eine kurze Beschreibung des Problems oder Ziels
- die betroffenen Bereiche, zum Beispiel Modelle, Tools, Filter, Doku oder Deployment
- die ausgeführten Prüfungen mit Ergebnis
- Hinweise auf bewusst nicht getestete optionale Pfade
- keine irrelevanten Formatierungsänderungen

Branch-Namen sollten den Zweck erkennen lassen, zum Beispiel `docs/import-guide`, `tools/json-validator-tests` oder `models/presentation-profile`.

## Commit-Stil

Kurze, aussagekräftige Commit-Nachrichten reichen aus. Bewährt sind Präfixe wie:

- `docs:`
- `test:`
- `tools:`
- `models:`
- `ci:`
- `chore:`

## Issues

Bitte Issues mit klarer Reproduktion, Umgebung und erwarteter Wirkung erstellen. Sicherheitsrelevante Details gehören nicht in öffentliche Issues; siehe `SECURITY.md`.

## Kommunikation

Alle Beiträge sollen respektvoll, konkret und überprüfbar bleiben. Kritik an Code, Dokumentation oder Architektur ist willkommen, wenn sie nachvollziehbar begründet und auf das Repository bezogen ist.
