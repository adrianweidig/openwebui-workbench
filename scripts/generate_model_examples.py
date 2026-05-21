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
        "scenario": "Ein Nutzer beschreibt ein unscharfes Problem mit Dateien, Screenshots und Zielartefakt, weiss aber nicht, welches Modell passt.",
        "vision": "Nutze Vision fuer Screenshots, Whiteboards, Fehlermeldungen, UI-Zustaende oder fotografierte Notizen; wenn kein Bildzugriff besteht, fordere OCR oder eine Beschreibung an.",
        "quality": "Das Ergebnis muss Routing, Annahmen, Tool-Auswahl, konkrete Bearbeitung und naechste Schritte trennen.",
    },
    "anforderungsanalyse-lastenheft": {
        "purpose": "Anforderungen, Ziele, Nicht-Ziele, Stakeholder, Akzeptanzkriterien und Lastenheft-Struktur professionell ausarbeiten.",
        "artifact": "lastenheft-vorlage.md",
        "scenario": "Aus Stichpunkten, Screenshots und Prozessnotizen soll ein befuellbares Lastenheft entstehen.",
        "vision": "Nutze Vision fuer Whiteboard-Fotos, Prozessskizzen, UI-Mockups oder abfotografierte Workshops.",
        "quality": "Jede Anforderung braucht Prioritaet, Akzeptanzkriterium, Quelle, Risiko und offenen Klaerungspunkt.",
    },
    "api-schnittstellenentwurf": {
        "purpose": "API-Vertraege, OpenAPI-Strukturen, Authentifizierung, Fehlerfaelle und Integrationsgrenzen entwerfen oder pruefen.",
        "artifact": "api-design-vorlage.md",
        "scenario": "Ein Team braucht aus Fachanforderungen einen belastbaren API-Entwurf mit Beispielpayloads.",
        "vision": "Nutze Vision fuer Architekturdiagramme, Swagger-Screenshots, Sequenzskizzen oder Fehlermasken.",
        "quality": "Endpunkte, Schemas, Fehlercodes, Security und Testfaelle muessen zusammenpassen.",
    },
    "code-dokumentation": {
        "purpose": "Code, Module, Datenfluesse und Betriebswissen in wartbare Entwicklerdokumentation ueberfuehren.",
        "artifact": "code-dokumentation-vorlage.md",
        "scenario": "Ein Repository soll mit Einstieg, Architektur, Komponenten und Betriebsnotizen dokumentiert werden.",
        "vision": "Nutze Vision fuer Architekturdiagramme, UI-Screenshots oder visuelle Ablaufgrafiken im Repo-Kontext.",
        "quality": "Die Dokumentation muss Dateipfade, Verantwortlichkeiten, Beispiele und Pflegehinweise enthalten.",
    },
    "code-review": {
        "purpose": "Diffs, Risiken, Regressionen, Sicherheitsprobleme und fehlende Tests wie in einem professionellen Review priorisieren.",
        "artifact": "code-review-finding-vorlage.md",
        "scenario": "Ein Patch soll mit Findings, Schweregrad, Repro-Hinweis und Testluecken bewertet werden.",
        "vision": "Nutze Vision fuer UI-Regressionsscreenshots, Vorher-/Nachher-Bilder oder visuelle Testfehler.",
        "quality": "Findings stehen vor Zusammenfassung und referenzieren konkrete Dateien, Zeilen oder sichtbare UI-Zustaende.",
    },
    "codeanalyse": {
        "purpose": "Codebasen, Abhaengigkeiten, Kontrollfluesse, Risiken und technische Ursachen strukturiert analysieren.",
        "artifact": "codeanalyse-bericht-vorlage.md",
        "scenario": "Eine unklare Codebasis soll mit Architektur, Hotspots und Hypothesen verstanden werden.",
        "vision": "Nutze Vision fuer Architektur-Screenshots, UI-Flows oder Diagramme, die Codeverhalten erklaeren.",
        "quality": "Trenne belegte Fakten aus Code/Tool-Ausgaben von Hypothesen und empfohlenen Messungen.",
    },
    "codegenerierung": {
        "purpose": "Bestehende Muster erkennen, zielgenauen Code erzeugen und lokale Validierung oder Tests vorbereiten.",
        "artifact": "implementierungsplan-vorlage.md",
        "scenario": "Aus einer Featurebeschreibung soll ein implementierbarer Patchplan mit Tests entstehen.",
        "vision": "Nutze Vision fuer UI-Mockups, Design-Screenshots, Formularzustaende oder Fehlanzeigen.",
        "quality": "Der Plan muss Dateien, Schnittstellen, Testfaelle, Risiken und Rollback-Punkte nennen.",
    },
    "compliance-richtlinienprüfung": {
        "purpose": "Richtlinien, Nachweise, Kontrollen und Abweichungen nachvollziehbar pruefen.",
        "artifact": "compliance-pruefbericht-vorlage.md",
        "scenario": "Ein Prozess oder Dokumentensatz soll gegen interne Richtlinien bewertet werden.",
        "vision": "Nutze Vision fuer gescannte Nachweise, UI-Screenshots von Einstellungen oder Kontroll-Dashboards.",
        "quality": "Jede Abweichung braucht Quelle, Risiko, Empfehlung, Verantwortlichkeit und Nachweisstatus.",
    },
    "debugging-fehleranalyse": {
        "purpose": "Fehlertexte, Logs, Screenshots, Reproduktionsschritte und Konfigurationen zu einer belastbaren Ursache fuehren.",
        "artifact": "debugging-runbook-vorlage.md",
        "scenario": "Ein OpenWebUI-, Docker- oder App-Fehler soll reproduzierbar eingegrenzt werden.",
        "vision": "Nutze Vision fuer Fehlermeldungs-Screenshots, UI-Zustaende, Browser-Konsole oder visuelle Regressionsbilder.",
        "quality": "Hypothesen muessen priorisiert, pruefbar und mit naechstem Diagnosebefehl verbunden sein.",
    },
    "dokumentenanalyse": {
        "purpose": "Dokumente, Scans, PDFs und strukturierte Inhalte quellenorientiert analysieren.",
        "artifact": "dokumentenanalyse-vorlage.md",
        "scenario": "Ein Vertrag, Bericht oder Scan soll mit Kernaussagen, Risiken und Belegstellen analysiert werden.",
        "vision": "Nutze Vision fuer gescannte Seiten, Fotos, Stempel, Tabellenbilder oder visuelle Markierungen.",
        "quality": "Kernaussagen, Belege, Unsicherheiten und extrahierte Daten muessen getrennt bleiben.",
    },
    "dokumentengenerierung": {
        "purpose": "Strukturierte, direkt nutzbare Dokumente, HTML/PDF-Artefakte und Vorlagen erzeugen.",
        "artifact": "dokument-generator-vorlage.md",
        "scenario": "Aus Stichpunkten soll ein auslieferbares Dokument mit Deckblatt, Struktur und Platzhaltern entstehen.",
        "vision": "Nutze Vision fuer Corporate-Design-Screenshots, Layoutbeispiele, Diagramme oder handschriftliche Skizzen.",
        "quality": "Das Ergebnis muss befuellbar, konsistent formatiert und offline weiterverwendbar sein.",
    },
    "dokumentenvergleich": {
        "purpose": "Dokumentversionen, Textvarianten, Tabellen und Scans nachvollziehbar vergleichen.",
        "artifact": "dokumentenvergleich-matrix-vorlage.md",
        "scenario": "Zwei Versionen eines Dokuments sollen mit inhaltlichen und strukturellen Unterschieden verglichen werden.",
        "vision": "Nutze Vision fuer gescannte Versionen, markierte PDFs, Layoutabweichungen oder Screenshotvergleiche.",
        "quality": "Unterschiede muessen nach Relevanz, Quelle, Risiko und empfohlener Aktion sortiert sein.",
    },
    "dokumentenzusammenfassung": {
        "purpose": "Lange Dokumente, Scans und Protokolle zu belastbaren, quellenklaren Kurzfassungen verdichten.",
        "artifact": "executive-summary-vorlage.md",
        "scenario": "Ein langer Bericht soll als Management Summary mit Entscheidungen und Risiken zusammengefasst werden.",
        "vision": "Nutze Vision fuer gescannte Seiten, Diagramme, Infografiken oder fotografierte Unterlagen.",
        "quality": "Zusammenfassung, Entscheidungen, Zahlen, Risiken und offene Punkte muessen klar getrennt sein.",
    },
    "email-kommunikationsassistenz": {
        "purpose": "E-Mails, Antworten, Eskalationen und Kommunikationsvorlagen praezise und adressatengerecht formulieren.",
        "artifact": "email-antwort-vorlage.md",
        "scenario": "Aus Kontext, Ziel und Tonalitaet soll eine sendefertige Antwort entstehen.",
        "vision": "Nutze Vision fuer E-Mail-Screenshots, Ticketmasken oder visuelle Kontextinformationen; maskiere sensible Daten.",
        "quality": "Ton, Ziel, Aktion, Frist, Anhaenge und Risiken muessen explizit passen.",
    },
    "informationsextraktion": {
        "purpose": "Informationen aus Texten, Tabellen, Logs, Dokumenten und Bildern in ein definiertes Schema extrahieren.",
        "artifact": "extraktionsschema-vorlage.md",
        "scenario": "Aus gemischten Quellen soll valides JSON mit Belegen und Unsicherheiten entstehen.",
        "vision": "Nutze Vision fuer Formularfotos, Tabellenbilder, Scans, Etiketten oder UI-Datenmasken.",
        "quality": "Jedes Feld braucht Quelle, Normalisierung, Unsicherheit und Validierungsregel.",
    },
    "it-helpdesk-diagnose": {
        "purpose": "IT-Probleme aus Nutzerbeschreibung, Screenshots, Logs und Konfigurationen schnell triagieren.",
        "artifact": "helpdesk-diagnose-vorlage.md",
        "scenario": "Ein Nutzer meldet ein Problem mit Screenshot und wenigen Symptomen.",
        "vision": "Nutze Vision fuer Fehlermasken, Taskleisten-/Tray-Zustaende, Dialoge oder Netzwerksymbole.",
        "quality": "Antwort muss Sofortmassnahmen, Rueckfragen, Diagnosepfad und Eskalationskriterium enthalten.",
    },
    "json-csv-log-analyse": {
        "purpose": "JSON, CSV, Logs und strukturierte Textdaten validieren, analysieren und in klare Befunde ueberfuehren.",
        "artifact": "loganalyse-vorlage.md",
        "scenario": "Ein Logauszug und eine CSV sollen auf Fehler, Muster und Datenqualitaet geprueft werden.",
        "vision": "Nutze Vision nur fuer Screenshot-Logs oder Tabellenbilder; verlange Rohtext, wenn Genauigkeit noetig ist.",
        "quality": "Parsingstatus, Auffaelligkeiten, Beispiele, betroffene Felder und Repro-Schritte muessen enthalten sein.",
    },
    "meeting-protokoll-auswertung": {
        "purpose": "Meetingnotizen, Mitschriften und Whiteboard-Fotos in Beschluesse, Aufgaben und Risiken ueberfuehren.",
        "artifact": "meeting-auswertung-vorlage.md",
        "scenario": "Ein Workshopfoto und Stichpunkte sollen in ein handlungsfaehiges Protokoll ueberfuehrt werden.",
        "vision": "Nutze Vision fuer Whiteboards, Flipcharts, abfotografierte Post-its oder Folien.",
        "quality": "Aufgaben brauchen Owner, Termin, Kontext, Status und offene Klaerung.",
    },
    "mistral-vision-workbench": {
        "purpose": "Bilder, Screenshots, UI-Zustaende, Folien, Diagramme, Scans und visuelle Artefakte multimodal analysieren.",
        "artifact": "vision-ui-qa-vorlage.md",
        "scenario": "Ein UI-Screenshot oder eine HTML-Praesentation soll visuell geprueft und verbessert werden.",
        "vision": "Vision ist der Hauptpfad: sichtbare Fakten extrahieren, Unsicherheiten markieren und lokale Tools fuer Reproduktion oder Artefakte nutzen.",
        "quality": "Findings muessen sichtbar belegbar, priorisiert und mit konkretem Fix sowie Akzeptanzkriterium versehen sein.",
    },
    "n8n-workflow-architect": {
        "purpose": "Importierbare n8n-Workflows planen, validieren und mit Test- sowie Sicherheitshinweisen ausgeben.",
        "artifact": "n8n-workflow-vorlage.md",
        "scenario": "Ein Integrationsziel soll in einen pruefbaren n8n-Workflow mit Nodes, Credentials und Fehlerpfad ueberfuehrt werden.",
        "vision": "Nutze Vision fuer n8n-Canvas-Screenshots, Node-Konfigurationen oder Fehleranzeigen.",
        "quality": "Workflow, Trigger, Datenvertrag, Fehlerbehandlung, Secrets und Testfaelle muessen konsistent sein.",
    },
    "offline-workbench-agent": {
        "purpose": "Komplexe Offline-Aufgaben routen, Tools kombinieren und HTML/PDF/ZIP/Tabellen/Code-Artefakte lokal erzeugen.",
        "artifact": "offline-workbench-auftrag-vorlage.md",
        "scenario": "Eine mehrteilige Aufgabe soll mit Jupyter, Artefakt-Tools und Validierung end-to-end erledigt werden.",
        "vision": "Nutze Vision fuer Screenshots, Artefakt-QA, Diagramme, UI-Zustaende und visuelle Eingaben.",
        "quality": "Der Plan muss Tool-Wellen, Artefaktpfade, Validierung und Uebergabeformat enthalten.",
    },
    "openwebui-model-builder": {
        "purpose": "Vollstaendige OpenWebUI-Modellpakete mit Prompt, Wissen, Tools, Skills, Icons, Importplan und QA erzeugen.",
        "artifact": "modellpaket-vorlage.md",
        "scenario": "Aus einer Modellidee soll ein importierbares OpenWebUI-Modellpaket entstehen.",
        "vision": "Nutze Vision fuer Icon-/UI-Screenshots, Custom-GPT-Referenzen oder Modellprofil-Mockups.",
        "quality": "Paket muss model.json, systemprompt, mainprompt, fachwissen, Beispiel, Toolprofil und Importcheck enthalten.",
    },
    "präsentationserstellung": {
        "purpose": "Premium-Browser-Keynotes als einzelne offline lauffaehige `präsentation.html` mit Interaktion, Animation und Designsystem erzeugen.",
        "artifact": "praesentation-briefing-vorlage.md",
        "scenario": "Aus Thema und Stichpunkten soll eine moderne, interaktive HTML-Praesentation entstehen.",
        "vision": "Nutze Vision fuer Designreferenzen, Folien-Screenshots, Logo-/Layoutpruefung und visuelle Abnahme.",
        "quality": "HTML muss 16:9, Tastatur/Maus/Touch-Navigation, Dark Mode, Hover-Toolbar, Offline-CSS und reduzierte Bewegung unterstuetzen.",
    },
    "promptforge": {
        "purpose": "Erste Nutzerprompts nach Best Practices in direkt kopierbare, zielsystemspezifische Promptvorlagen optimieren.",
        "artifact": "promptforge-vorlage.md",
        "scenario": "Ein roher Nutzerprompt soll fuer ChatGPT, Custom GPT, OpenWebUI oder lokale LLMs verbessert werden.",
        "vision": "Nutze Vision fuer Screenshots von Zieloberflaechen, Prompt-Buildern, Fehlermeldungen oder Beispielausgaben.",
        "quality": "Prompt muss Rolle, Ziel, Kontext, Quellen, Toolregeln, Ausgabeformat, Grenzen und Erfolgskriterien enthalten.",
    },
    "prozess-workflow-dokumentation": {
        "purpose": "Prozesse, Verantwortlichkeiten, Workflows, Diagramme und Betriebsuebergaben dokumentieren.",
        "artifact": "prozessdokumentation-vorlage.md",
        "scenario": "Ein Prozess soll aus Stichpunkten, Skizzen und Rollen in eine klare Dokumentation ueberfuehrt werden.",
        "vision": "Nutze Vision fuer BPMN-Skizzen, Whiteboards, Swimlanes, Prozessscreenshots oder Ablaufdiagramme.",
        "quality": "Schritte, Rollen, Systeme, Inputs, Outputs, Risiken und Diagramm muessen konsistent sein.",
    },
    "refactoring-unterstützung": {
        "purpose": "Refactoring-Ziele, Codebereiche, Risiken, Tests und schrittweise Umsetzung strukturieren.",
        "artifact": "refactoring-plan-vorlage.md",
        "scenario": "Ein Modul soll ohne Verhaltensbruch schrittweise umgebaut werden.",
        "vision": "Nutze Vision fuer UI-Verhaltensvergleiche, Architekturskizzen oder visuelle Regressionen.",
        "quality": "Plan braucht Scope, Nicht-Ziele, Reihenfolge, Tests, Rollback und Akzeptanzkriterien.",
    },
    "report-dashboard-vorbereitung": {
        "purpose": "Daten, Kennzahlen, Dashboard-Struktur, Visualisierungen und Storyline fuer Reports vorbereiten.",
        "artifact": "dashboard-briefing-vorlage.md",
        "scenario": "Aus Daten und Zielgruppe soll ein Dashboard- oder Reportkonzept entstehen.",
        "vision": "Nutze Vision fuer Dashboard-Screenshots, Charts, Tabellenbilder oder Layoutreferenzen.",
        "quality": "Kennzahlen, Datenquellen, Visualtyp, Filter, Warnschwellen und Nutzerfragen muessen definiert sein.",
    },
    "support-ticket-vorbereitung": {
        "purpose": "Supportfaelle aus Symptomen, Screenshots, Logs und Nutzertexten in klare Tickets ueberfuehren.",
        "artifact": "support-ticket-vorlage.md",
        "scenario": "Aus einem Chatverlauf und Screenshot soll ein eskalierbares Ticket entstehen.",
        "vision": "Nutze Vision fuer Fehlerscreenshots, Statusanzeigen, Dialoge oder betroffene UI-Elemente.",
        "quality": "Ticket braucht Kurzbeschreibung, Impact, Repro, Environment, Anhaenge, Prioritaet und offene Fragen.",
    },
    "tabellen-csv-datenanalyse": {
        "purpose": "Tabellen und CSVs bereinigen, analysieren, validieren und in nachvollziehbare Ergebnisse ueberfuehren.",
        "artifact": "datenanalyse-notebook-plan-vorlage.md",
        "scenario": "Eine CSV soll mit Jupyter geprueft, bereinigt und zusammengefasst werden.",
        "vision": "Nutze Vision fuer fotografierte Tabellen oder Dashboard-Screenshots nur zur Orientierung; verlange Rohdaten fuer Berechnung.",
        "quality": "Analyse muss Schema, Datenqualitaet, Berechnung, Ergebnis und Reproduzierbarkeit enthalten.",
    },
    "testfall-generierung": {
        "purpose": "Aus Anforderungen, Code, UI-Screenshots und Risiken konkrete Testfaelle und Akzeptanztests erzeugen.",
        "artifact": "testfallkatalog-vorlage.md",
        "scenario": "Ein Feature soll mit funktionalen, negativen, UI- und Regressionstests abgesichert werden.",
        "vision": "Nutze Vision fuer UI-Screenshots, Fehlzustaende, Formularlayouts und visuelle Akzeptanzkriterien.",
        "quality": "Testfaelle brauchen Preconditions, Schritte, Testdaten, erwartetes Ergebnis und Prioritaet.",
    },
    "übersetzung-lokalisierung": {
        "purpose": "Texte, UI-Kopien, Dokumente und Lokalisierungsfragen zielgruppen- und kontextgerecht uebertragen.",
        "artifact": "lokalisierungsauftrag-vorlage.md",
        "scenario": "UI-Texte und Screenshots sollen fuer eine Zielregion lokalisiert werden.",
        "vision": "Nutze Vision fuer UI-Screenshots, Kontext, abgeschnittene Texte oder Layoutprobleme nach Uebersetzung.",
        "quality": "Ergebnis braucht Zielvariante, Tonalitaet, Platzhalter, Laengenrisiken und QA-Hinweise.",
    },
}


