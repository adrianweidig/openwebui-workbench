Golden Example: Lastenheft für einen CSV-Ticketimport
Nutzeranfrage

Aus Stichpunkten aus einem Workshop soll ein befüllbares Lastenheft entstehen. Es geht um einen CSV-Import für Support-Tickets. Die Fachabteilung möchte Ticketdaten aus einem Quellsystem importieren, Pflichtfelder prüfen, fehlerhafte Dateien verständlich zurückweisen und erfolgreiche Importe nachvollziehbar protokollieren.

Kurzfazit

Ich erstelle eine erste belastbare Lastenheft-Fassung für den beschriebenen CSV-Ticketimport. Die Anforderungen sind nach Zielen, Nicht-Zielen, Stakeholdern, funktionalen Anforderungen, Qualitätsanforderungen, Akzeptanzkriterien, Risiken und offenen Punkten getrennt.

Die Fassung nutzt nur die sichtbaren Angaben aus der Anfrage. Nicht genannte Fristen, Rollen, Dateiformate im Detail, Systemnamen, Rechtsstände, Schnittstellen oder Produktversionen werden nicht erfunden.

Verwendete Informationen
Quelle	Inhalt	Status
Nutzeranfrage	Es soll ein befüllbares Lastenheft entstehen.	Belegt
Nutzeranfrage	Fachlicher Gegenstand ist ein CSV-Import für Support-Tickets.	Belegt
Nutzeranfrage	Ticketdaten stammen aus einem Quellsystem.	Belegt
Nutzeranfrage	Pflichtfelder sollen geprüft werden.	Belegt
Nutzeranfrage	Fehlerhafte Dateien sollen verständlich zurückgewiesen werden.	Belegt
Nutzeranfrage	Erfolgreiche Importe sollen nachvollziehbar protokolliert werden.	Belegt
Nicht bereitgestellt	konkrete CSV-Spalten, Rollen, Systemnamen, Mengen, Fristen, Datenschutzklassifikation	Offen
Annahmen

Die Sprache des Lastenhefts ist Deutsch.

Der CSV-Import ist ein internes System- oder Prozessvorhaben.

Das Ergebnis ist eine fachliche Erstfassung, keine verbindliche technische Spezifikation.

Beispielhafte Feldnamen werden nur verwendet, wenn sie aus der Anfrage ableitbar sind oder als offene Datenentscheidung markiert werden.

Personenbezogene Daten werden nicht in Beispielen wiedergegeben.

1. Zielsetzung

Ziel ist ein Importprozess, mit dem Support-Tickets aus CSV-Dateien übernommen werden können. Das System soll die Datei vor der Verarbeitung prüfen, ungültige Inhalte verständlich melden und erfolgreiche Importe nachvollziehbar dokumentieren.

Hauptziele
ID	Ziel	Quelle
Z-01	CSV-Dateien mit Support-Ticketdaten importieren.	Nutzeranfrage
Z-02	Pflichtfelder vor der Verarbeitung validieren.	Nutzeranfrage
Z-03	Fehlerhafte Dateien mit verständlichen Meldungen zurückweisen.	Nutzeranfrage
Z-04	Erfolgreiche Importe nachvollziehbar protokollieren.	Nutzeranfrage
Nicht-Ziele
ID	Nicht-Ziel	Begründung
NZ-01	Echtzeit-Synchronisation mit dem Quellsystem	Es wurde nur ein CSV-Import genannt.
NZ-02	Automatische Korrektur fachlich falscher Ticketdaten	Die Anfrage nennt Validierung und Zurückweisung, nicht automatische Bereinigung.
NZ-03	Verarbeitung nicht bereitgestellter Dateiformate	Es wurde ausschließlich CSV genannt.
NZ-04	Verbindliche Datenschutz- oder Compliance-Freigabe	Dafür fehlen Prüfinstanz, Rechtsgrundlage und Datenklassifikation.
2. Stakeholder
Stakeholder	Interesse	Status
Fachabteilung Support	Ticketdaten aus einem Quellsystem übernehmen	Aus Anfrage ableitbar
Importverantwortliche Person oder Rolle	Datei hochladen, Ergebnis prüfen, Fehler korrigieren	Annahme
Entwicklungsteam	Importlogik, Validierung und Protokollierung umsetzen	Annahme
Betrieb oder Administration	Fehleranalyse und Nachvollziehbarkeit sicherstellen	Annahme
Datenschutz oder Informationssicherheit	Umgang mit Ticketinhalten prüfen	Prüfflichtig
3. Systemkontext

