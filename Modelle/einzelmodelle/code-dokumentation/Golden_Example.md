Golden Example: Entwicklerdokumentation für einen CSV-Ticketimport
Überblick

src/importer.py stellt einen CSV-Import für Support-Tickets bereit. Das Modul liest Ticketdaten aus einer CSV-Datei, validiert die Struktur und Pflichtfelder, normalisiert gültige Datensätze und übergibt sie an den Repository-Layer. Ungültige Dateien werden vor der Persistenz abgelehnt.

Diese Dokumentation beschreibt nur das sichtbare und fachlich belegte Verhalten aus dem bereitgestellten Kontext: CSV-Dateien, Pflichtfeldprüfung, verständliche Fehlermeldungen und nachvollziehbare Importprotokollierung. Nicht sichtbare Implementierungsdetails, Frameworks, Datenbanken, Queues, Performancewerte, Roadmaps oder Supportkanäle werden nicht ergänzt.

Dokumenttyp

Diese Datei ist eine kombinierte Reference und How-to-Dokumentation für Entwickler und Betreiber:

Reference für Datenvertrag, Konfiguration und Fehlerverhalten.

How-to für lokale Nutzung und Tests.

Keine Marketingbeschreibung und kein Architekturversprechen über nicht sichtbare Komponenten.

Verantwortlichkeit des Moduls

Das Importmodul ist für folgende Aufgaben zuständig:

CSV-Datei öffnen und gemäß konfiguriertem Dialekt lesen.

Kopfzeile und Pflichtspalten prüfen.

Datensätze feldweise validieren.

Valide Zeilen in eine interne Ticketstruktur überführen.

Importergebnis und Fehler so melden, dass Fachanwender Korrekturen durchführen können.

Erfolgreiche und fehlgeschlagene Importversuche protokollierbar machen.

Nicht belegt und deshalb nicht dokumentiert als vorhandenes Verhalten:

Echtzeit-Synchronisation mit dem Quellsystem.

Automatische Korrektur fachlich falscher Daten.

Verarbeitung anderer Dateiformate als CSV.

Produktive Authentifizierung, Rollenmodell oder UI-Workflow.

Konkrete Datenbanktechnologie oder Queue-Mechanik.

Nutzung

Der Import kann lokal als Modul ausgeführt werden, sofern das Projekt einen entsprechenden Einstiegspunkt bereitstellt:

Bash
python -m app.importer tickets.csv --dry-run

--dry-run steht für eine Vorprüfung ohne dauerhafte Übernahme. Falls dieser Schalter im sichtbaren Code nicht existiert, darf er nicht in die produktive README übernommen werden. In diesem Fall muss die Dokumentation an den tatsächlichen CLI-Einstieg angepasst werden.

Typischer Ablauf
CSV-Datei
  -> Parser liest Kopfzeile und Zeilen
  -> Strukturprüfung validiert Pflichtspalten
  -> Feldprüfung validiert Werte
  -> Normalisierung erzeugt Ticketdatensätze
  -> Repository-Layer persistiert gültige Daten
  -> Importprotokoll hält Ergebnis fest

Der Ablauf ist so zu verstehen, dass ungültige Dateien vor der Persistenz abbrechen. Wenn die Implementierung Teilimporte unterstützt, muss die Dokumentation explizit beschreiben, welche Zeilen übernommen und welche verworfen werden.

Datenvertrag

Der konkrete Feldkatalog muss aus Code, Tests oder fachlich freigegebenen Beispieldateien abgeleitet werden. Für den beschriebenen Ticketimport ist folgende Struktur plausibel, aber vor produktiver Übernahme gegen die Implementierung zu prüfen:

Spalte	Pflicht	Erwartung	Hinweise
ticket_id	ja	stabile Ticketkennung aus dem Quellsystem	Darf keine personenbezogenen Inhalte enthalten.
priority	ja	kontrollierter Wert wie critical, high, medium oder low	Erlaubte Werte müssen aus Code oder Tests bestätigt werden.
summary	ja	kurzer Ticketbetreff	Mindest- und Maximallänge müssen aus der Implementierung kommen.
category	offen	fachliche Kategorie	Nur dokumentieren, wenn im Code sichtbar.
sla_due_at	offen	Datum im Format YYYY-MM-DD	Nur dokumentieren, wenn im Code sichtbar.
Validierungsregeln
Regel	Erwartetes Verhalten
Datei ist nicht lesbar	Import bricht mit verständlicher Fehlermeldung ab.
Kopfzeile fehlt	Import bricht vor Persistenz ab.
Pflichtspalte fehlt	Fehlermeldung nennt die fehlende Spalte.
Pflichtwert fehlt	Fehlermeldung nennt Zeile und Feld, sofern eindeutig bestimmbar.
Wert liegt außerhalb erlaubter Werte	Fehlermeldung nennt das Feld und den ungültigen Wertebereich, ohne sensible Freitexte zu protokollieren.
CSV-Struktur ist defekt	Import bricht kontrolliert ab, ohne Stacktrace für Fachanwender.
Konfiguration

Die folgenden Konfigurationspunkte sind für einen CSV-Importer wartungsrelevant. Sie sollten aus Code oder Projektkonfiguration dokumentiert werden:

