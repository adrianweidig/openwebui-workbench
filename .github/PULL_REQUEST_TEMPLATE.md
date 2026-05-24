# Pull Request

## Zusammenfassung

Beschreibe kurz, welches Problem dieser Pull Request löst und welche Dateien oder Artefakte betroffen sind.

## Betroffene Bereiche

- [ ] Modelle
- [ ] Tools
- [ ] Filter
- [ ] Skills
- [ ] Import/Export
- [ ] Deployment
- [ ] Tests/CI
- [ ] Dokumentation
- [ ] Repository-Pflege

## Validierung

- [ ] `python scripts/verify_openwebui_workspace.py`
- [ ] `python scripts/configure_openwebui_tool_models.py --check`
- [ ] `python -m unittest discover Tools.openwebui_ext.tests`
- [ ] Docker-Compose-Prüfung, falls relevant und Docker verfügbar
- [ ] Nicht zutreffend, weil es sich nur um eine klar begrenzte Dokumentationsänderung handelt

## Sicherheit

- [ ] Keine Secrets, Tokens, privaten URLs oder produktiven Konfigurationsdateien hinzugefügt
- [ ] Keine öffentlichen Netzwerk-Defaults für Offline-Tools aktiviert
- [ ] Drittanbieterquellen oder übernommene Exports in `THIRD_PARTY_NOTICES.md` dokumentiert, falls relevant

## Hinweise

Beschreibe hier bewusst nicht getestete optionale Pfade, bekannte Grenzen oder Follow-up-Arbeit.
