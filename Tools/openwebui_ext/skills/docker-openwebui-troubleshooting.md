---
name: docker-openwebui-troubleshooting
description: Fehleranalyse für Docker-, Compose- und OpenWebUI-Deployments ohne destruktive Befehle.
---

# Docker OpenWebUI Troubleshooting

## Diagnose-Reihenfolge
- Containerstatus, Logs, Ports, Volumes, Umgebungsvariablen und Reverse Proxy prüfen.
- Bei OpenWebUI zusätzlich Datenvolume, Modellanbieter, Base-URLs und Auth-Konfiguration prüfen.
- Erst lesen und erklären, dann Änderungen vorschlagen.

## Häufige Problemklassen
- Portkonflikte zwischen Host und Container.
- Fehlende Persistenz für `/app/backend/data`.
- Falsche Provider-URL aus Container-Sicht.
- Reverse-Proxy-Header, WebSocket- oder TLS-Probleme.
- Rechteprobleme auf gemounteten Volumes.

## Sicherheit
- Keine destruktiven Befehle wie Volume-Löschung ohne explizite Sicherung und Freigabe.
- Secrets aus `.env`, Compose-Dateien und Logs nicht wiederholen.
- Änderungen als kleine, überprüfbare Schritte formulieren.
