# Goldstandard-Ergebnis: Offline Workbench Agent

## Nutzerauftrag

Erstelle aus einer CSV mit Ticketkennzahlen und einem kurzen Projekttext einen offline nutzbaren HTML-Report, eine JSON-Zusammenfassung und ein ZIP-Übergabepaket. Es gibt keinen Internetzugang und keine freigegebenen Logos.

## Annahmen

- Die CSV-Datei liegt im erlaubten Arbeitsverzeichnis.
- Es werden keine externen Bilder, Fonts, CDNs oder APIs genutzt.
- Konkrete Kennzahlen werden nur aus der bereitgestellten CSV übernommen.
- PDF-Erzeugung ist optional und nur möglich, wenn ein lokaler Konverter vorhanden ist.

## Tool-Plan

| Welle | Zweck | Werkzeugklasse | Ergebnis |
|---|---|---|---|
| 1 | Eingaben prüfen | Datei-/Textvalidierung | Dateiliste, Schema, fehlende Spalten |
| 2 | Daten berechnen | lokales Python/Jupyter | aggregierte Kennzahlen, Plausibilitätsnotizen |
| 3 | Artefakte bauen | Offline-HTML/ZIP | `ticket-report.html`, `summary.json`, `handover.zip` |
| 4 | Qualität prüfen | JSON-/HTML-/Linkprüfung | Validierungsprotokoll |

## Artefaktmanifest

```json
{
  "artifacts": [
    {
      "path": "Artefakte/output/ticket-report.html",
      "purpose": "Offline lesbarer Management-Report mit eingebettetem CSS",
      "offlineSafe": true
    },
    {
      "path": "Artefakte/output/summary.json",
      "purpose": "Maschinenlesbare Zusammenfassung der berechneten Kennzahlen",
      "offlineSafe": true
    },
    {
      "path": "Artefakte/output/handover.zip",
      "purpose": "Übergabepaket aus Report, JSON und Validierungsnotiz",
      "offlineSafe": true
    }
  ],
  "validation": [
    "CSV-Spalten geprüft",
    "JSON syntaktisch geprüft",
    "HTML auf externe URLs geprüft",
    "ZIP-Inhaltsliste geprüft"
  ],
  "openItems": [
    "PDF wurde nicht erzeugt, falls kein lokaler Browser- oder PDF-Konverter verfügbar ist",
    "Kennzahlen müssen fachlich freigegeben werden"
  ]
}
```

## HTML-Offlineregeln

- CSS direkt in `<style>`.
- Keine `http://`- oder `https://`-Ressourcen.
- Systemschriften statt Webfonts.
- Tabellen mit Umbruchregeln.
- Druckstylesheet für A4.
- Keine Tracker, Telemetrie oder externen Skripte.

## Abschlussbericht

```md
# Ergebnis

Erstellt wurden ein offline nutzbarer HTML-Report, eine JSON-Zusammenfassung und ein ZIP-Übergabepaket.

# Validierung

- CSV-Struktur gelesen und Pflichtspalten geprüft.
- Kennzahlen aus den bereitgestellten Daten berechnet.
- HTML enthält keine externen Runtime-URLs.
- JSON ist syntaktisch gültig.
- ZIP enthält nur die vorgesehenen Artefakte.

# Grenzen

Die Auswertung ersetzt keine fachliche Freigabe. Fehlende CSV-Spalten, unklare Definitionen und nicht bereitgestellte Zielwerte wurden als offene Punkte markiert.
```
