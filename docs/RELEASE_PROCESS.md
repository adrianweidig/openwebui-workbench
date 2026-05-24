# Release Process

Das Repository hat aktuell keine veröffentlichte Versionierung über Tags oder Releases. Dieser Prozess beschreibt einen sicheren Ablauf, falls Maintainer künftig versionierte Handover-Stände veröffentlichen.

## Vorbereitende Prüfung

1. Arbeitsbaum prüfen:

   ```powershell
   git status --short --branch
   ```

2. Falls Modell-, Tool-, Filter- oder Skill-Artefakte geändert wurden:

   ```powershell
   python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
   ```

3. Zentrale Prüfung ausführen:

   ```powershell
   python scripts/verify_openwebui_workspace.py
   ```

4. Optional mit Docker:

   ```powershell
   python scripts/verify_openwebui_workspace.py --include-docker-compose
   ```

## Changelog

`CHANGELOG.md` vor einer Release-Erstellung aktualisieren. Es sollten nur tatsächlich enthaltene Änderungen dokumentiert werden.

## Tagging

Falls eine Versionierung eingeführt wird, sollte sie einheitlich bleiben. Ein mögliches Schema ist `vYYYY.MM.DD` für datierte Handover-Stände oder SemVer, falls künftig eine klar versionierte API entsteht. Diese Entscheidung liegt bei den Maintainern.

## Release Notes

Release Notes sollten enthalten:

- Zweck des Releases
- relevante Modell-, Tool-, Filter- oder Skill-Änderungen
- ausgeführte Checks
- bekannte Einschränkungen
- Hinweise zu lokalen Konfigurationsdateien und Secrets

## Keine automatische Veröffentlichung

Dieses Repository enthält keine automatische Release-Pipeline. Veröffentlichungen, GitHub Releases und Social Preview Uploads bleiben bewusste Maintainer-Aktionen.