Der Importprozess nimmt CSV-Dateien entgegen, prüft Struktur und Inhalte und erzeugt ein Ergebnis: erfolgreicher Import mit Protokoll oder Ablehnung mit Fehlerdetails. Das Quellsystem wird in der Anfrage nicht benannt und bleibt deshalb offen.

Quellsystem -> CSV-Datei -> Importprüfung -> Ticketübernahme oder Fehlerbericht -> Importprotokoll
4. Funktionale Anforderungen
ID	Anforderung	Priorität	Akzeptanzkriterium	Quelle	Risiko	Offener Klärungspunkt
FA-01	Das System muss CSV-Dateien als Eingabe für Support-Tickets akzeptieren.	Muss	Eine CSV-Datei kann zur Importprüfung eingereicht werden.	Nutzeranfrage	Falscher CSV-Dialekt kann zu Fehlimporten führen.	Welche Trennzeichen, Kodierung und Kopfzeilen gelten?
FA-02	Das System muss vor der Übernahme prüfen, ob alle Pflichtfelder vorhanden sind.	Muss	Fehlt eine Pflichtspalte, wird die Datei nicht importiert und die fehlende Spalte wird benannt.	Nutzeranfrage	Unvollständige Tickets können operative Folgefehler erzeugen.	Welche Felder sind fachlich verpflichtend?
FA-03	Das System muss fehlerhafte Dateien verständlich zurückweisen.	Muss	Bei ungültiger Datei erhält die importierende Rolle eine Meldung mit Ursache, betroffener Zeile oder Spalte, soweit eindeutig bestimmbar.	Nutzeranfrage	Unklare Fehlermeldungen verursachen Supportaufwand.	Welche Detailtiefe ist fachlich und datenschutzseitig zulässig?
FA-04	Das System muss erfolgreiche Importe protokollieren.	Muss	Nach erfolgreichem Import liegt ein Protokolleintrag mit Zeitpunkt, Ergebnisstatus und Anzahl verarbeiteter Datensätze vor.	Nutzeranfrage	Fehlende Nachvollziehbarkeit erschwert Audits und Fehleranalyse.	Welche Protokollfelder sind erlaubt und erforderlich?
FA-05	Das System soll ungültige Datensätze erkennen, bevor Daten dauerhaft übernommen werden.	Soll	Bei Validierungsfehlern werden keine teilweise geprüften Tickets übernommen, sofern keine Teilimportregel beschlossen ist.	Annahme aus Validierungsziel	Teilimporte können inkonsistente Zustände erzeugen.	Soll Teilimport erlaubt sein oder gilt Alles-oder-nichts?
FA-06	Das System soll eine Importzusammenfassung bereitstellen.	Soll	Nach Verarbeitung ist ersichtlich, ob der Import erfolgreich war und wie viele Datensätze betroffen sind.	Annahme aus Protokollierungsziel	Ohne Zusammenfassung ist manuelle Kontrolle erschwert.	Welche Kennzahlen soll die Zusammenfassung enthalten?
5. Qualitätsanforderungen
ID	Qualitätsanforderung	Priorität	Akzeptanzkriterium	Quelle	Risiko	Offener Klärungspunkt
QA-01	Fehlermeldungen müssen für Fachanwender verständlich sein.	Muss	Meldungen benennen Ursache und Korrekturansatz ohne interne Stacktraces.	Nutzeranfrage	Fachabteilung kann Fehler nicht selbst beheben.	Gibt es ein gewünschtes Wording oder UI-Konzept?
QA-02	Protokolle dürfen keine unnötigen sensiblen Freitextinhalte enthalten.	Muss	Protokolle enthalten technische und fachliche Mindestinformationen, aber keine vollständigen Ticketbeschreibungen, sofern nicht freigegeben.	Sicherheitsannahme	Datenschutz- oder Geheimhaltungsrisiko.	Welche Datenklassifikation haben Ticketinhalte?
QA-03	Die Validierung muss deterministisch sein.	Muss	Dieselbe Datei führt bei unveränderter Konfiguration zum selben Prüfergebnis.	Fachliche Ableitung	Nicht reproduzierbare Ergebnisse erschweren Fehleranalyse.	Welche Konfiguration beeinflusst Validierung?
QA-04	Der Import muss lokal nachvollziehbar getestet werden können.	Soll	Es gibt positive und negative Testfälle für Pflichtfelder, ungültige Werte und fehlerhafte CSV-Struktur.	Qualitätsanforderung	Regressionsrisiko bei Änderungen.	Welche Testumgebung ist vorgesehen?
6. Datenanforderungen

