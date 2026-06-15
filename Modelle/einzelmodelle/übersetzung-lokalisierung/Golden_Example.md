Golden Example: Übersetzung und Lokalisierung
Zweck dieses Golden Examples

Dieses Beispiel ist der verbindliche Qualitäts-, Stil-, Struktur- und Formatanker für das Modell übersetzung-lokalisierung.

Das Modell überträgt Texte, UI-Kopien, Dokumente und Lokalisierungsfragen zielgruppen- und kontextgerecht. Es bewahrt Bedeutung, Platzhalter, Terminologie, Tonalität, Locale-Regeln und Längenrisiken. Es arbeitet offline-first und markiert offene Punkte statt fehlende Informationen zu erfinden.

Nutzeranfrage

Bitte lokalisiere diese UI-Texte von Deutsch nach Englisch für eine B2B-Web-App. Tonalität: klar, professionell, nicht zu locker. Platzhalter müssen exakt erhalten bleiben.

Key	Deutsch	Kontext
user.import.title	Benutzer importieren	Seitentitel im Admin-Bereich
user.import.description	Laden Sie eine CSV-Datei hoch, um mehrere Benutzer gleichzeitig anzulegen.	Hilfetext unter dem Seitentitel
user.import.button	Import starten	Primärer Button
user.import.progress	{count} Benutzer werden importiert.	Statusmeldung während des Imports
user.import.success	Import abgeschlossen. {count} Benutzer wurden angelegt.	Erfolgsmeldung
user.import.error	Import fehlgeschlagen. Bitte versuchen Sie es später erneut.	Fehlermeldung
user.import.cancel	Abbrechen	Sekundärer Button
Gute Antwort
Kurzfazit

Die Texte können auf Basis der bereitgestellten Informationen direkt lokalisiert werden. Zielvariante ist professionelles Englisch für eine B2B-Web-App. Die Platzhalter bleiben unverändert. Nicht angegebene Locale-Details wie US- oder UK-Englisch werden nicht geraten.

Annahmen

Zielsprache: Englisch.

Zielkontext: B2B-Web-App im Admin-Bereich.

Tonalität: klar, professionell, nicht zu locker.

Platzhalter wie {count} müssen exakt erhalten bleiben.

Es liegt kein Screenshot vor; Layout- und Längenrisiken werden daher textbasiert bewertet.

Lokalisierte UI-Texte
Key	Deutsch	Englisch	QA-Hinweis
user.import.title	Benutzer importieren	Import users	Als Seitentitel kurz und handlungsorientiert.
user.import.description	Laden Sie eine CSV-Datei hoch, um mehrere Benutzer gleichzeitig anzulegen.	Upload a CSV file to create multiple users at once.	Bedeutung erhalten; „at once“ ist knapp und UI-tauglich.
user.import.button	Import starten	Start import	Für primären Button klar und direkt.
user.import.progress	{count} Benutzer werden importiert.	{count} users are being imported.	Platzhalter exakt erhalten; Pluralisierung für {count} = 1 ist prüfpflichtig.
user.import.success	Import abgeschlossen. {count} Benutzer wurden angelegt.	Import complete. {count} users have been created.	Platzhalter exakt erhalten; Pluralisierung für {count} = 1 ist prüfpflichtig.
user.import.error	Import fehlgeschlagen. Bitte versuchen Sie es später erneut.	Import failed. Please try again later.	Professionell und neutral; keine Ursache ergänzt.
user.import.cancel	Abbrechen	Cancel	Standard-UI-Label für sekundären Button.
Terminologie
Deutsch	Englisch	Entscheidung
Benutzer	users	Standardbegriff für B2B-Web-App; nicht „members“, da kein Membership-Kontext genannt wurde.
importieren	import	Als UI-Aktion beibehalten.
CSV-Datei	CSV file	Fachbegriff bleibt erhalten.
anlegen	create	Für Nutzerverwaltung fachlich passend.
fehlgeschlagen	failed	Neutraler Fehlerstatus ohne Schuldzuweisung.
Platzhalter- und Formatprüfung
Element	Ergebnis
{count}	In allen Zieltexten exakt erhalten.
Key-Namen	Unverändert übernommen.
Satzzeichen	Zielsprachlich angepasst.
Höflichkeitsform	Im Englischen neutral-professionell übertragen.
Nicht bereitgestellte Variablen	Keine ergänzt.
Längenrisiken
Key	Einschätzung	Empfehlung
user.import.button	Niedrig	„Start import“ ist kurz genug für einen Button.
user.import.progress	Mittel	Bei hohen Zahlen und schmalen Statusflächen kann der Text umbrechen.
user.import.success	Mittel	Erfolgsmeldung ist länger als der deutsche Ausgangstext; in Toasts oder schmalen Bannern prüfen.
user.import.description	Mittel	Hilfetext ist verständlich, sollte aber im Layout geprüft werden.
Offene Punkte

Die genaue Zielvariante ist offen: US-Englisch, UK-Englisch oder neutrales Englisch.

Für {count} = 1 ist eine Singularform nötig, falls das Lokalisierungssystem keine Pluralregeln unterstützt.

Ohne Screenshot ist nicht prüfbar, ob Buttonbreiten, Toasts oder mobile Breakpoints betroffen sind.

Empfohlene nächste Schritte

Ziel-Locale festlegen.

Prüfen, ob das i18n-System Pluralformen unterstützt.

Die Texte in der UI testen, besonders Fortschritts- und Erfolgsmeldungen.

Bei Screenshot oder Layoutvorgaben die Längenrisiken visuell nachprüfen.

Qualitätscheck

Zielvariante, Tonalität, Platzhalter, Längenrisiken und QA-Hinweise sind enthalten.

Bedeutung und Terminologie wurden konsistent übertragen.

Platzhalter und Keys wurden nicht verändert.

Keine nicht bereitgestellten Produktdetails, Versionen oder Quellen wurden ergänzt.

Offene Locale- und Pluralisierungsfragen sind markiert.

Das Ergebnis ist offline weiterverwendbar.
