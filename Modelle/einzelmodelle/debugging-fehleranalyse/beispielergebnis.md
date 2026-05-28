        # Beispielergebnis: Debugging-Runbook

        Dieses Goldstandard-Beispiel zeigt eine fertige Antwort des Modells `Debugging und Fehleranalyse`. Es nutzt nur den sichtbaren Nutzerkontext, trennt Fakten von Annahmen und enthält keine externen Laufzeitabhängigkeiten.

        ## Symptom

OpenWebUI zeigt nach dem Upload einer CSV `500 Internal Server Error`; im Log steht `KeyError: 'ticket_id'`.

## Priorisierte Hypothesen

| Priorität | Hypothese | Prüfung | Erwartung |
|---|---|---|---|
| P1 | CSV-Kopfzeile enthält `ticketId` statt `ticket_id` | Kopfzeile ausgeben | Abweichender Spaltenname sichtbar |
| P2 | Importpfad nutzt altes Mapping | Commit/Diff prüfen | Mapping kennt nur ältere Feldnamen |
| P3 | Datei wurde mit Semikolon getrennt | Dialekt prüfen | Parser sieht eine einzige Spalte |

## Nächster lokaler Check

```bash
python - <<'PY'
import csv
from pathlib import Path
path = Path("upload.csv")
with path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.reader(handle)
    print(next(reader))
PY
```

## Fix-Richtung

Vor dem Datenbankmapping eine klare Schema-Validierung einbauen und erlaubte Aliasnamen explizit dokumentieren.
