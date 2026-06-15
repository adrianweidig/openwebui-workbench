Golden Example: IT-Helpdesk-Diagnose
Zweck dieses Golden Examples

Dieses Beispiel zeigt das verbindliche Zielbild für das Modell it-helpdesk-diagnose: aus einer knappen Nutzerbeschreibung entsteht eine strukturierte Helpdesk-Diagnose mit Sofortmaßnahmen, Diagnosepfad, Rückfragen, Risiken und Eskalationskriterium. Das Ergebnis nutzt nur bereitgestellte Informationen, markiert Annahmen und erfindet keine Testergebnisse, Systemstände oder Ursachen.

Nutzeranfrage

Ein Nutzer meldet:

„Seit heute Morgen kann ich mich nicht mehr in der Zeiterfassung anmelden. Im Browser erscheint nur ‚Anmeldung fehlgeschlagen‘. Gestern ging es noch. Kolleginnen und Kollegen scheinen arbeiten zu können. Ich habe mein Passwort nicht geändert.“

Bitte als Ticketnotiz für den Helpdesk strukturieren.

Gute Antwort
Kurzfazit

Es handelt sich nach aktueller Beschreibung um ein Anmeldeproblem bei der Zeiterfassung, das offenbar einen einzelnen Nutzer betrifft. Die Ursache ist noch nicht belegt. Priorität: arbeitsrelevant, aber zunächst kein Hinweis auf einen flächigen Ausfall.

Ticketnotiz
Feld	Eintrag
Kategorie	Anwendung / Login / Zeiterfassung
Symptom	Anmeldung in der Zeiterfassung schlägt fehl. Angezeigte Meldung: „Anmeldung fehlgeschlagen“.
Beginn	Heute Morgen laut Nutzerangabe
Letzter funktionierender Stand	Gestern laut Nutzerangabe
Betroffene Personengruppe	Nach aktuellem Stand ein einzelner Nutzer
Impact	Nutzer kann Zeiterfassung nicht verwenden
Umgebung	Browser wird erwähnt; Browsertyp, Gerät, Netzwerk und Betriebssystem sind offen
Aktueller Verdacht	Nutzer-, Sitzungs-, Browser-, Berechtigungs- oder Kontostatusproblem möglich; Ursache nicht belegt
Sicherheitsrelevanz	Keine Passwörter oder privaten Zugangsdaten im Ticket erfassen
Belegte Fakten

Der Nutzer kann sich seit heute Morgen nicht mehr in der Zeiterfassung anmelden.

Die sichtbare oder gemeldete Fehlermeldung lautet: „Anmeldung fehlgeschlagen“.

Gestern funktionierte die Anmeldung laut Nutzer noch.

Kolleginnen und Kollegen scheinen laut Nutzer arbeiten zu können.

Der Nutzer gibt an, das Passwort nicht geändert zu haben.

Annahmen

Es handelt sich um die reguläre Zeiterfassungsanwendung des Unternehmens.

Die Meldung tritt beim Login im Browser auf.

Es liegt bisher kein Nachweis für einen allgemeinen Systemausfall vor.

Offene Rückfragen an den Nutzer

Welcher Browser und welches Gerät werden verwendet?

Tritt der Fehler auch in einem privaten Browserfenster oder nach Abmeldung und erneutem Login auf?

Wurde die Anmeldung heute bereits über ein anderes Gerät oder Netzwerk getestet?

Sofortmaßnahmen

Nutzer bitten, keine weiteren Passwortdaten im Ticket zu senden.

Browserseite neu laden und bestehende Sitzung vollständig abmelden, falls möglich.

Privates Browserfenster testen.

Falls zulässig: Browsercache nur für die Zeiterfassungsseite löschen.

Anmeldung auf einem zweiten Browser oder Gerät testen, um Browser- und Gerätebezug einzugrenzen.

Diagnosepfad für den Helpdesk

Prüfen, ob weitere Tickets zur Zeiterfassung seit heute Morgen eingegangen sind.

Prüfen, ob das Nutzerkonto aktiv, nicht gesperrt und für die Zeiterfassung berechtigt ist.

Prüfen, ob kürzlich Rollen-, Gruppen- oder Berechtigungsänderungen am Nutzerkonto vorgenommen wurden.

Falls die Anwendung zentrale Authentifizierung nutzt: Loginstatus dort prüfen, ohne Passwörter abzufragen.

Falls nur dieser Nutzer betroffen ist und ein anderer Browser funktioniert, lokale Browserdaten oder Sitzung als wahrscheinlichen Ansatz weiterverfolgen.

Falls mehrere Nutzer betroffen sind, Störung der Zeiterfassung oder der Authentifizierung als mögliche Sammelstörung behandeln.

Risiken

Passwort- oder Zugangsdaten dürfen nicht im Ticket oder per E-Mail abgefragt werden.

Ohne Systemprüfung darf keine Ursache wie Kontosperre, Serverausfall oder Berechtigungsentzug behauptet werden.

Ein Passwortreset sollte nicht als erste Maßnahme erzwungen werden, solange Konto- und Berechtigungsstatus ungeprüft sind.

Eskalationskriterium

An den Second-Level-Support oder Anwendungssupport eskalieren, wenn mindestens eines der folgenden Kriterien erfüllt ist:

Konto ist aktiv und berechtigt, der Login schlägt aber weiterhin in mehreren Browsern oder auf mehreren Geräten fehl.

Mehrere Nutzer melden zeitgleich vergleichbare Loginprobleme.

Die Anwendung zeigt dieselbe Fehlermeldung trotz geprüfter Berechtigungen und sauberer Sitzung.

Es gibt Hinweise auf eine Störung der zentralen Authentifizierung oder der Zeiterfassungsanwendung.

Nächster lokaler Schritt

Zuerst Nutzerkontext vervollständigen: Browser, Gerät, zweiter Browsertest und Kontostatus dokumentieren. Danach anhand der Ergebnisse entweder lokal weiter eingrenzen oder mit den gesammelten Fakten eskalieren.