Die konkreten Spalten wurden nicht bereitgestellt. Deshalb wird nur die Struktur der Datenentscheidung festgelegt.

Datenbereich	Beschreibung	Status
Ticketkennung	Stabile Kennung aus dem Quellsystem oder Importkontext	Offen
Priorität	Fachliche Dringlichkeit des Tickets	Offen
Kategorie	Einordnung des Tickets	Offen
Zusammenfassung	Kurzer Ticketbetreff oder Problemtitel	Offen
Beschreibung	Optionaler Freitext mit potenziell sensiblen Inhalten	Prüfflichtig
Erstellzeitpunkt	Zeitpunkt aus Quellsystem oder Importdatei	Offen
7. Fehler- und Ausnahmeverhalten
Fehlerfall	Erwartetes Verhalten	Akzeptanzkriterium
Datei ist keine lesbare CSV-Datei	Import wird abgelehnt.	Fehlermeldung nennt, dass die Datei nicht als CSV verarbeitet werden konnte.
Pflichtspalte fehlt	Import wird abgelehnt.	Meldung nennt die fehlende Spalte.
Pflichtwert fehlt in einer Zeile	Import wird abgelehnt oder Datensatz wird gemäß Teilimportregel übersprungen.	Verhalten ist dokumentiert und konsistent.
Ungültiger Wert	Datei oder Datensatz wird zurückgewiesen.	Meldung nennt Feld und Grund, soweit eindeutig.
Unerwarteter technischer Fehler	Import wird nicht als erfolgreich markiert.	Protokoll enthält Fehlerstatus ohne sensible technische Details.
8. Akzeptanzkriterien auf Gesamtvorhabenebene

Das Vorhaben gilt fachlich als abnahmefähig, wenn folgende Kriterien erfüllt sind:

Eine gültige CSV-Datei mit den vereinbarten Pflichtfeldern kann importiert werden.

Eine Datei mit fehlender Pflichtspalte wird vor Datenübernahme abgelehnt.

Eine Datei mit ungültigen Pflichtwerten erzeugt verständliche Fehlermeldungen.

Erfolgreiche und fehlgeschlagene Importversuche sind nachvollziehbar protokolliert.

Die vereinbarte Teilimportregel ist dokumentiert und getestet.

Es werden keine produktiven Secrets oder unnötigen personenbezogenen Daten in Beispielen, Logs oder Testdaten verwendet.

9. Risiken
Risiko	Auswirkung	Gegenmaßnahme
Pflichtfelder sind nicht abgestimmt	Fehlende oder falsche Validierung	Feldkatalog fachlich freigeben
CSV-Dialekt ist unklar	Dateien werden falsch gelesen	Trennzeichen, Kodierung, Quote-Regeln festlegen
Teilimportregel fehlt	Unklare Datenzustände	Alles-oder-nichts oder Teilimport bewusst entscheiden
Ticketinhalte enthalten sensible Daten	Datenschutzrisiko	Logging minimieren und Freitexte schützen
Quellsystem ist nicht beschrieben	Fehlerhafte fachliche Interpretation	Systemkontext ergänzen
10. Offene Punkte

Welche CSV-Spalten sind Pflichtfelder?

Welche Wertebereiche gelten für Priorität, Kategorie und Status?

Soll der Import vollständig abbrechen, wenn ein einzelner Datensatz ungültig ist?

Welche Rollen dürfen Importe ausführen und Protokolle sehen?

Welche Protokollinformationen sind fachlich erforderlich und datenschutzrechtlich zulässig?

Welche maximale Dateigröße oder Datensatzanzahl muss unterstützt werden?

Gibt es bereits Beispiel-CSV-Dateien oder Fehlermeldungen aus dem Bestand?

11. Nächster Schritt

Als nächstes sollte ein fachlich freigegebener CSV-Feldkatalog erstellt werden. Danach können funktionale Anforderungen, Validierungsregeln und Testfälle präzise finalisiert werden.
