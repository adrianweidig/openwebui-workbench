        # Beispielergebnis: Code-Review-Findingliste

        Dieses Goldstandard-Beispiel zeigt eine fertige Antwort des Modells `Code-Review`. Es nutzt nur den sichtbaren Nutzerkontext, trennt Fakten von Annahmen und enthält keine externen Laufzeitabhängigkeiten.

        ## Findings

### P1 - Zugriffskontrolle wird clientseitig entschieden

Datei: `app/routes/admin.py`, Zeile 42

Der neue Endpunkt verlässt sich auf `request.json["isAdmin"]`. Diese Angabe kommt vom Client und darf nicht über Adminrechte entscheiden. Prüfe die Berechtigung serverseitig aus Session, Token-Claims oder Rollenmodell und ergänze einen negativen Test.

Reproduktion: Request mit `{"isAdmin": true}` gegen den Endpunkt senden, obwohl der angemeldete Nutzer keine Adminrolle hat.

Testlücke: Es fehlt ein Test für Nutzer ohne Adminrolle.

### P2 - Fehlerpfad verliert Diagnosekontext

Datei: `app/services/export.py`, Zeile 88

Der generische `except Exception` gibt nur `Export fehlgeschlagen` zurück. Damit fehlen Fehlerklasse und Korrelations-ID im Log. Nutzerantworten dürfen knapp bleiben, aber interne Logs müssen Ursache und Ticket-ID enthalten.

## Zusammenfassung

Der Patch ist fachlich nachvollziehbar, blockiert aber wegen der serverseitigen Autorisierung. Nach Fix und negativem Test ist ein erneutes Review sinnvoll.
