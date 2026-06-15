Findings
P1 - Autorisierung wird nach dem Datenzugriff geprüft

Datei: app/api/reports.py, Zeile 47

Der Handler lädt den Report über ReportRepository.get(report_id) bereits vor der Mandanten- und Rollenprüfung. Wenn get() mandantenübergreifend sucht, kann ein angemeldeter Nutzer über eine fremde report_id unterscheiden, ob ein Report existiert: Bei existierendem fremdem Report entsteht später 403, bei unbekannter ID 404. Das ist eine vermeidbare Informationspreisgabe und kann außerdem unbeabsichtigte Seiteneffekte auslösen, falls get() Zugriffszeitpunkte, Cache-Einträge oder Audit-Daten aktualisiert.

Korrektur: Die Repository-Abfrage sollte den Autorisierungskontext einbeziehen, zum Beispiel get_for_tenant(report_id, current_user.tenant_id), und erst danach rollenbasierte Freigaben prüfen. Für nicht zugängliche oder nicht vorhandene Reports sollte der Endpunkt nach außen einheitlich antworten, sofern das Produkt keine bewusste Unterscheidung verlangt.

Testlücke: Es fehlt ein negativer Integrationstest mit zwei Mandanten:

Report gehört Mandant A.

Nutzer aus Mandant B ruft dieselbe report_id auf.

Erwartung: keine Reportdaten, keine unterscheidbare Existenzantwort, kein Exportjob und kein Audit-Event mit fremder Report-ID.

P1 - CSV-Export kann Formeln in Tabellenprogrammen ausführen

Datei: app/services/report_export.py, Zeile 88

Die neuen CSV-Zeilen schreiben nutzerkontrollierte Felder wie customer_name, comment und external_reference unverändert in den Export. Beginnen diese Werte mit =, +, -, @, Tab oder Carriage Return, interpretieren gängige Tabellenprogramme sie als Formel oder Steuerinhalt. Der Export ist damit für interne Analysten riskant, sobald sie die Datei lokal öffnen.

Korrektur: Vor dem Schreiben in CSV müssen alle Textfelder, die aus Nutzer- oder Drittsystemdaten stammen, neutralisiert werden. Üblich ist eine zentrale Escape-Funktion im Exportpfad, die gefährliche Präfixe erkennt und den Wert als Text erzwingt. Diese Logik sollte nur auf CSV-/Spreadsheet-Ausgaben wirken, nicht auf die gespeicherten Rohdaten.

Testlücke: Es fehlt ein Parametertest für Werte mit Präfixen =, +, -, @, \t und \r. Der Test sollte prüfen, dass die exportierte Zelle nicht mehr als Formel interpretierbar ist und normale Werte unverändert bleiben.

P2 - Fehlerbehandlung verschluckt Ursache und erschwert Betrieb

Datei: app/api/reports.py, Zeile 73

Der neue except Exception-Block gibt immer {"error": "export_failed"} mit Status 500 zurück und loggt nur die Report-ID. Dadurch gehen Fehlerklasse, Korrelations-ID und auslösender Verarbeitungsschritt verloren. Für Nutzer ist eine generische Fehlermeldung sinnvoll; intern fehlt aber die Diagnosebasis für wiederkehrende Exportfehler.

Korrektur: Der Handler sollte erwartete Fehler getrennt behandeln, zum Beispiel Validierungsfehler als 400 und fehlende Berechtigung als 403 oder einheitliches 404. Unerwartete Fehler sollten mit logger.exception(...) und Korrelations-ID geloggt werden. Sensible Reportinhalte dürfen dabei nicht in Logs landen.

Testlücke: Es fehlt ein Test, der einen Repository- oder Storage-Fehler simuliert und prüft, dass der Endpunkt stabil antwortet und der Fehlerpfad ein strukturiertes Logereignis erzeugt. Ohne Log-Capture kann mindestens der HTTP-Status und die Antwortform abgesichert werden.

P2 - Export baut komplette Datei im Speicher auf

Datei: app/services/report_export.py, Zeile 64

Der Export sammelt alle CSV-Zeilen in einer Liste und fügt sie anschließend zu einem String zusammen. Für kleine Reports ist das unproblematisch, bei großen Reports wächst der Speicherbedarf jedoch mit der vollständigen Exportgröße plus Zwischenstrukturen. Der Diff enthält keine Begrenzung der Reportgröße und keinen Streamingpfad.

Korrektur: Falls große Reports fachlich möglich sind, sollte der Export zeilenweise streamen oder in einen temporären Writer schreiben. Wenn große Exporte nicht erlaubt sind, braucht der Endpunkt eine explizite Größenbegrenzung mit verständlicher Fehlermeldung.

Testlücke: Es fehlt ein Grenzfalltest für einen Report oberhalb der erwarteten Maximalgröße. Der Test sollte nicht primär Performance messen, sondern das definierte Verhalten absichern: Stream, kontrollierter Abbruch oder klare Limitantwort.

Zusammenfassung

Der Patch ist fachlich nachvollziehbar, aber in der sichtbaren Form nicht freigabereif. Blockierend sind vor allem der Datenzugriff vor der Autorisierung und die ungesicherten CSV-Zellen. Beide Punkte betreffen reale Schutzgrenzen: Mandantentrennung und sichere Weiterverarbeitung exportierter Daten.

Die übrigen Punkte sind relevante Betriebs- und Skalierungsrisiken. Sie müssen nicht zwingend denselben Patch blockieren, sollten aber vor produktivem Rollout entweder behoben oder bewusst als akzeptiertes Restrisiko dokumentiert werden.

Testlücken

Negativer Mandantentest für fremde report_id.

CSV-Escape-Tests für formelartige Zellwerte und normale Kontrollwerte.

Fehlerpfadtest für Repository-, Storage- oder Serialisierungsfehler.

Grenzfalltest für sehr große Reports oder definierte Exportlimits.

Regressionstest, dass berechtigte Nutzer weiterhin Reports des eigenen Mandanten exportieren können.

Offene Fragen

Ist eine einheitliche Außenantwort für „nicht vorhanden“ und „nicht berechtigt“ fachlich gewünscht?

Gibt es ein definiertes maximales Reportvolumen pro Export?

Werden CSV-Dateien primär in Tabellenprogrammen geöffnet oder maschinell weiterverarbeitet?
