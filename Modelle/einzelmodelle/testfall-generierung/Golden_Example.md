Golden Example: Testfall-Generierung

Nutzerkontext: Ein CSV-Ticketimport soll getestet werden. Sichtbares Verhalten: Die CLI liest eine CSV-Datei, validiert Pflichtfelder, normalisiert Prioritäten und erzeugt im Dry-Run keine Datenbankeinträge. Bekannte Pflichtfelder sind ticket_id, title, priority und sla_due_at. Erlaubte Prioritäten sind critical, high, medium und low. Produktive Daten und externe Dienste dürfen nicht genutzt werden.

Teststrategie

Der Testfokus liegt auf beobachtbarem Importverhalten, Validierung vor Persistenz und stabilen CLI-Ergebnissen. Die wichtigsten Risiken sind falsch akzeptierte CSV-Dateien, unklare Fehler, unbeabsichtigte Schreibzugriffe im Dry-Run und Regressionen bei Prioritäts- oder Datumsverarbeitung.

Priorisierung:

hoch: Datenverlust, falsche Persistenz, fehlerhafte Validierung, instabile Exit-Codes.

mittel: unklare Fehlermeldungen, Grenzwerte, Normalisierung.

niedrig: rein kosmetische Ausgabe ohne Einfluss auf Verarbeitung.

Testdaten sind anonym, klein und deterministisch. Externe Systeme werden durch lokale Fixtures oder Fakes ersetzt.

Testfallkatalog
ID	Risiko	Vorbedingung	Schritte	Testdaten	Erwartetes Ergebnis	Priorität
T-001	gültige CSV wird abgelehnt	CLI ist lokal ausführbar; Dry-Run ist verfügbar	Import mit valider CSV im Dry-Run starten	ticket_id,title,priority,sla_due_at mit T-1001,Login defekt,high,2026-07-15 und T-1002,Export langsam,medium,2026-07-20	Import validiert 2 Tickets; Exit-Code ist 0; es wird nichts persistiert	hoch
T-002	fehlende Pflichtspalte erzeugt Folgefehler	Persistenz ist durch Fake beobachtbar	Import mit CSV ohne ticket_id starten	Header: title,priority,sla_due_at; Zeile: Login defekt,high,2026-07-15	Validierungsfehler vor Persistenz; Exit-Code ungleich 0; Fake zeigt 0 Schreibzugriffe	hoch
T-003	leere Pflichtwerte werden akzeptiert	Dry-Run ist verfügbar	Import mit leerem Titel starten	ticket_id,title,priority,sla_due_at; Zeile: T-1003,,low,2026-07-21	Fehler nennt Feld title und betroffene Zeile; kein Ticket wird persistiert	hoch
T-004	ungültige Priorität wird normalisiert statt abgelehnt	Erlaubte Prioritäten sind bekannt	Import mit nicht erlaubter Priorität starten	T-1004,Passwortseite prüfen,urgent,2026-07-22	Validierungsfehler nennt priority; erlaubte Werte bleiben auf critical, high, medium, low begrenzt	hoch
T-005	erlaubte Prioritäten werden regressiv abgelehnt	Dry-Run ist verfügbar	Import je Priorität einmal starten	Vier Zeilen mit critical, high, medium, low	Alle vier Zeilen werden akzeptiert; Exit-Code ist 0	hoch
T-006	falsches Datumsformat wird akzeptiert	Datumsformat ist YYYY-MM-DD	Import mit deutschem Datumsformat starten	T-1005,Datumsprüfung,medium,15.07.2026	Validierungsfehler nennt sla_due_at; keine Persistenz	mittel
T-007	ungültiges Kalenderdatum wird akzeptiert	Dry-Run ist verfügbar	Import mit unmöglichem Datum starten	T-1006,Kalendergrenze,low,2026-02-30	Validierungsfehler für sla_due_at; Exit-Code ungleich 0	mittel
T-008	teilweise valide Datei führt zu Teilimport	Persistenz-Fake protokolliert Schreibzugriffe	CSV mit einer validen und einer invaliden Zeile importieren	Zeile 1 valide; Zeile 2 ohne title	Gesamter Import wird abgelehnt oder dokumentiert konsistent behandelt; kein stiller Teilimport ohne klare Meldung	hoch
T-009	Dry-Run schreibt dennoch Daten	Persistenz-Fake ist aktiv	Valide CSV mit Dry-Run importieren	Zwei valide Tickets	Validierung erfolgreich; Fake zeigt 0 Schreibzugriffe	hoch
T-010	Normalisierung verändert Ticket-ID	Dry-Run gibt validierte Tickets oder interne Struktur prüfbar zurück	Ticket-ID mit Bindestrich importieren	T-ABC-001,ID prüfen,low,2026-08-01	Ticket-ID bleibt exakt T-ABC-001	mittel
T-011	Leerzeichen um Werte verursachen falsche Ablehnung	Verhalten für Trimmen ist als bestehendes Verhalten zu sichern	CSV mit Leerzeichen um Priorität starten	T-1007,Whitespace, high ,2026-08-02	Ergebnis entspricht dokumentiertem Bestand: entweder akzeptiert nach Trimmen oder klarer Validierungsfehler; Verhalten wird als Regressionstest fixiert	mittel
T-012	Fehlerausgabe enthält sensible Rohdaten	Fehlerausgabe ist sichtbar	Import mit ungültiger Zeile starten	Titel enthält anonymen langen Text: Interner Hinweis A	Fehler nennt Feld und Zeile, aber keine unnötigen vollständigen Rohdaten oder Secrets	mittel
Automatisierbare Tests

