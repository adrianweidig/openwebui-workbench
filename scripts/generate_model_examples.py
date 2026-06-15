#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
EXAMPLE_DIR = "beispiele"


MODEL_EXAMPLES: dict[str, dict[str, str]] = {
    "allgemein": {
        "purpose": "Freie oder gemischte Nutzerprobleme einordnen, passende Spezialmodelle empfehlen und mit dem kleinsten ausreichenden Tool-Satz direkt bearbeiten.",
        "artifact": "allgemein-arbeitsauftrag-vorlage.md",
        "scenario": "Ein Nutzer beschreibt ein unscharfes Problem mit Dateien, Screenshots und Zielartefakt, weiß aber nicht, welches Modell passt.",
        "vision": "Nutze Vision für Screenshots, Whiteboards, Fehlermeldungen, UI-Zustände oder fotografierte Notizen; wenn kein Bildzugriff besteht, fordere OCR oder eine Beschreibung an.",
        "quality": "Das Ergebnis muss Routing, Annahmen, Tool-Auswahl, konkrete Bearbeitung und nächste Schritte trennen.",
    },
    "anforderungsanalyse-lastenheft": {
        "purpose": "Anforderungen, Ziele, Nicht-Ziele, Stakeholder, Akzeptanzkriterien und Lastenheft-Struktur professionell ausarbeiten.",
        "artifact": "lastenheft-vorlage.md",
        "scenario": "Aus Stichpunkten, Screenshots und Prozessnotizen soll ein befüllbares Lastenheft entstehen.",
        "vision": "Nutze Vision für Whiteboard-Fotos, Prozessskizzen, UI-Mockups oder abfotografierte Workshops.",
        "quality": "Jede Anforderung braucht Priorität, Akzeptanzkriterium, Quelle, Risiko und offenen Klärungspunkt.",
    },
    "api-schnittstellenentwurf": {
        "purpose": "API-Verträge, OpenAPI-Strukturen, Authentifizierung, Fehlerfälle und Integrationsgrenzen entwerfen oder prüfen.",
        "artifact": "api-design-goldstandard-briefing.md",
        "scenario": "Ein Team braucht aus Fachanforderungen einen belastbaren API-Entwurf mit Beispielpayloads.",
        "vision": "Nutze Vision für Architekturdiagramme, Swagger-Screenshots, Sequenzskizzen oder Fehlermasken.",
        "quality": "Endpunkte, Schemas, Fehlercodes, Security und Testfälle müssen zusammenpassen.",
    },
    "code-dokumentation": {
        "purpose": "Code, Module, Datenflüsse und Betriebswissen in wartbare Entwicklerdokumentation überführen.",
        "artifact": "code-dokumentation-goldstandard-briefing.md",
        "scenario": "Ein Repository soll mit Einstieg, Architektur, Komponenten und Betriebsnotizen dokumentiert werden.",
        "vision": "Nutze Vision für Architekturdiagramme, UI-Screenshots oder visuelle Ablaufgrafiken im Repo-Kontext.",
        "quality": "Die Dokumentation muss Dateipfade, Verantwortlichkeiten, Beispiele und Pflegehinweise enthalten.",
    },
    "code-review": {
        "purpose": "Diffs, Risiken, Regressionen, Sicherheitsprobleme und fehlende Tests wie in einem professionellen Review priorisieren.",
        "artifact": "code-review-goldstandard-briefing.md",
        "scenario": "Ein Patch soll mit Findings, Schweregrad, Repro-Hinweis und Testlücken bewertet werden.",
        "vision": "Nutze Vision für UI-Regressionsscreenshots, Vorher-/Nachher-Bilder oder visuelle Testfehler.",
        "quality": "Findings stehen vor Zusammenfassung und referenzieren konkrete Dateien, Zeilen oder sichtbare UI-Zustände.",
    },
    "codeanalyse": {
        "purpose": "Codebasen, Abhängigkeiten, Kontrollflüsse, Risiken und technische Ursachen strukturiert analysieren.",
        "artifact": "codeanalyse-goldstandard-briefing.md",
        "scenario": "Eine unklare Codebasis soll mit Architektur, Hotspots und Hypothesen verstanden werden.",
        "vision": "Nutze Vision für Architektur-Screenshots, UI-Flows oder Diagramme, die Codeverhalten erklären.",
        "quality": "Trenne belegte Fakten aus Code/Tool-Ausgaben von Hypothesen und empfohlenen Messungen.",
    },
    "codegenerierung": {
        "purpose": "Bestehende Muster erkennen, zielgenauen Code erzeugen und lokale Validierung oder Tests vorbereiten.",
        "artifact": "codegenerierung-goldstandard-briefing.md",
        "scenario": "Aus einer Featurebeschreibung soll ein implementierbarer Patchplan mit Tests entstehen.",
        "vision": "Nutze Vision für UI-Mockups, Design-Screenshots, Formularzustände oder Fehlanzeigen.",
        "quality": "Der Plan muss Dateien, Schnittstellen, Testfälle, Risiken und Rollback-Punkte nennen.",
    },
    "compliance-richtlinienprüfung": {
        "purpose": "Richtlinien, Nachweise, Kontrollen und Abweichungen nachvollziehbar prüfen.",
        "artifact": "compliance-pruefbericht-vorlage.md",
        "scenario": "Ein Prozess oder Dokumentensatz soll gegen interne Richtlinien bewertet werden.",
        "vision": "Nutze Vision für gescannte Nachweise, UI-Screenshots von Einstellungen oder Kontroll-Dashboards.",
        "quality": "Jede Abweichung braucht Quelle, Risiko, Empfehlung, Verantwortlichkeit und Nachweisstatus.",
    },
    "debugging-fehleranalyse": {
        "purpose": "Fehlertexte, Logs, Screenshots, Reproduktionsschritte und Konfigurationen zu einer belastbaren Ursache führen.",
        "artifact": "debugging-goldstandard-briefing.md",
        "scenario": "Ein OpenWebUI-, Docker- oder App-Fehler soll reproduzierbar eingegrenzt werden.",
        "vision": "Nutze Vision für Fehlermeldungs-Screenshots, UI-Zustände, Browser-Konsole oder visuelle Regressionsbilder.",
        "quality": "Hypothesen müssen priorisiert, prüfbar und mit nächstem Diagnosebefehl verbunden sein.",
    },
    "dokumentenanalyse": {
        "purpose": "Dokumente, Scans, PDFs und strukturierte Inhalte quellenorientiert analysieren.",
        "artifact": "dokumentenanalyse-vorlage.md",
        "scenario": "Ein Vertrag, Bericht oder Scan soll mit Kernaussagen, Risiken und Belegstellen analysiert werden.",
        "vision": "Nutze Vision für gescannte Seiten, Fotos, Stempel, Tabellenbilder oder visuelle Markierungen.",
        "quality": "Kernaussagen, Belege, Unsicherheiten und extrahierte Daten müssen getrennt bleiben.",
    },
    "dokumentengenerierung": {
        "purpose": "Strukturierte, direkt nutzbare Dokumente, HTML/PDF-Artefakte und Vorlagen erzeugen.",
        "artifact": "dokument-generator-vorlage.md",
        "scenario": "Aus Stichpunkten soll ein auslieferbares Dokument mit Deckblatt, Struktur und Platzhaltern entstehen.",
        "vision": "Nutze Vision für Corporate-Design-Screenshots, Layoutbeispiele, Diagramme oder handschriftliche Skizzen.",
        "quality": "Das Ergebnis muss befüllbar, konsistent formatiert und offline weiterverwendbar sein.",
    },
    "dokumentenvergleich": {
        "purpose": "Dokumentversionen, Textvarianten, Tabellen und Scans nachvollziehbar vergleichen.",
        "artifact": "dokumentenvergleich-matrix-vorlage.md",
        "scenario": "Zwei Versionen eines Dokuments sollen mit inhaltlichen und strukturellen Unterschieden verglichen werden.",
        "vision": "Nutze Vision für gescannte Versionen, markierte PDFs, Layoutabweichungen oder Screenshotvergleiche.",
        "quality": "Unterschiede müssen nach Relevanz, Quelle, Risiko und empfohlener Aktion sortiert sein.",
    },
    "dokumentenzusammenfassung": {
        "purpose": "Lange Dokumente, Scans und Protokolle zu belastbaren, quellenklaren Kurzfassungen verdichten.",
        "artifact": "executive-summary-vorlage.md",
        "scenario": "Ein langer Bericht soll als Management Summary mit Entscheidungen und Risiken zusammengefasst werden.",
        "vision": "Nutze Vision für gescannte Seiten, Diagramme, Infografiken oder fotografierte Unterlagen.",
        "quality": "Zusammenfassung, Entscheidungen, Zahlen, Risiken und offene Punkte müssen klar getrennt sein.",
    },
    "email-kommunikationsassistenz": {
        "purpose": "E-Mails, Antworten, Eskalationen und Kommunikationsvorlagen präzise und adressatengerecht formulieren.",
        "artifact": "email-antwort-vorlage.md",
        "scenario": "Aus Kontext, Ziel und Tonalität soll eine sendefertige Antwort entstehen.",
        "vision": "Nutze Vision für E-Mail-Screenshots, Ticketmasken oder visuelle Kontextinformationen; maskiere sensible Daten.",
        "quality": "Ton, Ziel, Aktion, Frist, Anhänge und Risiken müssen explizit passen.",
    },
    "informationsextraktion": {
        "purpose": "Informationen aus Texten, Tabellen, Logs, Dokumenten und Bildern in ein definiertes Schema extrahieren.",
        "artifact": "informationsextraktion-goldstandard-briefing.md",
        "scenario": "Aus gemischten Quellen soll valides JSON mit Belegen und Unsicherheiten entstehen.",
        "vision": "Nutze Vision für Formularfotos, Tabellenbilder, Scans, Etiketten oder UI-Datenmasken.",
        "quality": "Jedes Feld braucht Quelle, Normalisierung, Unsicherheit und Validierungsregel.",
    },
    "internetwissen": {
        "purpose": "Offline-Wissensfragen, Quellenkritik, Aktualitätsgrenzen und Recherchepläne strukturiert bearbeiten, ohne Live-Webzugriff vorzutäuschen.",
        "artifact": "internetwissen-rechercheplan-vorlage.md",
        "scenario": "Ein Nutzer will ein zeitabhängiges oder quellennahes Thema verstehen und braucht eine belastbare Offline-Einordnung mit Prüffragen.",
        "vision": "Nutze Vision nur für sichtbare Quellen-Screenshots, Tabellen oder Webseitenausschnitte; markiere alles Nicht-Sichtbare als unbestätigt.",
        "quality": "Antworten trennen bekannte Fakten, Nutzerangaben, Annahmen, Aktualitätsrisiken, Quellenarten, Prüffragen und nächsten Recherchepfad.",
    },
    "it-helpdesk-diagnose": {
        "purpose": "IT-Probleme aus Nutzerbeschreibung, Screenshots, Logs und Konfigurationen schnell triagieren.",
        "artifact": "helpdesk-diagnose-vorlage.md",
        "scenario": "Ein Nutzer meldet ein Problem mit Screenshot und wenigen Symptomen.",
        "vision": "Nutze Vision für Fehlermasken, Taskleisten-/Tray-Zustände, Dialoge oder Netzwerksymbole.",
        "quality": "Antwort muss Sofortmaßnahmen, Rückfragen, Diagnosepfad und Eskalationskriterium enthalten.",
    },
    "json-csv-log-analyse": {
        "purpose": "JSON, CSV, Logs und strukturierte Textdaten validieren, analysieren und in klare Befunde überführen.",
        "artifact": "json-csv-log-analyse-goldstandard-briefing.md",
        "scenario": "Ein Logauszug und eine CSV sollen auf Fehler, Muster und Datenqualität geprüft werden.",
        "vision": "Nutze Vision nur für Screenshot-Logs oder Tabellenbilder; verlange Rohtext, wenn Genauigkeit nötig ist.",
        "quality": "Parsingstatus, Auffälligkeiten, Beispiele, betroffene Felder und Repro-Schritte müssen enthalten sein.",
    },
    "meeting-protokoll-auswertung": {
        "purpose": "Meetingnotizen, Mitschriften und Whiteboard-Fotos in Beschlüsse, Aufgaben und Risiken überführen.",
        "artifact": "meeting-auswertung-vorlage.md",
        "scenario": "Ein Workshopfoto und Stichpunkte sollen in ein handlungsfähiges Protokoll überführt werden.",
        "vision": "Nutze Vision für Whiteboards, Flipcharts, abfotografierte Post-its oder Folien.",
        "quality": "Aufgaben brauchen Owner, Termin, Kontext, Status und offene Klärung.",
    },
    "mistral-vision-workbench": {
        "purpose": "Bilder, Screenshots, UI-Zustände, Folien, Diagramme, Scans und visuelle Artefakte multimodal analysieren.",
        "artifact": "vision-ui-qa-vorlage.md",
        "scenario": "Ein UI-Screenshot oder eine HTML-Praesentation soll visuell geprüft und verbessert werden.",
        "vision": "Vision ist der Hauptpfad: sichtbare Fakten extrahieren, Unsicherheiten markieren und lokale Tools für Reproduktion oder Artefakte nutzen.",
        "quality": "Findings müssen sichtbar belegbar, priorisiert und mit konkretem Fix sowie Akzeptanzkriterium versehen sein.",
    },
    "n8n-workflow-architect": {
        "purpose": "Importierbare n8n-Workflows planen, validieren und mit Test- sowie Sicherheitshinweisen ausgeben.",
        "artifact": "n8n-workflow-goldstandard-briefing.md",
        "scenario": "Ein Integrationsziel soll in einen prüfbaren n8n-Workflow mit Nodes, Credentials und Fehlerpfad überführt werden.",
        "vision": "Nutze Vision für n8n-Canvas-Screenshots, Node-Konfigurationen oder Fehleranzeigen.",
        "quality": "Importierbares Workflow-JSON, Trigger, Datenvertrag, Fehlerbehandlung, Secrets und Testfälle müssen konsistent sein.",
    },
    "offline-workbench-agent": {
        "purpose": "Komplexe Offline-Aufgaben routen, Tools kombinieren und HTML/PDF/ZIP/Tabellen/Code-Artefakte lokal erzeugen.",
        "artifact": "offline-workbench-auftrag-goldstandard.md",
        "scenario": "Eine mehrteilige Aufgabe soll mit Jupyter, Artefakt-Tools und Validierung end-to-end erledigt werden.",
        "vision": "Nutze Vision für Screenshots, Artefakt-QA, Diagramme, UI-Zustände und visuelle Eingaben.",
        "quality": "Der Plan muss Tool-Wellen, Offline-Artefakte, Validierung, Sicherheitsgrenzen und Übergabeformat enthalten.",
    },
    "openwebui-model-builder": {
        "purpose": "Vollständige OpenWebUI-Modellpakete mit Prompt, Wissen, Tools, Skills, Icons, Importplan und QA erzeugen.",
        "artifact": "openwebui-modellpaket-goldstandard.md",
        "scenario": "Aus einer Modellidee soll ein importierbares OpenWebUI-Modellpaket entstehen.",
        "vision": "Nutze Vision für Icon-/UI-Screenshots, Custom-GPT-Referenzen oder Modellprofil-Mockups.",
        "quality": "Paket muss model.json, kurzen Bootloader-Systemprompt, mainprompt, fachwissen, Beispiel, Toolprofil und Importcheck enthalten.",
    },
    "präsentationserstellung": {
        "purpose": "Premium-Browser-Keynotes als einzelne offline lauffähige `präsentation.html` mit Interaktion, Animation und Designsystem erzeugen.",
        "artifact": "praesentation-goldstandard-briefing.md",
        "scenario": "Aus Thema und Stichpunkten soll eine moderne, interaktive HTML-Präsentation entstehen.",
        "vision": "Nutze Vision für Designreferenzen, Folien-Screenshots, Logo-/Layoutprüfung und visuelle Abnahme.",
        "quality": "Fertige offline lauffähige HTML-Keynote, Storyline, Inline-CSS, Vanilla-JavaScript, reduzierte Bewegung und responsive 16:9-Darstellung.",
    },
    "promptforge": {
        "purpose": "Erste Nutzerprompts nach Best Practices in direkt kopierbare, zielsystemspezifische Promptvorlagen optimieren.",
        "artifact": "promptforge-goldstandard-briefing.md",
        "scenario": "Ein roher Nutzerprompt soll für ChatGPT, Custom GPT, OpenWebUI oder lokale LLMs verbessert werden.",
        "vision": "Nutze Vision für Screenshots von Zieloberflächen, Prompt-Buildern, Fehlermeldungen oder Beispielausgaben.",
        "quality": "Promptvorlage muss Rolle, Ziel, Kontextnutzung, Rückfragenlogik, Ausgabeformat, Grenzen, Prüfregeln und Erfolgskriterien enthalten.",
    },
    "prozess-workflow-dokumentation": {
        "purpose": "Prozesse, Verantwortlichkeiten, Workflows, Diagramme und Betriebsübergaben dokumentieren.",
        "artifact": "prozessdokumentation-vorlage.md",
        "scenario": "Ein Prozess soll aus Stichpunkten, Skizzen und Rollen in eine klare Dokumentation überführt werden.",
        "vision": "Nutze Vision für BPMN-Skizzen, Whiteboards, Swimlanes, Prozessscreenshots oder Ablaufdiagramme.",
        "quality": "Schritte, Rollen, Systeme, Inputs, Outputs, Risiken und Diagramm müssen konsistent sein.",
    },
    "refactoring-unterstützung": {
        "purpose": "Refactoring-Ziele, Codebereiche, Risiken, Tests und schrittweise Umsetzung strukturieren.",
        "artifact": "refactoring-goldstandard-briefing.md",
        "scenario": "Ein Modul soll ohne Verhaltensbruch schrittweise umgebaut werden.",
        "vision": "Nutze Vision für UI-Verhaltensvergleiche, Architekturskizzen oder visuelle Regressionen.",
        "quality": "Plan braucht Scope, Nicht-Ziele, Reihenfolge, Tests, Rollback und Akzeptanzkriterien.",
    },
    "report-dashboard-vorbereitung": {
        "purpose": "Daten, Kennzahlen, Dashboard-Struktur, Visualisierungen und Storyline für Reports vorbereiten.",
        "artifact": "dashboard-goldstandard-briefing.md",
        "scenario": "Aus Daten und Zielgruppe soll ein Dashboard- oder Reportkonzept entstehen.",
        "vision": "Nutze Vision für Dashboard-Screenshots, Charts, Tabellenbilder oder Layoutreferenzen.",
        "quality": "Kennzahlen, Datenquellen, Visualtyp, Filter, Warnschwellen und Nutzerfragen müssen definiert sein.",
    },
    "support-ticket-vorbereitung": {
        "purpose": "Supportfälle aus Symptomen, Screenshots, Logs und Nutzertexten in klare Tickets überführen.",
        "artifact": "support-ticket-vorlage.md",
        "scenario": "Aus einem Chatverlauf und Screenshot soll ein eskalierbares Ticket entstehen.",
        "vision": "Nutze Vision für Fehlerscreenshots, Statusanzeigen, Dialoge oder betroffene UI-Elemente.",
        "quality": "Ticket braucht Kurzbeschreibung, Impact, Repro, Environment, Anhänge, Priorität und offene Fragen.",
    },
    "tabellen-csv-datenanalyse": {
        "purpose": "Tabellen und CSVs bereinigen, analysieren, validieren und in nachvollziehbare Ergebnisse überführen.",
        "artifact": "tabellen-csv-datenanalyse-goldstandard-briefing.md",
        "scenario": "Eine CSV soll mit Jupyter geprüft, bereinigt und zusammengefasst werden.",
        "vision": "Nutze Vision für fotografierte Tabellen oder Dashboard-Screenshots nur zur Orientierung; verlange Rohdaten für Berechnung.",
        "quality": "Analyse muss Schema, Datenqualität, Berechnung, Ergebnis und Reproduzierbarkeit enthalten.",
    },
    "testfall-generierung": {
        "purpose": "Aus Anforderungen, Code, UI-Screenshots und Risiken konkrete Testfälle und Akzeptanztests erzeugen.",
        "artifact": "testfall-generierung-goldstandard-briefing.md",
        "scenario": "Ein Feature soll mit funktionalen, negativen, UI- und Regressionstests abgesichert werden.",
        "vision": "Nutze Vision für UI-Screenshots, Fehlzustände, Formularlayouts und visuelle Akzeptanzkriterien.",
        "quality": "Testfälle brauchen Preconditions, Schritte, Testdaten, erwartetes Ergebnis und Priorität.",
    },
    "übersetzung-lokalisierung": {
        "purpose": "Texte, UI-Kopien, Dokumente und Lokalisierungsfragen zielgruppen- und kontextgerecht übertragen.",
        "artifact": "lokalisierungsauftrag-vorlage.md",
        "scenario": "UI-Texte und Screenshots sollen für eine Zielregion lokalisiert werden.",
        "vision": "Nutze Vision für UI-Screenshots, Kontext, abgeschnittene Texte oder Layoutprobleme nach Übersetzung.",
        "quality": "Ergebnis braucht Zielvariante, Tonalität, Platzhalter, Längenrisiken und QA-Hinweise.",
    },
}


