# Fachwissen für Internetwissen

Diese KnowledgeBase enthält bewusst keine kopierten Webartikel und keine großen externen Korpora. Sie beschreibt Arbeitsmethoden, Bewertungsregeln, Antwortmuster und kompaktes Grundlagenwissen, das direkt im Repository gepflegt werden kann.

## 1. Grundprinzipien der Offline-Recherche

Offline-Recherche bedeutet, mit lokal vorhandenem Wissen, Nutzerdateien, repo-interner Knowledge und allgemeinem Modellwissen zu arbeiten. Das Modell darf daraus hilfreiche Erklärungen, Anleitungen und Recherchepläne ableiten, darf aber keine aktuelle Webprüfung vortäuschen.

Wichtige Trennung:

- **Repo-interne Knowledge:** explizit mitgelieferte Dateien wie `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md` und Beispiele.
- **Nutzerkontext:** Dateien, Texte, Screenshots oder Angaben, die der Nutzer im Chat bereitstellt.
- **Allgemeines Modellwissen:** vortrainiertes Sprachmodellwissen ohne aktuelle Verifikation.
- **Annahmen:** plausible, aber nicht belegte Ergänzungen.
- **Aktualitätslücken:** Punkte, die nur mit aktuellen Quellen belastbar beantwortet werden können.

Wenn eine Antwort vom aktuellen Stand der Welt abhängt, muss das Modell das markieren. Typische Themen mit hohem Aktualitätsrisiko sind Gesetze, Preise, Produktverfügbarkeiten, Softwareversionen, Sicherheitslücken, medizinische Empfehlungen, politische Rollen, Nachrichten, Sportergebnisse, Wetter, Lieferzeiten, Börsenkurse und Anbieterbedingungen.

## 2. Recherchemethodik

Eine belastbare Recherche beginnt nicht mit der Antwort, sondern mit der Struktur der Frage.

### Vorgehen

1. **Fragestellung klären:** Was soll entschieden, verstanden, erstellt oder geprüft werden?
2. **Begriffe sammeln:** zentrale Begriffe, Synonyme, Abkürzungen, Fachwörter und Gegenbegriffe.
3. **Suchaspekte bilden:** Technik, Recht, Risiken, Kosten, Alternativen, Zielgruppen, Aktualität, Qualität.
4. **Quellenarten festlegen:** Primärquelle, Dokumentation, Standard, Fachartikel, Herstellerangabe, Statistik, Gesetzestext, Praxisbericht.
5. **Evidenzgrad bewerten:** direkte Quelle, unabhängige Bestätigung, plausibler Hinweis oder ungesicherte Behauptung.
6. **Widersprüche dokumentieren:** Was sagen Quellen unterschiedlich und warum könnte das so sein?
7. **Grenzen festhalten:** Was konnte nicht geprüft werden?

### Rechercheplan-Template

```md
## Ziel
[Was soll geklärt werden?]

## Suchaspekte
- Begriffsklärung:
- Technik/Funktion:
- Risiken/Grenzen:
- Alternativen:
- Aktualitätsprüfung:

## Geeignete Quellenarten
- Primärquellen:
- Sekundärquellen:
- Community-/Praxisquellen:

## Prüffragen
- Wer sagt das?
- Wann wurde es veröffentlicht oder aktualisiert?
- Welche Belege werden genannt?
- Gibt es Interessenkonflikte?
- Ist die Aussage noch aktuell?

## Ergebnisformat
[Zusammenfassung, Tabelle, Anleitung, Entscheidungsvorlage]
```

## 3. Quellenkritik

Eine Quelle ist nicht automatisch belastbar, nur weil sie öffentlich zugänglich ist. Das Modell bewertet bereitgestellte Quellen anhand nachvollziehbarer Kriterien.

### Prüfkriterien

- **Autorität:** Wer ist Autor, Herausgeber oder Institution?
- **Aktualität:** Gibt es ein Veröffentlichungs- oder Änderungsdatum?
- **Nachvollziehbarkeit:** Sind Behauptungen belegt, verlinkt oder reproduzierbar?
- **Interessenlage:** Besteht Werbung, Lobbying, Affiliate-Interesse oder Eigenwerbung?
- **Vollständigkeit:** Werden Einschränkungen, Gegenpositionen und Nebenwirkungen genannt?
- **Konsistenz:** Passt die Aussage zu bekannten Standards oder widerspricht sie ohne Begründung?
- **Präzision:** Werden konkrete Begriffe, Versionen, Bedingungen und Messgrößen genannt?
- **Übertragbarkeit:** Gilt die Aussage für den Nutzerkontext oder nur für einen Spezialfall?

### Warnsignale

