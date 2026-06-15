Golden Example: Support-Ticket-Vorbereitung
Zweck dieses Golden Examples

Dieses Beispiel ist der verbindliche Qualitäts-, Stil-, Struktur- und Formatanker für das Modell support-ticket-vorbereitung.

Das Modell erstellt aus Nutzertexten, Screenshots, Logs, Tabellen oder Chatverläufen ein eskalierbares Supportticket. Es arbeitet offline-first, trennt belegte Fakten von Annahmen und markiert offene Punkte statt fehlende Informationen zu erfinden.

Nutzeranfrage

Erstelle daraus bitte ein Supportticket für die Eskalation:

Nutzerin kann im Admin-Portal keine CSV-Datei importieren.

Beim Klick auf „Import starten“ erscheint nach ungefähr 20 Sekunden die Meldung: „Import fehlgeschlagen“.

Screenshot zeigt oben rechts eine rote Fehlermeldung mit dem Text „Import failed. Please try again later.“

Betroffen ist der Menüpunkt „Benutzerverwaltung > Import“.

Die CSV-Datei wurde laut Nutzerin vorher schon einmal erfolgreich verwendet.

Der Fehler tritt seit heute Morgen auf.

Browser: Chrome auf Windows.

Es gibt keine weiteren Logs.

Impact: Neue Benutzer können aktuell nicht per CSV angelegt werden.

Gute Antwort
Kurzfazit

Aus den bereitgestellten Informationen lässt sich ein eskalierbares Supportticket erstellen. Die Ursache ist noch nicht belegt. Das Ticket trennt daher sichtbare Fakten, Nutzerangaben, Annahmen und offene Prüfpunkte.

Supportticket
Feld	Inhalt
Titel	CSV-Import in der Benutzerverwaltung schlägt im Admin-Portal fehl
Kategorie	Admin-Portal / Benutzerverwaltung / CSV-Import
Priorität	Hoch
Prioritätsbegründung	Neue Benutzer können laut Nutzerangabe aktuell nicht per CSV angelegt werden. Der betroffene Prozess ist damit blockiert.
Status	Bereit zur technischen Analyse
Eskalationsgrund	Wiederholbarer Importfehler ohne verfügbare Logs; produktiver Arbeitsprozess ist beeinträchtigt.
Beschreibung

Im Admin-Portal schlägt der CSV-Import unter Benutzerverwaltung > Import fehl. Beim Klick auf „Import starten“ erscheint nach ungefähr 20 Sekunden eine Fehlermeldung. Der Screenshot zeigt eine rote Fehlermeldung oben rechts mit dem Text:

Import failed. Please try again later.

Laut Nutzerangabe wurde dieselbe CSV-Datei zuvor bereits erfolgreich verwendet. Der Fehler tritt seit heute Morgen auf. Weitere Logs liegen nicht vor.

Impact

Neue Benutzer können aktuell nicht per CSV angelegt werden.

Der reguläre Importprozess in der Benutzerverwaltung ist blockiert.

Ein manueller Workaround wurde nicht genannt.

Die Anzahl betroffener Nutzer, Mandanten oder Dateien ist offen.

Reproduktion

Admin-Portal öffnen.

Menüpunkt Benutzerverwaltung > Import aufrufen.

CSV-Datei auswählen.

„Import starten“ anklicken.

Ungefähr 20 Sekunden warten.

Fehlermeldung erscheint: „Import failed. Please try again later.“

Erwartetes Ergebnis

Der CSV-Import wird erfolgreich abgeschlossen und die Benutzer werden angelegt.

Tatsächliches Ergebnis

Der Import bricht mit einer roten Fehlermeldung ab. Die Benutzer werden nicht per CSV angelegt.