Geeignet für Automatisierung:

T-001 bis T-010 als Unit- oder CLI-nahe Integrationstests mit lokalen Fixture-Dateien.

T-009 mit Persistenz-Fake oder Mock, damit Dry-Run-Schreibzugriffe sicher erkennbar sind.

T-005 als parametrisierter Test über alle erlaubten Prioritäten.

T-006 und T-007 als negative Validierungstests für Datumsverarbeitung.

Beispielhafte pytest-Skizze, nur wenn im Projekt bereits pytest genutzt wird:

Python
Ausgeführt
import pytest

@pytest.mark.parametrize("priority", ["critical", "high", "medium", "low"])
def test_allowed_priorities_are_accepted(import_cli, tmp_path):
    csv_file = tmp_path / "tickets.csv"
    csv_file.write_text(
        "ticket_id,title,priority,sla_due_at\n"
        f"T-2001,Priorität prüfen,{priority},2026-07-15\n",
        encoding="utf-8",
    )

    result = import_cli(["--dry-run", str(csv_file)])

    assert result.exit_code == 0
    assert "T-2001" in result.output


def test_missing_ticket_id_fails_before_persistence(import_cli, tmp_path, persistence_fake):
    csv_file = tmp_path / "missing-ticket-id.csv"
    csv_file.write_text(
        "title,priority,sla_due_at\n"
        "Login defekt,high,2026-07-15\n",
        encoding="utf-8",
    )

    result = import_cli(["--dry-run", str(csv_file)])

    assert result.exit_code != 0
    assert "ticket_id" in result.output
    assert persistence_fake.write_count == 0
Manuelle Prüfungen

CLI-Ausgabe für Fehlermeldungen lesen: Feldname, Zeilennummer und Handlungshinweis müssen verständlich sein.

Prüfen, ob die Ausgabe keine produktiven Pfade, Tokens oder vollständigen sensiblen Rohdaten enthält.

Bei bestehenden Support- oder Betriebsanleitungen abgleichen, ob Exit-Codes und Fehlermuster weiterhin kompatibel sind.

Einen realistischen, anonymisierten CSV-Ausschnitt aus dem Fachbereich lokal gegen den Dry-Run prüfen.

Offene Fragen

Ist bei gemischt validen und invaliden Zeilen ein kompletter Abbruch oder ein Teilimport fachlich gewünscht?

Sollen Leerzeichen um Werte getrimmt oder als ungültig behandelt werden?

Gibt es bestehende Snapshot- oder CLI-Tests, deren Ausgabeformat stabil bleiben muss?

Welche maximale Dateigröße oder Zeilenanzahl soll lokal getestet werden?