def read_model_name(model_id: str) -> str:
    model_path = SINGLE_MODELS / model_id / "model.json"
    data = json.loads(model_path.read_text(encoding="utf-8"))
    return str(data[0].get("name") or model_id)


def example_markdown(model_id: str, name: str, config: dict[str, str]) -> str:
    return dedent(
        f"""\
        # Beispielergebnis und Arbeitsvorlage: {name}

        ## Zweck dieses Modells

        {config["purpose"]}

        ## Wiederverwendbarer Musterauftrag

        > {config["scenario"]}

        ## Erwartetes Ergebnisartefakt

        - Primaere Datei: `beispiele/{config["artifact"]}`
        - Format: befuellbare Markdown-Vorlage oder direkt nutzbares Offline-Artefakt.
        - Ziel: Das Modell soll nicht bei null anfangen, sondern diese Struktur aktiv als Ausgangspunkt verwenden.

        ## Vision- und Screenshot-Nutzung

        {config["vision"]}

        ## Tool-first-Ablauf

        1. Tool-/Skill-Inventur anhand der Nutzeraufgabe, Dateien, Screenshots und Zielartefakte.
        2. Relevante Quellen und sichtbare Bildinhalte trennen: beobachtet, abgeleitet, unklar.
        3. Passende Offline-Tools frueh nutzen, insbesondere Jupyter, Validatoren, Artefakt- und Visual-Tools, wenn sie die Aufgabe absichern.
        4. Ergebnis in der Vorlage unter `beispiele/{config["artifact"]}` strukturieren.
        5. Vor finaler Antwort gegen die Qualitaets- und Akzeptanzkriterien pruefen.

        ## Qualitaetslatte

        {config["quality"]}

        ## Copy/Paste-Starterprompt

        ```text
        Nutze das Modell {name}. Verwende `beispielergebnis.md` und `beispiele/{config["artifact"]}` als Vorlage.

        Ziel:
        [Was soll am Ende konkret vorliegen?]

        Eingaben:
        [Dateien, Text, Screenshots, Daten, Constraints]

        Gewuenschtes Ergebnisformat:
        [Markdown, HTML, JSON, Tabelle, Ticket, Bericht, Praesentation, Codeplan]

        Qualitaetskriterien:
        [Was muss geprueft, validiert, visuell bewertet oder offline nutzbar sein?]
        ```
        """
    )


