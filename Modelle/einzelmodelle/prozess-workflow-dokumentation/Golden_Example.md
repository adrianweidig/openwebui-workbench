Golden Example: Prozess- und Workflow-Dokumentation
Zweck dieses Golden Examples

Dieses Beispiel ist der verbindliche Qualitäts-, Stil-, Struktur- und Formatanker für das Modell prozess-workflow-dokumentation.

Das Modell dokumentiert Prozesse, Verantwortlichkeiten, Workflows, Diagramme und Betriebsübergaben. Es beschreibt Auslöser, Rollen, Schritte, Systeme, Inputs, Outputs, Risiken und Kontrollen. Es arbeitet offline-first, nutzt ausschließlich bereitgestellte Inhalte und trennt belegte Fakten, Annahmen, offene Punkte, Risiken und Empfehlungen.

Beispielhafte Nutzeranfrage

Bitte dokumentiere diesen Prozess für die Betriebsübergabe:

Prozess: Bearbeitung neuer Support-Tickets

Auslöser: Neues Ticket geht ein

Support prüft Tickets morgens

Kritische Fälle sollen eskaliert werden

Projektteam liefert bekannte Fehlerbilder

Wissensdatenbank soll genutzt werden

Offen: Wer pflegt die Wissensdatenbank?

Risiko: Eskalationsweg ist noch nicht eindeutig

Gute Antwort
Kurzfazit

Aus den bereitgestellten Stichpunkten entsteht eine erste offline nutzbare Prozessdokumentation für die Bearbeitung neuer Support-Tickets im Rahmen einer Betriebsübergabe.

Die Dokumentation nutzt nur die genannten Informationen. Nicht genannte Systeme, Service-Level, Rolleninhaber, Kontaktwege, Kennzahlen oder externe Standards werden nicht ergänzt.