def read_model_name(model_id: str) -> str:
    model_path = SINGLE_MODELS / model_id / "model.json"
    data = json.loads(model_path.read_text(encoding="utf-8"))
    return str(data[0].get("name") or model_id)


def fallback_example_config(model_id: str, name: str) -> dict[str, str]:
    slug = model_id.replace("_", "-")
    return {
        "purpose": f"Das Modell `{name}` soll lokale Nutzeraufträge strukturiert, quellenbewusst und ohne erfundene Fakten bearbeiten.",
        "artifact": f"{slug}-goldstandard-briefing.md",
        "scenario": f"Ein Nutzer benötigt ein prüfbares Ergebnis für den Aufgabenbereich `{name}` mit lokalem Kontext und optionalen Beispielen.",
        "vision": "Nutze Vision nur für bereitgestellte Screenshots, UI-Zustände, Scans oder Diagramme und markiere unsichere visuelle Beobachtungen.",
        "quality": "Das Ergebnis muss Quellen, Annahmen, offene Punkte, konkrete Arbeitsschritte und prüfbare Qualitätsgrenzen trennen.",
    }


EXAMPLE_RESULT_FILE_OVERRIDES = {
    "api-schnittstellenentwurf": "beispielergebnis.yaml",
    "codegenerierung": "beispielergebnis.py",
    "informationsextraktion": "beispielergebnis.json",
    "json-csv-log-analyse": "beispielergebnis.json",
    "n8n-workflow-architect": "beispielergebnis.json",
    "präsentationserstellung": "beispielergebnis.html",
    "report-dashboard-vorbereitung": "beispielergebnis.html",
    "tabellen-csv-datenanalyse": "beispielergebnis.py",
}

CODE_BATCH_STALE_EXAMPLES = {
    "code-dokumentation": ["code-dokumentation-vorlage.md"],
    "code-review": ["code-review-finding-vorlage.md"],
    "codeanalyse": ["codeanalyse-bericht-vorlage.md"],
    "codegenerierung": ["implementierungsplan-vorlage.md"],
    "debugging-fehleranalyse": ["debugging-runbook-vorlage.md"],
    "refactoring-unterstützung": ["refactoring-plan-vorlage.md"],
    "testfall-generierung": ["testfallkatalog-vorlage.md"],
}

CODE_BATCH_MODELS = set(CODE_BATCH_STALE_EXAMPLES)

DATA_BATCH_STALE_EXAMPLES = {
    "api-schnittstellenentwurf": ["api-design-vorlage.md"],
    "informationsextraktion": ["extraktionsschema-vorlage.md"],
    "json-csv-log-analyse": ["loganalyse-vorlage.md"],
    "report-dashboard-vorbereitung": ["dashboard-briefing-vorlage.md"],
    "tabellen-csv-datenanalyse": ["datenanalyse-notebook-plan-vorlage.md"],
}

DATA_BATCH_MODELS = set(DATA_BATCH_STALE_EXAMPLES)


def example_result_file_for_model(model_id: str) -> str:
    return EXAMPLE_RESULT_FILE_OVERRIDES.get(model_id, "beispielergebnis.md")


def example_markdown(model_id: str, name: str, config: dict[str, str]) -> str:
    example_result = example_result_file_for_model(model_id)
    return dedent(
        f"""\
        # Beispielergebnis: {name}

        Dieses Goldstandard-Beispiel zeigt eine direkt nutzbare Offline-Antwort des Modells `{model_id}`. Es nutzt nur sichtbare Nutzerinformationen, markiert Annahmen und vermeidet erfundene Quellen, Zahlen oder Dateiinhalte.

        ## Nutzeranfrage

        {config["scenario"]}

        ## Gute Antwort

        ### Kurzfazit

        Ich erstelle eine erste belastbare Fassung für diesen Auftrag: {config["purpose"]}

        Die Antwort bleibt offline nutzbar. Nicht bereitgestellte Fakten, aktuelle Versionen, Rechtsstände, Kennzahlen, Dateiinhalte oder Toolausgaben werden nicht ergänzt.

        ### Annahmen

        - Die Sprache bleibt Deutsch.
        - Der Auftrag basiert auf den vom Nutzer bereitgestellten Stichpunkten, Dateien oder Screenshots.
        - Fehlende Pflichtinformationen werden als offen markiert statt erfunden.
        - Falls Bilder oder Screenshots fehlen, wird nur mit Text gearbeitet und Vision nicht vorgetäuscht.

        ### Arbeitsprodukt

        | Abschnitt | Inhalt |
        |---|---|
        | Ziel | {config["purpose"]} |
        | Eingangsquellen | Nutzertext, bereitgestellte Dateien und sichtbare Bildinhalte; keine Live-Websuche |
        | Zielformat | `{example_result}`; ergänzendes Few-Shot-Material in `beispiele/{config["artifact"]}` |
        | Kernstruktur | Kurzfazit, verwendete Quellen, Hauptteil, Risiken, offene Punkte, nächste Schritte |
        | Prüflogik | {config["quality"]} |
        | Offline-Grenze | Aktuelle externe Fakten werden als prüfpflichtig markiert |

        ### Musterabschnitt für das Ergebnis

        #### Verwendete Informationen

        - Direkt aus der Anfrage übernommen: {config["scenario"]}
        - Sichtbare Zusatzquellen: nur berücksichtigen, wenn sie im Chat oder als Datei vorliegen.
        - Nicht belegt: externe Aktualität, nicht bereitgestellte Dateien, interne Kennzahlen und fremde Systeme.

        #### Ergebnisentwurf

        1. Den Auftrag in das passende Zielformat überführen.
        2. Belegte Inhalte und Annahmen getrennt darstellen.
        3. Risiken und offene Punkte so formulieren, dass ein Mensch sie prüfen kann.
        4. Mit einem konkreten nächsten Schritt schließen, der lokal ausführbar ist.

        ### Vision- und Screenshot-Regel

        {config["vision"]}

        ### Qualitätscheck

        - {config["quality"]}
        - Keine erfundenen Quellen, Dateien, Kennzahlen oder Toolergebnisse.
        - Keine Secrets, produktiven Tokens oder personenbezogenen Beispieldaten.
        - Offline weiterverwendbar.

        ## Warum dieses Beispiel gut ist

        - Es zeigt das gewünschte Arbeitsmuster ohne Platzhalter.
        - Es trennt belegte Informationen und Annahmen.
        - Es macht Offline-Grenzen explizit.
        - Es verweist auf das echte Beispielartefakt.
        """
    )


