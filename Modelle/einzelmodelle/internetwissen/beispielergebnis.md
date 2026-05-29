# Beispielergebnis: Internetwissen

## Nutzeranfrage

„Wir überlegen, ob wir unser internes Wiki auf eine neue Version aktualisieren sollen. Ich habe gerade keinen Webzugriff. Erkläre mir bitte, was ich offline sinnvoll prüfen kann, was aktuell verifiziert werden muss und welche Quellen ich später nutzen sollte.“

## Kurzfazit

Offline lässt sich die Entscheidung vorbereiten, aber nicht abschließend treffen. Stabil beantwortbar sind Vorgehen, Prüfkriterien, typische Risiken und lokale Bestandsaufnahme. Prüfpflichtig bleiben die tatsächlich aktuelle Zielversion, bekannte Sicherheitslücken, Breaking Changes, Lizenz- oder Supportstatus und anbieterspezifische Migrationshinweise.

## Was offline belastbar beantwortbar ist

- Der lokale Ist-Zustand kann aus vorhandenen Dateien, Exporten, Changelogs, Plugin-Listen, Container-Tags, Lockfiles und Administrationsnotizen ermittelt werden.
- Eine Migrationsentscheidung sollte mindestens Funktionsumfang, Datenmodell, Erweiterungen, Authentifizierung, Backup, Rollback, Testsystem, Downtime und Verantwortlichkeiten abdecken.
- Eine seriöse Entscheidung trennt technische Machbarkeit, fachlichen Nutzen, Betriebsrisiken und Sicherheitsprüfung.
- Vor jedem Update braucht es ein wiederherstellbares Backup, ein Testprotokoll und klare Abbruchkriterien.

## Was aktuell geprüft werden muss

- Neueste stabile Version und unterstützte Upgrade-Pfade.
- Aktive Sicherheitslücken, CVEs oder Herstellerwarnungen für die eingesetzte und geplante Version.
- Kompatibilität aller genutzten Erweiterungen, Themes, Authentifizierungsadapter und Integrationen.
- Lizenz-, Support- oder API-Änderungen.
- Offizielle Migrationshinweise, falls die Zielversion Datenbank- oder Konfigurationsänderungen verlangt.

Diese Punkte darf ich offline nicht als aktuell bestätigen, solange keine lokale Quelle oder kein KnowledgePack mit passendem Snapshot vorliegt.

## Geeignete Quellenarten

| Quellenart | Zweck |
|---|---|
| lokale Konfigurationsdateien und Inventare | installierte Version, Plugins, Datenbank, Authentifizierung und Integrationen erfassen |
| lokales Backup- oder Betriebsprotokoll | Wiederherstellbarkeit und letzte Änderungen prüfen |
| offizielle Herstellerdokumentation | unterstützte Upgrade-Pfade und Breaking Changes verifizieren |
| Release Notes der Zielversion | neue Funktionen, Entferntes und Migrationsschritte prüfen |
| Security Advisories oder CVE-Datenbank | bekannte Schwachstellen bewerten |
| lokales Testsystem | Update technisch ohne Produktionsrisiko erproben |

## Prüffragen

- Welche Version läuft aktuell wirklich in Produktion?
- Welche Erweiterungen oder Anpassungen sind geschäftskritisch?
- Gibt es ein aktuelles Backup, das testweise wiederhergestellt wurde?
- Welche Version ist das konkrete Ziel und warum?
- Welche Breaking Changes betreffen Datenbank, Authentifizierung, API oder Plugins?
- Welche Sicherheitslücken werden durch das Update geschlossen oder neu relevant?
- Wer entscheidet über Downtime, Rollback und Abnahme?

## Nächster lokaler Schritt

Erstelle zuerst ein lokales Update-Inventar:

```md
## Wiki-Update-Inventar

- Aktuelle Version:
- Laufzeitform: Container, VM, Paketinstallation oder anderer Betrieb:
- Datenbank:
- Authentifizierung:
- Erweiterungen/Plugins:
- Lokale Anpassungen:
- Backup vorhanden:
- Restore getestet:
- Zielversion:
- Offene Online-Prüfungen:
```

Wenn ein lokales KnowledgePack mit Herstellerdokumentation vorhanden ist, nutze nur dessen Manifest, Snapshot-Datum und enthaltene Artefakte. Fehlt ein solches Pack, bleibt die Hersteller- und Sicherheitsprüfung offen.

## Qualitätscheck

- Keine neueste Version wurde erfunden.
- Keine Website wurde als geprüft behauptet.
- Aktualitätskritische Aussagen sind prüfpflichtig markiert.
- Die Antwort enthält konkrete lokale Prüfschritte.
- Die Antwort bleibt ohne Internetzugriff nutzbar.
