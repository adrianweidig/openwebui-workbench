        # Beispielergebnis: Testfallkatalog

        Dieses Goldstandard-Beispiel zeigt eine fertige Antwort des Modells `Testfall-Generierung`. Es nutzt nur den sichtbaren Nutzerkontext, trennt Fakten von Annahmen und enthält keine externen Laufzeitabhängigkeiten.

        ## Testfälle für CSV-Ticketimport

| ID | Risiko | Vorbedingung | Schritte | Erwartetes Ergebnis | Priorität |
|---|---|---|---|---|---|
| T-001 | gültige Daten werden abgelehnt | valide CSV liegt vor | Dry-Run starten | 4 Tickets validiert, Exit-Code 0 | hoch |
| T-002 | fehlende Pflichtspalte erzeugt Folgefehler | CSV ohne `ticket_id` | Dry-Run starten | klare Fehlermeldung vor Persistenz | hoch |
| T-003 | falsches Datumsformat wird akzeptiert | `sla_due_at=28.05.2026` | Dry-Run starten | Validierungsfehler mit Zeile und Feld | mittel |
| T-004 | geschlossene Tickets werden eskaliert | CSV mit `status=closed` | SLA-Report erzeugen | geschlossenes Ticket nicht in offener SLA-Liste | mittel |

## Automatisierbarer Pytest-Kern

```python
import pytest

@pytest.mark.parametrize("priority", ["critical", "high", "medium", "low"])
def test_allowed_priorities_are_accepted(priority):
    assert normalize_priority(priority, row_number=2) == priority
```