Umgebung
Bereich	Bekannte Information
Anwendung	Admin-Portal
Modul	Benutzerverwaltung > Import
Betriebssystem	Windows
Browser	Chrome
Dateiart	CSV
Zeitpunkt	seit heute Morgen
Logs	nicht vorhanden
Screenshot	vorhanden; zeigt rote Fehlermeldung oben rechts
Verwendete Informationen
Belegte oder direkt genannte Fakten

Betroffen ist der CSV-Import im Admin-Portal.

Betroffener Menüpunkt: Benutzerverwaltung > Import.

Fehler erscheint nach Klick auf „Import starten“.

Fehlermeldung laut Screenshot: „Import failed. Please try again later.“

Browser: Chrome.

Betriebssystem: Windows.

Es liegen keine weiteren Logs vor.

Neue Benutzer können aktuell nicht per CSV angelegt werden.

Nutzerangaben

Die CSV-Datei wurde früher bereits erfolgreich verwendet.

Der Fehler tritt seit heute Morgen auf.

Die Meldung erscheint nach ungefähr 20 Sekunden.

Annahmen

Die CSV-Datei wird im gleichen oder sehr ähnlichen Format wie beim früheren erfolgreichen Import verwendet.

Der Fehler betrifft mindestens den gemeldeten Nutzerkontext.

Die Priorität ist hoch, weil ein administrativer Kernprozess blockiert ist.

Anhänge und Referenzen
Anhang	Status	Relevanz
Screenshot der Fehlermeldung	vorhanden	Belegt UI-Fehlertext und Position der Meldung
CSV-Datei	offen	Für Reproduktion und Formatprüfung erforderlich
Browser-Konsole	offen	Hilfreich zur Prüfung von Frontend- oder Netzwerkfehlern
Backend-Logs	offen	Hilfreich zur Ursachenanalyse
HAR-Datei	offen	Hilfreich bei Timeout, API-Fehlern oder Uploadproblemen
Risiken

Ohne CSV-Datei kann nicht geprüft werden, ob Dateiinhalt, Encoding, Spaltenstruktur oder Dateigröße beteiligt sind.

Ohne Backend-Logs bleibt offen, ob der Fehler durch Validierung, Timeout, Berechtigung, Serviceausfall oder ein anderes Systemproblem verursacht wird.

Die Angabe „seit heute Morgen“ ist zeitlich relevant, aber ohne konkrete Uhrzeit und Zeitzone nicht ausreichend für eine Log-Korrelation.

Da die Datei früher funktioniert haben soll, ist eine Regression oder Änderung an Importlogik, Berechtigungen oder Infrastruktur möglich, aber nicht belegt.

Offene Fragen

Welche konkrete Uhrzeit und Zeitzone gelten für den ersten fehlgeschlagenen Importversuch?

Kann die betroffene CSV-Datei oder eine datenschutzbereinigte Variante zur Prüfung bereitgestellt werden?

Tritt der Fehler bei allen CSV-Dateien, nur bei dieser Datei oder nur bei bestimmten Admin-Nutzern auf?

Empfohlene nächste Schritte

CSV-Datei oder anonymisierte Testdatei sichern.

Zeitpunkt des Fehlers mit Backend- und API-Logs abgleichen.

Browser-Konsole und Netzwerkaufrufe beim Import prüfen.

Mit einer minimalen CSV-Datei testen, ob der Fehler dateispezifisch ist.

Prüfen, ob seit dem letzten erfolgreichen Import Änderungen an Importservice, Berechtigungen, Validierung oder Deployment vorgenommen wurden.

Qualitätscheck

Kurzbeschreibung, Impact, Reproduktion, Umgebung, Anhänge, Priorität und offene Fragen sind enthalten.

Fakten, Nutzerangaben, Annahmen, Risiken und Empfehlungen sind getrennt.

Keine Ursache wurde erfunden.

Keine nicht bereitgestellten Logs, Versionen, Systeme oder Kennzahlen wurden ergänzt.

Sensible Daten wurden nicht wiederholt oder konstruiert.

Das Ticket ist offline weiterverwendbar.
