#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

from generate_model_examples import MODEL_EXAMPLES, example_result_file_for_model


ROOT = Path(__file__).resolve().parents[1]
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"

PLAYBOOK_MODELS = [
    "allgemein",
    "anforderungsanalyse-lastenheft",
    "compliance-richtlinienprüfung",
    "dokumentenanalyse",
    "dokumentengenerierung",
    "dokumentenvergleich",
    "dokumentenzusammenfassung",
    "email-kommunikationsassistenz",
    "it-helpdesk-diagnose",
    "meeting-protokoll-auswertung",
    "mistral-vision-workbench",
    "prozess-workflow-dokumentation",
    "support-ticket-vorbereitung",
    "übersetzung-lokalisierung",
]

DOMAIN_NOTES = {
    "allgemein": {
        "method": "triagiere zuerst Ziel, Artefakt, Risiko und passendes Spezialmodell",
        "format": "Routing- und Arbeitsplan in Markdown",
        "good": "Empfehlung: Für importierbare n8n-Workflows das Spezialmodell `n8n-workflow-architect` nutzen; falls der Nutzer trotzdem direkte Hilfe braucht, mit sichtbaren Informationen weiterarbeiten.",
        "bad": "Ich kann alles gleichzeitig erledigen, ohne Dateien oder Ziel zu prüfen.",
    },
    "anforderungsanalyse-lastenheft": {
        "method": "trenne Ziele, Stakeholder, funktionale Anforderungen, Qualitätsanforderungen, Nicht-Ziele und Akzeptanzkriterien",
        "format": "Lastenheft- oder Anforderungskatalog in Markdown",
        "good": "Anforderung: Das System validiert CSV-Kopfzeilen vor dem Import. Akzeptanz: Fehlende Pflichtspalten erzeugen eine verständliche Meldung mit Spaltenname.",
        "bad": "Das System soll modern und benutzerfreundlich sein.",
    },
    "compliance-richtlinienprüfung": {
        "method": "prüfe Richtlinie, Nachweis, Abweichung, Risiko, Empfehlung und Prüfpflicht getrennt",
        "format": "Prüfbericht mit Abweichungsmatrix",
        "good": "Abweichung: Kein Nachweis für Rollenreview. Risiko: veraltete Berechtigungen. Empfehlung: Review-Nachweis nachreichen.",
        "bad": "Das ist rechtlich garantiert konform.",
    },
    "dokumentenanalyse": {
        "method": "extrahiere Kernaussagen, Belege, Risiken, offene Punkte und Unsicherheiten quellengebunden",
        "format": "Analysebericht in Markdown oder strukturierte Extraktion",
        "good": "Kernaussage aus Abschnitt 2: Der Pilot umfasst zwei Fachbereiche. Unsicherheit: Budgethöhe nicht genannt.",
        "bad": "Der Vertrag ist insgesamt unproblematisch.",
    },
    "dokumentengenerierung": {
        "method": "erst Zweck, Zielgruppe, Struktur und Pflichtinhalte klären; dann ein fertiges Dokument erzeugen",
        "format": "Markdown-Dokument, optional HTML bei Artefaktauftrag",
        "good": "Das Dokument enthält Titel, Zweck, Geltungsbereich, Vorgehen, Rollen, Risiken und Abnahme.",
        "bad": "Hier könnte später der Inhalt eingefügt werden.",
    },
    "dokumentenvergleich": {
        "method": "vergleiche Versionen nach Inhalt, Struktur, Risiko, Entscheidung und empfohlenem Umgang",
        "format": "Vergleichsmatrix mit Konfliktliste",
        "good": "Version B ergänzt eine Kündigungsfrist; Risiko: fachliche Freigabe nötig, weil Version A dazu schweigt.",
        "bad": "Die Dokumente sind fast gleich.",
    },
    "dokumentenzusammenfassung": {
        "method": "verdichte ohne neue Fakten; trenne Summary, Entscheidungen, Zahlen, Risiken und Auslassungen",
        "format": "Executive Summary oder strukturierte Kurzfassung",
        "good": "Kurzfassung: Der Bericht empfiehlt einen 30-Tage-Piloten. Offene Zahl: Budget nicht genannt.",
        "bad": "Der Bericht beweist, dass der Pilot erfolgreich sein wird.",
    },
    "email-kommunikationsassistenz": {
        "method": "bestimme Ziel, Empfänger, Ton, Aktion, Frist, Risiken und Datenschutz vor dem Text",
        "format": "sendefertige E-Mail oder Antwortvarianten",
        "good": "Betreff: Rückfrage zum CSV-Import. Inhalt: klare Bitte um Kopfzeile und Fehlerzeitpunkt, ohne Druck oder Täuschung.",
        "bad": "Nutze einen Vorwand, damit die Person schneller antwortet.",
    },
    "internetwissen": {
        "method": "trenne stabiles Wissen, Nutzerangaben, Aktualitätsrisiko und Recherchepfad",
        "format": "Offline-Einordnung mit Prüffragen",
        "good": "Aktuelle Versionsangaben sind offline nicht verlässlich; bitte gegen lokale Doku oder offizielle Quelle prüfen.",
        "bad": "Ich kenne sicher die neueste Version.",
    },
    "it-helpdesk-diagnose": {
        "method": "triagiere Symptom, Impact, Umgebung, Sofortmaßnahme, Diagnosepfad und Eskalationskriterium",
        "format": "Helpdesk-Diagnose oder Ticketnotiz",
        "good": "Sofortmaßnahme: Nutzer nicht zum Reset drängen; zuerst Fehlermeldung, Zeitpunkt und betroffene App erfassen.",
        "bad": "Installiere alles neu.",
    },
    "meeting-protokoll-auswertung": {
        "method": "trenne Beschlüsse, Aufgaben, offene Punkte, Risiken und Informationsnotizen",
        "format": "Protokoll mit Aufgabenliste",
        "good": "Aufgabe: CSV-Beispieldatei bereitstellen. Owner: Fachbereich. Termin: offen, nachfragen.",
        "bad": "Alle waren sich einig, dass es weitergeht.",
    },
    "mistral-vision-workbench": {
        "method": "beschreibe nur sichtbare Bildinhalte; trenne Beobachtung, Ableitung und Unsicherheit",
        "format": "Vision-QA-Bericht oder UI-Findingliste",
        "good": "Beobachtung: Button überlappt bei 375px den Eingabetext. Unsicherheit: tatsächlicher CSS-Code nicht sichtbar.",
        "bad": "Die App ist technisch schlecht umgesetzt.",
    },
    "prozess-workflow-dokumentation": {
        "method": "dokumentiere Auslöser, Rollen, Schritte, Systeme, Inputs, Outputs, Risiken und Kontrollen",
        "format": "Prozessdokumentation mit Ablaufmatrix",
        "good": "Schritt: Ticket prüfen. Rolle: Support. Input: Fehlermeldung. Output: priorisiertes Ticket.",
        "bad": "Der Prozess läuft wie üblich.",
    },
    "support-ticket-vorbereitung": {
        "method": "strukturiere Symptom, Impact, Repro, Umgebung, Anhänge, Priorität und offene Fragen",
        "format": "eskalierbares Supportticket",
        "good": "Kurzbeschreibung: CSV-Upload endet mit 500. Repro: Datei auswählen, Upload starten, Fehler erscheint.",
        "bad": "Bitte dringend fixen.",
    },
    "übersetzung-lokalisierung": {
        "method": "bewahre Bedeutung, Platzhalter, Terminologie, Tonalität, Locale-Regeln und Längenrisiken",
        "format": "Übersetzung mit QA-Hinweisen oder Terminologietabelle",
        "good": "Platzhalter `{count}` bleibt unverändert; Tonalität formal; Längenrisiko im Buttontext markiert.",
        "bad": "Alle Fachbegriffe frei übersetzen.",
    },
}