Konfiguration	Zweck	Dokumentationsregel
Trennzeichen	Unterscheidet Komma, Semikolon oder andere Dialekte	Nur den tatsächlich unterstützten Dialekt nennen.
Encoding	Zeichensatz der CSV-Datei	Keine automatische Unterstützung behaupten, wenn nicht implementiert.
Pflichtspalten	Mindeststruktur für gültige Dateien	Muss mit Tests und Datenvertrag übereinstimmen.
erlaubte Werte	Validierung von Priorität, Status oder Kategorie	Enum-Werte aus Code oder Tests übernehmen.
maximale Dateigröße	Schutz vor zu großen Dateien	Nur dokumentieren, wenn technisch umgesetzt.
Logging-Level	Detailgrad der Protokolle	Keine sensiblen Ticketfreitexte in Logs aufnehmen.
Fehlerverhalten

Ungültige Dateien werden vor der Persistenz abgelehnt. Fehlermeldungen sollen die Korrektur ermöglichen, ohne interne Details oder sensible Inhalte offenzulegen.

Erwartete Fehlertypen
Fehlertyp	Beispielhafte Ursache	Empfohlene Meldungsstruktur
invalid_csv	Datei kann nicht als CSV gelesen werden	Datei konnte nicht als CSV verarbeitet werden.
missing_required_column	Kopfzeile enthält eine Pflichtspalte nicht	Pflichtspalte fehlt: priority.
missing_required_value	Zeile enthält leeren Pflichtwert	Zeile 12: Pflichtwert für summary fehlt.
invalid_value	Feld enthält nicht erlaubten Wert	Zeile 8: priority enthält keinen erlaubten Wert.
duplicate_ticket	Ticketkennung kommt mehrfach vor	Ticketkennung kommt mehrfach vor.

Fehler für Fachanwender sollen keine Python-Tracebacks, SQL-Fehler, interne Pfade, Hostnamen, Tokens oder vollständige Freitexte aus Tickets enthalten.

Beispiele
Gültige minimale CSV-Datei
csv
ticket_id,priority,summary
TCK-1001,medium,Notebook startet nach Update nicht
TCK-1002,high,VPN-Verbindung bricht regelmäßig ab
Ungültige CSV-Datei mit fehlender Pflichtspalte
csv
ticket_id,summary
TCK-1001,Notebook startet nach Update nicht

Erwartetes Verhalten: Der Import bricht vor der Persistenz ab und meldet, dass die Pflichtspalte priority fehlt.

Ungültige CSV-Datei mit leerem Pflichtwert
csv
ticket_id,priority,summary
TCK-1001,medium,

Erwartetes Verhalten: Der Import meldet eine fehlende oder ungültige summary in der betroffenen Zeile. Ob die gesamte Datei abgelehnt wird oder nur der Datensatz fehlschlägt, hängt von der implementierten Teilimportregel ab und muss dokumentiert werden.

Lokale Tests

Mindestens folgende Tests sollten vorhanden sein, wenn das Modul produktiv genutzt wird:

Testfall	Erwartung
gültige Datei mit allen Pflichtspalten	Import oder Dry-Run ist erfolgreich.
fehlende Pflichtspalte	Import bricht vor Persistenz ab.
leerer Pflichtwert	Fehler enthält Feld und Zeile.
ungültiger Enum-Wert	Fehler nennt erlaubte Werte oder fachlichen Grund.
defekte CSV-Struktur	kontrollierter Fehler ohne ungefangenen Stacktrace.
Datei mit sensiblen Freitexten	Logs enthalten keine vollständigen sensiblen Inhalte.
wiederholte Ticketkennung	Verhalten ist definiert und getestet.
Betriebs- und Pflegehinweise

Wenn neue CSV-Spalten produktiv werden, zuerst Datenvertrag und Tests aktualisieren, danach Parser und Dokumentation.

Wenn sich erlaubte Werte ändern, müssen Validierung, Fehlermeldungen und Beispiele synchron angepasst werden.

Wenn Teilimporte eingeführt werden, muss die Dokumentation klar beschreiben, ob fehlerfreie Zeilen trotz fehlerhafter Zeilen übernommen werden.

Wenn Logging erweitert wird, muss geprüft werden, ob personenbezogene oder vertrauliche Ticketinhalte unbeabsichtigt ausgegeben werden.

Wenn ein CLI-Einstieg, API-Endpunkt oder Hintergrundjob ergänzt wird, sollte diese Dokumentation nach Dokumenttyp getrennt erweitert werden: Nutzung, Datenvertrag, Konfiguration und Fehlerverhalten.

Offene Punkte für Maintainer

Welche Datei enthält den tatsächlichen CLI- oder Job-Einstieg?

Welche Pflichtspalten sind im Code verbindlich implementiert?

Welche CSV-Dialekte und Encodings werden tatsächlich unterstützt?

Gibt es eine Alles-oder-nichts-Regel oder Teilimportlogik?

Wo werden Importprotokolle gespeichert?

Welche Fehlerklassen oder Rückgabewerte existieren im Code?

Welche Tests gelten als Abnahme für den Import?

Abnahmekriterien für diese Dokumentation

Diese Dokumentation ist wartbar, wenn folgende Bedingungen erfüllt sind:

Jede beschriebene Funktion lässt sich auf sichtbaren Code, Tests oder freigegebenen Fachkontext zurückführen.

Beispiele verletzen den beschriebenen Datenvertrag nicht.

Fehlende Informationen sind als offen markiert.

Keine produktiven Secrets, internen URLs oder personenbezogenen Beispieldaten sind enthalten.

Fehlerverhalten, Konfiguration und Pflegehinweise sind konkret genug für lokale Weiterarbeit.
