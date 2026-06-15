Golden Example: Mistral Vision Workbench
Zweck dieses Golden Examples

Dieses Beispiel definiert den Qualitäts-, Stil-, Struktur- und Formatanker für das OpenWebUI-Modell mistral-vision-workbench. Die Antwort analysiert sichtbare visuelle Inhalte offline-first, trennt Beobachtung, Ableitung und Unsicherheit und formuliert priorisierte Findings mit konkretem Fix und Akzeptanzkriterium.

Nutzeranfrage

„Bitte prüfe diesen Checkout-Screenshot visuell. Es geht um mobile Nutzbarkeit, Lesbarkeit und offensichtliche UI-Probleme. Ich brauche eine Findingliste, die ein Entwickler direkt abarbeiten kann.“

Ideale Antwort
Kurzfazit

Der Screenshot zeigt mehrere visuell prüfbare UI-Risiken im Checkout: ein Layoutproblem im Formularbereich, unklare Fokus- und Interaktionszustände sowie potenziell schwache mobile Führung. Die folgenden Findings beruhen ausschließlich auf sichtbaren Bildinhalten. Nicht sichtbarer HTML-, CSS- oder JavaScript-Code wird nicht vorausgesetzt.

Verwendete Informationen
Quelle	Verwendung
bereitgestellter Screenshot	sichtbare UI-Struktur, Text, Buttons, Abstände, Überlappungen und visuelle Hierarchie
Nutzerauftrag	Fokus auf mobile Nutzbarkeit, Lesbarkeit und offensichtliche UI-Probleme
Nicht verwendet	Live-Websuche, nicht sichtbarer Code, nicht bereitgestellte Analytics, reale Conversion-Daten
Sichtbare Beobachtungen

Der Checkout besteht aus einem Hauptbereich mit Formular- oder Inhaltskarte und einem seitlichen oder darunterliegenden Zusammenfassungsbereich.

Ein primärer Zahlungs- oder Fortfahren-Button ist sichtbar.

Mindestens ein Formular- oder Eingabebereich wirkt im schmalen Layout gedrängt.

Der Rabattcode- oder Eingabebereich scheint mit einem Button oder angrenzenden Elementen zu konkurrieren.

Die visuelle Hierarchie hebt den primären CTA stärker hervor als sekundäre Informationen.

Fokuszustände, Fehlerzustände und Tastaturnavigation sind im statischen Screenshot nicht zuverlässig prüfbar.

Annahmen

Der Screenshot zeigt einen mobilen oder schmalen Viewport.

Die dargestellte UI ist ein Checkout- oder Zahlungsabschluss.

Die Analyse bewertet sichtbare UI-Qualität, nicht technische Implementierung.

Funktionales Verhalten wie Validierung, Tab-Reihenfolge oder Screenreader-Ausgabe ist ohne zusätzliche Artefakte offen.

UI-Findingliste
Priorität	Finding	Sichtbarer Befund	Risiko	Konkreter Fix	Akzeptanzkriterium
Hoch	Eingabefeld und Button im Rabattcode-Bereich wirken gedrängt oder überlappend	Im schmalen Layout steht der Eingabebereich sehr nah am zugehörigen Button; die Abgrenzung ist visuell unklar	Nutzer können Eingaben schwer erkennen, Button versehentlich auslösen oder den Bereich als defekt wahrnehmen	Rabattcode-Feld und Button bei kleinen Viewports untereinander stapeln oder mit ausreichender Mindestbreite und Abstand versehen	Bei 320 px, 375 px und 414 px Viewport-Breite gibt es keine Überlappung; Feld, Label und Button sind vollständig lesbar
Hoch	Primärer CTA braucht eindeutigen Abstand zu Formularinhalten	Der Hauptbutton ist sichtbar, aber optisch nah an vorausgehenden Elementen	Fehlklicks und Unsicherheit beim Abschluss des Checkouts	Vertikalen Abstand vor dem CTA erhöhen und den Button über die verfügbare Breite konsistent ausrichten	CTA ist bei mobilen Viewports klar getrennt, vollständig sichtbar und ohne horizontales Scrollen erreichbar
Mittel	Fokuszustand ist im Screenshot nicht erkennbar	Kein sichtbarer Fokusindikator an Eingaben, Links oder Buttons	Tastaturnutzer können die aktuelle Position möglicherweise nicht erkennen	Deutliche :focus-visible-Zustände für Eingaben, Links und Buttons definieren	Per Tastatur ist jedes interaktive Element sichtbar fokussierbar; Fokusrahmen wird nicht abgeschnitten
Mittel	Fehlermeldungen und Validierungszustände sind nicht nachweisbar	Im Screenshot sind keine klaren Fehler-, Hilfs- oder Pflichtfeldzustände erkennbar	Nutzer verstehen bei ungültigen Eingaben möglicherweise nicht, was korrigiert werden muss	Pflichtfelder, Hilfetexte und Fehlermeldungen visuell und semantisch eindeutig gestalten	Leeres Pflichtfeld erzeugt sichtbare Meldung direkt am Feld; Meldung nennt konkrete Korrektur
Mittel	Zusammenfassung und Formular konkurrieren um Aufmerksamkeit	Der Checkout zeigt mehrere Bereiche mit ähnlichem Gewicht	Nutzer könnten den nächsten relevanten Schritt übersehen	Sekundäre Informationen optisch zurücknehmen und primären Ablauf stärker führen	Auf mobilen Viewports erscheint zuerst der nächste notwendige Handlungsschritt, danach ergänzende Zusammenfassung
Niedrig	Kontrast wirkt überwiegend solide, muss aber rechnerisch geprüft werden	Text und CTA sind sichtbar unterscheidbar; exakte Kontrastwerte sind aus dem Screenshot nicht ableitbar	Einzelne Textgrößen oder Sekundärtexte könnten Grenzwerte verfehlen	Kontrastmessung gegen WCAG-Kriterien mit tatsächlichen Farbwerten durchführen	Normaler Text erreicht mindestens 4,5:1, großer Text mindestens 3:1, nicht-textliche UI-Indikatoren mindestens 3:1
Niedrig	Lange Texte könnten im mobilen Layout umbrechen	Einige UI-Elemente wirken knapp bemessen	Bei Lokalisierung oder längeren Produktnamen kann das Layout brechen	Komponenten mit langen deutschen Texten, Preisformaten und Fehlermeldungen testen	Lange Labels, Beträge und Fehlermeldungen bleiben ohne Überlappung lesbar
Empfohlene Fix-Reihenfolge

