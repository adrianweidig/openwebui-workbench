        # Beispielergebnis: Refactoring-Plan

        Dieses Goldstandard-Beispiel zeigt eine fertige Antwort des Modells `Refactoring-Unterstützung`. Es nutzt nur den sichtbaren Nutzerkontext, trennt Fakten von Annahmen und enthält keine externen Laufzeitabhängigkeiten.

        ## Ziel

`TicketImporter` soll Parsing, Validierung und Persistenz trennen, ohne das Ausgabeformat oder bestehende CLI-Optionen zu ändern.

## Nicht-Ziele

- Keine neue Datenbankabstraktion.
- Keine Änderung an CSV-Spaltennamen.
- Keine Performanceoptimierung vor Baseline-Messung.

## Invarianten

- Gleiche gültige CSV erzeugt gleiche Datensätze.
- Ungültige CSV erzeugt verständlichere, aber weiterhin nicht erfolgreiche Fehler.
- CLI-Exit-Codes bleiben stabil.

## Schritte

1. Aktuelle Tests grün ausführen und zwei negative CSV-Tests ergänzen.
2. Reine Funktion `parse_rows(text)` extrahieren.
3. Schema-Validierung vor Mapping verschieben.
4. Persistenzaufruf unverändert lassen und über Adapter testen.
5. Nach jedem Schritt Tests ausführen.

## Rollback

Jeder Schritt bleibt einzeln revertierbar; kein Datenformat wird migriert.
