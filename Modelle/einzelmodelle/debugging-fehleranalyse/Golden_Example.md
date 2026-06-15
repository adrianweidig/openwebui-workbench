Golden Example: Debugging und Fehleranalyse
Nutzeranfrage

Wir bekommen beim CSV-Import in OpenWebUI sporadisch einen Fehler. Bitte grenze das ein und gib mir sichere nächste Checks. Keine produktiven Änderungen.

Sichtbarer Kontext

Fehlermeldung im UI:

Import failed: 500 Internal Server Error

Relevanter Logauszug:

2026-06-12T09:14:22Z INFO  import started file=customers.csv rows=248
2026-06-12T09:14:23Z ERROR import failed request_id=req-7f2a
Traceback (most recent call last):
  File "/app/importer/csv_import.py", line 88, in import_rows
    customer_id = row["customer_id"]
KeyError: 'customer_id'

Ausschnitt aus der Importfunktion:

Python
Ausgeführt
import csv

def import_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            customer_id = row["customer_id"]
            email = row["email"]
            save_customer(customer_id, email)

Kopfzeilen aus zwei Dateien:

customers_ok.csv:
customer_id,email,name

customers_fail.csv:
customerId;email;name

Zuletzt geändert:

2026-06-11: Export aus dem Altsystem auf Semikolon-Trennung umgestellt.
Gute Antwort
Symptom

Der CSV-Import bricht mit 500 Internal Server Error ab. Im Serverlog endet die Verarbeitung mit KeyError: 'customer_id' in import_rows, sobald der Code row["customer_id"] liest.

Der sichtbare Vergleich der Kopfzeilen zeigt:

funktionierende Datei: customer_id,email,name

fehlschlagende Datei: customerId;email;name

zuletzt geändert: Export aus dem Altsystem wurde auf Semikolon-Trennung umgestellt.

Eine endgültige Ursache ist noch nicht durch einen lokalen Lauf bestätigt. Die stärkste Hypothese ist aber ein Format- und Schema-Mismatch: Der Import erwartet Komma-Trennung und die Spalte customer_id; die fehlschlagende Datei enthält Semikolon-Trennung und customerId.

Bekannte Fakten
Fakt	Quelle	Bedeutung
UI meldet 500 Internal Server Error.	sichtbare Fehlermeldung	Nutzer sieht einen generischen Serverfehler statt einer verständlichen Validierungsmeldung.
Log zeigt KeyError: 'customer_id'.	Stacktrace	Der Code greift auf eine fehlende DictReader-Spalte zu.
Importcode nutzt csv.DictReader(handle) ohne expliziten Delimiter.	Codeausschnitt	Der Default-Delimiter ist Komma.
Code erwartet row["customer_id"] und row["email"].	Codeausschnitt	customer_id ist aktuell Pflichtfeld im Mapping.
Erfolgreiche Datei nutzt customer_id,email,name.	Kopfzeile customers_ok.csv	Passt zum erwarteten Kommaformat und Spaltennamen.
Fehlerhafte Datei nutzt customerId;email;name.	Kopfzeile customers_fail.csv	Weicht bei Delimiter und Spaltenname ab.
Export wurde auf Semikolon-Trennung umgestellt.	Änderungsnotiz vom 2026-06-11	Plausibler Auslöser für neue Importfehler.
Priorisierte Hypothesen
Priorität	Hypothese	Prüfung	Erwartetes Signal
P1	Die fehlschlagende CSV wird als eine einzige Spalte gelesen, weil csv.DictReader standardmäßig Komma statt Semikolon erwartet.	Kopfzeile und reader.fieldnames lokal für die fehlschlagende Datei ausgeben.	reader.fieldnames ist ['customerId;email;name'] statt einzelner Spalten.
P2	Zusätzlich weicht der Pflichtspaltenname ab: Export liefert customerId, Import erwartet customer_id.	Datei mit Semikolon-Delimiter lesen und reader.fieldnames prüfen.	reader.fieldnames enthält customerId, aber nicht customer_id.
P3	Fehlerbehandlung fehlt: Schemafehler werden als KeyError bis zum 500er durchgereicht.	Codepfad auf Validierung vor der Schleife prüfen.	Keine Prüfung auf Pflichtspalten vor Zugriff auf row[...].
P4	Der Fehler wirkt sporadisch, weil nur Dateien aus dem geänderten Altsystemexport betroffen sind.	Fehlschläge nach Dateiquelle, Exportdatum und Kopfzeile gruppieren.	Fehler korrelieren mit Semikolon-Dateien oder Exporten ab 2026-06-11.
Nächste sichere Checks

Diese Checks sind lokal, read-only und verändern keine produktiven Daten.

1. Tatsächlich gelesene CSV-Spalten prüfen
Bash
python - <<'PY'
import csv
from pathlib import Path

for filename in ["customers_ok.csv", "customers_fail.csv"]:
    path = Path(filename)
    if not path.exists():
        print(f"{filename}: Datei nicht gefunden")
        continue

    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        print(f"{filename}: {reader.fieldnames}")
PY

Erwartung bei P1:

customers_ok.csv: ['customer_id', 'email', 'name']
customers_fail.csv: ['customerId;email;name']
2. Semikolon-Lesart gegenprüfen
Bash
python - <<'PY'
import csv
from pathlib import Path

