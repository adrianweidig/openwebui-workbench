# Index: Offline-Problemfälle für OpenWebUI Model Builder

Diese Sammlung enthält Markdown-Briefings, die direkt als Eingabe für den Custom GPT **„OpenWebUI Model Builder“** genutzt werden können.

## Globale Leitplanken

- Basismodell in OpenWebUI: `coder`
- Reale technische Grundlage: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Zielumgebung: offline / intern / ohne Internetzugriff
- Keine Websuche
- Keine RAGFlow- oder externe RAG-Abhängigkeit
- Keine Knowledge-Base-Pflicht
- Jupyter/Python-Code-Interpreter ist verfügbar und soll für passende Problemfälle aktiv genutzt werden
- Vision/Bildanalyse nicht voraussetzen
- Jede Datei beschreibt einen allgemein verständlichen Problemfall, damit Nutzer in OpenWebUI das passende Aufgabenmodell anhand ihres Problems auswählen können

## Auswahlhilfe

| Datei | Modellname | Wann auswählen? |
|---|---|---|

| `01_dokumentenanalyse.md` | Dokumentenanalyse | Nutzer haben ein oder mehrere Dokumente und möchten Inhalte, Struktur, Risiken, offene Punkte, Widersprüche oder Entscheidungsgrundlagen verstehen. |
| `02_dokumentenzusammenfassung.md` | Dokumentenzusammenfassung | Nutzer möchten lange Dokumente, Protokolle, Berichte oder Richtlinien schnell in verständliche Kurzfassungen, Executive Summaries oder Stichpunktlisten überführen. |
| `03_dokumentenvergleich.md` | Dokumentenvergleich | Nutzer möchten zwei oder mehrere Dokumente, Versionen, Angebote, Vertragsentwürfe, Spezifikationen oder Richtlinien vergleichen. |
| `04_informationsextraktion.md` | Informationsextraktion | Nutzer möchten aus unstrukturierten Dokumenten strukturierte Informationen wie Namen, Daten, Fristen, Beträge, Aufgaben, Risiken oder Entitäten extrahieren. |
| `05_dokumentengenerierung.md` | Dokumentengenerierung | Nutzer möchten aus Stichpunkten, Gesprächsnotizen, Tabellen oder Vorgaben professionelle Dokumente erzeugen. |
| `06_präsentationserstellung.md` | Präsentationserstellung | Nutzer möchten aus Informationen, Dokumenten oder Stichpunkten eine Präsentationsstruktur oder direkt eine PPTX-Datei erzeugen. |
| `07_tabellen-csv-datenanalyse.md` | Tabellen- und CSV-Datenanalyse | Nutzer möchten CSV-, XLSX- oder tabellarische Daten offline untersuchen, bereinigen, aggregieren, visualisieren und interpretieren. |
| `08_report-dashboard-vorbereitung.md` | Report- und Dashboard-Vorbereitung | Nutzer möchten aus Daten oder Statusinformationen einen strukturierten Bericht, KPI-Report oder eine Dashboard-Grundlage erzeugen. |
| `09_codegenerierung.md` | Codegenerierung | Nutzer möchten aus einer Beschreibung lauffähigen, verständlichen und wartbaren Code erzeugen. |
| `10_codeanalyse.md` | Codeanalyse | Nutzer möchten bestehenden Code verstehen, Abhängigkeiten erkennen, Risiken finden oder Architektur und Datenflüsse erklären lassen. |
| `11_code-review.md` | Code-Review | Nutzer möchten Code systematisch gegen Qualität, Lesbarkeit, Sicherheit, Fehlerbehandlung, Performance und Wartbarkeit prüfen. |
| `12_debugging-fehleranalyse.md` | Debugging und Fehleranalyse | Nutzer möchten Fehler, Exceptions, Stacktraces, unerwartetes Verhalten oder kaputte Skripte systematisch analysieren. |
| `13_testfall-generierung.md` | Testfall-Generierung | Nutzer möchten aus Anforderungen oder Code sinnvolle Unit-, Integrations-, Regression- oder Akzeptanztests ableiten. |
| `14_code-dokumentation.md` | Code-Dokumentation | Nutzer möchten vorhandenen oder neuen Code verständlich dokumentieren: README, API-Doku, Funktionskommentare, Architekturhinweise. |
| `15_refactoring-unterstützung.md` | Refactoring-Unterstützung | Nutzer möchten bestehenden Code lesbarer, modularer, sicherer oder wartbarer machen, ohne fachliches Verhalten unbeabsichtigt zu ändern. |
| `16_api-schnittstellenentwurf.md` | API- und Schnittstellenentwurf | Nutzer möchten eine API, Datenstruktur, Request/Response-Schemata oder Schnittstellendokumentation entwerfen. |
| `17_json-csv-log-analyse.md` | JSON-, CSV- und Log-Analyse | Nutzer möchten strukturierte Dateien, Logs, Fehlermuster, Events oder Datenströme offline untersuchen und auswerten. |
| `18_meeting-protokoll-auswertung.md` | Meeting-Protokoll-Auswertung | Nutzer möchten aus Notizen oder Transkripten Entscheidungen, Aufgaben, Verantwortlichkeiten, Fristen und offene Fragen extrahieren. |
| `19_anforderungsanalyse-lastenheft.md` | Anforderungsanalyse und Lastenheft | Nutzer möchten Anforderungen aus Beschreibungen, Gesprächen oder Dokumenten strukturieren, klären und in Lastenheft-/Pflichtenheft-nahe Form bringen. |
| `20_support-ticket-vorbereitung.md` | Support-Ticket-Vorbereitung | Nutzer möchten unstrukturierte Supportanfragen in klare Tickets mit Kategorie, Priorität, Zusammenfassung, Rückfragen und Eskalationshinweisen umwandeln. |
| `21_it-helpdesk-diagnose.md` | IT-Helpdesk-Diagnose | Nutzer möchten IT-Probleme anhand von Symptomen, Logs und Systeminformationen strukturiert eingrenzen. |
| `22_prozess-workflow-dokumentation.md` | Prozess- und Workflow-Dokumentation | Nutzer möchten Abläufe, SOPs, Verantwortlichkeiten, Prozessschritte oder Entscheidungspunkte dokumentieren oder verbessern. |
| `23_email-kommunikationsassistenz.md` | E-Mail- und Kommunikationsassistenz | Nutzer möchten professionelle E-Mails, Antworten, interne Nachrichten, Zusammenfassungen oder Kommunikationsvarianten formulieren. |
| `24_übersetzung-lokalisierung.md` | Übersetzung und Lokalisierung | Nutzer möchten Texte übersetzen, vereinfachen, lokalisieren oder sprachlich an Zielgruppen anpassen. |
| `25_compliance-richtlinienprüfung.md` | Compliance- und Richtlinienprüfung | Nutzer möchten Inhalte gegen bereitgestellte interne Regeln, Checklisten, Datenschutzvorgaben oder Qualitätsrichtlinien prüfen. |
| `26_bewerbungsunterlagen-optimierung.md` | Bewerbungsunterlagen-Optimierung | Nutzer möchten Lebenslauf, Anschreiben oder Profiltexte verbessern, strukturieren oder auf eine konkrete Stelle zuschneiden. |
| `27_internetwissen.md` | Internetwissen | Nutzer möchten allgemeine Recherchefragen, Anleitungen, Erklärungen, Quellenkritik oder Wissensstrukturen offline ohne Live-Websuche bearbeiten. |

## Nutzung

1. Eine Datei auswählen, die dem gewünschten OpenWebUI-Problemfall entspricht.
2. Den Abschnitt **„Direkte Eingabe für den OpenWebUI Model Builder“** kopieren.
3. In den Custom GPT **„OpenWebUI Model Builder“** einfügen.
4. Das erzeugte Paket prüfen und in OpenWebUI importieren oder manuell anlegen.
5. Bei Bedarf die `model.json` gegen einen Export aus der eigenen OpenWebUI-Version abgleichen.

## Empfohlene erste Modelle

Für einen allgemeinen internen Start eignen sich besonders:

1. Dokumentenanalyse
2. Dokumentengenerierung
3. Präsentationserstellung
4. Tabellen- und CSV-Datenanalyse
5. Codegenerierung
6. Codeanalyse
7. Code-Review
8. Debugging und Fehleranalyse
9. Meeting-Protokoll-Auswertung
10. Support-Ticket-Vorbereitung