- keine Autor- oder Herausgeberangabe
- kein Datum bei zeitabhängigen Themen
- starke Werbesprache statt Belegen
- absolute Aussagen wie „immer“, „garantiert“, „100 % sicher“
- fehlende Methodik bei Statistiken
- unklare Zitate oder Zitatketten ohne Primärquelle
- fehlende Risikohinweise bei sicherheitskritischen Handlungen

## 4. Anleitungswissen

Gute Anleitungen sind nicht nur Listen von Schritten. Sie erklären Voraussetzungen, Risiken, Kontrollpunkte und Fehlerbehandlung.

### Standardstruktur einer Anleitung

```md
## Ziel
Was soll am Ende erreicht sein?

## Voraussetzungen
- Wissen:
- Material/Dateien:
- Rechte/Zugriffe:
- Sicherheitsbedingungen:

## Vorgehen
1. Schritt mit Zweck
2. Schritt mit Zweck
3. Schritt mit Zweck

## Ergebnis prüfen
- Woran erkennt man, dass es funktioniert?
- Welche Datei, Ausgabe oder Änderung muss sichtbar sein?

## Typische Fehler
- Fehlerbild:
- Ursache:
- Behebung:

## Grenzen
- Was hängt von aktuellen Quellen, Versionen oder lokalen Bedingungen ab?
```

### Qualitätsregeln für Anleitungen

- zuerst Ziel und Kontext klären
- gefährliche oder irreversible Schritte deutlich kennzeichnen
- keine Tool-, Produkt- oder Versionsbehauptung ohne aktuelle Prüfung
- Anfänger- und Expertenvarianten trennen, wenn nötig
- Ergebnisprüfung immer ergänzen
- bei unklaren Voraussetzungen konservativ bleiben

## 5. Allgemeine Wissensstrukturierung

Viele Wissensfragen werden besser beantwortet, wenn sie in eine passende Denkform übersetzt werden.

### Geeignete Strukturen

- **Begriffserklärung:** Definition, Abgrenzung, Beispiel, Gegenbeispiel.
- **Vergleich:** Kriterien, Optionen, Vor-/Nachteile, Empfehlung mit Annahmen.
- **Ursache-Wirkung:** Auslöser, Mechanismus, sichtbares Ergebnis, Gegenmaßnahmen.
- **Entscheidungsbaum:** Bedingungen, Verzweigungen, Ergebnis je Fall.
- **Checkliste:** prüfbare Punkte in sinnvoller Reihenfolge.
- **FAQ:** typische Fragen mit kurzen Antworten.
- **Glossar:** Fachbegriffe mit knapper Erklärung.
- **Lernplan:** Ziel, Reihenfolge, Übungen, Kontrollfragen.

## 6. Web- und Internet-Grundlagen

### Begriffe

- **Internet:** globales Netzwerk aus verbundenen Netzen und Protokollen.
- **Web:** Dienst auf dem Internet, typischerweise über HTTP/HTTPS.
- **Website:** Sammlung zusammengehöriger Webseiten unter einer Domain oder Subdomain.
- **Webseite:** einzelnes Dokument oder einzelner Zustand einer Website.
- **URL:** genaue Adresse einer Ressource.
- **Domain:** menschenlesbarer Name, der über DNS auf technische Ziele verweist.
- **Server:** System oder Dienst, der Ressourcen bereitstellt.
- **Client:** Programm, das Ressourcen anfragt, z. B. Browser oder API-Client.
- **Suchmaschinenindex:** Datenbestand einer Suchmaschine; nicht identisch mit dem Live-Web.
- **Archiv:** gespeicherter Stand einer Ressource zu einem bestimmten Zeitpunkt.

### Crawling und Wiederverwendung

Öffentliche Abrufbarkeit bedeutet nicht automatisch freie Wiederverwendung. Für ein Repository dürfen nur Inhalte übernommen werden, wenn Lizenz, Rechte und Attribution geprüft sind. Deshalb enthält das initiale Modell keine kopierten Webkorpora und keine fremden Masseninhalte.

`robots.txt` ist ein technisches Signal für Crawler-Verhalten. Es ersetzt keine Lizenzprüfung und keine rechtliche Bewertung.

## 7. Technisches Basiswissen für Recherchefragen

### Dateiformate

- **Markdown:** gut für strukturierte, menschenlesbare Texte.
- **JSON:** gut für maschinenlesbare Objekte, APIs und Konfiguration.
- **CSV:** gut für Tabellen, aber anfällig für Trennzeichen- und Encoding-Probleme.
- **YAML:** gut lesbar für Konfiguration, aber einrückungssensibel.
- **PDF:** gut für Layouttreue, aber schlechter für strukturierte Weiterverarbeitung.
- **HTML:** gut für Webinhalte, enthält aber oft Navigation, Werbung und Skripte.

### Prüffragen bei technischen Inhalten

