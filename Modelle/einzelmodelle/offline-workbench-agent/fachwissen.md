# Fachwissen für Offline Workbench Agent

## Offline-Architektur

- OpenWebUI ist die Chat-Oberfläche.
- Das Basismodell `coder` liefert Sprach- und Denkfähigkeit.
- Jupyter übernimmt kontrollierte Python-Ausführung.
- Das Artefakt-Tool schreibt HTML, PDF und ZIP in ein gemountetes Volume.
- Skills steuern Arbeitsweisen wie sichere Toolnutzung, Artefaktproduktion und Review.

## Gute HTML/PDF-Artefakte

- vollständiger HTML-Rahmen
- eingebettetes CSS
- `@page` für A4 oder 16:9-Landscape
- keine externen Ressourcen
- Tabellen mit Umbruchregeln
- klare Überschriftenhierarchie
- druckbare Farben und ausreichender Kontrast

## Gute Präsentationen

- eine Aussage pro Folie
- kurze Headlines
- maximal 5 bis 7 Bullet Points
- optionale Sprechernotizen
- 16:9-Seitenformat
- keine Abhängigkeit von externen Medien

## Jupyter-Einsatz

Nutze Jupyter für:

- Berechnungen
- CSV/JSON-Verarbeitung
- Diagrammdaten
- Validierung von Dateiinhalten
- Generierung von Zwischenartefakten

Nutze Jupyter nicht für:

- Internetzugriffe
- Shell-Umgehung
- Zugriff auf nicht erlaubte Pfade
- Ausgabe von Secrets

## Sicherheitscheck vor Abschluss

- Keine Secrets im Ergebnis?
- Keine externen Abhängigkeiten im HTML?
- Artefakte im erlaubten Verzeichnis?
- Annahmen gekennzeichnet?
- PDF-Fallback erklärt, falls kein Konverter verfügbar?
