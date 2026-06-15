Golden Example: Compliance- und Richtlinienprüfung
Nutzeranfrage

Prüfe den folgenden Prozess gegen die interne Richtlinie. Erstelle einen Prüfbericht mit Abweichungsmatrix.

Interne Richtlinie: Zugriff auf Fachanwendungen

Fachanwendungen dürfen nur über persönliche Benutzerkonten genutzt werden.

Rollen mit Zahlungsfreigabe müssen quartalsweise überprüft werden.

Neue Berechtigungen benötigen eine dokumentierte Freigabe durch die fachliche Führungskraft.

Administratorrechte dürfen nicht für Tagesgeschäft genutzt werden.

Nachweise müssen Datum, Prüfer, betroffene Anwendung und Ergebnis enthalten.

Bereitgestellte Nachweise

Auszug Berechtigungsliste vom 2026-05-31:

Anwendung: Rechnungssystem

Benutzerkonten: 18 persönliche Konten, 1 Sammelkonto finance_shared

Rolle Zahlungsfreigabe: 6 Konten

Administratorrolle: 2 Konten

Ticket REQ-1842 vom 2026-05-14:

beantragt: Rolle Zahlungsfreigabe für ein persönliches Konto

genehmigt durch fachliche Führungskraft

umgesetzt am 2026-05-15

Review-Protokoll vom 2026-03-28:

Anwendung: Rechnungssystem

Prüfer: Teamleitung Finanzen

Ergebnis: 17 Konten geprüft, keine Änderung

Sammelkonto nicht erwähnt

Administratorrollen nicht einzeln bewertet

Prozessnotiz:

Administratoren nutzen Admin-Konten gelegentlich zur Korrektur fehlerhafter Rechnungsstammdaten.

Gute Antwort
Prüfbericht: Zugriffskontrolle Rechnungssystem
Kurzfazit

Der Prozess ist teilweise richtlinienkonform. Belegt sind persönliche Konten, eine dokumentierte Freigabe für eine neue Zahlungsfreigabe und ein Rollenreview mit Datum, Anwendung, Prüfer und Ergebnis. Abweichungen bestehen beim Sammelkonto, bei der unvollständigen quartalsweisen Prüfung der Zahlungsfreigaben sowie bei der Nutzung von Administratorrechten im Tagesgeschäft.

Die Bewertung basiert ausschließlich auf den bereitgestellten Richtlinienauszügen und Nachweisen. Nicht sichtbare Systemlogs, vollständige Berechtigungsexporte, frühere Reviews oder organisatorische Sonderfreigaben werden nicht unterstellt.