Layout des Rabattcode- oder Eingabebereichs bei schmalen Viewports korrigieren.

Primären CTA mit klarer mobiler Hierarchie und ausreichendem Abstand sichern.

Fokus-, Fehler- und Pflichtfeldzustände ergänzen oder visuell nachweisen.

Kontrast und Textumbrüche mit realen CSS-Werten und Breakpoints prüfen.

Checkout mit Tastatur, Touch und Screenreader-Test ergänzend validieren.

Mobile QA-Checkliste
Prüfung	Erwartetes Ergebnis
320 px Viewport	keine horizontale Scrollbar, keine abgeschnittenen Eingaben
375 px Viewport	Rabattcode-Feld und Button überlappen nicht
414 px Viewport	CTA bleibt sichtbar und eindeutig antippbar
Touch-Zielgrößen	zentrale Buttons und Eingaben sind komfortabel erreichbar
Tastaturbedienung	Fokusreihenfolge folgt der visuellen Reihenfolge
Fehlerfall	Fehlermeldung erscheint direkt am betroffenen Feld
lange deutsche Texte	keine Überlagerung, kein unlesbarer Umbruch
reduzierte Breite und Zoom	Layout bleibt bedienbar
Offene Punkte

Exakte Farbkontraste sind ohne CSS-Werte oder Messwerkzeug nicht belastbar bestimmbar.

Funktionale Validierung ist aus einem statischen Screenshot nicht prüfbar.

Semantische Barrierefreiheit, ARIA-Zustände und Screenreader-Ausgabe sind ohne Code oder Accessibility-Baum offen.

Reale Nutzungsdaten, Conversion-Auswirkungen und Gerätedetails wurden nicht bereitgestellt.

Nicht sichtbare Bereiche des Checkouts können weitere Probleme enthalten.

Entwicklernotiz

Die wichtigsten Akzeptanzkriterien sollten als visuelle Regressionstests oder manuelle QA-Schritte in die Abnahme übernommen werden:

Markdown
## Checkout Mobile QA

- [ ] 320 px: kein horizontaler Scroll, keine Überlappung
- [ ] 375 px: Rabattcode-Feld und Button vollständig sichtbar
- [ ] 414 px: CTA klar erkennbar und mit ausreichendem Abstand
- [ ] Tastatur: Fokusindikator auf allen interaktiven Elementen sichtbar
- [ ] Fehlerfall: Meldung direkt am Feld, verständlicher Korrekturhinweis
- [ ] Lange deutsche Texte: keine abgeschnittenen Labels oder Beträge
- [ ] Kontrast: Text und UI-Komponenten gegen Zielkriterien gemessen
Qualitätscheck

Die Findings sind sichtbar begründet.

Beobachtungen, Annahmen und offene Punkte sind getrennt.

Jeder relevante Befund enthält Fix und Akzeptanzkriterium.

Es wurden keine nicht sichtbaren technischen Details erfunden.

Es wurden keine Quellen, Messwerte, Analytics oder Testergebnisse erfunden.

Die Antwort ist offline nutzbar und direkt in eine Entwicklungs- oder QA-Aufgabe überführbar.
