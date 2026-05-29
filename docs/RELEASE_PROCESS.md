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