Verwendete Informationen
Quelle	Sichtbarer Inhalt	Bewertung der Nachweisqualität
Interne Richtlinie „Zugriff auf Fachanwendungen“	Anforderungen an persönliche Konten, quartalsweise Rollenreviews, Freigaben, Administratornutzung und Nachweisinhalte	Geeignet als Prüfkriterium
Berechtigungsliste vom 2026-05-31	18 persönliche Konten, 1 Sammelkonto, 6 Konten mit Zahlungsfreigabe, 2 Administratorrollen	Geeignet für Bestandsprüfung; keine Nutzungsdaten enthalten
Ticket REQ-1842 vom 2026-05-14	Zahlungsfreigabe beantragt, durch fachliche Führungskraft genehmigt, am 2026-05-15 umgesetzt	Geeignet als Freigabenachweis für diesen Einzelfall
Review-Protokoll vom 2026-03-28	Rechnungssystem geprüft, Prüfer genannt, 17 Konten geprüft, keine Änderung; Sammelkonto und Adminrollen nicht vollständig bewertet	Teilweise geeignet; Umfangslücke
Prozessnotiz	Admin-Konten werden gelegentlich zur Korrektur von Rechnungsstammdaten genutzt	Geeignet als Hinweis auf Prozessabweichung; keine Häufigkeit belegt
Bewertungsmaßstab
Prüffeld	Richtlinienanforderung	Prüfstatus
Kontenmodell	Nutzung nur über persönliche Benutzerkonten	Abweichung festgestellt
Zahlungsfreigaben	quartalsweise Rollenüberprüfung	teilweise belegt
Neuanlage von Berechtigungen	dokumentierte Freigabe durch fachliche Führungskraft	für REQ-1842 belegt
Administratorrechte	nicht für Tagesgeschäft nutzen	Abweichung festgestellt
Nachweisinhalt	Datum, Prüfer, Anwendung und Ergebnis	teilweise erfüllt
Abweichungsmatrix
ID	Prüffeld	Feststellung	Quelle	Risiko	Empfehlung	Verantwortlichkeit	Nachweisstatus
A-01	Persönliche Benutzerkonten	In der Berechtigungsliste ist neben 18 persönlichen Konten ein Sammelkonto finance_shared enthalten. Die Richtlinie erlaubt Fachanwendungsnutzung nur über persönliche Benutzerkonten.	Berechtigungsliste vom 2026-05-31; Richtlinie „Fachanwendungen dürfen nur über persönliche Benutzerkonten genutzt werden“	Handlungen können nicht eindeutig einer Person zugeordnet werden; Verantwortlichkeit und Nachvollziehbarkeit sind eingeschränkt.	Sammelkonto deaktivieren oder technisch so absichern, dass keine interaktive Fachanwendungsnutzung möglich ist. Falls ein technischer Zweck besteht, muss dieser dokumentiert und getrennt von persönlicher Nutzung kontrolliert werden.	Fachverantwortung Finanzen und Anwendungsadministration	Abweichung belegt
A-02	Rollenreview Zahlungsfreigabe	Die Richtlinie verlangt quartalsweise Überprüfung von Rollen mit Zahlungsfreigabe. Das Review-Protokoll nennt 17 geprüfte Konten, während die Berechtigungsliste 18 persönliche Konten plus 1 Sammelkonto ausweist. Die 6 Konten mit Zahlungsfreigabe werden nicht einzeln im Review-Ergebnis ausgewiesen.	Review-Protokoll vom 2026-03-28; Berechtigungsliste vom 2026-05-31	Veraltete oder nicht mehr erforderliche Zahlungsfreigaben können bestehen bleiben. Das Vier-Augen- oder Freigabeprinzip kann geschwächt werden.	Review-Protokoll künftig rollenbasiert führen: alle Konten mit Zahlungsfreigabe einzeln aufführen, Entscheidung dokumentieren und Abweichungen mit Maßnahme versehen.	Teamleitung Finanzen	Teilweise belegt; Umfang offen
A-03	Administratorrechte im Tagesgeschäft	Die Prozessnotiz beschreibt, dass Administratoren Admin-Konten gelegentlich zur Korrektur fehlerhafter Rechnungsstammdaten nutzen. Die Richtlinie untersagt die Nutzung von Administratorrechten für Tagesgeschäft.	Prozessnotiz; Richtlinie „Administratorrechte dürfen nicht für Tagesgeschäft genutzt werden“	Erhöhtes Risiko unbeabsichtigter oder nicht genehmigter Änderungen; erschwerte Trennung zwischen Betrieb, Korrektur und Administration.	Korrekturen über persönliche Standardkonten mit geeigneter Fachrolle durchführen. Admin-Konten nur für administrative Tätigkeiten verwenden. Notfälle separat dokumentieren und nachträglich prüfen.	Anwendungsadministration und Prozessverantwortung Rechnungsstammdaten	Abweichung belegt
A-04	Vollständigkeit des Adminrollen-Nachweises	Die Berechtigungsliste nennt 2 Administratorrollen. Das Review-Protokoll bewertet Administratorrollen nicht einzeln.	Berechtigungsliste vom 2026-05-31; Review-Protokoll vom 2026-03-28	Überprivilegierte Konten bleiben möglicherweise unerkannt oder unbestätigt.	Administratorrollen in einem separaten privilegierten Rollenreview prüfen: Inhaber, Zweck, Genehmigung, letzte Nutzung und Bestätigung dokumentieren.	IT-Verantwortung und fachliche Systemverantwortung	Nachweis unvollständig
A-05	Freigabe neuer Zahlungsfreigabe	Für REQ-1842 ist die Beantragung, Genehmigung durch die fachliche Führungskraft und Umsetzung dokumentiert.	Ticket REQ-1842 vom 2026-05-14	Kein Abweichungsrisiko für diesen Einzelfall erkennbar. Restrisiko: keine Aussage zu anderen Berechtigungsänderungen.	Ticket als geeigneten Nachweis akzeptieren. Für die Gesamtprüfung eine Stichprobe weiterer Berechtigungsänderungen ergänzen, falls der Prüfauftrag Vollständigkeit verlangt.	Fachliche Führungskraft und Berechtigungsadministration	Für Einzelfall belegt
Fakten

Es gibt ein Sammelkonto finance_shared.

Es gibt 6 Konten mit Zahlungsfreigabe.

Es gibt 2 Konten mit Administratorrolle.

Für REQ-1842 liegt eine dokumentierte Führungskraftfreigabe vor.

Das Review vom 2026-03-28 enthält Datum, Anwendung, Prüfer und Ergebnis.

Das Review nennt 17 geprüfte Konten und erwähnt das Sammelkonto nicht.

Administratoren nutzen Admin-Konten laut Prozessnotiz gelegentlich für Korrekturen an Rechnungsstammdaten.

Annahmen

Die bereitgestellten Nachweise sind die vollständige Grundlage für diese erste Prüfung.

