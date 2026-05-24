# Maintainer Checklist

Diese Checkliste enthält manuelle GitHub- und Veröffentlichungsaufgaben, die nicht sicher allein aus dem lokalen Repository erledigt werden können oder bewusste Maintainer-Entscheidungen brauchen.

## Repository-Metadaten

Erledigt am 2026-05-24:

- Repository Description gesetzt: `Portable OpenWebUI workbench with offline model packages, tools, filters, skills and import artifacts.`
- Topics gesetzt: `openwebui`, `offline-ai`, `llm-tools`, `jupyter`, `air-gap`, `python`, `model-packages`, `developer-tools`.
- Issues aktiviert.
- Discussions aktiviert.
- Wiki deaktiviert, weil die Repository-Dokumentation in Markdown-Dateien gepflegt wird.

Offen:

- Website-URL nur setzen, wenn eine belastbare Dokumentations- oder Projektseite existiert.

## Social Preview

- `docs/assets/social-preview.svg` als bearbeitbare Vorlage nutzen.
- `docs/assets/social-preview.png` ist als 1280 x 640 PNG für GitHub Social Preview vorbereitet.
- Social Preview im GitHub-Repository unter `Settings > Social preview` hochladen.

## Branch Protection und Rulesets

Erledigt am 2026-05-24:

- Branch Protection für `main` aktiviert.
- Required Status Checks gesetzt: `Verify workspace (3.10)` und `Verify workspace (3.13)`.
- Strict Status Checks aktiviert.
- Force-Pushes und Branch-Löschungen für `main` deaktiviert.

Offen:

- Entscheiden, ob zusätzlich Pull-Request-Reviews oder Conversation Resolution verpflichtend werden sollen.
- CodeQL-Workflow weiter beobachten; aktuell ist er als Security-Signal aktiv, aber nicht als Required Check gesetzt.

## Security Settings

Erledigt am 2026-05-24:

- Dependabot alerts aktiviert.
- Dependabot security updates aktiviert.
- Code scanning über CodeQL aktiviert; erster Lauf erfolgreich, 0 Alerts.
- Secret scanning aktiviert.
- Secret scanning push protection aktiviert.
- Private Vulnerability Reporting aktiviert.

Offen:

- Optional einen zusätzlichen privaten Sicherheitskontakt außerhalb von GitHub dokumentieren, falls gewünscht.

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
