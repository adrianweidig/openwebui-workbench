# Maintainer Checklist

Diese Checkliste enthält manuelle GitHub- und Veröffentlichungsaufgaben, die nicht sicher allein aus dem lokalen Repository erledigt werden können oder bewusste Maintainer-Entscheidungen brauchen.

## Repository-Metadaten

- Repository Description setzen, zum Beispiel: `Portable OpenWebUI workbench with offline model packages, tools, filters, skills and import artifacts.`
- Topics prüfen und setzen, zum Beispiel: `openwebui`, `offline-ai`, `llm-tools`, `jupyter`, `air-gap`, `python`, `model-packages`, `developer-tools`.
- Website-URL nur setzen, wenn eine belastbare Dokumentations- oder Projektseite existiert.
- Wiki deaktivieren, falls die Repository-Dokumentation ausschließlich in Markdown-Dateien gepflegt werden soll.
- Discussions aktivieren, falls allgemeine Fragen und Ideen getrennt von Issues laufen sollen.

## Social Preview

- `docs/assets/social-preview.svg` als Vorlage nutzen.
- Falls GitHub einen PNG-Upload verlangt, lokal als 1280 x 640 PNG exportieren.
- Social Preview im GitHub-Repository unter `Settings > Social preview` hochladen.

## Branch Protection und Rulesets

- Für `main` Pull Requests vor Merge verlangen.
- CI-Workflow `Verify workspace` als Required Status Check setzen, sobald er auf GitHub einmal erfolgreich gelaufen ist.
- CodeQL-Workflow als Security-Signal beobachten, aber erst nach erfolgreichem Lauf als verpflichtend setzen.
- Force-Pushes und Branch-Löschungen für `main` einschränken.

## Security Settings

- Dependabot alerts aktivieren.
- Dependabot security updates aktivieren.
- Code scanning aktivieren und ersten CodeQL-Lauf prüfen.
- Secret scanning aktivieren, falls für das Repository verfügbar.
- Private Vulnerability Reporting aktivieren oder einen privaten Sicherheitskontakt dokumentieren.

## Releases

- Entscheiden, ob Releases datiert oder semantisch versioniert werden.
- Vor dem ersten Release `CHANGELOG.md` prüfen.
- Release Notes mit ausgeführten Checks und bekannten Grenzen schreiben.
- Keine lokalen Secret- oder Runtime-Konfigurationsdateien in Release-Artefakte aufnehmen.

## Lizenz und Drittanbieter

- Apache-2.0-Lizenz und `THIRD_PARTY_NOTICES.md` vor externer oder kommerziell relevanter Veröffentlichung rechtlich prüfen.
- Bei neuen externen Tool-Exports Lizenz, Quelle, Übernahmedatum und Anpassungen dokumentieren.

## Dokumentations-Hosting

- GitHub Pages nur aktivieren, wenn eine klare Docs-Struktur veröffentlicht werden soll.
- Bei GitHub Pages interne Links und Assets nach der Veröffentlichung prüfen.

## Lokale Pflege

- Nach wesentlichen Änderungen `python scripts/verify_openwebui_workspace.py` ausführen.
- Bei geändertem Dist-Zustand Generatorlauf und Diff prüfen.
- Ignorierte lokale Dateien wie `scripts/openwebui_workspace_config.yaml` nicht in Issues, PRs oder Releases kopieren.
