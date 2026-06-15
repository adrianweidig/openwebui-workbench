Golden Example: Allgemeines Routing und Arbeitsprodukt
Nutzeranfrage

Ich habe mehrere Notizen, einen Screenshot aus einem Tool und ein paar Stichpunkte aus einem Meeting. Daraus soll ein Ergebnis entstehen, das ich intern weitergeben kann. Ich bin mir aber nicht sicher, ob daraus eher ein Lastenheft, eine technische Dokumentation oder ein Arbeitsplan werden soll.

Kurzfazit

Der Auftrag ist gemischt und noch nicht eindeutig einem Spezialmodell zuordenbar. Ich erstelle deshalb zuerst eine belastbare Einordnung und liefere anschließend ein direkt verwendbares Arbeitsprodukt im kleinsten sinnvollen Format: einen strukturierten Routing- und Arbeitsplan.

Die Bearbeitung nutzt ausschließlich die sichtbaren Nutzerinformationen. Nicht bereitgestellte Dateien, konkrete Screenshots, externe Fakten, Tools, Kennzahlen, Fristen oder Zuständigkeiten werden nicht ergänzt.

Verwendete Informationen
Quelle	Sicher sichtbarer Inhalt	Bewertung
Nutzertext	Es gibt Notizen, einen Screenshot aus einem Tool und Meeting-Stichpunkte.	Belegt
Nutzertext	Das Ergebnis soll intern weitergegeben werden.	Belegt
Nutzertext	Zielformat ist noch unklar: Lastenheft, technische Dokumentation oder Arbeitsplan.	Belegt
Screenshot	Nicht sichtbar oder nicht bereitgestellt.	Offen
Dateien	Nicht sichtbar oder nicht bereitgestellt.	Offen
Annahmen

Die Arbeitssprache bleibt Deutsch.

Das Ergebnis soll ohne Websuche und ohne externe API nutzbar sein.

Es geht zunächst um Strukturierung und Entscheidungshilfe, nicht um verbindliche Rechts-, Sicherheits- oder Budgetfreigabe.

Der Screenshot kann erst ausgewertet werden, wenn er sichtbar vorliegt oder inhaltlich beschrieben wird.

Routing
Kandidat	Passt, wenn	Bewertung
allgemein	Zielartefakt, Quellenlage oder Fachmodell noch unklar sind.	Aktuell passend
anforderungsanalyse-lastenheft	Aus Notizen sollen Anforderungen, Ziele, Nicht-Ziele, Stakeholder und Akzeptanzkriterien entstehen.	Wahrscheinlich passend nach Sichtung
code-dokumentation	Sichtbarer Code, Modulverhalten, Konfiguration oder Entwicklerbetrieb dokumentiert werden sollen.	Nur passend, wenn Code oder technische Schnittstellen vorliegen
api-schnittstellenentwurf	Ein API-Vertrag, OpenAPI-YAML, Datenvertrag oder Fehlervertrag erstellt werden soll.	Nur passend bei API-Bezug
Empfohlenes Vorgehen

Quellen inventarisieren
Alle vorhandenen Inputs werden getrennt erfasst: Notizen, Screenshot, Meeting-Stichpunkte, bestehende Dokumente und bereits bekannte Zielgruppe.

Zielartefakt bestimmen
Aus Inhalt und Zielgruppe wird abgeleitet, ob ein Lastenheft, eine technische Dokumentation, ein Entscheidungsbriefing oder ein Arbeitsplan die beste Form ist.

Fakten und Annahmen trennen
Sichtbare Informationen werden nicht mit plausiblen, aber unbelegten Ergänzungen vermischt.

Risiken und offene Punkte markieren
Fehlende Pflichtinformationen werden nicht erfunden, sondern prüfbar benannt.

Erste verwendbare Fassung liefern
Wenn der Kontext ausreicht, entsteht direkt ein intern weitergebbares Dokument. Wenn nicht, entsteht ein konservativer Arbeitsplan mit maximal drei gezielten Klärungspunkten.

Arbeitsprodukt
1. Zielbild

Aus heterogenen Eingangsinformationen soll ein klares, intern nutzbares Ergebnis entstehen. Da das endgültige Artefakt noch offen ist, wird zunächst eine belastbare Struktur erstellt, die später in ein Lastenheft, eine Dokumentation oder einen Umsetzungsplan überführt werden kann.

2. Vorläufige Struktur für die interne Weitergabe
Ausgangslage

Es liegen mehrere Informationsquellen vor: Notizen, ein Tool-Screenshot und Meeting-Stichpunkte. Der fachliche Schwerpunkt ist noch nicht eindeutig genug beschrieben, um direkt ein Spezialartefakt zu erstellen.

Ziel

