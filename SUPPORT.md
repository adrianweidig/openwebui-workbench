# Support

## Öffentliche Fragen

Für reproduzierbare Fehler, Dokumentationslücken und konkrete Verbesserungsvorschläge bitte GitHub Issues verwenden:

- Bug Report für fehlerhafte Tools, Filter, Importartefakte oder Prüfskripte
- Documentation für unklare Anleitungen, Pfade oder Importreihenfolgen
- Feature Request für neue Modelle, Tools, Skills oder Prüfungen

## Vor einer Anfrage

Bitte nach Möglichkeit prüfen:

```powershell
python scripts/verify_openwebui_workspace.py
```

Bei Docker-/Compose-Fragen zusätzlich, falls Docker lokal verfügbar ist:

```powershell
python scripts/verify_openwebui_workspace.py --include-docker-compose
```

## Keine öffentlichen Secrets

Bitte keine Admin-Tokens, Jupyter-Tokens, privaten Hostnamen, `.env`-Dateien oder produktiven Konfigurationsdateien in Issues, Pull Requests oder Screenshots teilen.

## Sicherheitsprobleme

Sicherheitsrelevante Details nicht öffentlich melden. Der Ablauf steht in `SECURITY.md`.
