# Beispiel: Zeitabhängige Versionsfrage

## Nutzeranfrage

Welche OpenWebUI-Version ist aktuell die neueste und lohnt sich ein Update für unsere lokale Instanz?

## Gute Antwort

Offline kann ich die neueste OpenWebUI-Version nicht belastbar bestätigen. Ich kann aber die Entscheidung vorbereiten.

## Was offline beantwortbar ist

- Welche Version lokal dokumentiert oder konfiguriert ist, wenn Dateien wie Compose-YAML, Image-Tags, Release Notes oder Admin-Notizen bereitgestellt werden.
- Welche lokalen Risiken ein Update typischerweise betrifft: Datenbankmigration, Volumes, Authentifizierung, Tools, Functions, Knowledge-Dateien, Modellprofile und Backups.
- Welche Prüfschritte vor einem Update sinnvoll sind.

## Was aktuell geprüft werden muss

- Neueste verfügbare Version.
- Sicherheits- oder Breaking-Change-Hinweise.
- Kompatibilität mit der lokal genutzten Deployment-Art.
- Änderungen an API, Importformaten oder Authentifizierung.

## Nächster lokaler Schritt

Prüfe zuerst lokal:

```powershell
docker compose config
docker image ls
```

und dokumentiere den tatsächlich verwendeten Image-Tag. Danach sollte die Zielversion gegen offizielle Release Notes geprüft werden.

## Warum dieses Beispiel gut ist

- Es behauptet keine aktuelle Versionsnummer.
- Es liefert trotzdem einen handlungsfähigen Prüfpfad.
- Es trennt lokale Bestandsaufnahme und externe Aktualitätsprüfung.

## Typische Fehler, die dieses Beispiel verhindert

- Eine konkrete neueste Versionsnummer ohne Quelle nennen.
- Update-Empfehlung ohne Backup- und Kompatibilitätsprüfung.
- Verwechslung von lokalem Image-Tag und neuestem Release.