Die Inhalte sollen so geordnet werden, dass ein Team entscheiden kann:

welches Ergebnis gebraucht wird,

welche Informationen bereits belastbar sind,

welche Punkte noch geprüft werden müssen,

welches Spezialmodell oder welcher Bearbeitungsschritt als Nächstes sinnvoll ist.

Nicht-Ziele

Es werden keine externen Fakten ergänzt.

Es werden keine nicht sichtbaren Inhalte aus dem Screenshot angenommen.

Es werden keine Zuständigkeiten, Termine, Budgets oder technischen Versionen erfunden.

Es entsteht noch keine verbindliche fachliche Freigabe.

Quellenlage
Informationsart	Status	Konsequenz
Notizen	erwähnt, aber nicht inhaltlich sichtbar	Inhalt muss bereitgestellt oder zusammengefasst werden
Screenshot	erwähnt, aber nicht sichtbar	Auswertung erst nach Upload oder Beschreibung möglich
Meeting-Stichpunkte	erwähnt, aber nicht sichtbar	Struktur kann vorbereitet werden, Details bleiben offen
Zielgruppe	nicht genannt	Dokument wird neutral für interne Weitergabe formuliert
gewünschtes Endformat	unklar	Routing bleibt Teil des Ergebnisses
3. Entscheidungsmatrix für das Zielformat
Beobachtung aus den Quellen	Bestes Zielformat	Warum
Viele Anforderungen, Ziele, Rollen und Abnahmekriterien	Lastenheft oder Anforderungskatalog	Anforderungen brauchen Priorität, Akzeptanzkriterien und offene Klärungspunkte
Viel Code, Modulbeschreibung, CLI, API oder Konfiguration	Entwicklerdokumentation	Technische Nutzung, Datenverträge und Fehlerverhalten müssen wartbar dokumentiert werden
Mehrere Optionen, Risiken und unklare Entscheidung	Entscheidungs- oder Arbeitsplan	Erst Einordnung, dann Umsetzung
API-Endpunkte, Request-/Response-Felder oder Authentifizierung	OpenAPI-Spezifikation	API-Vertrag muss maschinenlesbar und lokal prüfbar sein
Nur grobe Stichpunkte ohne belastbare Quelle	Strukturierte Erstfassung mit Annahmen	Fehlende Informationen dürfen nicht erfunden werden
4. Konkreter Arbeitsplan
Schritt	Ergebnis	Tool- oder Quellenbedarf
1. Inputs sammeln	Liste aller sichtbaren Quellen	Nutzertext, Dateien, Screenshot
2. Inhalte extrahieren	Faktenliste nach Quelle	Nur sichtbare oder bereitgestellte Inhalte
3. Zielartefakt wählen	Routing-Entscheidung	Entscheidungsmatrix
4. Erstfassung erstellen	Intern nutzbares Dokument	Markdown als Standard
5. Risiken prüfen	Risiko- und Lückenliste	Keine externen Annahmen
6. Nächsten Schritt definieren	Lokale Folgeaktion	Ohne Websuche ausführbar
5. Risiken
Risiko	Auswirkung	Gegenmaßnahme
Screenshot ist nicht sichtbar	Inhalte könnten falsch angenommen werden	Keine Bilddetails erfinden; Upload oder Beschreibung nutzen
Zielgruppe fehlt	Ton und Detailgrad könnten nicht passen	Neutraler interner Stil
Zielformat ist unklar	Ergebnis könnte am Bedarf vorbeigehen	Routing vor Artefakterstellung
Externe Aktualität wäre nötig	Aussagen könnten veraltet oder unbelegt sein	Als prüfpflichtig markieren
Notizen enthalten sensible Daten	Datenschutzrisiko	Personenbezogene Daten minimieren oder anonymisieren
Offene Punkte

Welche Inhalte stehen tatsächlich in den Notizen und Meeting-Stichpunkten?

Was ist auf dem Screenshot sichtbar?

Wer nutzt das Ergebnis intern: Management, Fachbereich, Entwicklung, Betrieb oder Einkauf?

Empfehlung

Auf Basis der aktuellen Anfrage bleibt allgemein das richtige Startmodell. Sobald die Inhalte sichtbar sind, sollte das Ergebnis voraussichtlich in eines dieser Formate überführt werden:

bei Anforderungen: anforderungsanalyse-lastenheft,

bei Code oder technischer Nutzung: code-dokumentation,

bei API-Verträgen: api-schnittstellenentwurf.

Nächster lokaler Schritt

Die vorhandenen Notizen, den Screenshot und die Meeting-Stichpunkte in einem gemeinsamen Input bündeln. Danach kann daraus ohne Websuche eine erste belastbare Version des passenden Zielartefakts erstellt werden.
