# Security Policy

## Geltungsbereich

Dieses Repository enthält OpenWebUI-Modellartefakte, Python-Tools, Filter, Skills, Importskripte und Deployment-Vorlagen. Sicherheitsrelevant sind besonders:

- serverseitig ausgeführte OpenWebUI-Tools
- Jupyter- und Artefakt-Valves
- optionale Netzwerktools
- Importskripte mit Admin-API-Zugriff
- lokale Konfigurationsdateien und Tokens

## Sicherheitsprobleme melden

Bitte keine sensiblen Schwachstellendetails, Tokens, privaten URLs oder Exploit-Schritte in öffentlichen Issues posten.

Wenn GitHub Private Vulnerability Reporting für dieses Repository aktiviert ist, nutze diesen privaten Kanal. Falls er nicht aktiviert ist, sollte der Maintainer zuerst einen privaten Sicherheitskontakt oder GitHub Security Advisories konfigurieren; konkrete Schritte stehen in `docs/MAINTAINER_CHECKLIST.md`.

## Umgang mit Secrets

- Echte Werte gehören nicht in Git.
- Lokale Konfigurationen wie `scripts/openwebui_workspace_config.yaml` bleiben ignoriert.
- Beispielwerte müssen offensichtliche Platzhalter bleiben.
- Logs und Screenshots vor dem Teilen auf Tokens, Hostnamen und interne Pfade prüfen.

## Erwarteter Ablauf

Nach einer privaten Meldung sollte der Maintainer:

1. Eingang und Reproduzierbarkeit prüfen.
2. Betroffene Tools, Filter, Importpfade oder Dokumente eingrenzen.
3. Eine minimale Korrektur oder klare Mitigation vorbereiten.
4. Validierung über `python scripts/verify_openwebui_workspace.py` ausführen.
5. Veröffentlichung und Hinweise so wählen, dass Nutzer geschützt werden.

## Grenzen

Dieses Repository gibt keine Sicherheitsgarantie für eine konkrete OpenWebUI-Instanz. Jede Zielumgebung muss eigene Authentifizierung, Netzwerkgrenzen, Tool-Valves, Jupyter-Sandboxing, Dateisystem-Mounts und Admin-Rechte prüfen.
