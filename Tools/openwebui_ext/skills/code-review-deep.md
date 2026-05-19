---
name: code-review-deep
description: Gründlicher Code-Review mit Fokus auf Korrektheit, Wartbarkeit, Sicherheit, Edge Cases und Testabdeckung.
---

# Code Review Deep

## Review-Reihenfolge
- Prüfe zuerst Korrektheit, Datenverlust, Sicherheitsrisiken und Produktionsausfälle.
- Danach Wartbarkeit, Performance, Lesbarkeit und Stil.
- Findings immer mit Datei, Stelle und konkreter Auswirkung benennen.

## Risikoanalyse
- Suche nach unvalidierten Eingaben, Secret-Leaks, fehlerhafter Authentifizierung, unsicheren Defaults und fehlender Fehlerbehandlung.
- Prüfe Grenzfälle: leere Eingaben, große Eingaben, Timeouts, ungültige Formate, Nebenläufigkeit und Wiederholbarkeit.

## Tests
- Bewerte, ob Tests das geänderte Verhalten tatsächlich absichern.
- Nenne fehlende Tests als konkrete Fälle, nicht als allgemeine Aufforderung.

## Ausgabe
- Findings zuerst, nach Schwere sortiert.
- Danach offene Fragen und knappe Zusammenfassung.
- Keine unnötigen Lob- oder Stilkommentare ohne Risiko.
