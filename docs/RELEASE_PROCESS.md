# Release-Prozess

Das Repository veröffentlicht versionierte Handover-Stände über GitHub Releases. Dieser Prozess beschreibt den lokalen Ablauf, bevor ein Tag oder Release erstellt wird.

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

## Erwartete Release-Artefakte

- `Modelle/dist/openwebui-models-import.json`
- `Modelle/dist/openwebui-registration-plan.json`
- `Modelle/dist/openwebui-model-params-summary.json`
- `Modelle/dist/openwebui-offline-artifacts.zip`
- `Tools/dist/openwebui-tools-offline-import.json`
- `Tools/dist/openwebui-functions-import.json`
- `Tools/dist/openwebui-tools-skills-offline.zip`
- `SHA256SUMS.txt`
- `RELEASE_NOTES.md`
- optional: `Deployment/images/*.tar.zst`

## Automatisches Snapshot-Artefakt

Bei jedem Push auf `main` und bei Pull Requests gegen `main` erstellt `.github/workflows/release-artifact.yml` ein Actions-Artefakt aus dem aktuellen Commit. Der Workflow nutzt `git archive`, enthält keine `.git`-Daten und erzeugt:

- ein ZIP mit Root-Verzeichnis aus Projektname, Branch und Kurz-SHA,
- `RELEASE_NOTES.md` mit Repository, Branch, Commit, Event, Actor, UTC-Zeit und Commitliste,
- `SHA256SUMS.txt` für ZIP und Release Notes.

Branch-Namen werden für ZIP-Root und Actions-Artefaktnamen auf einen sicheren Slug normalisiert. Das verhindert ungültige Artefaktnamen oder verschachtelte Pfade, wenn der Workflow manuell auf einem Branch mit `/` oder anderen Sonderzeichen gestartet wird.

Dieses Actions-Artefakt ist ein reproduzierbarer Snapshot für Prüfung und Handover. Es erstellt keine Tags und keine GitHub Releases. Die Veröffentlichung als GitHub Release bleibt eine bewusste Maintainer-Aktion.

Der Pull-Request-Trigger ist ein Preflight für Änderungen am Release-Artefakt-Workflow selbst, zum Beispiel Dependabot-Updates von `actions/upload-artifact`. Major-Upgrades bleiben trotzdem manuell zu prüfen und werden nicht allein durch einen grünen PR-Preflight automatisch gemergt.

## Ablauf

1. Verify ausführen.
2. Dist-Artefakte bauen.
3. Checksums erzeugen.
4. Changelog prüfen.
5. Tag erstellen.
6. Release Notes erzeugen.
7. Assets hochladen.
8. GHCR-Image-Tags prüfen, wenn ein Dashboard-Image gebaut wurde.

## Checksums

Beispiel:

```powershell
Get-FileHash Modelle/dist/openwebui-models-import.json -Algorithm SHA256
Get-FileHash Modelle/dist/openwebui-registration-plan.json -Algorithm SHA256
Get-FileHash Modelle/dist/openwebui-offline-artifacts.zip -Algorithm SHA256
Get-FileHash Tools/dist/openwebui-tools-offline-import.json -Algorithm SHA256
Get-FileHash Tools/dist/openwebui-tools-skills-offline.zip -Algorithm SHA256
```

## Release Notes

Release Notes sollten enthalten:

- Zweck des Releases,
- relevante Modell-, Tool-, Filter- oder Skill-Änderungen,
- Dist-Artefakte und Checksums,
- ausgeführte Checks,
- bekannte Einschränkungen,
- Container-Image-Hinweise,
- Hinweise zu lokalen Konfigurationsdateien und Secrets.

## Container-Images

GHCR-Images werden nur als aktualisiert dokumentiert, wenn der zugehörige GitHub-Actions-Lauf erfolgreich war oder ein Maintainer den Build manuell geprüft hat. Air-Gap-Image-Archive gehören nach `Deployment/images/` nur mit Hash, Manifest, Budgetprüfung und geklärter LFS-/Release-Asset-Strategie.

## Veröffentlichung

GitHub Releases und Social-Preview-Uploads bleiben bewusste Maintainer-Aktionen. Lokale Release Notes unter `docs/releases/` dürfen vorbereitet werden, ohne zu behaupten, dass ein GitHub Release bereits veröffentlicht wurde.