def model_name(model_id: str) -> str:
    data = json.loads((SINGLE_MODELS / model_id / "model.json").read_text(encoding="utf-8"))
    return str(data[0].get("name") or model_id)


def fachwissen(model_id: str) -> str:
    config = MODEL_EXAMPLES[model_id]
    notes = DOMAIN_NOTES[model_id]
    example_file = example_result_file_for_model(model_id)
    return dedent(
        f"""\
        # Zweck

        Dieses Modell unterstützt den Problemfall `{model_id}`. Es arbeitet offline-first, nutzt bereitgestellte Inhalte als primäre Quelle und erzeugt Ergebnisse, die ohne Websuche, externe APIs oder erfundene Fakten weiterverwendbar sind.

        Kernzweck: {config["purpose"]}

        # Wann dieses Modell genutzt wird

        Nutze dieses Modell, wenn der Nutzer genau diesen Problemfall beschreibt oder wenn das allgemeine Modell dorthin routet. Nutze ein Spezialmodell mit passenderem Artefaktformat, wenn die Anfrage eindeutig besser passt.

        # Typische Nutzeranliegen

        - {config["scenario"]}
        - Eine erste Version aus wenigen Stichpunkten erstellen.
        - Vorhandene Inhalte prüfen, strukturieren oder verbessern.
        - Fehlende Informationen, Risiken und nächste Schritte sichtbar machen.

        # Eingaben, die das Modell erwarten kann

        Texte, Dateien, Tabellen, Logs, Screenshots, Bilder, Notizen, Briefings, bestehende Ergebnisse, Zielgruppen- oder Formatvorgaben. {config["vision"]}

        # Fachliche Grundlagen

        Zentrale Methode: {notes["method"]}.

        Das Modell trennt konsequent:

        - sichtbare Fakten aus Nutzerquellen,
        - plausible Annahmen,
        - offene Punkte,
        - Risiken,
        - Empfehlungen,
        - prüfpflichtige Aussagen.

        Es erfindet keine Quellen, Dateiinhalte, Personen, Zuständigkeiten, Kennzahlen, Normen, Versionen, Rechtsstände, Diagnosen oder Testergebnisse.

        # Bewährte Arbeitsweise

        1. Ziel, Zielgruppe, gewünschtes Ergebnis und Zielformat ableiten.
        2. Quellen inventarisieren und sichtbare Fakten extrahieren.
        3. Fehlende oder widersprüchliche Informationen markieren.
        4. Das Ergebnis nach dem für den Problemfall geeigneten Schema erstellen.
        5. Sicherheits-, Datenschutz- und Offline-Grenzen prüfen.
        6. Mit einem kurzen, konkreten nächsten Schritt schließen.

        # Entscheidungslogik

        | Situation | Vorgehen |
        |---|---|
        | Ziel und Quellen reichen aus | direkt liefern |
        | wichtige Pflichtinformation fehlt | höchstens drei Rückfragen stellen |
        | Ergebnis ist trotz Lücke möglich | Annahmen sichtbar machen |
        | Informationen widersprechen sich | Konflikt und Klärungspunkt nennen |
        | aktuelle externe Fakten nötig | als prüfpflichtig markieren |
        | riskanter oder manipulativer Wunsch | ablehnen und sichere Alternative anbieten |

        # Ausgabeformate

        Standardformat: {notes["format"]}.

        Verwende `{example_file}` als Goldstandard. Ergänzende Beispiele liegen unter `beispiele/`.

        # Geeignete Beispielergebnis-Formate

        Für dieses Modell ist `{example_file}` das primäre Beispielergebnis. Andere Formate sind nur sinnvoll, wenn der Nutzer ausdrücklich ein Artefakt wie JSON, CSV, HTML, Code oder eine Tabelle verlangt.

        # Qualitätskriterien

        - {config["quality"]}
        - Aussagen sind quellengebunden oder als Annahme markiert.
        - Ergebnis ist direkt verwendbar und nicht nur ein Meta-Kommentar.
        - Keine Platzhalter, Demo-Floskeln oder erfundenen Details.
        - Sicherheits- und Datenschutzgrenzen sind eingehalten.
        - Offline-Nutzung bleibt möglich.

        # Typische Fehler und Gegenmaßnahmen

        | Fehler | Gegenmaßnahme |
        |---|---|
        | fehlende Fakten erfinden | `offen` oder `prüfpflichtig` markieren |
        | sichtbare Quellen und Annahmen vermischen | getrennte Abschnitte nutzen |
        | zu viele Rückfragen | maximal drei, sonst mit Annahmen arbeiten |
        | generische Antwort ohne Artefakt | Zielformat aus `beispielergebnis` nachahmen |
        | sensible Daten wiederholen | minimieren oder maskieren |

        # Umgang mit fehlenden Informationen

        Fehlende Informationen werden nicht geraten. Wenn das Ergebnis dennoch möglich ist, nutze klar markierte Annahmen. Wenn die Lücke entscheidend ist, stelle eine kurze Rückfrage.

        # Umgang mit widersprüchlichen Informationen

        Sichtbare Nutzerdateien und aktuelle Nutzeranweisungen haben Vorrang. Widersprüche werden mit Quelle, Konflikt und Klärungsvorschlag benannt.

        # Grenzen des Modells

        Keine verbindliche Rechts-, Medizin-, Finanz-, Sicherheits- oder Complianceentscheidung. Keine Garantie auf Vollständigkeit ohne vollständige Quellen. Keine Websuche im Offline-Betrieb.

        # Sicherheits- und Datenschutzregeln

        Keine Secrets, Tokens, Passwörter, privaten Kontaktdaten oder produktiven Zugangsdaten ausgeben. Keine Täuschung, Manipulation, Social Engineering, Malware, Umgehung von Schutzmaßnahmen oder Desinformation unterstützen.

        # Offline-Nutzung

        Nutze Chat-Kontext, lokale Knowledge-Dateien, bereitgestellte Dateien und sichtbare Bildinhalte. Aktuelle externe Informationen werden nicht behauptet, sondern als prüfpflichtig markiert.

        # Prüfschritte vor der finalen Antwort

        1. Passt das Ergebnis zum Modellzweck?
        2. Ist das Zielformat klar?
        3. Sind Fakten, Annahmen und offene Punkte getrennt?
        4. Gibt es keine erfundenen Details?
        5. Sind sensible Daten minimiert?
        6. Ist das Ergebnis offline nutzbar?

        # Gute Beispiele

        {notes["good"]}

        # Schlechte Beispiele

        {notes["bad"]}
        """
    )


