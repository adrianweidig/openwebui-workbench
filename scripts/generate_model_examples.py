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
        "artifact": "api-design-vorlage.md",
        "scenario": "Ein Team braucht aus Fachanforderungen einen belastbaren API-Entwurf mit Beispielpayloads.",
        "vision": "Nutze Vision für Architekturdiagramme, Swagger-Screenshots, Sequenzskizzen oder Fehlermasken.",
        "quality": "Endpunkte, Schemas, Fehlercodes, Security und Testfälle müssen zusammenpassen.",
    },
    "code-dokumentation": {
        "purpose": "Code, Module, Datenflüsse und Betriebswissen in wartbare Entwicklerdokumentation überführen.",
        "artifact": "code-dokumentation-vorlage.md",
        "scenario": "Ein Repository soll mit Einstieg, Architektur, Komponenten und Betriebsnotizen dokumentiert werden.",
        "vision": "Nutze Vision für Architekturdiagramme, UI-Screenshots oder visuelle Ablaufgrafiken im Repo-Kontext.",
        "quality": "Die Dokumentation muss Dateipfade, Verantwortlichkeiten, Beispiele und Pflegehinweise enthalten.",
    },
    "code-review": {
        "purpose": "Diffs, Risiken, Regressionen, Sicherheitsprobleme und fehlende Tests wie in einem professionellen Review priorisieren.",
        "artifact": "code-review-finding-vorlage.md",
        "scenario": "Ein Patch soll mit Findings, Schweregrad, Repro-Hinweis und Testlücken bewertet werden.",
        "vision": "Nutze Vision für UI-Regressionsscreenshots, Vorher-/Nachher-Bilder oder visuelle Testfehler.",
        "quality": "Findings stehen vor Zusammenfassung und referenzieren konkrete Dateien, Zeilen oder sichtbare UI-Zustände.",
    },
    "codeanalyse": {
        "purpose": "Codebasen, Abhängigkeiten, Kontrollflüsse, Risiken und technische Ursachen strukturiert analysieren.",
        "artifact": "codeanalyse-bericht-vorlage.md",
        "scenario": "Eine unklare Codebasis soll mit Architektur, Hotspots und Hypothesen verstanden werden.",
        "vision": "Nutze Vision für Architektur-Screenshots, UI-Flows oder Diagramme, die Codeverhalten erklären.",
        "quality": "Trenne belegte Fakten aus Code/Tool-Ausgaben von Hypothesen und empfohlenen Messungen.",
    },
    "codegenerierung": {
        "purpose": "Bestehende Muster erkennen, zielgenauen Code erzeugen und lokale Validierung oder Tests vorbereiten.",
        "artifact": "implementierungsplan-vorlage.md",
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
        "artifact": "debugging-runbook-vorlage.md",
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
        "artifact": "extraktionsschema-vorlage.md",
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
        "artifact": "loganalyse-vorlage.md",
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
        "artifact": "n8n-workflow-vorlage.md",
        "scenario": "Ein Integrationsziel soll in einen prüfbaren n8n-Workflow mit Nodes, Credentials und Fehlerpfad überführt werden.",
        "vision": "Nutze Vision für n8n-Canvas-Screenshots, Node-Konfigurationen oder Fehleranzeigen.",
        "quality": "Workflow, Trigger, Datenvertrag, Fehlerbehandlung, Secrets und Testfälle müssen konsistent sein.",
    },
    "offline-workbench-agent": {
        "purpose": "Komplexe Offline-Aufgaben routen, Tools kombinieren und HTML/PDF/ZIP/Tabellen/Code-Artefakte lokal erzeugen.",
        "artifact": "offline-workbench-auftrag-vorlage.md",
        "scenario": "Eine mehrteilige Aufgabe soll mit Jupyter, Artefakt-Tools und Validierung end-to-end erledigt werden.",
        "vision": "Nutze Vision für Screenshots, Artefakt-QA, Diagramme, UI-Zustände und visuelle Eingaben.",
        "quality": "Der Plan muss Tool-Wellen, Artefaktpfade, Validierung und Übergabeformat enthalten.",
    },
    "openwebui-model-builder": {
        "purpose": "Vollständige OpenWebUI-Modellpakete mit Prompt, Wissen, Tools, Skills, Icons, Importplan und QA erzeugen.",
        "artifact": "modellpaket-vorlage.md",
        "scenario": "Aus einer Modellidee soll ein importierbares OpenWebUI-Modellpaket entstehen.",
        "vision": "Nutze Vision für Icon-/UI-Screenshots, Custom-GPT-Referenzen oder Modellprofil-Mockups.",
        "quality": "Paket muss model.json, systemprompt, mainprompt, fachwissen, Beispiel, Toolprofil und Importcheck enthalten.",
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
        "artifact": "promptforge-vorlage.md",
        "scenario": "Ein roher Nutzerprompt soll für ChatGPT, Custom GPT, OpenWebUI oder lokale LLMs verbessert werden.",
        "vision": "Nutze Vision für Screenshots von Zieloberflaechen, Prompt-Buildern, Fehlermeldungen oder Beispielausgaben.",
        "quality": "Prompt muss Rolle, Ziel, Kontext, Quellen, Toolregeln, Ausgabeformat, Grenzen und Erfolgskriterien enthalten.",
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
        "artifact": "refactoring-plan-vorlage.md",
        "scenario": "Ein Modul soll ohne Verhaltensbruch schrittweise umgebaut werden.",
        "vision": "Nutze Vision für UI-Verhaltensvergleiche, Architekturskizzen oder visuelle Regressionen.",
        "quality": "Plan braucht Scope, Nicht-Ziele, Reihenfolge, Tests, Rollback und Akzeptanzkriterien.",
    },
    "report-dashboard-vorbereitung": {
        "purpose": "Daten, Kennzahlen, Dashboard-Struktur, Visualisierungen und Storyline für Reports vorbereiten.",
        "artifact": "dashboard-briefing-vorlage.md",
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
        "artifact": "datenanalyse-notebook-plan-vorlage.md",
        "scenario": "Eine CSV soll mit Jupyter geprüft, bereinigt und zusammengefasst werden.",
        "vision": "Nutze Vision für fotografierte Tabellen oder Dashboard-Screenshots nur zur Orientierung; verlange Rohdaten für Berechnung.",
        "quality": "Analyse muss Schema, Datenqualität, Berechnung, Ergebnis und Reproduzierbarkeit enthalten.",
    },
    "testfall-generierung": {
        "purpose": "Aus Anforderungen, Code, UI-Screenshots und Risiken konkrete Testfälle und Akzeptanztests erzeugen.",
        "artifact": "testfallkatalog-vorlage.md",
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


def example_result_file_for_model(model_id: str) -> str:
    return "beispielergebnis.html" if model_id == "präsentationserstellung" else "beispielergebnis.md"


def example_markdown(model_id: str, name: str, config: dict[str, str]) -> str:
    example_result = example_result_file_for_model(model_id)
    return dedent(
        f"""\
        # Beispielergebnis und Arbeitsvorlage: {name}

        ## Zweck dieses Modells

        {config["purpose"]}

        ## Wiederverwendbarer Musterauftrag

        > {config["scenario"]}

        ## Erwartetes Ergebnisartefakt

        - Primäre Datei: `beispiele/{config["artifact"]}`
        - Format: befüllbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
        - Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

        ## Vision- und Screenshot-Nutzung

        {config["vision"]}

        ## Tool-first-Ablauf

        1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
        2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
        3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
        4. Ergebnis in der Vorlage unter `beispiele/{config["artifact"]}` strukturieren.
        5. Vor finaler Antwort gegen die Qualitäts- und Akzeptanzkriterien prüfen.

        ## Qualitätslatte

        {config["quality"]}

        ## Copy/Paste-Starterprompt

        ```text
        Nutze das Modell {name}. Verwende `{example_result}` und `beispiele/{config["artifact"]}` als Vorlage.

        Ziel:
        [Was soll am Ende konkret vorliegen?]

        Eingaben:
        [Dateien, Text, Screenshots, Daten, Constraints]

        Gewuenschtes Ergebnisformat:
        [Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Präsentation, Codeplan]

        Qualitätskriterien:
        [Was muss geprüft, validiert, visuell bewertet oder offline nutzbar sein?]
        ```
        """
    )


def template_markdown(model_id: str, name: str, config: dict[str, str]) -> str:
    return dedent(
        f"""\
        # {name} - befüllbare Ergebnisvorlage

        ## 1. Auftrag

        **Ziel:** [konkretes Ziel eintragen]

        **Eingaben:** [Dateien, Text, Screenshots, Daten, Constraints]

        **Nutzerkontext:** [Zielgruppe, Umgebung, Sprache, Prioritäten]

        ## 2. Tool- und Vision-Check

        | Prüfpunkt | Entscheidung | Begruendung |
        |---|---|---|
        | Bild/Screenshot vorhanden | [ja/nein] | [sichtbarer Nutzen] |
        | Vision direkt nutzbar | [ja/nein/unklar] | [OpenWebUI/Basismodell-Fähigkeit] |
        | Lokales Tool erforderlich | [Tool-ID] | [Validierung/Artefakt/Analyse] |
        | Rückfrage nötig | [ja/nein] | [fehlende Pflichtangabe] |

        ## 3. Strukturierter Ergebnisentwurf

        ### Kurzfazit

        [2-4 Sätze]

        ### Hauptteil

        [fachliches Ergebnis in der für den Use Case passenden Struktur]

        ### Sichtbare oder belegte Quellen

        - [Datei, Screenshot, Bildbereich, Tabelle, Log, Codepfad]

        ### Unsicherheiten

        - [Was ist nicht belegt, unscharf, unvollständig oder nicht prüfbar?]

        ## 4. Akzeptanzcheck

        - [ ] Zweck des Modells erfüllt: {config["purpose"]}
        - [ ] Vision-/Screenshot-Regel beachtet: {config["vision"]}
        - [ ] Qualitätslatte erfüllt: {config["quality"]}
        - [ ] Tool-Ausgaben kritisch geprüft.
        - [ ] Ergebnis ist offline weiterverwendbar.

        ## 5. Nächste Schritte

        1. [Nächster konkreter Schritt]
        2. [Optionaler Test oder Review]
        3. [Freigabe-/Rückfragepunkt]
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
    missing = [path.name for path in model_dirs if path.name not in MODEL_EXAMPLES]
    if missing:
        raise SystemExit(f"Missing example definitions for models: {', '.join(missing)}")

    for model_dir in model_dirs:
        model_id = model_dir.name
        config = MODEL_EXAMPLES[model_id]
        name = read_model_name(model_id)
        examples_dir = model_dir / EXAMPLE_DIR
        examples_dir.mkdir(parents=True, exist_ok=True)

        if model_id == "präsentationserstellung":
            stale_example = model_dir / "beispielergebnis.md"
            stale_briefing = examples_dir / "praesentation-briefing-vorlage.md"
            if stale_example.exists():
                stale_example.unlink()
            if stale_briefing.exists():
                stale_briefing.unlink()
        else:
            (model_dir / "beispielergebnis.md").write_text(example_markdown(model_id, name, config), encoding="utf-8", newline="\n")
        example_template = (
            presentation_goldstandard_briefing()
            if model_id == "präsentationserstellung"
            else template_markdown(model_id, name, config)
        )
        (examples_dir / config["artifact"]).write_text(example_template, encoding="utf-8", newline="\n")

        if model_id == "präsentationserstellung":
            (examples_dir / "praesentation-premium-demo.html").write_text(premium_presentation_demo(), encoding="utf-8", newline="\n")
        if model_id == "mistral-vision-workbench":
            (examples_dir / "vision-ui-qa-demo.html").write_text(vision_demo_html(), encoding="utf-8", newline="\n")

    print(f"Generated examples for {len(model_dirs)} models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
