Kurzfazit

Der sichtbare Importpfad ist funktional klar, koppelt aber Dateiannahme, CSV-Parsing, fachliche Validierung, Persistenz und Fehlerausgabe eng in einem synchronen Request. Das macht den Ablauf leicht verständlich, erhöht aber das Risiko für sporadische 500-Fehler bei abweichenden CSV-Dateien, erschwert gezielte Tests und begrenzt die Skalierbarkeit bei größeren Uploads.

Belastbar belegt sind drei Hotspots: späte Schema-Prüfung, uneinheitliche Fehlerbehandlung und fehlende negative Tests für fehlerhafte Eingaben. Nicht belegt sind konkrete Laufzeitgrenzen, produktive Datenmengen oder aktuelle Bibliotheksstände.

Genutzte Quellen
Quelle	Sichtbarer Inhalt	Nutzung in der Analyse
app/routes/imports.py	Upload-Endpunkt, Request-Validierung, Aufruf des Importservice	Einstiegspunkt, Fehlerpfad, HTTP-Verhalten
app/services/csv_importer.py	CSV-Lesen, Spaltenmapping, Validierung, Speichern	Datenfluss, Hotspots, Seiteneffekte
app/repositories/orders.py	upsert_order() und Transaktionsgrenze	Persistenzverhalten und Wiederholbarkeit
tests/test_csv_importer.py	Tests für erfolgreichen Import und leere Datei	Testabdeckung und fehlende Grenzfälle
Nutzerbeschreibung	sporadische 500 bei bestimmten CSV-Dateien	Hypothesenpriorisierung
Belegte Fakten
Fakt	Quelle	Auswirkung
Der Request-Handler nimmt Uploads synchron entgegen und wartet auf das Importergebnis.	app/routes/imports.py, Funktion upload_orders_csv()	Lange oder fehlerhafte Dateien blockieren den HTTP-Pfad.
Der Importer liest die CSV vollständig ein, bevor fachliche Fehler gesammelt zurückgegeben werden.	app/services/csv_importer.py, Funktion import_orders()	Speicherbedarf und Fehlerlatenz wachsen mit der Dateigröße.
Pflichtspalten werden nach dem Header-Mapping geprüft, nicht direkt gegen die Original-Kopfzeile.	app/services/csv_importer.py, Funktion map_headers()	Fehlermeldungen können interne Feldnamen statt Nutzer-Spalten zeigen.
ValueError wird im Handler in 400 übersetzt, andere Exceptions fallen in einen generischen 500-Pfad.	app/routes/imports.py, Fehlerbehandlung	Parser- und Persistenzfehler können für Nutzer ununterscheidbar erscheinen.
Die Tests decken den Erfolgsfall und eine leere Datei ab.	tests/test_csv_importer.py	Abweichende Delimiter, fehlende Pflichtspalten und ungültige Datumswerte sind nicht abgesichert.
upsert_order() schreibt pro Zeile und wird aus dem Importer heraus wiederholt aufgerufen.	app/repositories/orders.py	Teilimporte sind möglich, falls keine äußere Transaktion alle Zeilen umfasst.
Architektur und Datenfluss

HTTP-Einstieg
upload_orders_csv() nimmt Datei und Nutzerkontext entgegen. Der sichtbare Code prüft Dateiname und Content-Type nur oberflächlich. Die eigentliche inhaltliche Prüfung liegt im Service.

Parsing und Normalisierung
import_orders() decodiert die Datei, erzeugt einen CSV-Reader und normalisiert Header über map_headers(). Dadurch entsteht ein interner Datensatz mit Feldnamen wie order_id, customer_id, ordered_at und amount.

Fachliche Validierung
Einzelne Felder werden zeilenweise validiert. Fehler werden teilweise gesammelt, teilweise als Exception weitergereicht. Diese Mischung ist der wichtigste Hinweis auf sporadische 500, weil nicht jeder erwartbare Eingabefehler denselben Rückgabepfad nutzt.

Persistenz
Für jede gültige Zeile wird upsert_order() aufgerufen. Im sichtbaren Ausschnitt ist keine Batch-Grenze und keine explizite Gesamttransaktion erkennbar. Daraus folgt: Bei einem Fehler nach bereits geschriebenen Zeilen kann ein Teilzustand entstehen, sofern die Datenbankschicht nicht außerhalb des Ausschnitts rollbackt.

Antwort an den Client
Bei Erfolg gibt der Endpunkt Zähler zurück. Bei bekannten Validierungsfehlern entsteht 400. Bei unerwarteten Exceptions entsteht 500, ohne dass aus dem sichtbaren Code eine stabile Fehlerklassifikation für CSV-Varianten erkennbar ist.

Risiken und Hotspots
Hoch - Teilimporte bei später Zeilenexception

Wenn Zeile 1 bis 50 gespeichert wurden und Zeile 51 eine nicht behandelte Exception auslöst, kann der Import teilweise wirksam sein. Das ist besonders riskant, wenn Nutzer denselben Import erneut starten und upsert_order() bestehende Daten überschreibt.

Lokale Prüfung: Einen Test mit zwei gültigen Zeilen und einer ungültigen dritten Zeile ergänzen. Danach prüfen, ob keine, alle oder nur die ersten zwei Zeilen persistiert wurden. Das gewünschte Verhalten muss explizit festgelegt werden.

