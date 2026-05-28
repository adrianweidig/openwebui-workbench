# Custom-Model-Qualitätsinventar

Stand: 2026-05-28

Dieses Inventar priorisiert die Offline-Verbesserung der Custom-Modelle. Es ist bewusst knapp gehalten und dient als Arbeitsliste für weitere Batches.

| Modellordner | Zweck | Wichtige Dateien | Hauptproblem | Geeignetes Beispielergebnis-Format | Priorität | Bearbeitungsstatus |
|---|---|---|---|---|---|---|
| `allgemein` | Routing, Assistenz- und Fallback-Modus | `model.json`, Prompts, `fachwissen.md`, Beispiele | nicht vertieft geprüft | `.md` | P2 | offen |
| `anforderungsanalyse-lastenheft` | Anforderungen, Lastenheft, Pflichtenheft-Vorarbeit | `fachwissen.md`, Beispiele, `beispielergebnis.md` | Beispiel- und Schemaqualität prüfen | `.md` | P1 | offen |
| `api-schnittstellenentwurf` | API-Design und Schnittstellenspezifikation | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.yaml`, Beispiele, `model.json` | OpenAPI-YAML-Goldstandard, Fehlervertrag und Schema-Regeln ergänzt | `.yaml`, `.json`, `.md` | P1 | Batch 5 fertig |
| `code-dokumentation` | Code erklären und dokumentieren | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | Diátaxis-nahe Dokuarten, belegte Codebeispiele und Pflegehinweise ergänzt | `.md` | P1 | Batch 4 fertig |
| `code-review` | Defensives Code-Review | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | Findings-first-Review, Security-Grenzen und konkrete Testlücken ergänzt | `.md` | P1 | Batch 4 fertig |
| `codeanalyse` | Statische und semantische Codeanalyse | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | Fakten-/Hypothesentrennung, Hotspots und lokale Prüfpfade ergänzt | `.md`, `.json` | P1 | Batch 4 fertig |
| `codegenerierung` | Code erzeugen | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.py`, Beispiele, Scripts | Markdown-Goldstandard durch ausführbares Python-Offline-Artefakt ersetzt | `.py`, ergänzend `.md` | P1 | Batch 4 fertig |
| `compliance-richtlinienprüfung` | Richtlinien- und Compliance-Prüfung | `fachwissen.md`, Beispiele | sensible Domäne, Nachweis- und Normenrisiko | `.md` | P1 | offen |
| `debugging-fehleranalyse` | Fehleranalyse und Debugging | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | Hypothesenmatrix, sichere Checks und Runbook-Format ergänzt | `.md`, `.py`, `.txt` | P1 | Batch 4 fertig |
| `dokumentenanalyse` | Dokumente analysieren | `fachwissen.md`, Beispiele | Zitations- und Faktentrennung prüfen | `.md`, `.json` | P1 | offen |
| `dokumentengenerierung` | Dokumente erstellen | `fachwissen.md`, Beispiele | Goldstandard-Dokumente und Zielformate prüfen | `.md`, optional `.html` | P1 | offen |
| `dokumentenvergleich` | Dokumente vergleichen | `fachwissen.md`, Beispiele | Vergleichsmatrix und Konfliktlogik prüfen | `.md`, `.csv` | P1 | offen |
| `dokumentenzusammenfassung` | Dokumente zusammenfassen | `fachwissen.md`, Beispiele | Quellenbindung und Auslassungsrisiko prüfen | `.md` | P1 | offen |
| `email-kommunikationsassistenz` | E-Mails formulieren und prüfen | `fachwissen.md`, Beispiele | Phishing- und Social-Engineering-Grenzen prüfen | `.md`, `.txt` | P1 | offen |
| `informationsextraktion` | Strukturierte Extraktion | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.json`, Beispiele | valides JSON mit Belegen, Normalisierung und Unsicherheiten ergänzt | `.json`, `.csv`, `.md` | P1 | Batch 5 fertig |
| `internetwissen` | Offline-Recherche, Quellenkritik, Aktualitätsgrenzen | `fachwissen.md`, `beispielergebnis.md`, Beispiele | Generator- und Toolprofil fehlten | `.md` | P1 | Basis integriert |
| `it-helpdesk-diagnose` | IT-Support-Diagnose | `fachwissen.md`, Beispiele | Sicherheits- und Eskalationslogik prüfen | `.md` | P1 | offen |
| `json-csv-log-analyse` | Strukturierte Daten- und Loganalyse | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.json`, Beispiele | Parsingstatus, Datenqualitätsfindings und lokale Checks ergänzt | `.json`, `.csv`, `.md` | P1 | Batch 5 fertig |
| `meeting-protokoll-auswertung` | Protokolle, Aufgaben, Entscheidungen | `fachwissen.md`, Beispiele | Aktionslisten- und Entscheidungsformat prüfen | `.md`, `.csv` | P1 | offen |
| `mistral-vision-workbench` | Vision- und Screenshot-Analyse | `fachwissen.md`, Beispiele, HTML-Demo | visuelle QA und Grenzen prüfen | `.md`, `.html` | P1 | offen |
| `n8n-workflow-architect` | n8n-Workflow-Design | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.json`, Beispiele, `model.json` | Markdown-Goldstandard durch importierbares Workflow-JSON ersetzen | `.json` | P0 | Batch 2 fertig |
| `offline-workbench-agent` | lokale Workbench-Orchestrierung | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele, Tools | Tool-Wellen, Artefaktmanifest und Offline-Fallbacks geschärft | `.md`, ergänzend `.json`, `.html`, `.zip` | P0 | Batch 3 fertig |
| `openwebui-model-builder` | OpenWebUI-Modellpakete erzeugen | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | vollständiges Modellpaket mit kurzem Bootloader und Importcheck ergänzt | `.md` als Paketcontainer, enthaltenes `.json` | P0 | Batch 3 fertig |
| `promptforge` | Promptvorlagen erzeugen | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | Goldstandard-Promptvorlage ohne Platzhalter und robuste Few-Shots ergänzt | `.md` | P0 | Batch 3 fertig |
| `prozess-workflow-dokumentation` | Prozesse und Workflows dokumentieren | `fachwissen.md`, Beispiele | Diagramm- und Tabellenmuster prüfen | `.md`, optional `.svg` | P1 | offen |
| `präsentationserstellung` | browserbasierte HTML-Keynotes | `fachwissen.md`, `mainprompt.md`, `systemprompt.md`, `beispielergebnis.html`, Beispiele, Scripts | Markdown-Goldstandard durch fertiges HTML-Artefakt ersetzen | `.html` | P0 | Batch 1 fertig |
| `refactoring-unterstützung` | Code-Refactoring | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | Verhaltenserhalt, Invarianten, Charakterisierungstests und Rollback ergänzt | `.md`, `.diff`, `.py` | P1 | Batch 4 fertig |
| `report-dashboard-vorbereitung` | Reports und Dashboard-Vorbereitung | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.html`, Beispiele | offline HTML-Dashboard-Prototyp, KPI-Definition und Datenqualitätsregeln ergänzt | `.html`, `.csv`, `.md` | P1 | Batch 5 fertig |
| `support-ticket-vorbereitung` | Supportfälle strukturieren | `fachwissen.md`, Beispiele | Datenschutz und Eskalation prüfen | `.md`, `.json` | P1 | offen |
| `tabellen-csv-datenanalyse` | Tabellen- und CSV-Analyse | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.py`, Beispiele | ausführbares CSV-Profiling-Artefakt und reproduzierbare Analyse-Regeln ergänzt | `.py`, `.csv`, `.ipynb`, `.md` | P1 | Batch 5 fertig |
| `testfall-generierung` | Testfälle erzeugen | `fachwissen.md`, `mainprompt.md`, `beispielergebnis.md`, Beispiele | Risikobasierte Testmatrix, negative Fälle und Offline-Fixtures ergänzt | `.md`, `.csv`, `.py` | P1 | Batch 4 fertig |
| `übersetzung-lokalisierung` | Übersetzung und Lokalisierung | `fachwissen.md`, Beispiele, i18n | Terminologie- und Locale-Regeln prüfen | `.md`, `.json`, `.csv` | P1 | offen |