path = Path("customers_fail.csv")
with path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle, delimiter=";")
    print(reader.fieldnames)
PY

Erwartung bei P2:

['customerId', 'email', 'name']

Dann ist belegt, dass zwei Anpassungen nötig sind: Delimiter-Erkennung oder Konfiguration sowie ein dokumentiertes Spaltenmapping für customerId zu customer_id.

3. Minimalreproduktion ohne Datenimport
Bash
python - <<'PY'
import csv
from io import StringIO

sample = "customerId;email;name\n123;test@example.invalid;Test Name\n"
reader = csv.DictReader(StringIO(sample))
row = next(reader)
print("fieldnames:", reader.fieldnames)
print("row:", row)
print("has customer_id:", "customer_id" in row)
PY

Erwartetes Signal:

fieldnames: ['customerId;email;name']
row: {'customerId;email;name': '123;test@example.invalid;Test Name'}
has customer_id: False

Damit lässt sich der Fehlerpfad ohne echte Kundendaten reproduzieren.

Wahrscheinliche Fix-Richtung
1. Schema vor Verarbeitung validieren

Der Import sollte Pflichtspalten prüfen, bevor Zeilen verarbeitet werden. Ein fehlendes Feld darf nicht als unkontrollierter KeyError enden, sondern muss eine verständliche Validierungsmeldung erzeugen.

Mindestlogik:

Kopfzeile lesen.

Delimiter bestimmen oder explizit konfigurieren.

erlaubte Spaltenaliasse normalisieren.

Pflichtfelder validieren.

erst danach Daten speichern.

2. Delimiter bewusst behandeln

Da die Änderung auf Semikolon-Trennung sichtbar ist, sollte der Import entweder:

Semikolon als erlaubten Delimiter konfigurieren, oder

den CSV-Dialekt lokal erkennen und bei uneindeutigen Dateien abbrechen, oder

das Altsystem wieder auf das dokumentierte Kommaformat umstellen.

Die Entscheidung hängt davon ab, welches Format künftig verbindlich sein soll.

3. Alias für customerId nur explizit zulassen

Wenn customerId fachlich dieselbe Spalte wie customer_id ist, sollte das Mapping explizit dokumentiert und getestet werden. Keine stillen, unbegrenzten Namensumwandlungen einbauen, weil dadurch echte Schemafehler verdeckt werden können.

4. Fehler für Nutzer verständlich machen

Statt 500 Internal Server Error sollte der Import bei Schemafehlern kontrolliert abbrechen, zum Beispiel mit einer fachlichen Meldung:

CSV-Schema ungültig: Pflichtspalte customer_id fehlt. Gefundene Spalten: customerId, email, name.
Validierung nach Fix
Testfall	Erwartetes Ergebnis
customer_id,email,name mit Komma	Import erfolgreich
customerId;email;name mit Semikolon und erlaubtem Alias	Import erfolgreich oder kontrolliert abgelehnt, je nach Zielentscheidung
email,name ohne Kunden-ID	kein 500er; klare Validierungsmeldung
leere Datei	kein 500er; klare Meldung zur fehlenden Kopfzeile
Datei mit unbekanntem Delimiter	kein 500er; kontrollierte Ablehnung
Datei mit zusätzlichen Spalten	Import nur, wenn Pflichtfelder vorhanden sind; Zusatzspalten ignorieren oder protokollieren
Offene Informationen
Punkt	Warum relevant
Soll Semikolon künftig offiziell unterstützt werden?	Bestimmt, ob Importer angepasst oder Exportkonfiguration korrigiert wird.
Ist customerId fachlich identisch mit customer_id?	Bestimmt, ob ein Alias zulässig ist.
Gibt es weitere betroffene Pflichtfelder?	Verhindert den nächsten KeyError bei email oder späteren Feldern.
Wo wird der 500er in eine HTTP-Antwort übersetzt?	Nötig, um Nutzerfehler als Validierungsfehler statt Serverfehler auszugeben.
Gibt es Tests für fehlerhafte CSV-Kopfzeilen?	Nötig zur Absicherung des Fixes.
Nicht empfohlene Sofortmaßnahmen

Kein produktiver Restart als erster Schritt: Der Stacktrace zeigt einen daten- oder schemaabhängigen Fehler, keinen belegten Prozesshänger.

Kein Löschen fehlschlagender Dateien ohne Sicherung: Die Dateien sind Diagnosematerial.

Keine stille automatische Umbenennung beliebiger Spalten: Das kann echte Datenqualitätsprobleme verdecken.

Keine vollständigen Logs mit personenbezogenen Daten in Tickets kopieren: Nur relevante Zeilen verwenden und sensible Werte maskieren.

Ergebnis

Die wahrscheinlichste Fehlerklasse ist ein CSV-Formatwechsel mit anschließendem Schemafehler. Der nächste beste Schritt ist die lokale Prüfung von reader.fieldnames für eine erfolgreiche und eine fehlschlagende Datei. Wenn sich P1 und P2 bestätigen, sollte der Fix aus Delimiter-Behandlung, explizitem Spaltenmapping und früher Schema-Validierung bestehen. Dadurch wird aus dem aktuellen 500er ein kontrollierter, reproduzierbarer Validierungsfehler oder ein sauber unterstützter neuer Importpfad.