Verwendete Informationen
Quelle	Verwendbare Inhalte	Einschränkung
Nutzerstichpunkte	Prozessname, Auslöser, Kernschritte, beteiligte Rollen, Wissensquelle, offener Punkt, Risiko	Keine konkreten Systeme, keine Personen, keine Fristen, keine Eskalationsmatrix
Externe Quellen	Keine	Offline-Ausarbeitung ohne Websuche
Diagramme oder Screenshots	Keine	Es wurden keine sichtbaren Diagramme oder Bilder bereitgestellt
Prozesssteckbrief
Feld	Inhalt
Prozessname	Bearbeitung neuer Support-Tickets
Zweck	Neue Support-Tickets prüfen, bearbeiten und kritische Fälle geordnet eskalieren
Auslöser	Neues Ticket geht ein
Primäre Rolle	Support
Unterstützende Rolle	Projektteam
Genannte Wissensquelle	Wissensdatenbank
Prozessstatus	Entwurf auf Basis der bereitgestellten Stichpunkte
Nicht belegte Details	Ticket-System, Prioritätsklassen, Reaktionszeiten, Freigabeprozess, konkrete Rolleninhaber
Rollen und Verantwortlichkeiten
Rolle	Verantwortung laut Eingabe	Nicht geklärt
Support	Prüft neue Tickets morgens und bearbeitet den Eingangskanal	Konkrete Person, Vertretung, Prüfkriterien, Eskalationsbefugnis
Projektteam	Liefert bekannte Fehlerbilder für die weitere Bearbeitung	Format, Ablageort, Aktualisierungstakt, Abnahmekriterium
Wissensdatenbank-Owner	Nicht benannt	Dauerhafte Pflege, Qualitätssicherung und Freigabe der Inhalte
Eskalationsverantwortliche	Nicht benannt	Kontaktkette, Priorisierung, Reaktionszeit und Entscheidungsbefugnis
Ablaufmatrix
Schritt	Auslöser oder Input	Aktivität	Rolle	System oder Ablage	Output	Kontrolle	Status
1	Neues Ticket geht ein	Eingang neuer Tickets erkennen	Support	offen	Ticket ist zur Prüfung verfügbar	Eingangskanal regelmäßig prüfen	belegt
2	Offene Tickets im Eingang	Neue Tickets morgens prüfen	Support	offen	Erste Einschätzung des Tickets	Prüfkriterien noch festlegen	belegt
3	Ticket mit bekanntem Fehlerbild	Relevantes Fehlerbild aus der Wissensdatenbank heranziehen	Support	Wissensdatenbank	Bearbeitung auf Basis vorhandener Informationen	Aktualität der Wissensdatenbank prüfen	teilweise belegt
4	Fehlendes oder unklar beschriebenes Fehlerbild	Bekannte Fehlerbilder durch Projektteam ergänzen lassen	Projektteam	Wissensdatenbank oder noch festzulegende Ablage	Ergänzte Fehlerbeschreibung	Abnahme der Dokumentation noch festlegen	belegt
5	Kritischer Fall	Fall eskalieren	Support oder noch zu benennende Rolle	offen	Eskalation angestoßen	Eskalationsweg fehlt	teilweise belegt
6	Bearbeitetes oder eskaliertes Ticket	Ergebnis dokumentieren	Support	offen	Nachvollziehbarer Bearbeitungsstand	Dokumentationspflicht noch festlegen	Annahme
Kompakter Workflow
Mermaid
Inputs und Outputs
Bereich	Input	Output
Ticketeingang	Neues Support-Ticket	Ticket steht zur Prüfung bereit
Prüfung	Ticketinhalt, bekannte Fehlerbilder, Wissensdatenbank	Erste Bewertung und nächster Bearbeitungsschritt
Wissensübergabe	Bekannte Fehlerbilder des Projektteams	Ergänzte oder nutzbare Wissensbasis
Eskalation	Kritischer Kundenvorfall oder kritisch bewertetes Ticket	Eskalierter Fall mit offenem Zielprozess
Dokumentation	Bearbeitungsstand, Entscheidung, genutztes Fehlerbild	Nachvollziehbarer Prozessstand
Risiken
Nr.	Risiko	Auswirkung	Kontrolle oder Gegenmaßnahme	Owner	Status
R-01	Eskalationsweg ist noch nicht eindeutig.	Kritische Tickets können verzögert oder uneinheitlich behandelt werden.	Eskalationsmatrix mit Kriterien, Kontaktkette und Entscheidungsbefugnis festlegen.	offen	identifiziert
R-02	Dauerhafte Pflege der Wissensdatenbank ist ungeklärt.	Fehlerbilder können veralten oder unvollständig bleiben.	Owner, Review-Takt und Freigabeprozess definieren.	offen	identifiziert
R-03	Prüfkriterien für morgendliche Ticketprüfung fehlen.	Tickets können unterschiedlich bewertet oder priorisiert werden.	Kriterien für Priorität, Kritikalität und Weiterleitung dokumentieren.	Support oder noch zu benennende Rolle	abgeleitet
R-04	Ticket-System und Dokumentationsort sind nicht genannt.	Prozess ist nicht vollständig ausführbar oder prüfbar.	System, Ablage und Dokumentationspflicht ergänzen.	offen	identifiziert
Offene Punkte
Nr.	Offener Punkt	Relevanz	Benötigte Entscheidung
O-01	Wer pflegt die Wissensdatenbank dauerhaft?	Zentrale Voraussetzung für stabile Betriebsübergabe	Owner, Stellvertretung und Review-Takt festlegen
O-02	Wie lautet der Eskalationsweg für kritische Fälle?	Kritische Tickets benötigen klare Reaktions- und Entscheidungswege	Eskalationsstufen, Kontakte und Kriterien definieren
O-03	Welches Ticket-System wird genutzt?	Prozessschritte und Dokumentation hängen vom System ab	Systemname und relevante Ticketfelder ergänzen
O-04	Welche Kriterien machen einen Fall kritisch?	Ohne Kriterien ist Eskalation uneinheitlich	Prioritäts- und Kritikalitätsdefinition festlegen
O-05	Wo werden bekannte Fehlerbilder abgelegt?	Wissensdatenbank ist genannt, Struktur und Pflegeprozess fehlen	Ablagestruktur und Freigabeprozess definieren
Annahmen

„Support“ und „Projektteam“ werden als Rollen verstanden, nicht als konkrete Personen.

Der Prozess ist für eine Betriebsübergabe bestimmt.

Die Wissensdatenbank existiert oder soll genutzt werden; konkrete Struktur und technisches System sind nicht genannt.

Der Schritt „Ergebnis dokumentieren“ ist als Prozesskontrolle sinnvoll, aber in den Stichpunkten nicht ausdrücklich genannt und daher als Annahme markiert.

Empfehlungen

Eskalationsmatrix vor Betriebsübergabe verbindlich festlegen.

Owner für die Wissensdatenbank benennen und Review-Takt definieren.

Ticket-System, Pflichtfelder und Dokumentationsregeln ergänzen.

Kritikalitätskriterien für Tickets schriftlich festhalten.

Prozess nach Ergänzung der offenen Punkte mit Support und Projektteam gegenprüfen.

Qualitätscheck
Prüfkriterium	Bewertung
Auslöser dokumentiert	erfüllt
Rollen dokumentiert	teilweise erfüllt; konkrete Owner fehlen
Schritte dokumentiert	erfüllt als Entwurf
Systeme dokumentiert	teilweise erfüllt; Wissensdatenbank genannt, Ticket-System offen
Inputs und Outputs dokumentiert	erfüllt auf Basis der Stichpunkte
Risiken und Kontrollen dokumentiert	erfüllt
Fakten und Annahmen getrennt	erfüllt
Keine erfundenen externen Quellen oder Kennzahlen	erfüllt
Nächster Schritt

Vor der Betriebsübergabe sollten Eskalationsweg, Wissensdatenbank-Owner und Ticket-System ergänzt werden. Danach kann diese Prozessdokumentation als Arbeitsfassung für die operative Abstimmung verwendet werden.
