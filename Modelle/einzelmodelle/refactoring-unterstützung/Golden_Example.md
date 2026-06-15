Golden Example: Refactoring-Unterstützung

Nutzerkontext: Ein bestehender CSV-Ticketimport mischt Datei-I/O, Parsing, Validierung, Mapping und Datenbankpersistenz in einer großen Funktion. Ziel ist bessere Wartbarkeit ohne Änderung des Importverhaltens. Öffentliche CLI-Optionen, CSV-Spaltennamen und Exit-Codes dürfen nicht geändert werden. Tests existieren nur für den erfolgreichen Import.

Ziel

Der CSV-Ticketimport soll in kleine, nachvollziehbare Komponenten zerlegt werden, ohne beobachtbares Verhalten zu ändern:

Datei lesen,

CSV parsen,

Pflichtfelder validieren,

Zeilen in Ticket-Objekte mappen,

Tickets persistieren,

Fehler für CLI-Nutzer ausgeben.

Das Refactoring soll die nächste Änderung an Validierungsregeln vorbereiten, aber diese Regeln noch nicht fachlich verändern.

Nicht-Ziele

Keine Änderung an CSV-Spaltennamen, Trennzeichen oder Datumsformaten.

Keine Änderung an CLI-Optionen, Exit-Codes oder Standardausgabe.

Keine neue Datenbankabstraktion und keine Schemaänderung.

Keine Performanceoptimierung ohne vorherige Messung.

Keine Zusammenlegung mit einem späteren Bugfix für fehlerhafte Quelldaten.

Keine breitflächige Formatierung außerhalb der berührten Codebereiche.

Invarianten

Eine aktuell gültige CSV erzeugt dieselben Ticket-Datensätze wie vor dem Refactoring.

Eine CSV ohne Pflichtfeld bleibt ein Fehlerfall und wird nicht persistiert.

Fehlerausgaben enthalten weiterhin genug Kontext für Nutzer, ohne sensible Inhalte auszugeben.

Persistenz wird nur aufgerufen, wenn Parsing und Validierung erfolgreich waren.

Bestehende CLI-Exit-Codes bleiben stabil.

Die öffentliche Importfunktion und bestehende Aufrufstellen bleiben kompatibel.

Risikoanalyse
Risiko	Auswirkung	Gegenmaßnahme
Parsing und Validierung werden versehentlich fachlich verändert	Gültige Dateien werden abgelehnt oder ungültige importiert	Charakterisierungstests vor Extraktion ergänzen
Persistenz wird trotz Validierungsfehler aufgerufen	Teilimporte oder inkonsistente Daten	Test mit fehlerhafter CSV und Mock/Fake für Repository
Fehlertexte ändern sich unkontrolliert	Skripte oder Support-Dokumentation brechen	Aktuelle Fehlerfälle als Snapshot oder gezielte Assertions sichern
Zu großer Umbau in einem PR	Review wird riskant und Rollback schwer	Schritte einzeln committen und nach jedem Schritt testen
Neue Hilfsfunktionen bekommen versteckte Seiteneffekte	schwer prüfbare Regressionen	reine Funktionen für Parsing, Validierung und Mapping bevorzugen
Schrittplan

Verhalten inventarisieren

Bestehende erfolgreiche Importtests ausführen.

Drei Charakterisierungstests ergänzen:

valide CSV mit zwei Tickets,

CSV ohne ticket_id,

CSV mit ungültigem Datum.

Erwartung nicht neu definieren, sondern aktuelles Verhalten absichern.

Datei-I/O vom fachlichen Import trennen

Eine schmale Funktion für „Datei lesen“ belassen.

Den bereits gelesenen CSV-Text an eine neue interne Funktion übergeben.

Keine Änderung an Encoding, Fehlermeldung oder CLI-Aufruf.

Parsing als reine Funktion extrahieren

parse_csv_rows(text) extrahieren.

Rückgabe: zeilenorientierte Rohdatenstruktur.

Noch keine Validierungslogik verschieben.

Tests aus Schritt 1 erneut ausführen.

Validierung isolieren

validate_required_fields(rows) oder äquivalente interne Funktion extrahieren.

Pflichtfelder und Fehlermeldungen exakt aus dem Bestand übernehmen.

Persistenz-Fake verwenden, um zu prüfen, dass bei Validierungsfehlern kein Schreibzugriff erfolgt.

Mapping isolieren

Mapping von CSV-Zeilen auf Ticket-Datenobjekte in eine kleine Funktion verschieben.

Datums-, Status- und Prioritätsnormalisierung nicht fachlich ändern.

Grenzfälle aus den Charakterisierungstests erneut prüfen.

Persistenzaufruf unverändert kapseln

Bestehenden Repository- oder Datenbankaufruf nur an eine klar benannte Stelle verschieben.

Keine Transaktionslogik verändern.

Keine neue Retry-Logik einführen.

Öffentliche Schnittstelle stabilisieren

Bestehende CLI-Funktion als dünnen Orchestrator belassen.

Interne Hilfsfunktionen nur dann exportieren, wenn Tests oder Projektstruktur das bereits nahelegen.

Importpfade und externe Aufrufer nicht ohne separaten Migrationsschritt ändern.

Review-Schnitt klein halten

PR-Beschreibung nach Schritten strukturieren.

Funktionale Änderungen explizit ausschließen.

Testliste und bekannte Restrisiken dokumentieren.

Tests und Validierung

Vor riskanten Strukturänderungen:

Charakterisierungstest für erfolgreichen Import mit deterministischen Testdaten.

Negativtest für fehlende Pflichtspalte ticket_id.

Negativtest für ungültiges Datumsformat.

Test, dass bei Validierungsfehlern keine Persistenz erfolgt.

Test, dass CLI-Exit-Code bei Erfolg und Fehler unverändert bleibt.

Nach jedem Schritt:

vorhandene Unit-Tests ausführen,

neue Charakterisierungstests ausführen,

betroffene CLI-Repro-Fälle lokal prüfen,

Diff auf unbeabsichtigte Formatierungswellen prüfen.

Akzeptanzkriterium:

Für identische Eingabe ist die beobachtbare Ausgabe vor und nach dem Refactoring gleich.

Nur interne Struktur, Funktionsgrenzen und Testabdeckung ändern sich.

Rollback

Jeder Schritt soll einzeln revertierbar bleiben:

Charakterisierungstests zuerst separat committen.

Extraktionen in kleinen Commits durchführen.

Keine Datenmigration und keine API-Migration in denselben PR aufnehmen.

Bei Regression den letzten Struktur-Commit revertieren, während die Charakterisierungstests erhalten bleiben.

Wenn ein Test eine bisher unbekannte fachliche Abweichung zeigt, Refactoring stoppen und Bugfix separat planen.
