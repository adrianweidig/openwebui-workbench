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
