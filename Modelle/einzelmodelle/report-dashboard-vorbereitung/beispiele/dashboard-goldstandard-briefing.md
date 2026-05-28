# Beispiele: Report- und Dashboard-Vorbereitung

Diese Beispiele zeigen robuste Offline-Arbeit für `report-dashboard-vorbereitung`: schemaorientiert, quellengebunden, ohne erfundene Daten und mit dem passenden Artefaktformat `beispielergebnis.html`.

## Beispiel 1: Minimale Anfrage

### Nutzeranfrage

Mach daraus eine strukturierte Auswertung.

### Gute Antwort

Ich prüfe zuerst, welches Zielformat sinnvoll ist: API-Vertrag, JSON-Extraktion, Datenprofil, Logbefund oder Dashboard-Briefing. Ohne Rohdaten markiere ich Annahmen und fordere die kleinste relevante Quelle an.

## Beispiel 2: Realistischer Standardfall

### Nutzeranfrage

Aus diesen Ticketfeldern soll ein importierbares Artefakt entstehen. Es muss offline nutzbar sein und klare Validierungsregeln enthalten.

### Gute Antwort

Das Modell liefert `beispielergebnis.html` als fertiges Artefakt, trennt Datenvertrag, Beispiele, Fehlerfälle und Prüfschritte und nutzt keine externen APIs oder CDNs.

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

Die passende Musterantwort ist `beispielergebnis.html`. Qualitätslatte: Kennzahlen, Datenquellen, Visualtyp, Filter, Warnschwellen und Nutzerfragen müssen definiert sein.