Hoch - Erwartbare CSV-Fehler landen im 500-Pfad

Abweichende Delimiter, kaputte Encodings, ungültige Dezimalwerte oder unerwartete Header sind Nutzereingabefehler. Sie sollten kontrolliert als 400 mit verständlicher Fehlermeldung enden. Der sichtbare generische Exception-Pfad spricht dafür, dass mindestens ein Teil dieser Fälle als Serverfehler erscheint.

Lokale Prüfung: Parametertests für fehlende Pflichtspalte, Semikolon-Delimiter, ungültiges Datum, ungültige Zahl, Bytefolge mit falschem Encoding und zusätzliche unbekannte Spalten.

Mittel - Importer mischt Parsing, Validierung und Persistenz

Die Servicefunktion entscheidet gleichzeitig über CSV-Dialekt, fachliche Regeln und Datenbankoperationen. Das erschwert isolierte Tests. Besonders Fehler in frühen Phasen lassen sich schwer prüfen, ohne Repository-Doubles zu bauen.

Lokale Prüfung: Parser- und Validierungslogik in reine Funktionen kapseln und vor einem Refactoring Charakterisierungstests für den aktuellen Rückgabevertrag schreiben.

Mittel - Content-Type ist kein belastbarer Schutz

Die sichtbare Prüfung des Uploadtyps ist nur ein Komfortfilter. Sie ersetzt keine Prüfung von Dateigröße, Encoding, Headern und Zeilenlimit. Das ist kein isoliertes Security-Finding, aber ein Robustheitsrisiko.

Lokale Prüfung: Upload einer Datei mit .csv-Namen, aber leerem oder binärem Inhalt. Erwartung: kontrollierter 400, kein Stacktrace, keine Persistenz.

Hypothesen mit Prüfpfad
Hypothese	Begründung aus sichtbarem Kontext	Lokaler Prüfpfad	Erwartete Entscheidung
Sporadische 500 entstehen durch ungültige Datums- oder Zahlenformate.	Validierung ist sichtbar, aber Fehlerklassen werden nicht einheitlich übersetzt.	Testdaten mit ordered_at=31.12.2026 und amount=12,50 ausführen.	Als 400 behandeln oder Format explizit dokumentieren.
Semikolon-separierte CSVs werden als einspaltige Dateien gelesen.	Kein sichtbarer Dialekt-Sniffing-Pfad.	Datei mit Header order_id;customer_id;amount testen.	Entweder Delimiter ablehnen oder bewusst unterstützen.
Teilimporte entstehen bei Exceptions nach ersten Schreibvorgängen.	Persistenz erfolgt zeilenweise im Importpfad.	Repository-Double wirft ab dritter Zeile Exception.	Transaktion oder Vorabvalidierung einführen.
Supportprobleme entstehen durch interne Feldnamen in Fehlermeldungen.	Header werden auf interne Namen gemappt, Pflichtprüfung erfolgt danach.	CSV mit fehlender Originalspalte prüfen.	Fehlermeldung mit Originalspalten und Zeilennummer ausgeben.
Große Dateien blockieren den Webprozess.	Vollständiges Lesen und synchroner Ablauf sind sichtbar.	Lokaler Import mit steigenden Zeilenzahlen und Speicherbeobachtung.	Limit, Streaming oder Hintergrundjob definieren.
Empfohlene nächste Schritte

Fehlervertrag festlegen
Definieren, welche Importfehler als 400 gelten und welche tatsächlich 500 bleiben. Erwartbare CSV-Probleme sollten keine Serverfehler sein.

Charakterisierungstests ergänzen
Vor Umbauten Tests für Erfolg, leere Datei, fehlende Pflichtspalte, ungültiges Datum, ungültige Zahl, falsches Encoding, falschen Delimiter und Fehler nach Teilpersistenz schreiben.

Validierung vor Persistenz ziehen
Wenn fachlich möglich, erst alle Zeilen parsen und validieren, dann speichern. Das reduziert Teilimporte und macht Fehlermeldungen konsistenter.

Transaktionsgrenze sichtbar machen
Entweder Import als atomare Transaktion ausführen oder Teilimporte bewusst dokumentieren und im Ergebnis ausweisen.

CSV-Dialekt und Limits explizit machen
Unterstützte Delimiter, Encoding, maximale Dateigröße und maximale Zeilenzahl sollten im Code geprüft und in Fehlermeldungen erkennbar sein.

Observability verbessern
Für fehlgeschlagene Importe sollten strukturierte Logs mit Import-ID, Nutzer-/Mandantenkontext in minimierter Form, Fehlerklasse und Phase entstehen. Rohzeilen, personenbezogene Daten und vollständige CSV-Inhalte sollten nicht geloggt werden.

Grenzen

Diese Analyse basiert nur auf den sichtbaren Dateien und der Nutzerbeschreibung. Ich habe keine Tests ausgeführt, keine Laufzeit gemessen und keine externen Paket- oder Sicherheitsdatenbanken geprüft. Falls Transaktionen, Uploadlimits oder Fehlernormalisierung in Middleware außerhalb des sichtbaren Ausschnitts implementiert sind, sind die entsprechenden Risiken herabzustufen, aber weiterhin mit Integrationstests abzusichern.