- Welche Version ist gemeint?
- Auf welchem Betriebssystem oder Stack gilt die Aussage?
- Ist die Quelle eine offizielle Dokumentation, ein Blog, ein Forum oder ein Beispiel?
- Gibt es Sicherheits- oder Rechteanforderungen?
- Ist der Befehl destruktiv oder reversibel?

## 8. Offline-Grenzen und Standardformulierungen

Das Modell soll Grenzen knapp, aber deutlich ausdrücken.

### Standardformulierungen

- „Das kann ich offline ohne aktuelle Quelle nicht belastbar bestätigen.“
- „Ich kann eine allgemeine Vorgehensweise liefern, aber keine Live-Aktualität prüfen.“
- „Diese Antwort basiert auf allgemeinem Wissen und der repo-internen KnowledgeBase.“
- „Für konkrete Versionen, Preise, Anbieterbedingungen oder Rechtslage ist eine aktuelle Quelle nötig.“
- „Der lokale Wissensstand reicht dafür nicht aus; sinnvoll wäre folgender Rechercheplan.“

### Wann eine Grenze Pflicht ist

- der Nutzer fragt nach „heute“, „aktuell“, „neueste“, „letzte Version“, „Preis“, „Gesetz“, „Verfügbarkeit“
- die Antwort kann Schaden verursachen, wenn sie veraltet ist
- es geht um medizinische, rechtliche, finanzielle oder sicherheitskritische Entscheidungen
- der Nutzer verlangt eine Quelle, die nicht bereitgestellt wurde
- die Aussage hängt von einem konkreten Land, Anbieter, Produkt oder Datum ab

## 9. Antwortmuster

### Kurzantwort mit Grenze

```md
## Einordnung
[knappe Antwort]

## Grenze
Das ist zeitabhängig. Offline kann ich keine aktuelle Bestätigung liefern.

## Nächster sinnvoller Schritt
[Recherche- oder Prüfschritt]
```

### Quellenkritik

```md
## Kurzurteil
[belastbar / teilweise belastbar / schwach / nicht bewertbar]

## Stärken
- ...

## Schwächen
- ...

## Offene Prüfpunkte
- Autor/Herausgeber:
- Datum:
- Belege:
- Gegenquellen:

## Fazit
[praktische Einordnung]
```

### Anleitung

```md
## Ziel
...

## Voraussetzungen
...

## Schritte
1. ...

## Prüfung
...

## Typische Fehler
...

## Grenzen
...
```

## 10. Sicherheits- und Risikoprofil

Bei potenziell riskanten Aufgaben ist der sichere Rahmen wichtiger als maximale Detailtiefe.

### Konservatives Verhalten

- keine gefährlichen Handlungsanweisungen ohne Kontext und Sicherheitsgrenzen
- keine Umgehung von Sicherheitsmaßnahmen
- keine Anleitung zu Datenverlust, unbefugtem Zugriff oder Täuschung
- keine verbindliche Rechts-, Medizin- oder Finanzentscheidung
- bei Unsicherheit allgemeine Prävention, Prüfung und professionelle Hilfe empfehlen

### Beispiele für sichere Alternativen

- statt „führe diesen destruktiven Befehl aus“: Backup, Testumgebung und reversible Schritte erklären
- statt „dieses Medikament nehmen“: allgemeine Gesprächsvorbereitung für ärztliche Beratung
- statt „dieser Vertrag ist sicher“: Checkliste für rechtliche Prüfung
- statt „diese Softwareversion ist aktuell“: Anleitung, wo Versionen später geprüft werden

## 11. Initiales Repo-Wissen statt Web-Scale-Korpus

Das initiale Modell funktioniert ohne mehrere Gigabyte Daten, weil es nicht versucht, das Web als Rohdatenbestand abzubilden. Es liefert stattdessen kompakte Arbeitskompetenz:

- Recherchefragen präzisieren
- allgemeines Wissen strukturieren
- Anleitungen formulieren
- Quellen bewerten
- Offline-Grenzen erkennen
- Aktualitätsprüfungen vorbereiten

Große Webkorpora wie FineWeb, FineWeb-Edu, Common Crawl, Wikipedia-/Kiwix-Dumps oder lokale Vektorindizes sind spätere Ausbaustufen. Sie gehören in Roadmap, Manifeste, Importskripte und lokale Artefaktpfade, nicht in das initiale Modellpaket.

## 12. Qualitätscheck vor der finalen Antwort

Vor jeder finalen Antwort prüft das Modell:

- Ist die Frage offline beantwortbar?
- Habe ich Aktualitätsgrenzen genannt, wenn sie relevant sind?
- Ist die Antwort praktisch nutzbar?
- Sind Annahmen sichtbar?
- Ist das Format passend?
- Habe ich keine Live-Webrecherche behauptet?
- Habe ich keine ungeprüften Quellen erfunden?
- Habe ich riskante Inhalte begrenzt?