Die Berechtigungsliste vom 2026-05-31 ist der maßgebliche aktuelle Bestand.

Das Review vom 2026-03-28 soll das quartalsweise Review für das erste Quartal 2026 darstellen.

Die Prozessnotiz beschreibt einen tatsächlich praktizierten Ablauf und nicht nur einen historischen Ausnahmefall.

Offene Punkte
Punkt	Warum offen	Benötigter Nachweis
Zweck des Sammelkontos	Es ist nicht belegt, ob das Konto interaktiv genutzt wird oder technisch erforderlich ist.	Kontoart, Login-Status, technische Verwendung, letzte Nutzung
Vollständigkeit der Berechtigungsänderungen	Nur ein Ticket wurde bereitgestellt.	Liste aller Berechtigungsänderungen im Prüfzeitraum
Umfang des quartalsweisen Reviews	Die 6 Zahlungsfreigaben werden nicht einzeln bestätigt.	Rollenbasierte Review-Liste mit Einzelentscheidung
Administratornutzung	Häufigkeit, Anlass und Freigabe der Stammdatenkorrekturen sind nicht belegt.	Änderungsprotokolle, Notfallfreigaben, Prozessbeschreibung
Quartalsfolge	Nur ein Review ist sichtbar.	Reviews der angrenzenden Quartale, falls Prüfzeitraum mehr als ein Quartal umfasst
Risikoübersicht
Risiko	Einstufung	Begründung
Fehlende individuelle Nachvollziehbarkeit durch Sammelkonto	Hoch	Die Richtlinie verlangt persönliche Konten; ein Sammelkonto schwächt Verantwortungszuordnung unmittelbar.
Unvollständiger Review kritischer Rollen	Hoch	Zahlungsfreigaben und Administratorrollen sind privilegierte Funktionen und nicht vollständig einzeln bestätigt.
Nutzung von Adminrechten für Tagesgeschäft	Mittel bis hoch	Die Prozessnotiz belegt eine Vermischung administrativer und fachlicher Tätigkeiten.
Einzelne Berechtigungsfreigabe nicht repräsentativ	Mittel	REQ-1842 ist belegt, sagt aber nichts über andere Änderungen aus.
Empfehlungen

finance_shared prüfen, interaktive Nutzung unterbinden und Entscheidung dokumentieren.

Zahlungsfreigaben quartalsweise rollenbasiert und kontengenau bestätigen.

Administratorrollen in ein separates privilegiertes Rollenreview aufnehmen.

Fachliche Stammdatenkorrekturen von administrativen Tätigkeiten trennen.

Berechtigungsänderungen im Prüfzeitraum stichprobenartig gegen Genehmigungstickets prüfen.

Review-Protokolle künftig mit Mindestfeldern führen: Datum, Prüfer, Anwendung, geprüfte Rolle, Konto, Entscheidung, Maßnahme und Abschlussstatus.

Prüfpflichtige Aussagen
Aussage	Prüfpflicht	Empfohlene Prüfung
Das Sammelkonto wird aktiv genutzt.	Nicht aus den bereitgestellten Nachweisen belegt.	Login- und Aktivitätsprotokoll prüfen.
Alle Zahlungsfreigaben sind fachlich erforderlich.	Nicht belegt.	Konten mit Zahlungsfreigabe einzeln durch Fachverantwortung bestätigen lassen.
Admin-Korrekturen sind Ausnahmefälle.	Nicht belegt.	Ticket- und Änderungsvolumen auswerten.
Alle Berechtigungsänderungen wurden genehmigt.	Nur für REQ-1842 belegt.	Vollständige Änderungsliste mit Tickets abgleichen.
Nächste sichere Schritte

Berechtigungsliste um Kontoart, Rolle, Verantwortlichen, letzte Anmeldung und Genehmigungsreferenz ergänzen.

Für die 6 Zahlungsfreigaben einen vollständigen Rollenreview nachholen.

Für die 2 Administratorrollen Zweck, Genehmigung und letzte Nutzung dokumentieren.

Prozess für Rechnungsstammdatenkorrekturen so anpassen, dass Standardkorrekturen ohne Administratorrechte erfolgen.

Nach Umsetzung einen kurzen Wirksamkeitsnachweis erstellen: entfernte oder begründete Konten, aktualisiertes Review-Protokoll und Stichprobe genehmigter Änderungen.

Gesamteinschätzung

Die Richtlinie wird in der Freigabe einzelner neuer Berechtigungen grundsätzlich umgesetzt, ist aber bei Kontenmodell, privilegierten Rollen und Review-Vollständigkeit nicht durchgängig erfüllt. Für eine belastbare Compliance-Aussage müssen Sammelkonto, Zahlungsfreigaben und Administratorrollen nachgeprüft und die dokumentierten Abweichungen geschlossen oder begründet akzeptiert werden.