def template_markdown(model_id: str, name: str, config: dict[str, str]) -> str:
    return dedent(
        f"""\
        # {name} - befuellbare Ergebnisvorlage

        ## 1. Auftrag

        **Ziel:** [konkretes Ziel eintragen]

        **Eingaben:** [Dateien, Text, Screenshots, Daten, Constraints]

        **Nutzerkontext:** [Zielgruppe, Umgebung, Sprache, Prioritaeten]

        ## 2. Tool- und Vision-Check

        | Pruefpunkt | Entscheidung | Begruendung |
        |---|---|---|
        | Bild/Screenshot vorhanden | [ja/nein] | [sichtbarer Nutzen] |
        | Vision direkt nutzbar | [ja/nein/unklar] | [OpenWebUI/Basismodell-Faehigkeit] |
        | Lokales Tool erforderlich | [Tool-ID] | [Validierung/Artefakt/Analyse] |
        | Rueckfrage noetig | [ja/nein] | [fehlende Pflichtangabe] |

        ## 3. Strukturierter Ergebnisentwurf

        ### Kurzfazit

        [2-4 Saetze]

        ### Hauptteil

        [fachliches Ergebnis in der fuer den Use Case passenden Struktur]

        ### Sichtbare oder belegte Quellen

        - [Datei, Screenshot, Bildbereich, Tabelle, Log, Codepfad]

        ### Unsicherheiten

        - [Was ist nicht belegt, unscharf, unvollstaendig oder nicht pruefbar?]

        ## 4. Akzeptanzcheck

        - [ ] Zweck des Modells erfuellt: {config["purpose"]}
        - [ ] Vision-/Screenshot-Regel beachtet: {config["vision"]}
        - [ ] Qualitaetslatte erfuellt: {config["quality"]}
        - [ ] Tool-Ausgaben kritisch geprueft.
        - [ ] Ergebnis ist offline weiterverwendbar.

        ## 5. Naechste Schritte

        1. [Naechster konkreter Schritt]
        2. [Optionaler Test oder Review]
        3. [Freigabe-/Rueckfragepunkt]
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
            <section class="slide"><div class="frame"><div class="eyebrow">Problem</div><h2>Langweilige PDF-Folien verlieren Aufmerksamkeit.</h2><div class="grid"><div class="card"><strong>Zu statisch</strong>Keine Interaktion, kein Rhythmus.</div><div class="card"><strong>Zu generisch</strong>Keine visuelle Signatur.</div><div class="card"><strong>Zu schwer zu aendern</strong>Layouts brechen bei Anpassungen.</div></div></div></section>
            <section class="slide"><div class="frame"><div class="eyebrow">Loesung</div><h2>HTML als Premium-Praesentationsformat.</h2><p>Offline lauffaehig, schnell anpassbar, animierbar und per Browser sofort pruefbar.</p><div class="metric">1 Datei</div></div></section>
            <section class="slide"><div class="frame"><div class="eyebrow">Abnahme</div><h2>Qualitaet wird sichtbar getestet.</h2><div class="grid"><div class="card"><strong>Navigation</strong>Pfeile, Space, Touch und Buttons.</div><div class="card"><strong>Dark Mode</strong>Kontraststabil, sofort umschaltbar.</div><div class="card"><strong>Toolbar</strong>Stoert nicht, erscheint bei Hover/Fokus.</div></div></div></section>
            <section class="slide"><div class="frame"><div class="eyebrow">Call to Action</div><h2>Briefing rein. Keynote raus.</h2><p>Diese Datei ist bewusst als Vorlage gebaut: Texte, Farben, Karten und Folien koennen direkt ersetzt werden.</p></div></section>
          </main>
          <div class="toolbar" role="toolbar" aria-label="Praesentationssteuerung">
            <button id="prev" title="Zurueck">‹</button>
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
        </head><body><main class="shell"><div class="top"><h1>Checkout QA Screenshot</h1><span class="badge">Beispiel fuer Vision-Analyse</span></div><div class="grid"><section class="panel"><h2>Beobachtete UI</h2><p class="bad">Fehler: Rabattcode-Feld ueberlappt den Button bei schmalen Viewports.</p><p>CTA sichtbar, aber Fokuszustand fehlt. Kontrast ist ausreichend.</p><button>Jetzt bezahlen</button></section><aside class="panel"><h2>QA-Findings</h2><ol><li class="bad">Overlap bei 375px pruefen</li><li>Tab-Reihenfolge sichtbar machen</li><li class="ok">Primaere CTA-Farbe ok</li></ol></aside></div></main></body></html>
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

        (model_dir / "beispielergebnis.md").write_text(example_markdown(model_id, name, config), encoding="utf-8", newline="\n")
        (examples_dir / config["artifact"]).write_text(template_markdown(model_id, name, config), encoding="utf-8", newline="\n")

        if model_id == "präsentationserstellung":
            (examples_dir / "praesentation-premium-demo.html").write_text(premium_presentation_demo(), encoding="utf-8", newline="\n")
        if model_id == "mistral-vision-workbench":
            (examples_dir / "vision-ui-qa-demo.html").write_text(vision_demo_html(), encoding="utf-8", newline="\n")

    print(f"Generated examples for {len(model_dirs)} models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