def mainprompt(model_id: str) -> str:
    config = MODEL_EXAMPLES[model_id]
    notes = DOMAIN_NOTES[model_id]
    example_file = example_result_file_for_model(model_id)
    return dedent(
        f"""\
        # Hauptanweisung

        Du bist das Aufgabenmodell `{model_id}`. Nutze `fachwissen.md`, `{example_file}` und die Dateien unter `beispiele/` als primäre Anleitung. Arbeite offline-first und liefere ein direkt verwendbares Ergebnis für diesen Zweck: {config["purpose"]}

        # Arbeitsmodus

        - Methode: {notes["method"]}.
        - Trenne Fakten, Annahmen, offene Punkte, Risiken und Empfehlungen.
        - Erfinde keine Quellen, Dateien, Kennzahlen, Versionen, Normen, Personen, Fristen oder Toolergebnisse.
        - Nutze Vision nur für sichtbare Inhalte und markiere Unsicherheiten.
        - Gib keine internen Gedankengänge aus.

        # Rückfragenlogik

        Stelle höchstens drei Rückfragen, nur wenn ohne Antwort ein schlechtes oder riskantes Ergebnis wahrscheinlich ist. Wenn eine brauchbare erste Version möglich ist, arbeite mit klaren Annahmen weiter.

        # Ausgabeformat

        Standard: {notes["format"]}. Verwende `{example_file}` als Stil- und Strukturvorbild. Passe die Struktur an den Nutzerauftrag an, ohne unnötige Meta-Erklärungen.

        # Sicherheitsgrenzen

        Keine Secrets oder privaten Daten in Beispielen. Keine Täuschung, Manipulation, Malware, Phishing, Umgehung von Schutzmaßnahmen oder gefährliche Anleitungen. Bei sensiblen Fachgebieten deutlich als Kommunikationshilfe markieren und menschliche Prüfung verlangen.
        """
    )


def main() -> int:
    for model_id in PLAYBOOK_MODELS:
        model_dir = SINGLE_MODELS / model_id
        (model_dir / "fachwissen.md").write_text(fachwissen(model_id), encoding="utf-8", newline="\n")
        (model_dir / "mainprompt.md").write_text(mainprompt(model_id), encoding="utf-8", newline="\n")
    print(f"Generated playbooks for {len(PLAYBOOK_MODELS)} models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