def n8n_workflow_goldstandard() -> dict[str, object]:
    return {
        "name": "Offline Intake Review - sichere API-Freigabe",
        "nodes": [
            {
                "parameters": {},
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [-760, 0],
                "id": "0b1b8c2e-0d3f-4f5b-8f09-694f0a6a1001",
                "name": "When clicking 'Test workflow'",
            },
            {
                "parameters": {
                    "jsCode": "\n".join(
                        [
                            "const requests = [",
                            "  {",
                            "    requestId: 'REQ-2026-001',",
                            "    requesterEmail: 'teamlead@example.invalid',",
                            "    targetSystem: 'internal-ticketing',",
                            "    action: 'prepare-ticket-update',",
                            "    dataSensitivity: 'internal',",
                            "    approvedForAutomation: false,",
                            "    summary: 'Routingregel für Kategorie Hardware prüfen',",
                            "    payload: {",
                            "      ticketId: 'TCK-1001',",
                            "      category: 'Hardware',",
                            "      priority: 'medium'",
                            "    }",
                            "  }",
                            "];",
                            "",
                            "return requests.map((request) => ({ json: request }));",
                        ]
                    )
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [-520, 0],
                "id": "0b1b8c2e-0d3f-4f5b-8f09-694f0a6a1002",
                "name": "Beispieldaten laden",
            },
            {
                "parameters": {
                    "jsCode": "\n".join(
                        [
                            "const requiredFields = [",
                            "  'requestId',",
                            "  'requesterEmail',",
                            "  'targetSystem',",
                            "  'action',",
                            "  'dataSensitivity',",
                            "  'payload'",
                            "];",
                            "const sensitiveClasses = new Set(['personal', 'confidential', 'secret']);",
                            "",
                            "return $input.all().map((item) => {",
                            "  const source = item.json;",
                            "  const missing = requiredFields.filter((field) => source[field] === undefined || source[field] === null || source[field] === '');",
                            "  const action = String(source.action || '').toLowerCase();",
                            "  const dataSensitivity = String(source.dataSensitivity || '').toLowerCase();",
                            "  const riskyAction = /delete|close|send|create-user|payment|admin/.test(action);",
                            "  const needsHumanReview = riskyAction || source.approvedForAutomation !== true || sensitiveClasses.has(dataSensitivity);",
                            "",
                            "  return {",
                            "    json: {",
                            "      ...source,",
                            "      validation: {",
                            "        valid: missing.length === 0,",
                            "        missing,",
                            "        riskyAction,",
                            "        needsHumanReview",
                            "      }",
                            "    }",
                            "  };",
                            "});",
                        ]
                    )
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [-260, 0],
                "id": "0b1b8c2e-0d3f-4f5b-8f09-694f0a6a1003",
                "name": "Eingabe validieren",
            },
            {
                "parameters": {
                    "jsCode": "\n".join(
                        [
                            "return $input.all().map((item) => {",
                            "  const data = item.json;",
                            "  let status = 'ready_for_dry_run';",
                            "  let nextStep = 'Interne API in Testumgebung mit Credential-Platzhalter zuordnen.';",
                            "",
                            "  if (!data.validation.valid) {",
                            "    status = 'blocked_missing_fields';",
                            "    nextStep = `Fehlende Pflichtfelder ergänzen: ${data.validation.missing.join(', ')}`;",
                            "  } else if (data.validation.needsHumanReview) {",
                            "    status = 'needs_human_review';",
                            "    nextStep = 'Menschliche Freigabe einholen; Workflow führt noch keine produktive Aktion aus.';",
                            "  }",
                            "",
                            "  return {",
                            "    json: {",
                            "      requestId: data.requestId,",
                            "      status,",
                            "      nextStep,",
                            "      safePayload: {",
                            "        targetSystem: data.targetSystem,",
                            "        action: data.action,",
                            "        summary: data.summary,",
                            "        ticketId: data.payload.ticketId || null,",
                            "        category: data.payload.category || null,",
                            "        priority: data.payload.priority || null",
                            "      },",
                            "      validation: data.validation",
                            "    }",
                            "  };",
                            "});",
                        ]
                    )
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [0, 0],
                "id": "0b1b8c2e-0d3f-4f5b-8f09-694f0a6a1004",
                "name": "Freigabeentscheidung vorbereiten",
            },
            {
                "parameters": {
                    "jsCode": "\n".join(
                        [
                            "return $input.all().map((item) => ({",
                            "  json: {",
                            "    auditId: `audit-${item.json.requestId}`,",
                            "    generatedAt: new Date().toISOString(),",
                            "    workflowMode: 'dry-run',",
                            "    status: item.json.status,",
                            "    nextStep: item.json.nextStep,",
                            "    safePayload: item.json.safePayload,",
                            "    safety: {",
                            "      noSecretsInWorkflow: true,",
                            "      productiveActionExecuted: false,",
                            "      humanReviewRequired: item.json.validation.needsHumanReview",
                            "    }",
                            "  }",
                            "}));",
                        ]
                    )
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [260, 0],
                "id": "0b1b8c2e-0d3f-4f5b-8f09-694f0a6a1005",
                "name": "Audit-Record erzeugen",
            },
        ],
        "pinData": {},
        "connections": {
            "When clicking 'Test workflow'": {
                "main": [[{"node": "Beispieldaten laden", "type": "main", "index": 0}]]
            },
            "Beispieldaten laden": {
                "main": [[{"node": "Eingabe validieren", "type": "main", "index": 0}]]
            },
            "Eingabe validieren": {
                "main": [[{"node": "Freigabeentscheidung vorbereiten", "type": "main", "index": 0}]]
            },
            "Freigabeentscheidung vorbereiten": {
                "main": [[{"node": "Audit-Record erzeugen", "type": "main", "index": 0}]]
            },
        },
        "active": False,
        "settings": {"executionOrder": "v1"},
        "tags": [],
    }


def n8n_workflow_goldstandard_json() -> str:
    return json.dumps(n8n_workflow_goldstandard(), ensure_ascii=False, indent=2) + "\n"


def n8n_workflow_goldstandard_briefing() -> str:
    return dedent(
        """\
        # Beispiele: n8n Workflow Architect

        Diese Beispiele zeigen, wie das Modell aus Anforderungen importierbare n8n-Workflow-JSONs erzeugt, ohne Secrets, Cloud-Annahmen oder nicht geprüfte Node-Parameter zu erfinden. Das primäre Goldstandard-Artefakt liegt als `../beispielergebnis.json` vor.

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Erstelle einen n8n-Workflow, der eine interne Anfrage prüft und noch keine produktive Aktion ausführt.

        ### Gute Antwort

        Ich arbeite mit diesen Annahmen: n8n self-hosted oder lokal, Start per Manual Trigger, keine externen Dienste, keine Credentials im JSON, produktive Aktion nur nach menschlicher Freigabe.

        Passendes Ergebnis:

        - `beispielergebnis.json` als importierbarer Workflow,
        - Manual Trigger zum sicheren Test,
        - Code Nodes für Testdaten, Pflichtfeldprüfung, Freigabeentscheidung und Audit-Record,
        - `active: false`,
        - keine Secrets, keine externen URLs, keine Credential-IDs.

        ### Warum dieses Beispiel gut ist

        - Liefert JSON statt nur Beschreibung.
        - Nutzt sichere Offline-Bausteine.
        - Trennt Dry-Run, Validierung und Freigabe.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        Baue einen Workflow für Ticket-Routing: Webhook oder manuelles Testen, Pflichtfelder prüfen, Kategorie ableiten, bei unsicheren Fällen Kommentar vorbereiten. Keine Tickets automatisch schließen.

        ### Gute Antwort

        Der Workflow sollte in zwei Varianten gedacht werden:

        - Testvariante mit Manual Trigger und Beispielpayload,
        - produktive Variante mit Webhook Trigger, sobald Base-URL, Authentifizierung und Datenvertrag bekannt sind.

        Sicherheitsentscheidung: Ticketstatus wird nicht geändert. Der Workflow erzeugt nur Routingvorschlag, Begründung und Audit-Daten. Credentials werden nach Import im n8n UI zugeordnet.

        ### Warum dieses Beispiel gut ist

        - Produktive Aktion wird abgesichert.
        - Fehlende Hosting-Details blockieren nicht den Testentwurf.
        - Datenvertrag und Freigabe bleiben sichtbar.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Erstelle einen Self-hosted-n8n-Workflow für eine interne API, lokale LLM-Klassifikation und spätere Benachrichtigung. n8n läuft in Docker, Internet ist nicht verfügbar.

        ### Gute Antwort

        Vorgehen:

        1. Keine SaaS- oder OAuth-Nodes verwenden.
        2. Interne Endpunkte als Platzhalter aus n8n-Containersicht dokumentieren.
        3. Lokale LLM-URL nicht raten; `http://ollama:11434` nur verwenden, wenn der Service aus dem n8n-Netz erreichbar ist.
        4. HTTP Request Nodes erst nach bestätigtem Datenvertrag ausgeben oder als prüfpflichtig markieren.
        5. Fehlerpfad und Human-in-the-loop vor jede schreibende Aktion setzen.

        ### Warum dieses Beispiel gut ist

        - Beachtet Docker-Netzwerksicht.
        - Vermeidet Internetannahmen.
        - Schützt vor blindem API-Schreiben.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Mach einen n8n-Workflow für unsere API.

        ### Gute Antwort

        Ich kann einen sicheren Startworkflow erstellen, brauche für ein produktives API-JSON aber noch: Hosting-Modell, Trigger, API-Ziel, Authentifizierungsart, Datenvertrag und ob geschrieben werden darf.

        Bis dahin liefere ich eine importierbare Dry-Run-Version mit Manual Trigger, Beispielpayload, Validierung und Audit-Ausgabe. Externe API-Nodes bleiben bewusst draußen.

        ### Warum dieses Beispiel gut ist

        - Fragt nicht breit, sondern grenzt produktive Risiken ein.
        - Liefert trotzdem ein nutzbares Offline-Artefakt.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Erstelle einen Cloud-n8n-Workflow, der lokale Dateien unter `C:\\Daten` überwacht und bei Änderung verarbeitet.

        ### Gute Antwort

        Konflikt erkannt: n8n Cloud kann lokale Host-Dateipfade nicht überwachen. Saubere Optionen:

        - Self-hosted n8n mit Local File Trigger, wenn Dateizugriff ausdrücklich erlaubt ist.
        - Cloud-kompatibler Ansatz über Webhook, Cloud Storage oder manuelle Dateiübergabe.

        Ich erstelle keinen Cloud-Workflow mit `C:\\Daten`, weil der Pfad aus n8n Cloud nicht erreichbar ist.

        ### Warum dieses Beispiel gut ist

        - Erkennt Hosting-Konflikt.
        - Verhindert importierbare, aber nicht lauffähige Fantasie-Workflows.

        ## Beispiel 6: Sicherheits- oder Qualitätsgrenze

        ### Nutzeranfrage

        Baue einen Workflow, der fremde Logins einsammelt und an einen privaten Webhook sendet.

        ### Gute Antwort

        Dabei helfe ich nicht, weil der Workflow Credential-Abgriff und heimliche Datenexfiltration ermöglichen würde. Ich kann stattdessen einen defensiven Workflow entwerfen, der verdächtige Login-Formulare klassifiziert, Security-Awareness-Tickets erstellt oder Audit-Logs ohne Secrets auswertet.

        ### Warum dieses Beispiel gut ist

        - Lehnt Missbrauch klar ab.
        - Bietet eine defensive Alternative.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Nutze bitte eine KI-Klassifikation, aber unsere n8n-Instanz hat keinen Internetzugriff.

        ### Gute Antwort

        Offline-Fallback:

        - keine OpenAI-, Cloud-LLM- oder SaaS-Nodes,
        - lokale LLM-HTTP-API nur als vom Nutzer bestätigter interner Endpunkt,
        - ohne bestätigten Endpunkt: regelbasierte Klassifikation im Code Node,
        - Testdaten und Audit-Ausgabe im Workflow belassen.

        ### Warum dieses Beispiel gut ist

        - Funktioniert auch ohne Internet.
        - Trennt lokale Endpunkte von Annahmen.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Erstelle ein importierbares n8n-Workflow-JSON für einen sicheren Offline-Dry-Run: manuell starten, Beispielpayload laden, Pflichtfelder prüfen, Freigabeentscheidung vorbereiten und Audit-Record erzeugen.

        ### Gute Antwort

        Die passende Musterantwort ist `Modelle/einzelmodelle/n8n-workflow-architect/beispielergebnis.json`.

        Dieses Artefakt zeigt:

        - importierbares Workflow-JSON,
        - Manual Trigger als sicherer Teststart,
        - Code Nodes ohne externe Bibliotheken,
        - `active: false`,
        - keine Credentials, keine externen URLs, keine Secrets,
        - klaren Datenvertrag,
        - Human-in-the-loop-Entscheidung,
        - Audit-Ausgabe statt produktiver Aktion.
        """
    )


def template_markdown(model_id: str, name: str, config: dict[str, str]) -> str:
    example_result = example_result_file_for_model(model_id)
    return dedent(
        f"""\
        # Beispiele: {name}

        Diese Beispiele zeigen, wie das Modell `{model_id}` offline hochwertige Ergebnisse erzeugt. Sie sind als Few-Shot-Material für lokale Modelle gedacht.

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Ich brauche Hilfe dazu. Es geht ungefähr um: {config["scenario"]}

        ### Gute Antwort

        Ich liefere eine erste Fassung und markiere Annahmen. Ziel dieses Modells ist: {config["purpose"]}

        Annahmen:

        - Die Eingabe reicht für einen ersten Entwurf.
        - Fehlende Fakten werden als offen markiert.
        - Es wird keine Websuche vorausgesetzt.

        Erste Struktur:

        1. Ziel und Kontext aus der Anfrage ableiten.
        2. Sichtbare Informationen von Annahmen trennen.
        3. Ergebnis im Format `{example_result}` ausgeben.
        4. Offene Punkte und nächsten lokalen Prüfschritt nennen.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        {config["scenario"]}

        ### Gute Antwort

        #### Kurzfazit

        Ich erstelle ein offline weiterverwendbares Ergebnis im Format `{example_result}`. Die Antwort nutzt nur bereitgestellte Informationen und markiert nicht belegte Punkte.

        #### Arbeitsergebnis

        | Bereich | Ausarbeitung |
        |---|---|
        | Ziel | {config["purpose"]} |
        | Eingaben | Nutzertext, Dateien, Screenshots oder Notizen aus dem aktuellen Auftrag |
        | Struktur | Kurzfazit, Quellenlage, Hauptteil, Risiken, offene Punkte, nächste Schritte |
        | Abnahme | {config["quality"]} |

        #### Nächster Schritt

        Das Ergebnis kann lokal geprüft, erweitert oder in das Zielartefakt übernommen werden. Aktuelle externe Fakten bleiben prüfpflichtig.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Kombiniere Text, Screenshot und eine kurze Tabelle. Erstelle ein Ergebnis, das intern weiterverwendet werden kann.

        ### Gute Antwort

        #### Quellen- und Evidenztrennung

        - Text: direkt zitier- oder zusammenfassbar, wenn im Auftrag enthalten.
        - Screenshot/Bild: nur sichtbare Inhalte verwenden. {config["vision"]}
        - Tabelle: Werte nur übernehmen, wenn sie lesbar oder als Datei vorhanden sind.

        #### Ergebnislogik

        1. Beobachtungen getrennt nach Quelle erfassen.
        2. Ableitungen als Annahmen markieren.
        3. Widersprüche und Lücken sichtbar machen.
        4. Das Ergebnis im Zielformat `{example_result}` liefern.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Mach daraus bitte eine gute Version. Mehr Kontext habe ich gerade nicht.

        ### Gute Antwort

        Ich liefere eine erste Version mit Annahmen. Nicht vorhandene Informationen werden nicht erfunden.

        Offene Pflichtinformationen:

        - konkrete Zielgruppe,
        - gewünschtes Zielformat,
        - bereitgestellte Quellen oder Dateien,
        - Qualitätskriterium für Abnahme.

        Bis diese Angaben vorliegen, nutze ich ein konservatives Standardformat und markiere offene Punkte.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Nutze ausschließlich die bereitgestellten Informationen, aber ergänze aktuelle externe Fakten.

        ### Gute Antwort

        Konflikt erkannt: Offline-Nutzung und aktuelle externe Fakten passen ohne Quelle nicht zusammen. Ich verwende nur die bereitgestellten Informationen und markiere aktuelle Fakten als prüfpflichtig.

        ## Beispiel 6: Sicherheits- oder Qualitätsgrenze

        ### Nutzeranfrage

        Füge echte Zugangsdaten, interne URLs und private Kontaktdaten in das Beispiel ein.

        ### Gute Antwort

        Dabei helfe ich nicht. Ich verwende anonymisierte Beispielwerte, entferne produktive Secrets aus dem Ergebnis und verweise darauf, dass Zugangsdaten nur über lokale Secret-Mechanismen verarbeitet werden dürfen.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Wenn etwas fehlt, recherchiere es online.

        ### Gute Antwort

        Im Offline-Modus wird keine Websuche vorausgesetzt. Ich arbeite mit lokalen Dateien, Chat-Kontext und sichtbaren Screenshots. Fehlende aktuelle Informationen werden als offen oder prüfpflichtig markiert.

        Fallback-Struktur:

        - Was aus lokalen Quellen sicher bekannt ist.
        - Was nur eine Annahme ist.
        - Welche Quelle später zur Aktualisierung geprüft werden sollte.
        - Welcher nächste Schritt ohne Internet möglich ist.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Welches Beispiel soll das Modell nachahmen?

        ### Gute Antwort

        Das Goldstandard-Ergebnis liegt in `{example_result}`. Es soll als Format- und Qualitätsmuster nachgeahmt werden: direkt verwendbar, quellenbewusst, offlinefähig, ohne Platzhalter und ohne erfundene Fakten.
        """
    )


def generated_rag_example(model_id: str, name: str, config: dict[str, str], index: int) -> str:
    if index == 1:
        title = "Fokussierter Standardauftrag"
        request = config["scenario"]
        response_focus = (
            "Arbeite mit sichtbaren Quellen, markiere Annahmen und liefere ein direkt prüfbares "
            "Zwischenergebnis. Nutze die Pflichtdateien als Qualitätsanker; dieses Beispiel ist nur "
            "zusätzliches RAG-Material."
        )
    elif index == 2:
        title = "Unvollständige Eingabe mit Qualitätsgrenze"
        request = "Die Eingabe ist knapp, enthält aber genug Kontext für einen ersten sicheren Entwurf."
        response_focus = (
            "Stelle höchstens drei gezielte Rückfragen, erfinde keine fehlenden Fakten und liefere eine "
            "konservative Arbeitsfassung mit klaren offenen Punkten."
        )
    else:
        title = "Visuelle oder dateibasierte Ergänzung"
        request = "Es liegen Text, Screenshot oder Datei als ergänzende Quelle vor."
        response_focus = config["vision"]

    return dedent(
        f"""\
        # Zusatzbeispiel {index}: {name}

        Dieses Beispiel ist optionales Knowledge/RAG-Material für `{model_id}`. Es ersetzt nicht den Pflichtkontext aus `mainprompt.md`, `fachwissen.md` und `Golden_Example.<ext>`.

        ## Szenario

        {title}

        ## Nutzeranfrage

        {request}

        ## Gute Antwort

        {response_focus}

        Ergebnisziel: {config["purpose"]}

        Qualitätskriterium: {config["quality"]}
        """
    )


def ensure_generated_rag_examples(model_dir: Path, model_id: str, name: str, config: dict[str, str]) -> None:
    examples_dir = model_dir / EXAMPLE_DIR
    existing = [
        path
        for path in examples_dir.rglob("*")
        if path.is_file() and not path.relative_to(examples_dir).as_posix().startswith("generated/")
    ]
    needed = max(0, 3 - len(existing))
    if needed <= 0:
        return

    generated_dir = examples_dir / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    for index in range(1, needed + 1):
        target = generated_dir / f"zusatzbeispiel-{index:02d}.md"
        target.write_text(generated_rag_example(model_id, name, config, index), encoding="utf-8", newline="\n")


def code_generation_goldstandard_python() -> str:
    return dedent(
        """\
        #!/usr/bin/env python3
        \"\"\"Offline-Goldstandard für das Modell `codegenerierung`.

        Aufgabe: Aus einer CSV mit Support-Tickets einen validierten Markdown-
        Kurzreport erzeugen. Das Beispiel nutzt nur die Python-Standardbibliothek,
        lädt keine externen Daten und enthält einen eingebauten Selbsttest.

        Nutzung:
            python beispielergebnis.py --demo
            python beispielergebnis.py tickets.csv --review-date 2026-05-28
            python beispielergebnis.py --self-test
        \"\"\"

        from __future__ import annotations

        import argparse
        import csv
        import io
        import sys
        from collections import Counter
        from dataclasses import dataclass
        from datetime import date
        from pathlib import Path
        from typing import Iterable, Sequence


        REQUIRED_COLUMNS = {
            "ticket_id",
            "category",
            "priority",
            "status",
            "opened_at",
            "sla_due_at",
        }
        PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


        @dataclass(frozen=True)
        class Ticket:
            ticket_id: str
            category: str
            priority: str
            status: str
            opened_at: date
            sla_due_at: date

            @property
            def is_open(self) -> bool:
                return self.status in {"new", "open", "in_progress", "waiting"}


        def parse_iso_date(value: str, field_name: str, row_number: int) -> date:
            try:
                return date.fromisoformat(value.strip())
            except ValueError as exc:
                raise ValueError(
                    f"Zeile {row_number}: `{field_name}` muss YYYY-MM-DD sein."
                ) from exc


        def normalize_priority(value: str, row_number: int) -> str:
            priority = value.strip().lower()
            if priority not in PRIORITY_ORDER:
                allowed = ", ".join(PRIORITY_ORDER)
                raise ValueError(
                    f"Zeile {row_number}: unbekannte Priorität `{value}`. "
                    f"Erlaubt: {allowed}."
                )
            return priority


        def parse_tickets(csv_text: str) -> list[Ticket]:
            reader = csv.DictReader(io.StringIO(csv_text))
            if reader.fieldnames is None:
                raise ValueError("CSV enthält keine Kopfzeile.")

            missing = sorted(REQUIRED_COLUMNS.difference(reader.fieldnames))
            if missing:
                raise ValueError(f"CSV-Spalten fehlen: {', '.join(missing)}")

            tickets: list[Ticket] = []
            for row_number, row in enumerate(reader, start=2):
                ticket_id = (row.get("ticket_id") or "").strip()
                if not ticket_id:
                    raise ValueError(f"Zeile {row_number}: `ticket_id` fehlt.")

                tickets.append(
                    Ticket(
                        ticket_id=ticket_id,
                        category=(row.get("category") or "").strip() or "Unbekannt",
                        priority=normalize_priority(row.get("priority", ""), row_number),
                        status=(row.get("status") or "").strip().lower() or "open",
                        opened_at=parse_iso_date(row.get("opened_at", ""), "opened_at", row_number),
                        sla_due_at=parse_iso_date(row.get("sla_due_at", ""), "sla_due_at", row_number),
                    )
                )

            if not tickets:
                raise ValueError("CSV enthält keine Ticketzeilen.")
            return tickets


        def overdue_tickets(tickets: Iterable[Ticket], review_date: date) -> list[Ticket]:
            return sorted(
                (ticket for ticket in tickets if ticket.is_open and ticket.sla_due_at < review_date),
                key=lambda ticket: (PRIORITY_ORDER[ticket.priority], ticket.sla_due_at),
            )


        def build_markdown_report(tickets: Sequence[Ticket], review_date: date) -> str:
            by_priority = Counter(ticket.priority for ticket in tickets)
            by_category = Counter(ticket.category for ticket in tickets)
            overdue = overdue_tickets(tickets, review_date)

            lines = [
                "# Ticket-SLA-Kurzreport",
                "",
                f"Prüfdatum: {review_date.isoformat()}",
                f"Tickets gesamt: {len(tickets)}",
                f"Offene Tickets mit überschrittener SLA: {len(overdue)}",
                "",
                "## Prioritäten",
                "",
            ]

            for priority in PRIORITY_ORDER:
                lines.append(f"- {priority}: {by_priority.get(priority, 0)}")

            lines.extend(["", "## Kategorien", ""])
            for category, count in sorted(by_category.items()):
                lines.append(f"- {category}: {count}")

            lines.extend(["", "## Kritische nächste Prüfung", ""])
            if overdue:
                for ticket in overdue[:5]:
                    lines.append(
                        f"- {ticket.ticket_id}: {ticket.priority}, "
                        f"{ticket.category}, SLA {ticket.sla_due_at.isoformat()}"
                    )
            else:
                lines.append("- Keine offenen SLA-Überschreitungen im Datensatz.")

            lines.extend(
                [
                    "",
                    "## Grenzen",
                    "",
                    "- Der Report nutzt nur die übergebene CSV.",
                    "- Ursachen, Zuständigkeiten und Kundendaten werden nicht erfunden.",
                    "- Produktive Eskalationen brauchen menschliche Freigabe.",
                ]
            )
            return "\\n".join(lines) + "\\n"


        def demo_csv() -> str:
            return "\\n".join(
                [
                    "ticket_id,category,priority,status,opened_at,sla_due_at",
                    "TCK-1001,Login,high,open,2026-05-23,2026-05-27",
                    "TCK-1002,Hardware,medium,waiting,2026-05-25,2026-05-31",
                    "TCK-1003,Billing,critical,in_progress,2026-05-20,2026-05-24",
                    "TCK-1004,Access,low,closed,2026-05-12,2026-05-18",
                ]
            )


        def run_self_test() -> None:
            tickets = parse_tickets(demo_csv())
            report = build_markdown_report(tickets, date(2026, 5, 28))
            assert "Tickets gesamt: 4" in report
            assert "Offene Tickets mit überschrittener SLA: 2" in report
            assert "TCK-1003" in report


        def read_input(path: str | None, use_demo: bool) -> str:
            if use_demo:
                return demo_csv()
            if path is None:
                raise ValueError("Bitte CSV-Dateipfad angeben oder `--demo` nutzen.")
            return Path(path).read_text(encoding="utf-8")


        def main(argv: Sequence[str] | None = None) -> int:
            parser = argparse.ArgumentParser(description=__doc__)
            parser.add_argument("csv_path", nargs="?", help="Pfad zur Ticket-CSV")
            parser.add_argument("--demo", action="store_true", help="eingebaute Beispieldaten nutzen")
            parser.add_argument("--self-test", action="store_true", help="eingebauten Selbsttest ausführen")
            parser.add_argument("--review-date", default="2026-05-28", help="Prüfdatum im Format YYYY-MM-DD")
            args = parser.parse_args(argv)

            try:
                if args.self_test:
                    run_self_test()
                    print("Self-test passed.")
                    return 0
                review_date = date.fromisoformat(args.review_date)
                tickets = parse_tickets(read_input(args.csv_path, args.demo))
                print(build_markdown_report(tickets, review_date), end="")
                return 0
            except Exception as exc:
                print(f"Fehler: {exc}", file=sys.stderr)
                return 2


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    )


def code_model_example_result(model_id: str, name: str) -> str:
    examples = {
        "code-review": {
            "title": "Code-Review-Findingliste",
            "body": """\
            ## Findings

            ### P1 - Zugriffskontrolle wird clientseitig entschieden

            Datei: `app/routes/admin.py`, Zeile 42

            Der neue Endpunkt verlässt sich auf `request.json["isAdmin"]`. Diese Angabe kommt vom Client und darf nicht über Adminrechte entscheiden. Prüfe die Berechtigung serverseitig aus Session, Token-Claims oder Rollenmodell und ergänze einen negativen Test.

            Reproduktion: Request mit `{"isAdmin": true}` gegen den Endpunkt senden, obwohl der angemeldete Nutzer keine Adminrolle hat.

            Testlücke: Es fehlt ein Test für Nutzer ohne Adminrolle.

            ### P2 - Fehlerpfad verliert Diagnosekontext

            Datei: `app/services/export.py`, Zeile 88

            Der generische `except Exception` gibt nur `Export fehlgeschlagen` zurück. Damit fehlen Fehlerklasse und Korrelations-ID im Log. Nutzerantworten dürfen knapp bleiben, aber interne Logs müssen Ursache und Ticket-ID enthalten.

            ## Zusammenfassung

            Der Patch ist fachlich nachvollziehbar, blockiert aber wegen der serverseitigen Autorisierung. Nach Fix und negativem Test ist ein erneutes Review sinnvoll.
            """,
        },
        "codeanalyse": {
            "title": "Codeanalyse-Bericht",
            "body": """\
            ## Kurzfazit

            Der untersuchte Importpfad ist synchron aufgebaut, validiert CSV-Spalten spät und mischt Parsing, Fachlogik und Ausgabe. Das erhöht Fehlerfolgen und erschwert Tests.

            ## Belegte Fakten

            | Befund | Quelle | Auswirkung |
            |---|---|---|
            | `import_csv()` liest komplette Dateien in den Speicher | `src/importer.py:18` | große Dateien können den Prozess blockieren |
            | Pflichtfelder werden erst nach Datenbankmapping geprüft | `src/importer.py:61` | Fehlermeldungen zeigen interne Feldnamen |
            | Tests decken nur Erfolgsfall ab | `tests/test_importer.py` | negative Datenqualität bleibt ungesichert |

            ## Hypothesen

            - Die Laufzeitprobleme entstehen wahrscheinlich bei Dateien über 50 MB.
            - Der Supportaufwand steigt, weil Fehlermeldungen nicht quellnah sind.

            ## Empfohlene Messungen

            1. Import mit 10k, 100k und 500k Zeilen lokal benchmarken.
            2. Parserfehler mit fehlenden Spalten, ungültigem Datum und leerer Datei testen.
            3. Speicherverbrauch während des Imports protokollieren.
            """,
        },
        "debugging-fehleranalyse": {
            "title": "Debugging-Runbook",
            "body": """\
            ## Symptom

            OpenWebUI zeigt nach dem Upload einer CSV `500 Internal Server Error`; im Log steht `KeyError: 'ticket_id'`.

            ## Priorisierte Hypothesen

            | Priorität | Hypothese | Prüfung | Erwartung |
            |---|---|---|---|
            | P1 | CSV-Kopfzeile enthält `ticketId` statt `ticket_id` | Kopfzeile ausgeben | Abweichender Spaltenname sichtbar |
            | P2 | Importpfad nutzt altes Mapping | Commit/Diff prüfen | Mapping kennt nur ältere Feldnamen |
            | P3 | Datei wurde mit Semikolon getrennt | Dialekt prüfen | Parser sieht eine einzige Spalte |

            ## Nächster lokaler Check

            ```bash
            python - <<'PY'
            import csv
            from pathlib import Path
            path = Path("upload.csv")
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                print(next(reader))
            PY
            ```

            ## Fix-Richtung

            Vor dem Datenbankmapping eine klare Schema-Validierung einbauen und erlaubte Aliasnamen explizit dokumentieren.
            """,
        },
        "refactoring-unterstützung": {
            "title": "Refactoring-Plan",
            "body": """\
            ## Ziel

            `TicketImporter` soll Parsing, Validierung und Persistenz trennen, ohne das Ausgabeformat oder bestehende CLI-Optionen zu ändern.

            ## Nicht-Ziele

            - Keine neue Datenbankabstraktion.
            - Keine Änderung an CSV-Spaltennamen.
            - Keine Performanceoptimierung vor Baseline-Messung.

            ## Invarianten

            - Gleiche gültige CSV erzeugt gleiche Datensätze.
            - Ungültige CSV erzeugt verständlichere, aber weiterhin nicht erfolgreiche Fehler.
            - CLI-Exit-Codes bleiben stabil.

            ## Schritte

            1. Aktuelle Tests grün ausführen und zwei negative CSV-Tests ergänzen.
            2. Reine Funktion `parse_rows(text)` extrahieren.
            3. Schema-Validierung vor Mapping verschieben.
            4. Persistenzaufruf unverändert lassen und über Adapter testen.
            5. Nach jedem Schritt Tests ausführen.

            ## Rollback

            Jeder Schritt bleibt einzeln revertierbar; kein Datenformat wird migriert.
            """,
        },
        "code-dokumentation": {
            "title": "Entwicklerdokumentation",
            "body": """\
            ## Modul: CSV-Ticketimport

            `src/importer.py` liest Ticketdaten aus CSV-Dateien, validiert Pflichtfelder und übergibt normalisierte Datensätze an den Repository-Layer.

            ## Nutzung

            ```bash
            python -m app.importer tickets.csv --dry-run
            ```

            ## Datenvertrag

            | Spalte | Pflicht | Bedeutung |
            |---|---:|---|
            | `ticket_id` | ja | stabile Ticketkennung aus dem Quellsystem |
            | `priority` | ja | `critical`, `high`, `medium` oder `low` |
            | `sla_due_at` | ja | Datum im Format `YYYY-MM-DD` |

            ## Fehlerverhalten

            Ungültige Dateien brechen vor der Persistenz ab. Fehlermeldungen nennen Spalte und Zeile, aber keine personenbezogenen Inhalte aus Freitextfeldern.

            ## Pflegehinweis

            Wenn neue Spalten produktiv werden, zuerst Tests und Datenvertrag aktualisieren, danach Parser und Importdoku.
            """,
        },
        "testfall-generierung": {
            "title": "Testfallkatalog",
            "body": """\
            ## Testfälle für CSV-Ticketimport

            | ID | Risiko | Vorbedingung | Schritte | Erwartetes Ergebnis | Priorität |
            |---|---|---|---|---|---|
            | T-001 | gültige Daten werden abgelehnt | valide CSV liegt vor | Dry-Run starten | 4 Tickets validiert, Exit-Code 0 | hoch |
            | T-002 | fehlende Pflichtspalte erzeugt Folgefehler | CSV ohne `ticket_id` | Dry-Run starten | klare Fehlermeldung vor Persistenz | hoch |
            | T-003 | falsches Datumsformat wird akzeptiert | `sla_due_at=28.05.2026` | Dry-Run starten | Validierungsfehler mit Zeile und Feld | mittel |
            | T-004 | geschlossene Tickets werden eskaliert | CSV mit `status=closed` | SLA-Report erzeugen | geschlossenes Ticket nicht in offener SLA-Liste | mittel |

            ## Automatisierbarer Pytest-Kern

            ```python
            import pytest

            @pytest.mark.parametrize("priority", ["critical", "high", "medium", "low"])
            def test_allowed_priorities_are_accepted(priority):
                assert normalize_priority(priority, row_number=2) == priority
            ```
            """,
        },
    }
    item = examples[model_id]
    return dedent(
        f"""\
        # Beispielergebnis: {item["title"]}

        Dieses Goldstandard-Beispiel zeigt eine fertige Antwort des Modells `{name}`. Es nutzt nur den sichtbaren Nutzerkontext, trennt Fakten von Annahmen und enthält keine externen Laufzeitabhängigkeiten.

        {dedent(item["body"]).strip()}
        """
    )


def code_model_goldstandard_briefing(model_id: str, name: str, config: dict[str, str]) -> str:
    example_result = example_result_file_for_model(model_id)
    return dedent(
        f"""\
        # Beispiele: {name}

        Diese Beispiele zeigen, wie das Modell `{model_id}` offline arbeitet: kontextgebunden, ohne erfundene Dateien, ohne Websuche und mit prüfbaren Ergebnissen.

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Schau dir diesen Code an und sag mir, was wichtig ist.

        ### Gute Antwort

        Ich prüfe zuerst auf funktionale Risiken, Sicherheitsprobleme, Testlücken und Wartbarkeit. Wenn kein Code oder Diff sichtbar ist, fordere ich den relevanten Ausschnitt an. Sobald Code vorliegt, liefere ich priorisierte Befunde mit Datei-/Zeilenbezug statt allgemeiner Stilhinweise.

        ### Warum dieses Beispiel gut ist

        - Es arbeitet nicht ohne Quelle.
        - Es nennt die Prüfreihenfolge.
        - Es vermeidet erfundene Befunde.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        Prüfe den Diff für unseren CSV-Importer. Schwerpunkt: Bugs, Security, Tests. Ausgabe bitte als PR-Review.

        ### Gute Antwort

        Findings stehen zuerst. Jeder Befund enthält Schweregrad, betroffene Datei, reproduzierbare Begründung, konkrete Korrektur und Testlücke. Reine Geschmacksfragen werden nur genannt, wenn sie Wartbarkeit oder Fehlerrisiko messbar betreffen.

        ### Warum dieses Beispiel gut ist

        - Passt zu produktiver PR-Arbeit.
        - Trennt blockierende Findings von Empfehlungen.
        - Verlangt keine externen Tools.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Analysiere Importer, API-Endpunkt und Tests zusammen. Wir sehen sporadische 500er, aber nur bei bestimmten CSV-Dateien.

        ### Gute Antwort

        Das Modell bildet eine Hypothesenmatrix: Parser-Dialekt, Pflichtspalten, Datenformat, Fehlerbehandlung, Persistenz und Testabdeckung. Belegte Fakten kommen aus Code und Logs; Hypothesen werden mit konkreten lokalen Prüfungen verbunden.

        ### Warum dieses Beispiel gut ist

        - Kombiniert mehrere Quellen.
        - Priorisiert prüfbare Ursachen.
        - Trennt Analyse und Spekulation.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Mach den Import robuster.

        ### Gute Antwort

        Ohne Code kann ich keinen Patch behaupten. Ich arbeite mit Annahmen: CSV-Import, lokale Validierung, keine produktiven Daten. Ich bitte um Datei oder Diff und skizziere vorab sichere Prüfpunkte: Schema-Validierung, verständliche Fehler, negative Tests, keine Secrets in Logs.

        ### Warum dieses Beispiel gut ist

        - Bleibt handlungsfähig.
        - Markiert Annahmen.
        - Erfindet keine Implementierung.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Refactore das Modul komplett, aber ändere keine Tests und kein Verhalten. Große Umbauten sind okay.

        ### Gute Antwort

        Konflikt erkannt: Ein kompletter Umbau ohne Testanpassung erhöht Regressionsrisiko. Ich wähle kleine verhaltenswahrende Schritte, ergänze fehlende Charakterisierungstests vor Strukturänderungen und halte jeden Schritt separat prüfbar.

        ### Warum dieses Beispiel gut ist

        - Erkennt Zielkonflikte.
        - Priorisiert Verhaltenserhalt.
        - Vermeidet riskante Großänderungen.

        ## Beispiel 6: Sicherheits- oder Qualitätsgrenze

        ### Nutzeranfrage

        Zeig mir, wie ich die Authentifizierung im Review umgehen kann, damit der Test schneller ist.

        ### Gute Antwort

        Dabei helfe ich nicht. Ich kann stattdessen sichere Testmuster vorschlagen: autorisierte Testrollen, lokale Testtokens ohne produktive Secrets, negative Authorization-Tests und klare Fixtures.

        ### Warum dieses Beispiel gut ist

        - Lehnt Umgehung ab.
        - Bietet defensive Alternative.
        - Schützt produktive Systeme.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Nutze bitte aktuelle Best Practices und prüfe die Bibliotheksversionen online.

        ### Gute Antwort

        Im Offline-Modus prüfe ich nur lokale Dateien wie Lockfiles, README, Tests und Konfiguration. Aktuelle Versions- oder CVE-Aussagen markiere ich als prüfpflichtig. Ich kann lokale Kommandos für `--version`, Tests oder statische Checks vorschlagen, aber keine Webrecherche vortäuschen.

        ### Warum dieses Beispiel gut ist

        - Macht Aktualitätsgrenzen sichtbar.
        - Nutzt lokale Evidenz.
        - Verhindert Halluzinationen.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Gib mir ein Muster, wie ein gutes Ergebnis dieses Modells aussehen soll.

        ### Gute Antwort

        Nutze `{example_result}` als Goldstandard. Für dieses Modell gilt außerdem:

        - Zweck: {config["purpose"]}
        - Qualitätslatte: {config["quality"]}
        - Offline-Regel: keine nicht vorhandenen Dateien, Tools, Bibliotheken oder Webquellen voraussetzen.

        ### Warum dieses Beispiel gut ist

        - Verweist auf das echte Zielformat.
        - Fasst die Modellqualität knapp zusammen.
        - Ist als Few-Shot für lokale Modelle nutzbar.
        """
    )


def api_goldstandard_yaml() -> str:
    return dedent(
        """\
        openapi: 3.1.0
        info:
          title: Ticket Intake API
          version: 1.0.0
          summary: Offline-Beispiel für einen kleinen, prüfbaren API-Vertrag
        servers:
          - url: /api
            description: relativer Pfad für lokale oder interne Deployments
        tags:
          - name: tickets
            description: Ticketannahme und Statusabfrage
        paths:
          /tickets:
            post:
              tags: [tickets]
              operationId: createTicket
              summary: Nimmt ein Support-Ticket entgegen
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      $ref: "#/components/schemas/TicketCreateRequest"
                    examples:
                      minimal:
                        value:
                          requester: ops-team
                          category: hardware
                          priority: medium
                          summary: Notebook startet nach Update nicht
              responses:
                "201":
                  description: Ticket wurde angenommen
                  content:
                    application/json:
                      schema:
                        $ref: "#/components/schemas/TicketCreateResponse"
                "400":
                  $ref: "#/components/responses/BadRequest"
                "409":
                  description: Duplikat anhand Idempotency-Key oder fachlichem Fingerprint
                  content:
                    application/json:
                      schema:
                        $ref: "#/components/schemas/ErrorResponse"
            get:
              tags: [tickets]
              operationId: listTickets
              summary: Listet Tickets nach Status und Priorität
              parameters:
                - name: status
                  in: query
                  schema:
                    type: string
                    enum: [new, open, waiting, closed]
                - name: priority
                  in: query
                  schema:
                    type: string
                    enum: [critical, high, medium, low]
              responses:
                "200":
                  description: Gefilterte Ticketliste
                  content:
                    application/json:
                      schema:
                        type: object
                        required: [items]
                        properties:
                          items:
                            type: array
                            items:
                              $ref: "#/components/schemas/Ticket"
          /tickets/{ticketId}:
            get:
              tags: [tickets]
              operationId: getTicket
              summary: Gibt ein Ticket anhand der stabilen Ticket-ID zurück
              parameters:
                - $ref: "#/components/parameters/TicketId"
              responses:
                "200":
                  description: Ticket gefunden
                  content:
                    application/json:
                      schema:
                        $ref: "#/components/schemas/Ticket"
                "404":
                  description: Ticket nicht gefunden
                  content:
                    application/json:
                      schema:
                        $ref: "#/components/schemas/ErrorResponse"
        components:
          parameters:
            TicketId:
              name: ticketId
              in: path
              required: true
              schema:
                type: string
                pattern: "^TCK-[0-9]{4,}$"
              description: Stabile Ticketkennung ohne personenbezogene Daten
          responses:
            BadRequest:
              description: Anfrage ist syntaktisch oder fachlich ungültig
              content:
                application/json:
                  schema:
                    $ref: "#/components/schemas/ErrorResponse"
          schemas:
            TicketCreateRequest:
              type: object
              additionalProperties: false
              required: [requester, category, priority, summary]
              properties:
                requester:
                  type: string
                  minLength: 2
                  maxLength: 80
                  description: Team- oder Rollenkennung, keine private E-Mail-Adresse
                category:
                  type: string
                  enum: [access, hardware, software, network, other]
                priority:
                  type: string
                  enum: [critical, high, medium, low]
                summary:
                  type: string
                  minLength: 10
                  maxLength: 240
                idempotencyKey:
                  type: string
                  minLength: 12
                  maxLength: 80
            TicketCreateResponse:
              type: object
              required: [ticketId, status]
              properties:
                ticketId:
                  type: string
                  pattern: "^TCK-[0-9]{4,}$"
                status:
                  type: string
                  enum: [new, open]
            Ticket:
              type: object
              required: [ticketId, category, priority, status, summary]
              properties:
                ticketId:
                  type: string
                category:
                  type: string
                priority:
                  type: string
                status:
                  type: string
                  enum: [new, open, waiting, closed]
                summary:
                  type: string
            ErrorResponse:
              type: object
              required: [code, message]
              properties:
                code:
                  type: string
                  examples: [invalid_request]
                message:
                  type: string
                fieldErrors:
                  type: array
                  items:
                    type: object
                    required: [field, reason]
                    properties:
                      field:
                        type: string
                      reason:
                        type: string
        """
    )


def information_extraction_goldstandard_json() -> str:
    return json.dumps(
        {
            "schema_version": "1.0",
            "task": "support_ticket_extraction",
            "source_scope": "sichtbarer Nutzertext und angehängter Logauszug",
            "records": [
                {
                    "ticket_id": "TCK-1042",
                    "affected_service": "OpenWebUI",
                    "symptom": "Upload einer CSV bricht mit Status 500 ab",
                    "severity": "high",
                    "environment": {
                        "runtime": "lokale Workbench",
                        "network": "offline",
                    },
                    "evidence": [
                        {
                            "field": "symptom",
                            "source": "Nutzertext",
                            "quote": "CSV Upload endet mit 500",
                        },
                        {
                            "field": "ticket_id",
                            "source": "Logzeile 3",
                            "quote": "ticket=TCK-1042",
                        },
                    ],
                    "uncertainties": [
                        "exakte OpenWebUI-Version nicht im sichtbaren Kontext",
                        "CSV-Beispieldatei nicht bereitgestellt",
                    ],
                }
            ],
            "validation": {
                "missing_required_fields": [],
                "normalization_notes": [
                    "severity aus Auswirkung und Fehlerstatus abgeleitet",
                    "environment.network aus Nutzerhinweis 'offline' übernommen",
                ],
            },
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def log_analysis_goldstandard_json() -> str:
    return json.dumps(
        {
            "schema_version": "1.0",
            "input_profile": {
                "files": ["openwebui-upload.log", "tickets.csv"],
                "assumptions": ["Logzeitpunkte sind lokal und nicht zeitzonennormalisiert"],
            },
            "parse_status": {
                "json_valid": True,
                "csv_header_valid": False,
                "log_lines_read": 128,
            },
            "findings": [
                {
                    "severity": "P1",
                    "title": "CSV-Pflichtspalte `ticket_id` fehlt",
                    "evidence": "tickets.csv Kopfzeile enthält `ticketId`, aber Importer erwartet `ticket_id`",
                    "impact": "Upload endet vor fachlicher Verarbeitung mit 500 statt Validierungsfehler",
                    "next_check": "Importer-Schema gegen tatsächliche Kopfzeile prüfen",
                },
                {
                    "severity": "P2",
                    "title": "Fehlerantwort enthält keine Feldliste",
                    "evidence": "Log zeigt KeyError ohne validierte Fehlerstruktur",
                    "impact": "Support kann fehlerhafte Dateien schwer selbst korrigieren",
                    "next_check": "negativen Test für fehlende Pflichtspalte ergänzen",
                },
            ],
            "safe_commands": [
                "python -m json.tool payload.json",
                "python - <<'PY'\nimport csv\nprint(next(csv.reader(open('tickets.csv', encoding='utf-8-sig'))))\nPY",
            ],
            "limits": [
                "Keine personenbezogenen CSV-Zeilen ausgegeben",
                "Keine Ursache behauptet, die nicht aus Log oder Header ableitbar ist",
            ],
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def table_analysis_goldstandard_python() -> str:
    return dedent(
        """\
        #!/usr/bin/env python3
        \"\"\"Offline-Goldstandard für `tabellen-csv-datenanalyse`.

        Erstellt ein kleines, reproduzierbares CSV-Profil mit Spaltentypen,
        Missing-Value-Zählung und numerischen Kennzahlen. Nur Standardbibliothek.

        Nutzung:
            python beispielergebnis.py --demo
            python beispielergebnis.py daten.csv
            python beispielergebnis.py --self-test
        \"\"\"

        from __future__ import annotations

        import argparse
        import csv
        import io
        import json
        import statistics
        from pathlib import Path
        from typing import Sequence


        def demo_csv() -> str:
            return "\\n".join(
                [
                    "team,tickets,sla_hours,region",
                    "Service Desk,42,6.5,DACH",
                    "Field Support,18,14.0,DACH",
                    "Network,7,2.0,EMEA",
                    "Service Desk,39,7.5,DACH",
                ]
            )


        def read_rows(text: str) -> list[dict[str, str]]:
            reader = csv.DictReader(io.StringIO(text))
            if not reader.fieldnames:
                raise ValueError("CSV enthält keine Kopfzeile.")
            rows = list(reader)
            if not rows:
                raise ValueError("CSV enthält keine Datenzeilen.")
            return rows


        def as_float(value: str) -> float | None:
            value = value.strip().replace(",", ".")
            if not value:
                return None
            try:
                return float(value)
            except ValueError:
                return None


        def profile(rows: list[dict[str, str]]) -> dict[str, object]:
            columns = list(rows[0].keys())
            result: dict[str, object] = {"row_count": len(rows), "columns": []}
            column_profiles: list[dict[str, object]] = []
            for column in columns:
                values = [(row.get(column) or "").strip() for row in rows]
                missing = sum(1 for value in values if value == "")
                numeric = [number for value in values if (number := as_float(value)) is not None]
                item: dict[str, object] = {
                    "name": column,
                    "missing": missing,
                    "distinct": len(set(values)),
                    "inferred_type": "number" if len(numeric) == len(values) - missing else "text",
                }
                if numeric:
                    item["min"] = min(numeric)
                    item["max"] = max(numeric)
                    item["mean"] = round(statistics.fmean(numeric), 2)
                column_profiles.append(item)
            result["columns"] = column_profiles
            return result


        def run_self_test() -> None:
            rows = read_rows(demo_csv())
            result = profile(rows)
            assert result["row_count"] == 4
            tickets = next(item for item in result["columns"] if item["name"] == "tickets")
            assert tickets["inferred_type"] == "number"
            assert tickets["max"] == 42.0


        def main(argv: Sequence[str] | None = None) -> int:
            parser = argparse.ArgumentParser(description=__doc__)
            parser.add_argument("csv_path", nargs="?")
            parser.add_argument("--demo", action="store_true")
            parser.add_argument("--self-test", action="store_true")
            args = parser.parse_args(argv)
            if args.self_test:
                run_self_test()
                print("Self-test passed.")
                return 0
            text = demo_csv() if args.demo else Path(args.csv_path).read_text(encoding="utf-8-sig")
            print(json.dumps(profile(read_rows(text)), ensure_ascii=False, indent=2))
            return 0


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    )


def dashboard_goldstandard_html() -> str:
    return dedent(
        """\
        <!doctype html>
        <html lang="de">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Offline Dashboard Briefing</title>
          <style>
            :root { color-scheme: light; --bg:#f7f8fb; --text:#172033; --muted:#5d6b82; --line:#d8deea; --accent:#0f766e; --warn:#b45309; --panel:#ffffff; }
            * { box-sizing: border-box; }
            body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }
            header, main { max-width: 1180px; margin: 0 auto; padding: 28px; }
            header { display:flex; justify-content:space-between; gap:24px; align-items:flex-end; border-bottom:1px solid var(--line); }
            h1 { margin:0; font-size: clamp(28px, 4vw, 48px); letter-spacing:0; }
            p { color:var(--muted); line-height:1.5; }
            .grid { display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap:16px; margin:24px 0; }
            .card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:18px; }
            .metric { display:block; font-size:34px; font-weight:800; margin-top:8px; }
            .layout { display:grid; grid-template-columns: 1.1fr .9fr; gap:16px; }
            table { width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); border-radius:8px; overflow:hidden; }
            th, td { text-align:left; padding:12px 14px; border-bottom:1px solid var(--line); }
            th { background:#eef3f8; }
            .bars { display:grid; gap:12px; }
            .bar { display:grid; grid-template-columns:110px 1fr 44px; gap:10px; align-items:center; }
            .track { height:14px; background:#e6ebf2; border-radius:999px; overflow:hidden; }
            .fill { height:100%; background:var(--accent); }
            .warn { color:var(--warn); font-weight:700; }
            @media (max-width: 860px) { header { display:block; } .grid, .layout { grid-template-columns:1fr; } }
          </style>
        </head>
        <body>
          <header>
            <div>
              <h1>Support Intake Dashboard</h1>
              <p>Offline-Prototyp für Kennzahlen, Warnschwellen und Datenqualitätsfragen. Alle Daten sind eingebettet und anonymisiert.</p>
            </div>
            <p>Stand: lokaler Beispieldatensatz</p>
          </header>
          <main>
            <section class="grid" aria-label="Kennzahlen">
              <div class="card">Tickets gesamt<span class="metric">106</span></div>
              <div class="card">SLA-Risiko<span class="metric warn">12</span></div>
              <div class="card">Median SLA<span class="metric">7h</span></div>
              <div class="card">Datenlücken<span class="metric warn">3</span></div>
            </section>
            <section class="layout">
              <div class="card">
                <h2>Tickets nach Team</h2>
                <div class="bars" role="img" aria-label="Balkendiagramm Tickets nach Team">
                  <div class="bar"><span>Service Desk</span><span class="track"><span class="fill" style="width:100%"></span></span><strong>81</strong></div>
                  <div class="bar"><span>Field</span><span class="track"><span class="fill" style="width:22%"></span></span><strong>18</strong></div>
                  <div class="bar"><span>Network</span><span class="track"><span class="fill" style="width:9%"></span></span><strong>7</strong></div>
                </div>
              </div>
              <div class="card">
                <h2>Entscheidungsfragen</h2>
                <ol>
                  <li>Welche Tickets zählen als SLA-Risiko?</li>
                  <li>Welche Datenquelle ist führend?</li>
                  <li>Welche Schwelle löst Eskalation aus?</li>
                </ol>
              </div>
            </section>
            <section>
              <h2>Datenqualitätscheck</h2>
              <table>
                <thead><tr><th>Feld</th><th>Status</th><th>Regel</th></tr></thead>
                <tbody>
                  <tr><td>ticket_id</td><td>ok</td><td>eindeutig und nicht leer</td></tr>
                  <tr><td>sla_due_at</td><td class="warn">prüfen</td><td>3 fehlende Werte</td></tr>
                  <tr><td>priority</td><td>ok</td><td>critical, high, medium, low</td></tr>
                </tbody>
              </table>
            </section>
          </main>
        </body>
        </html>
        """
    )


def data_model_goldstandard_briefing(model_id: str, name: str, config: dict[str, str]) -> str:
    example_result = example_result_file_for_model(model_id)
    return dedent(
        f"""\
        # Beispiele: {name}

        Diese Beispiele zeigen robuste Offline-Arbeit für `{model_id}`: schemaorientiert, quellengebunden, ohne erfundene Daten und mit dem passenden Artefaktformat `{example_result}`.

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Mach daraus eine strukturierte Auswertung.

        ### Gute Antwort

        Ich prüfe zuerst, welches Zielformat sinnvoll ist: API-Vertrag, JSON-Extraktion, Datenprofil, Logbefund oder Dashboard-Briefing. Ohne Rohdaten markiere ich Annahmen und fordere die kleinste relevante Quelle an.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        Aus diesen Ticketfeldern soll ein importierbares Artefakt entstehen. Es muss offline nutzbar sein und klare Validierungsregeln enthalten.

        ### Gute Antwort

        Das Modell liefert `{example_result}` als fertiges Artefakt, trennt Datenvertrag, Beispiele, Fehlerfälle und Prüfschritte und nutzt keine externen APIs oder CDNs.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Kombiniere CSV, Logauszug und Zielgruppe. Leite Kennzahlen, Datenqualitätsrisiken und nächste Checks ab.

        ### Gute Antwort

        Das Modell trennt Parsingstatus, Datenprofil, fachliche Befunde, Unsicherheiten und Validierung. Kennzahlen werden nur berechnet, wenn Daten sichtbar sind; sonst werden sie als offen markiert.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Erstelle eine API oder ein Dashboard, Daten kommen später.

        ### Gute Antwort

        Ich kann Struktur und Datenvertrag vorbereiten, aber keine Kennzahlen erfinden. Ich nutze Beispielwerte nur anonymisiert und markiere sie als Demonstrationsdaten.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Gib valides JSON aus, aber bitte mit Kommentaren und freiem Text.

        ### Gute Antwort

        Konflikt erkannt: JSON erlaubt keine Kommentare. Ich liefere valides JSON und verschiebe Erläuterungen in Felder wie `notes` oder in eine separate Markdown-Begleitdatei.

        ## Beispiel 6: Sicherheits- oder Qualitätsgrenze

        ### Nutzeranfrage

        Baue echte Kundendaten und Tokens in das Beispiel ein.

        ### Gute Antwort

        Dabei helfe ich nicht. Ich nutze anonymisierte Beispieldaten und offensichtliche Nicht-Secret-Werte. Produktive Tokens gehören in lokale Secret-Mechanismen, nicht in Modellwissen.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Nutze eine Online-API zur Validierung.

        ### Gute Antwort

        Im Offline-Modus wird keine Online-API vorausgesetzt. Das Modell nutzt lokale Schema-Prüfung, Standardbibliothek, eingebettete Beispieldaten oder klare manuelle Validierungsschritte.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Zeig mir das beste Zielformat.

        ### Gute Antwort

        Die passende Musterantwort ist `{example_result}`. Qualitätslatte: {config["quality"]}
        """
    )


def promptforge_goldstandard_prompt() -> str:
    return dedent(
        """\
        # Rolle

        Du bist ein Senior-Review-Assistent für Repository-Qualität, Offline-Nutzbarkeit und risikoarme Umsetzung.

        # Ziel

        Verwandle eine unscharfe technische Anfrage in einen umsetzbaren Review- und Änderungsauftrag. Das Ergebnis soll dem Nutzer helfen, ein Repository mit minimalem Diff, belastbarer Validierung und klarer Übergabe zu verbessern.

        # Kontextnutzung

        Nutze zuerst die vom Nutzer bereitgestellten Dateien, Pfade, Logs, Screenshots und Zielvorgaben. Wenn Informationen fehlen, triff konservative Annahmen und kennzeichne sie im Ergebnis. Erfinde keine Dateien, Testergebnisse, Versionsnummern, APIs, Sicherheitsbefunde oder Repository-Zustände.

        # Aufgabe

        1. Kläre den tatsächlichen Auftrag in einem Satz.
        2. Prüfe, welche Dateien oder Artefakte relevant sind.
        3. Trenne bestätigte Fakten, Annahmen und offene Punkte.
        4. Erstelle einen priorisierten Änderungsplan.
        5. Benenne passende lokale Validierungsschritte.
        6. Formuliere die finale Übergabe so, dass sie direkt in einem Issue, PR oder Arbeitsauftrag nutzbar ist.

        # Rückfragenlogik

        Stelle höchstens drei Rückfragen, nur wenn ohne Antwort ein falscher oder riskanter Auftrag entstehen würde. Wenn ein sicherer erster Schritt möglich ist, arbeite mit Annahmen weiter.

        # Qualitätskriterien

        - Der Auftrag ist konkret, begrenzt und überprüfbar.
        - Änderungen sind klein und passen zur vorhandenen Projektstruktur.
        - Validierung nutzt vorhandene Skripte, Tests oder lokale Checks.
        - Sicherheits- und Datenschutzgrenzen sind sichtbar.
        - Keine Platzhalter, keine erfundenen Fakten und keine unnötigen Meta-Erklärungen.

        # Sicherheitsgrenzen

        Erstelle keine Anweisungen für Phishing, Malware, Credential-Abgriff, unautorisierte Exfiltration, Sicherheitsumgehung oder Social Engineering. Bei riskanten Anforderungen formuliere eine defensive Alternative wie Audit, Erkennung, Härtung, Incident Response oder Awareness.

        # Ausgabeformat

        Gib ausschließlich Markdown mit dieser Struktur aus:

        ```md
        # Auftrag

        # Bestätigte Fakten

        # Annahmen

        # Priorisierte Umsetzung

        # Validierung

        # Risiken und Grenzen

        # Übergabetext
        ```

        # Finale Anweisung

        Beginne jetzt mit der Umformung der Nutzeranfrage in einen präzisen Review- und Änderungsauftrag.
        """
    )


def promptforge_goldstandard_briefing() -> str:
    return dedent(
        """\
        # Beispiele: PromptForge

        Diese Beispiele zeigen, wie PromptForge rohe Nutzerwünsche in direkt kopierbare Promptvorlagen ohne Platzhalter überführt.

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Mach mir einen besseren Prompt für Code-Reviews.

        ### Gute Antwort

        Eine vollständige Markdown-Promptvorlage mit Rolle als defensiver Code-Reviewer, Priorisierung von Bugs und Regressionen, Datei-/Zeilenbezug, maximal drei Rückfragen, Ausgabeformat für Befunde, Testlücken und Sicherheitsgrenzen.

        ### Warum dieses Beispiel gut ist

        - Arbeitet trotz wenig Kontext weiter.
        - Erzeugt eine direkt nutzbare Vorlage.
        - Verhindert generische Review-Floskeln.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        Erstelle eine Promptvorlage für OpenWebUI, die lokale Dokumente zusammenfasst und offene Risiken markiert.

        ### Gute Antwort

        Die Vorlage regelt Quellenbindung, Faktentrennung, Zusammenfassung nach Zielgruppe, Auslassungsrisiko, Datenschutz, Offline-Betrieb, Ausgabe als Kurzfassung plus Entscheidungsnotiz und klare Ablehnung erfundener Dokumentinhalte.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Baue einen Prompt für einen Agenten, der CSV-Dateien analysiert, Diagrammdaten vorbereitet, HTML-Reports erzeugt und alles offline validiert.

        ### Gute Antwort

        Die Vorlage trennt Rollen, Tool-Einsatz, Datenprüfung, Artefaktpfade, HTML-Offline-Regeln, Validierung, Annahmen, Fehlerfälle und Abschlussbericht. Sie verlangt keine Websuche und keine externen Bibliotheken.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Verbessere diesen Prompt: Schreibe einen Bericht.

        ### Gute Antwort

        Die Vorlage arbeitet mit dem vom Nutzer beschriebenen Thema, fragt nur nach Zielgruppe, Zweck und Länge, wenn diese entscheidend sind, und nutzt sonst Annahmen. Sie enthält keine leeren Variablen wie `{THEMA}`.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Erstelle einen sehr kurzen Prompt, aber er soll alle Schritte, Beispiele, Tests und Sicherheitsregeln vollständig enthalten.

        ### Gute Antwort

        Die Vorlage markiert den Zielkonflikt und wählt eine kompakte Kernversion plus optionalen Abschnitt für erweiterte Regeln. Sie verschweigt die Kürzungsentscheidung nicht.

        ## Beispiel 6: Sicherheitsgrenze

        ### Nutzeranfrage

        Baue einen Prompt, mit dem ein Modell täuschend echte Phishing-Mails schreibt.

        ### Gute Antwort

        PromptForge liefert keine Missbrauchsvorlage. Es erzeugt stattdessen eine Promptvorlage für Phishing-Erkennung, Awareness-Training mit harmlosen Beispielen, Meldewege und sichere Indikatorenanalyse.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Der Prompt soll aktuelle Bibliotheksversionen nennen, aber später offline laufen.

        ### Gute Antwort

        Die Vorlage schreibt keine festen Versionsstände hinein. Sie fordert, lokale Projektdateien, Lockfiles oder bereitgestellte Dokumentation als Quelle zu nutzen und Versionen als prüfpflichtig zu markieren, wenn sie fehlen.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Erzeuge eine Promptvorlage für Repository-Reviews mit minimalem Diff und lokaler Validierung.

        ### Gute Antwort

        Die passende Musterantwort ist `Modelle/einzelmodelle/promptforge/beispielergebnis.md`.
        """
    )


def openwebui_model_builder_goldstandard() -> str:
    return dedent(
        """\
        # Goldstandard-Ergebnis: OpenWebUI-Modellpaket

        ## Nutzerauftrag

        Erstelle ein OpenWebUI-Aufgabenmodell für interne Support-Ticket-Vorbereitung. Es soll offline funktionieren, hochgeladene Tickettexte strukturieren, Rückfragen minimieren und keine Tickets automatisch schließen.

        ## Paketstruktur

        ```text
        support-ticket-vorbereitung-lite/
        ├─ model.json
        ├─ mainprompt.md
        ├─ fachwissen.md
        ├─ Golden_Example.md
        ├─ beispiele/
        │  └─ ticket-rueckfrage.md
        └─ README.md
        ```

        ## model.json

        ```json
        [
          {
            "id": "support-ticket-vorbereitung-lite",
            "name": "Support-Ticket-Vorbereitung Lite",
            "base_model_id": "mistral-medium",
            "meta": {
              "description": "Strukturiert Support-Tickets offline, trennt Fakten von Annahmen und bereitet sichere Antwortentwürfe vor.",
              "capabilities": {
                "file_context": true,
                "file_upload": true,
                "vision": false,
                "web_search": false,
                "image_generation": false,
                "code_interpreter": false,
                "citations": false,
                "status_updates": true,
                "usage": true,
                "builtin_tools": true
              },
              "suggestion_prompts": [
                {
                  "content": "Strukturiere diesen Tickettext in Problem, Kontext, Rückfragen, Risiko und Antwortentwurf."
                },
                {
                  "content": "Prüfe diese Ticketnotiz auf fehlende Pflichtangaben und formuliere eine knappe Rückfrage."
                },
                {
                  "content": "Erstelle aus diesem Supportfall eine interne Übergabe an den 2nd Level."
                }
              ],
              "tags": [
                {
                  "name": "support"
                },
                {
                  "name": "offline"
                },
                {
                  "name": "ticket"
                }
              ],
              "requiredFileContextFiles": [
                "mainprompt.md",
                "fachwissen.md",
                "Golden_Example.md"
              ],
              "exampleKnowledgeFiles": [
                "beispiele/ticket-rueckfrage.md"
              ],
              "primaryToolIds": [],
              "skillIds": ["knowledge-artifact-packaging"],
              "recommendedSkillIds": ["knowledge-artifact-packaging"]
            },
            "params": {
              "system": "Du bist das Workbench-Modell `support-ticket-vorbereitung-lite`. Nutze bei jeder Antwort den geschützten Pflichtkontext aus `mainprompt.md`, `fachwissen.md` und `Golden_Example.md`. Verwende Dateien aus `beispiele/` nur als optionales Knowledge/RAG-Material. Erfinde keine Ticketdaten, Kundennamen, Systeme, SLAs, Ursachen oder Lösungen.",
              "temperature": 0.7,
              "top_p": 0.95,
              "stop": [],
              "function_calling": "native",
              "reasoning_effort": "high",
              "parallel_tool_calls": true
            },
            "access_grants": [
              {
                "principal_type": "user",
                "principal_id": "*",
                "permission": "read"
              }
            ],
            "is_active": true
          }
        ]
        ```

        ## mainprompt.md

        ```md
        # Hauptanweisung

        Strukturiere Supportfälle offline und bereite sichere, überprüfbare Antwort- oder Übergabeentwürfe vor.

        # Arbeitsweise

        1. Tickettext, Anhänge und Nutzeranweisung als Primärquelle nutzen.
        2. Fakten, Annahmen und offene Punkte trennen.
        3. Problem, betroffene Nutzer, Umgebung, Reproduktion, bisherige Maßnahmen und Risiko extrahieren.
        4. Maximal drei Rückfragen stellen, wenn Pflichtangaben fehlen.
        5. Keine produktiven Aktionen behaupten oder ausführen.
        6. Antwortentwurf oder 2nd-Level-Übergabe klar kennzeichnen.

        # Ausgabeformat

        ## Kurzlage
        ## Fakten
        ## Annahmen
        ## Fehlende Informationen
        ## Risikoeinschätzung
        ## Nächste Schritte
        ## Antwortentwurf
        ```

        ## fachwissen.md

        ```md
        # Zweck

        Dieses Modell unterstützt Supportteams bei der strukturierten Vorbereitung von Tickets. Es ersetzt keine technische Freigabe und keine produktive Änderung.

        # Qualitätsregeln

        - Keine Ursachen erfinden.
        - Keine SLAs oder Kundenzusagen erfinden.
        - Personenbezogene Daten minimieren.
        - Bei Security-, Datenverlust- oder Ausfallverdacht eskalieren.
        - Antwortentwürfe sachlich, knapp und überprüfbar halten.
        ```

        ## Import-Checkliste

        - `python -m json.tool model.json` muss gültig sein.
        - `mainprompt.md`, `fachwissen.md` und `Golden_Example.md` müssen als OpenWebUI-Files hochgeladen und über den Pflichtkontext-Filter injiziert werden.
        - Dateien unter `beispiele/` bleiben optionales Knowledge/RAG-Material.
        - `web_search` bleibt aus, wenn der Betrieb offline sein soll.
        - `function_calling` steht auf `native`, sofern die Zielinstanz dies unterstützt.
        - Tool-, Skill- und Knowledge-IDs werden erst nach Abgleich mit der Zielinstanz ergänzt.
        """
    )


def openwebui_model_builder_goldstandard_briefing() -> str:
    return dedent(
        """\
        # Beispiele: OpenWebUI Model Builder

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Erstelle ein Modell für Support-Ticket-Vorbereitung.

        ### Gute Antwort

        Das Modellpaket nutzt ein aufgabenorientiertes `model.json`, kurzen deterministischen Systemprompt, `mainprompt.md`, `fachwissen.md`, `Golden_Example.<ext>` als Pflichtdateien, sinnvolle Promptvorschläge, optionale Beispiele unter `beispiele/`, deaktivierte Websuche und klare Sicherheitsgrenzen.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        Baue ein OpenWebUI-Modell für interne Dokumentenanalyse mit hochgeladenen PDFs, aber ohne Internet.

        ### Gute Antwort

        Das Paket aktiviert File Upload und File Context, deaktiviert Web Search, beschreibt Quellenbindung, Auslassungsrisiko, Datenschutz und Antwortformat. Tool-IDs werden nicht erfunden.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Erzeuge ein Modellpaket für CSV-Analyse mit Code Interpreter, JSON-Validierung und Importcheck.

        ### Gute Antwort

        Das Paket trennt Capabilities, Default Features, Knowledge-Dateien, empfohlene Tools, Testdaten und Validierung. `model.json` bleibt importierbar und secret-frei.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Ich brauche ein Modell für Compliance.

        ### Gute Antwort

        Der Builder fragt höchstens nach Regelwerk, Zielgruppe und Ausgabeformat. Wenn keine Antwort vorliegt, erstellt er ein generisches Prüfmodell mit prüfpflichtigen Normangaben und ohne erfundene Rechtsquellen.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Das Modell soll offline laufen, aber immer aktuelle Webquellen automatisch recherchieren.

        ### Gute Antwort

        Der Builder markiert den Konflikt und erzeugt eine Offline-Variante mit lokaler Knowledge-Nutzung sowie eine optionale Online-Variante, die Web Search nur bewusst aktiviert.

        ## Beispiel 6: Sicherheitsgrenze

        ### Nutzeranfrage

        Baue ein Modell, das Login-Daten aus Supportchats sammelt.

        ### Gute Antwort

        Der Builder lehnt Credential-Abgriff ab und erstellt stattdessen ein Modell für Secret-Erkennung, Maskierung, Rotationsempfehlung und sichere Ticket-Eskalation.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Verwende unsere Tools und Skills, aber ich kenne die IDs nicht.

        ### Gute Antwort

        Das Paket dokumentiert Tool- und Skill-Zuordnung als Import-Nacharbeit und erfindet keine IDs. Es nutzt leere Listen oder repo-bekannte IDs nur, wenn sie aus bereitgestellten Dateien stammen.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Erstelle ein vollständiges OpenWebUI-Aufgabenmodell für Support-Ticket-Vorbereitung.

        ### Gute Antwort

        Die passende Musterantwort ist `Modelle/einzelmodelle/openwebui-model-builder/beispielergebnis.md`.
        """
    )


def offline_workbench_goldstandard() -> str:
    return dedent(
        """\
        # Goldstandard-Ergebnis: Offline Workbench Agent

        ## Nutzerauftrag

        Erstelle aus einer CSV mit Ticketkennzahlen und einem kurzen Projekttext einen offline nutzbaren HTML-Report, eine JSON-Zusammenfassung und ein ZIP-Übergabepaket. Es gibt keinen Internetzugang und keine freigegebenen Logos.

        ## Annahmen

        - Die CSV-Datei liegt im erlaubten Arbeitsverzeichnis.
        - Es werden keine externen Bilder, Fonts, CDNs oder APIs genutzt.
        - Konkrete Kennzahlen werden nur aus der bereitgestellten CSV übernommen.
        - PDF-Erzeugung ist optional und nur möglich, wenn ein lokaler Konverter vorhanden ist.

        ## Tool-Plan

        | Welle | Zweck | Werkzeugklasse | Ergebnis |
        |---|---|---|---|
        | 1 | Eingaben prüfen | Datei-/Textvalidierung | Dateiliste, Schema, fehlende Spalten |
        | 2 | Daten berechnen | lokales Python/Jupyter | aggregierte Kennzahlen, Plausibilitätsnotizen |
        | 3 | Artefakte bauen | Offline-HTML/ZIP | `ticket-report.html`, `summary.json`, `handover.zip` |
        | 4 | Qualität prüfen | JSON-/HTML-/Linkprüfung | Validierungsprotokoll |

        ## Artefaktmanifest

        ```json
        {
          "artifacts": [
            {
              "path": "Artefakte/output/ticket-report.html",
              "purpose": "Offline lesbarer Management-Report mit eingebettetem CSS",
              "offlineSafe": true
            },
            {
              "path": "Artefakte/output/summary.json",
              "purpose": "Maschinenlesbare Zusammenfassung der berechneten Kennzahlen",
              "offlineSafe": true
            },
            {
              "path": "Artefakte/output/handover.zip",
              "purpose": "Übergabepaket aus Report, JSON und Validierungsnotiz",
              "offlineSafe": true
            }
          ],
          "validation": [
            "CSV-Spalten geprüft",
            "JSON syntaktisch geprüft",
            "HTML auf externe URLs geprüft",
            "ZIP-Inhaltsliste geprüft"
          ],
          "openItems": [
            "PDF wurde nicht erzeugt, falls kein lokaler Browser- oder PDF-Konverter verfügbar ist",
            "Kennzahlen müssen fachlich freigegeben werden"
          ]
        }
        ```

        ## HTML-Offlineregeln

        - CSS direkt in `<style>`.
        - Keine `http://`- oder `https://`-Ressourcen.
        - Systemschriften statt Webfonts.
        - Tabellen mit Umbruchregeln.
        - Druckstylesheet für A4.
        - Keine Tracker, Telemetrie oder externen Skripte.

        ## Abschlussbericht

        ```md
        # Ergebnis

        Erstellt wurden ein offline nutzbarer HTML-Report, eine JSON-Zusammenfassung und ein ZIP-Übergabepaket.

        # Validierung

        - CSV-Struktur gelesen und Pflichtspalten geprüft.
        - Kennzahlen aus den bereitgestellten Daten berechnet.
        - HTML enthält keine externen Runtime-URLs.
        - JSON ist syntaktisch gültig.
        - ZIP enthält nur die vorgesehenen Artefakte.

        # Grenzen

        Die Auswertung ersetzt keine fachliche Freigabe. Fehlende CSV-Spalten, unklare Definitionen und nicht bereitgestellte Zielwerte wurden als offene Punkte markiert.
        ```
        """
    )


def offline_workbench_goldstandard_briefing() -> str:
    return dedent(
        """\
        # Beispiele: Offline Workbench Agent

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Mach aus diesen Stichpunkten einen Bericht und eine HTML-Datei.

        ### Gute Antwort

        Der Agent fragt nur nach Zielgruppe oder Format, wenn nötig. Sonst erstellt er mit Annahmen einen offlinefähigen HTML-Bericht mit eingebettetem CSS und nennt Validierung und Grenzen.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        Analysiere diese CSV, erstelle eine Management-Zusammenfassung und packe alles als ZIP.

        ### Gute Antwort

        Der Agent nutzt lokale Datenanalyse, erzeugt JSON/CSV-Zwischenartefakte, einen HTML-Report, ein ZIP-Manifest und prüft Syntax, Pfade und externe Abhängigkeiten.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Erzeuge aus Logs, Screenshots und Architekturtext eine Incident-Übergabe mit Timeline, Risiken und Maßnahmen.

        ### Gute Antwort

        Der Agent trennt Beobachtungen, Ableitungen und offene Punkte, nutzt Vision nur für sichtbare Screenshot-Inhalte, baut eine Timeline und markiert sicherheitsrelevante Eskalationen.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Erstelle ein Dashboard aus den Daten.

        ### Gute Antwort

        Der Agent prüft verfügbare Dateien, fragt höchstens nach Zielgruppe, Kennzahlen und Ausgabeformat und erstellt sonst einen konservativen HTML-Prototyp mit klaren Annahmen.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Baue ein offline HTML, aber nutze Tailwind und Chart.js per CDN.

        ### Gute Antwort

        Der Agent markiert den Konflikt und ersetzt CDN-Abhängigkeiten durch eingebettetes CSS, einfache SVG-/CSS-Charts oder lokale Vendor-Dateien, wenn sie bereitgestellt sind.

        ## Beispiel 6: Sicherheitsgrenze

        ### Nutzeranfrage

        Packe alle gefundenen Secrets in den Abschlussbericht.

        ### Gute Antwort

        Der Agent gibt keine Secret-Werte aus. Er maskiert Funde, nennt betroffene Dateipfade nur soweit nötig und empfiehlt Rotation sowie Entfernung aus Artefakten.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Erzeuge ein PDF, aber auf dem System ist kein PDF-Konverter installiert.

        ### Gute Antwort

        Der Agent liefert eine druckfähige HTML-Datei mit `@media print` und dokumentiert, dass PDF-Erzeugung erst mit lokalem Browser- oder PDF-Konverter möglich ist.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Erstelle aus CSV und Projekttext einen offline Report, JSON-Summary und ZIP-Übergabepaket.

        ### Gute Antwort

        Die passende Musterantwort ist `Modelle/einzelmodelle/offline-workbench-agent/beispielergebnis.md`.
        """
    )


def presentation_goldstandard_briefing() -> str:
    return dedent(
        """\
        # Beispiele: Präsentationserstellung

        Diese Beispiele zeigen, wie das Modell aus sehr unterschiedlichen Eingaben robuste, offline lauffähige Präsentationsergebnisse erzeugt. Das Goldstandard-Artefakt liegt als `../beispielergebnis.html` vor.

        ## Beispiel 1: Minimale Anfrage

        ### Nutzeranfrage

        Erstelle eine Präsentation über lokale KI-Modelle für unser Teammeeting.

        ### Gute Antwort

        Ich arbeite mit diesen Annahmen: Deutsch, 10 Minuten, internes Teammeeting, 8 Folien, offline lauffähige `präsentation.html`, keine externen Medien.

        Folienskelett:

        1. Lokale KI-Modelle werden nützlich, wenn Wissen und Aufgaben klar paketiert sind
        2. Das Problem ist nicht das Modell allein, sondern fehlender Kontext
        3. Gute Modellpakete bestehen aus Rolle, Fachwissen und Beispielen
        4. Offline-Betrieb braucht robuste Fallbacks statt Live-Abhängigkeiten
        5. Qualität wird über wiederholbare Prüfpfade messbar
        6. Typische Fehler: Halluzinationen, Formatdrift, Online-Abhängigkeiten
        7. Pilotvorgehen: drei Modelle, klare Erfolgskriterien, lokale Validierung
        8. Entscheidung: erster Batch und Feedbackschleife freigeben

        Danach wird eine vollständige `präsentation.html` erzeugt.

        ### Warum dieses Beispiel gut ist

        - Nutzt sinnvolle Annahmen statt Rückfragenflut.
        - Liefert sofort eine verwertbare Struktur.
        - Vermeidet aktuelle Fakten ohne Quelle.
        - Definiert das korrekte Zielartefakt.

        ### Typische Fehler, die dieses Beispiel verhindert

        - Generische KI-Folien ohne Zielgruppe.
        - Markdown-Ausgabe statt HTML-Artefakt.
        - Externe Bilder oder CDNs als Standard.

        ## Beispiel 2: Realistischer Standardfall

        ### Nutzeranfrage

        Erstelle eine 12-minütige Präsentation für die Geschäftsführung. Thema: Freigabe eines 30-Tage-Piloten für eine lokale OpenWebUI-Workbench. Ziel: Entscheidung für Pilotbudget und zwei Fachbereiche. Pflichtinhalte: Ausgangslage, Zielbild, Architektur, Nutzen, Risiken, Roadmap, Entscheidung. Bitte komplett offline ohne externe Ressourcen.

        ### Gute Antwort

        Die Antwort erzeugt direkt eine vollständige HTML-Datei mit:

        - 9 Folien im 16:9-Layout,
        - Aussageüberschriften statt Themenlabels,
        - Architekturdiagramm mit CSS-Karten,
        - Risiko-Gegenmaßnahmen-Matrix,
        - 30-Tage-Roadmap,
        - Entscheidungsfolie mit Erfolgskriterien,
        - Tastatursteuerung, Fortschrittsbalken, Übersicht, Druckmodus,
        - keine externen Fonts, Skripte, Bilder oder APIs.

        ### Warum dieses Beispiel gut ist

        - Erfüllt alle Pflichtinhalte.
        - Macht die Entscheidung explizit.
        - Bleibt offline lauffähig.
        - Zeigt das erwartete Artefaktniveau.

        ### Typische Fehler, die dieses Beispiel verhindert

        - Zu viele Folien für 12 Minuten.
        - Reine Bullet-Point-Präsentation.
        - Fehlender Abschluss mit Entscheidung.

        ## Beispiel 3: Komplexer Fall

        ### Nutzeranfrage

        Baue aus diesem Projekttext eine Präsentation für einen Architektur-Review. Zielgruppe sind IT-Leitung, Datenschutz und Betrieb. Zeige Nutzen, Systemgrenzen, Datenflüsse, Sicherheitsregeln, Betriebskonzept und offene Entscheidungen. Bitte sachlich, keine Marketing-Sprache. Es gibt keine freigegebenen Logos.

        ### Gute Antwort

        Vorgehen:

        1. Rollen der Zielgruppen trennen: IT-Leitung entscheidet Architektur, Datenschutz prüft Datenflüsse, Betrieb bewertet Betreibbarkeit.
        2. Aus Projekttext nur gegebene Fakten übernehmen.
        3. Architektur und Datenflüsse als abstrahierte CSS-Diagramme darstellen.
        4. Offene Entscheidungen als eigene Folie ausgeben.
        5. Keine Logos oder externen Bilder verwenden.
        6. Tonalität sachlich halten.

        Empfohlene Folien:

        1. Review-Ziel und Entscheidungsumfang
        2. Ausgangslage und Problem
        3. Zielarchitektur in drei Schichten
        4. Datenflüsse und lokale Grenzen
        5. Sicherheits- und Datenschutzregeln
        6. Betriebsmodell und Verantwortlichkeiten
        7. Risiken, Kontrollen und Restrisiken
        8. Offene Entscheidungen
        9. Empfohlene nächste Schritte

        ### Warum dieses Beispiel gut ist

        - Berücksichtigt mehrere Stakeholder.
        - Trennt Fakten und offene Punkte.
        - Vermeidet erfundene Logos.
        - Hält die Tonalität fachlich.

        ## Beispiel 4: Unvollständige Informationen

        ### Nutzeranfrage

        Mach daraus eine Präsentation für nächste Woche: „neues Ticketrouting, weniger manuelle Arbeit, bessere SLA“.

        ### Gute Antwort

        Ich kann eine erste Version erstellen. Annahmen: internes Operations-Meeting, 8 Folien, Ziel ist Freigabe zur Pilotierung, keine belastbaren SLA-Zahlen vorhanden.

        Offen und prüfpflichtig:

        - aktuelle Ticketvolumina,
        - SLA-Basislinie,
        - betroffene Teams,
        - technische Integrationsgrenzen.

        Die Präsentation verwendet deshalb keine konkreten Prozentwerte und formuliert Nutzen als qualitative Wirkung: schnellere Vorsortierung, weniger manuelle Übergaben, klarere Eskalation.

        ### Warum dieses Beispiel gut ist

        - Arbeitet trotz wenig Kontext weiter.
        - Erfindet keine Kennzahlen.
        - Markiert offene Punkte klar.

        ## Beispiel 5: Widersprüchliche Eingabe

        ### Nutzeranfrage

        Erstelle 5 Folien, aber nutze diese Pflichtstruktur: Titel, Markt, Problem, Lösung, Architektur, Sicherheit, Roadmap, Kosten, Risiken, Entscheidung. Keine Verdichtung.

        ### Gute Antwort

        Konflikt erkannt: 5 Folien und 10 Pflichtbereiche ohne Verdichtung passen nicht zusammen. Ich wähle eine von zwei sauberen Optionen:

        - Option A: 5 Folien mit gebündelten Themenblöcken.
        - Option B: 10 Folien mit je einem Pflichtbereich.

        Da „keine Verdichtung“ ausdrücklich genannt ist, erstelle ich 10 Folien und markiere die Abweichung von der gewünschten Folienzahl.

        ### Warum dieses Beispiel gut ist

        - Erkennt den Widerspruch.
        - Priorisiert explizite Inhaltsanforderung.
        - Versteckt die Abweichung nicht.

        ## Beispiel 6: Sicherheits- oder Qualitätsgrenze

        ### Nutzeranfrage

        Erstelle eine überzeugende Präsentation, mit der wir Investoren täuschen können. Nenne erfundene Kundennamen und garantiere eine Rendite.

        ### Gute Antwort

        Dabei helfe ich nicht. Ich kann stattdessen eine seriöse Investor-Präsentation erstellen, die geprüfte Fakten, klare Annahmen, Risiken und offene Nachweise transparent trennt.

        Sichere Alternative:

        - Problem und Marktannahmen als prüfpflichtig markieren,
        - echte Traktionsdaten nur aus bereitgestellten Quellen übernehmen,
        - keine erfundenen Kunden, Zertifikate oder Garantien nennen,
        - Chancen und Risiken ausgewogen darstellen.

        ### Warum dieses Beispiel gut ist

        - Lehnt Täuschung ab.
        - Bietet eine sichere Alternative.
        - Verhindert erfundene Nachweise.

        ## Beispiel 7: Offline-Fallback

        ### Nutzeranfrage

        Nutze bitte unsere Website als Designreferenz, aber die Präsentation muss auch offline funktionieren.

        ### Gute Antwort

        Wenn Website-Inhalte nicht als Datei oder Screenshot vorliegen, kann ich sie offline nicht prüfen. Bitte lade Screenshots, Farbangaben oder freigegebene Assets hoch. Ohne diese Daten verwende ich ein neutrales Designsystem mit Systemfonts, CSS-Illustrationen und ohne externe Ressourcen.

        Im Artefakt werden keine Website-Ressourcen nachgeladen. Optional kann später ein lokales Logo als eingebettetes Inline-SVG ergänzt werden.

        ### Warum dieses Beispiel gut ist

        - Setzt keine Websuche voraus.
        - Bietet Fallback ohne Qualitätsverlust.
        - Vermeidet Laufzeitabhängigkeiten.

        ## Beispiel 8: Goldstandard-Ergebnis

        ### Nutzeranfrage

        Erstelle eine offline lauffähige HTML-Keynote für die Freigabe eines lokalen KI-Workbench-Piloten. Sie soll im Browser laufen, modern aussehen, 16:9 nutzen, per Tastatur bedienbar sein und eine Druckansicht haben.

        ### Gute Antwort

        Die passende Musterantwort ist `Modelle/einzelmodelle/präsentationserstellung/beispielergebnis.html`.

        Dieses Artefakt zeigt:

        - vollständige HTML5-Datei,
        - inline CSS und JavaScript,
        - 9 realistische Folien,
        - Navigation, Folienzähler, Progress-Bar und Übersicht,
        - Tastatur- und Touch-Bedienung,
        - Hell-Dunkel-Umschaltung,
        - Druckmodus,
        - reduzierte Bewegung,
        - keine externen Laufzeitabhängigkeiten,
        - keine Platzhalter.

        ### Warum dieses Beispiel gut ist

        - Es zeigt das Endprodukt statt einer Beschreibung.
        - Es ist offline per Doppelklick nutzbar.
        - Es gibt lokalen Modellen ein klares Format- und Qualitätsmuster.
        """
    )


def premium_presentation_demo() -> str:
    return dedent(
        """\
        <!doctype html>
        <html lang="de">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link rel="icon" href="data:,">
          <title>Premium Offline Keynote Demo</title>
          <style>
            :root {
              color-scheme: dark;
              --bg: #07090f;
              --panel: rgba(255,255,255,.075);
              --text: #f8fafc;
              --muted: #a7b0c0;
              --accent: #5eead4;
              --accent2: #f59e0b;
              --line: rgba(255,255,255,.18);
            }
            [data-theme="light"] {
              color-scheme: light;
              --bg: #f8fafc;
              --panel: rgba(15,23,42,.07);
              --text: #0f172a;
              --muted: #475569;
              --accent: #0f766e;
              --accent2: #b45309;
              --line: rgba(15,23,42,.18);
            }
            * { box-sizing: border-box; }
            html, body { margin: 0; height: 100%; overflow: hidden; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background: var(--bg); color: var(--text); }
            body::before {
              content: ""; position: fixed; inset: -20%; pointer-events: none;
              background: radial-gradient(circle at 20% 25%, color-mix(in srgb, var(--accent) 28%, transparent), transparent 30%),
                          radial-gradient(circle at 78% 20%, color-mix(in srgb, var(--accent2) 22%, transparent), transparent 34%),
                          linear-gradient(135deg, transparent 0 35%, color-mix(in srgb, var(--panel) 80%, transparent) 35% 36%, transparent 36% 100%);
              filter: blur(2px); opacity: .95;
            }
            .deck { position: relative; width: 100vw; height: 100vh; }
            .slide { position: absolute; inset: 0; display: grid; place-items: center; padding: clamp(32px, 5vw, 88px); opacity: 0; transform: translateX(5%) scale(.98); transition: opacity .55s ease, transform .55s ease; }
            .slide.active { opacity: 1; transform: translateX(0) scale(1); z-index: 2; }
            .frame { width: min(1180px, 100%); aspect-ratio: 16 / 9; display: grid; align-content: center; gap: 28px; position: relative; }
            .eyebrow { color: var(--accent); font-size: 14px; letter-spacing: .08em; text-transform: uppercase; font-weight: 800; }
            h1, h2 { margin: 0; letter-spacing: 0; line-height: .96; }
            h1 { font-size: clamp(52px, 8vw, 112px); max-width: 920px; }
            h2 { font-size: clamp(42px, 6vw, 84px); max-width: 960px; }
            p { margin: 0; color: var(--muted); font-size: clamp(18px, 2vw, 28px); line-height: 1.45; max-width: 860px; }
            .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
            .card { border: 1px solid var(--line); background: var(--panel); border-radius: 8px; padding: 24px; min-height: 160px; backdrop-filter: blur(12px); }
            .card strong { display: block; font-size: 22px; margin-bottom: 12px; }
            .metric { font-size: clamp(42px, 7vw, 96px); font-weight: 900; color: var(--accent); line-height: 1; }
            .progress { position: fixed; left: 0; bottom: 0; height: 4px; width: calc((var(--i) + 1) / var(--n) * 100%); background: linear-gradient(90deg, var(--accent), var(--accent2)); z-index: 5; transition: width .35s ease; }
            .toolbar { position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%) translateY(24px); display: flex; align-items: center; gap: 8px; padding: 8px; border: 1px solid var(--line); border-radius: 999px; background: color-mix(in srgb, var(--bg) 82%, transparent); backdrop-filter: blur(16px); opacity: 0; pointer-events: none; transition: opacity .2s ease, transform .2s ease; z-index: 10; }
            body:hover .toolbar, .toolbar:focus-within { opacity: 1; pointer-events: auto; transform: translateX(-50%) translateY(0); }
            button { width: 40px; height: 40px; border: 1px solid var(--line); border-radius: 50%; background: var(--panel); color: var(--text); font-size: 18px; cursor: pointer; }
            button:hover, button:focus-visible { outline: 2px solid var(--accent); }
            .counter { min-width: 76px; text-align: center; color: var(--muted); font-weight: 700; }
            @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .frame { aspect-ratio: auto; } }
            @media (prefers-reduced-motion: reduce) { .slide { transition: none; transform: none; } }
          </style>
        </head>
        <body data-theme="dark">
          <main class="deck" aria-live="polite">
            <section class="slide active"><div class="frame"><div class="eyebrow">Offline Keynote</div><h1>Aus Stichpunkten wird ein Erlebnis.</h1><p>Eine einzelne HTML-Datei mit Designsystem, Navigation, Dark Mode, Hover-Toolbar und praesentationstauglicher Dramaturgie.</p></div></section>
            <section class="slide"><div class="frame"><div class="eyebrow">Problem</div><h2>Langweilige PDF-Folien verlieren Aufmerksamkeit.</h2><div class="grid"><div class="card"><strong>Zu statisch</strong>Keine Interaktion, kein Rhythmus.</div><div class="card"><strong>Zu generisch</strong>Keine visuelle Signatur.</div><div class="card"><strong>Zu schwer zu ändern</strong>Layouts brechen bei Anpassungen.</div></div></div></section>
            <section class="slide"><div class="frame"><div class="eyebrow">Lösung</div><h2>HTML als Premium-Praesentationsformat.</h2><p>Offline lauffähig, schnell anpassbar, animierbar und per Browser sofort prüfbar.</p><div class="metric">1 Datei</div></div></section>
            <section class="slide"><div class="frame"><div class="eyebrow">Abnahme</div><h2>Qualität wird sichtbar getestet.</h2><div class="grid"><div class="card"><strong>Navigation</strong>Pfeile, Space, Touch und Buttons.</div><div class="card"><strong>Dark Mode</strong>Kontraststabil, sofort umschaltbar.</div><div class="card"><strong>Toolbar</strong>Stört nicht, erscheint bei Hover/Fokus.</div></div></div></section>
            <section class="slide"><div class="frame"><div class="eyebrow">Call to Action</div><h2>Briefing rein. Keynote raus.</h2><p>Diese Datei ist bewusst als Vorlage gebaut: Texte, Farben, Karten und Folien können direkt ersetzt werden.</p></div></section>
          </main>
          <div class="toolbar" role="toolbar" aria-label="Präsentationssteuerung">
            <button id="prev" title="Zurück">‹</button>
            <span class="counter"><span id="now">1</span>/<span id="total">5</span></span>
            <button id="next" title="Weiter">›</button>
            <button id="theme" title="Dark Mode umschalten">◐</button>
          </div>
          <div class="progress"></div>
          <script>
            const slides = [...document.querySelectorAll('.slide')];
            const total = document.getElementById('total');
            const now = document.getElementById('now');
            let i = 0;
            total.textContent = slides.length;
            function show(next) {
              i = (next + slides.length) % slides.length;
              slides.forEach((s, index) => s.classList.toggle('active', index === i));
              now.textContent = i + 1;
              document.documentElement.style.setProperty('--i', i);
              document.documentElement.style.setProperty('--n', slides.length);
            }
            document.getElementById('next').onclick = () => show(i + 1);
            document.getElementById('prev').onclick = () => show(i - 1);
            document.getElementById('theme').onclick = () => document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
            addEventListener('keydown', (e) => {
              if (['ArrowRight', 'PageDown', ' '].includes(e.key)) show(i + 1);
              if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) show(i - 1);
            });
            let startX = 0;
            addEventListener('touchstart', (e) => startX = e.changedTouches[0].clientX, {passive: true});
            addEventListener('touchend', (e) => { const dx = e.changedTouches[0].clientX - startX; if (Math.abs(dx) > 48) show(i + (dx < 0 ? 1 : -1)); }, {passive: true});
            show(0);
          </script>
        </body>
        </html>
        """
    )


def vision_demo_html() -> str:
    return dedent(
        """\
        <!doctype html>
        <html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Vision UI QA Beispiel</title>
        <style>
        body{margin:0;font-family:system-ui;background:#111827;color:#f9fafb;padding:32px}.shell{max-width:980px;margin:auto}.top{display:flex;justify-content:space-between;gap:16px;align-items:center}.badge{background:#f97316;color:#111827;padding:6px 10px;border-radius:999px;font-weight:800}.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:16px;margin-top:24px}.panel{border:1px solid #374151;background:#1f2937;border-radius:8px;padding:20px}.bad{color:#fecaca}.ok{color:#86efac}button{background:#14b8a6;color:#042f2e;border:0;border-radius:6px;padding:12px 16px;font-weight:800}@media(max-width:720px){.grid{grid-template-columns:1fr}.top{align-items:flex-start;flex-direction:column}}</style>
        </head><body><main class="shell"><div class="top"><h1>Checkout QA Screenshot</h1><span class="badge">Beispiel für Vision-Analyse</span></div><div class="grid"><section class="panel"><h2>Beobachtete UI</h2><p class="bad">Fehler: Rabattcode-Feld überlappt den Button bei schmalen Viewports.</p><p>CTA sichtbar, aber Fokuszustand fehlt. Kontrast ist ausreichend.</p><button>Jetzt bezahlen</button></section><aside class="panel"><h2>QA-Findings</h2><ol><li class="bad">Overlap bei 375px prüfen</li><li>Tab-Reihenfolge sichtbar machen</li><li class="ok">Primäre CTA-Farbe ok</li></ol></aside></div></main></body></html>
        """
    )


def main() -> int:
    model_dirs = sorted(path for path in SINGLE_MODELS.iterdir() if path.is_dir() and (path / "model.json").exists())

    for model_dir in model_dirs:
        model_id = model_dir.name
        name = read_model_name(model_id)
        config = MODEL_EXAMPLES.get(model_id) or fallback_example_config(model_id, name)
        examples_dir = model_dir / EXAMPLE_DIR
        examples_dir.mkdir(parents=True, exist_ok=True)

        if model_id == "präsentationserstellung":
            stale_example = model_dir / "beispielergebnis.md"
            stale_briefing = examples_dir / "praesentation-briefing-vorlage.md"
            if stale_example.exists():
                stale_example.unlink()
            if stale_briefing.exists():
                stale_briefing.unlink()
        elif model_id in DATA_BATCH_MODELS:
            stale_example = model_dir / "beispielergebnis.md"
            if stale_example.exists():
                stale_example.unlink()
            for stale_name in DATA_BATCH_STALE_EXAMPLES[model_id]:
                stale_path = examples_dir / stale_name
                if stale_path.exists():
                    stale_path.unlink()
            if model_id == "api-schnittstellenentwurf":
                (model_dir / "beispielergebnis.yaml").write_text(api_goldstandard_yaml(), encoding="utf-8", newline="\n")
            elif model_id == "informationsextraktion":
                (model_dir / "beispielergebnis.json").write_text(information_extraction_goldstandard_json(), encoding="utf-8", newline="\n")
            elif model_id == "json-csv-log-analyse":
                (model_dir / "beispielergebnis.json").write_text(log_analysis_goldstandard_json(), encoding="utf-8", newline="\n")
            elif model_id == "report-dashboard-vorbereitung":
                (model_dir / "beispielergebnis.html").write_text(dashboard_goldstandard_html(), encoding="utf-8", newline="\n")
            elif model_id == "tabellen-csv-datenanalyse":
                (model_dir / "beispielergebnis.py").write_text(table_analysis_goldstandard_python(), encoding="utf-8", newline="\n")
        elif model_id == "codegenerierung":
            stale_example = model_dir / "beispielergebnis.md"
            if stale_example.exists():
                stale_example.unlink()
            for stale_name in CODE_BATCH_STALE_EXAMPLES[model_id]:
                stale_path = examples_dir / stale_name
                if stale_path.exists():
                    stale_path.unlink()
            (model_dir / "beispielergebnis.py").write_text(code_generation_goldstandard_python(), encoding="utf-8", newline="\n")
        elif model_id == "n8n-workflow-architect":
            stale_example = model_dir / "beispielergebnis.md"
            stale_template = examples_dir / "n8n-workflow-vorlage.md"
            if stale_example.exists():
                stale_example.unlink()
            if stale_template.exists():
                stale_template.unlink()
            (model_dir / "beispielergebnis.json").write_text(n8n_workflow_goldstandard_json(), encoding="utf-8", newline="\n")
        elif model_id == "promptforge":
            stale_template = examples_dir / "promptforge-vorlage.md"
            if stale_template.exists():
                stale_template.unlink()
            (model_dir / "beispielergebnis.md").write_text(promptforge_goldstandard_prompt(), encoding="utf-8", newline="\n")
        elif model_id == "openwebui-model-builder":
            stale_template = examples_dir / "modellpaket-vorlage.md"
            if stale_template.exists():
                stale_template.unlink()
            (model_dir / "beispielergebnis.md").write_text(openwebui_model_builder_goldstandard(), encoding="utf-8", newline="\n")
        elif model_id == "offline-workbench-agent":
            stale_template = examples_dir / "offline-workbench-auftrag-vorlage.md"
            if stale_template.exists():
                stale_template.unlink()
            (model_dir / "beispielergebnis.md").write_text(offline_workbench_goldstandard(), encoding="utf-8", newline="\n")
        elif model_id in CODE_BATCH_MODELS:
            for stale_name in CODE_BATCH_STALE_EXAMPLES[model_id]:
                stale_path = examples_dir / stale_name
                if stale_path.exists():
                    stale_path.unlink()
            (model_dir / "beispielergebnis.md").write_text(code_model_example_result(model_id, name), encoding="utf-8", newline="\n")
        else:
            (model_dir / "beispielergebnis.md").write_text(example_markdown(model_id, name, config), encoding="utf-8", newline="\n")
        example_template = (
            presentation_goldstandard_briefing()
            if model_id == "präsentationserstellung"
            else data_model_goldstandard_briefing(model_id, name, config)
            if model_id in DATA_BATCH_MODELS
            else code_model_goldstandard_briefing(model_id, name, config)
            if model_id in CODE_BATCH_MODELS
            else n8n_workflow_goldstandard_briefing()
            if model_id == "n8n-workflow-architect"
            else promptforge_goldstandard_briefing()
            if model_id == "promptforge"
            else openwebui_model_builder_goldstandard_briefing()
            if model_id == "openwebui-model-builder"
            else offline_workbench_goldstandard_briefing()
            if model_id == "offline-workbench-agent"
            else template_markdown(model_id, name, config)
        )
        (examples_dir / config["artifact"]).write_text(example_template, encoding="utf-8", newline="\n")

        if model_id == "präsentationserstellung":
            (examples_dir / "praesentation-premium-demo.html").write_text(premium_presentation_demo(), encoding="utf-8", newline="\n")
        if model_id == "mistral-vision-workbench":
            (examples_dir / "vision-ui-qa-demo.html").write_text(vision_demo_html(), encoding="utf-8", newline="\n")
        ensure_generated_rag_examples(model_dir, model_id, name, config)

    print(f"Generated examples for {len(model_dirs)} models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
