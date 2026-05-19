---
name: data-cleaning-analysis
description: Strukturierte Analyse und Bereinigung von JSON-, CSV- und Textdaten mit Datenschutz- und Review-Hinweisen.
---

# Data Cleaning Analysis

## Vorgehen
- Format erkennen: JSON, CSV, Log, Markdown, Freitext oder Mischform.
- Syntax validieren und Fehler mit Zeile, Spalte oder Muster beschreiben.
- Spalten, Datensätze, Pflichtfelder, Typabweichungen und Duplikate prüfen.

## Datenschutz
- Sensible Feldnamen markieren und Werte redigieren.
- Personenbezogene Daten nicht unnötig wiederholen.
- Bei produktiven Daten nur aggregierte oder gekürzte Beispiele ausgeben.

## Ausgabe
- Status der Validierung.
- Erkannte Struktur.
- Probleme nach Schwere.
- Konkrete Bereinigungsschritte.
- Optional maschinenlesbare Zusammenfassung als JSON.
