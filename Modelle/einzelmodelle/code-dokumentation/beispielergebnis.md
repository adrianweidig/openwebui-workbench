        # Beispielergebnis: Entwicklerdokumentation

        Dieses Goldstandard-Beispiel zeigt eine fertige Antwort des Modells `Code-Dokumentation`. Es nutzt nur den sichtbaren Nutzerkontext, trennt Fakten von Annahmen und enthält keine externen Laufzeitabhängigkeiten.

        ## Modul: CSV-Ticketimport

`src/importer.py` liest Ticketdaten aus CSV-Dateien, validiert Pflichtfelder und übergibt normalisierte Datensätze an den Repository-Layer.

## Nutzung

```bash
python -m app.importer tickets.csv --dry-run
```

## Datenvertrag

| Spalte | Pflicht | Bedeutung |
|---|---:|---|
| `ticket_id` | ja | stabile Ticketkennung aus dem Quellsystem |
| `priority` | ja | `critical`, `high`, `medium` oder `low` |
| `sla_due_at` | ja | Datum im Format `YYYY-MM-DD` |

## Fehlerverhalten

Ungültige Dateien brechen vor der Persistenz ab. Fehlermeldungen nennen Spalte und Zeile, aber keine personenbezogenen Inhalte aus Freitextfeldern.

## Pflegehinweis

Wenn neue Spalten produktiv werden, zuerst Tests und Datenvertrag aktualisieren, danach Parser und Importdoku.
