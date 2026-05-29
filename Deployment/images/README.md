# Offline-Container-Images

Dieser Ordner dokumentiert optionale Air-Gap-Image-Artefakte. Große Image-Tars werden nicht automatisch versioniert. Nutze Git LFS oder GitHub Release Assets erst nach Maintainer-Entscheidung und innerhalb des 10-GiB-Gesamtbudgets aus `docs/OFFLINE_DATA_POLICY.md`.

## Exportbeispiel

```powershell
docker pull ghcr.io/open-webui/open-webui:<pin>
docker pull ghcr.io/adrianweidig/openwebui-workbench/workbench-dashboard:<pin>

docker save ghcr.io/open-webui/open-webui:<pin> -o Deployment/images/openwebui-<pin>.tar
docker save ghcr.io/adrianweidig/openwebui-workbench/workbench-dashboard:<pin> -o Deployment/images/workbench-dashboard-<pin>.tar
```

Optional komprimieren:

```powershell
zstd -19 Deployment/images/openwebui-<pin>.tar
zstd -19 Deployment/images/workbench-dashboard-<pin>.tar
```

Prüfsummen erzeugen:

```powershell
Get-FileHash Deployment/images/*.tar* -Algorithm SHA256 | Format-Table
```

## Regeln

- Image-Dateien nur mit eindeutigem Tag oder Digest exportieren.
- Keine `latest`-Only-Archive als langfristiges Handover verwenden.
- `manifest.example.json` als Vorlage nutzen und echte Artefakte mit Größe und SHA256 dokumentieren.
- Keine produktiven `.env`-Dateien, Tokens oder privaten Registry-Zugänge beilegen.
