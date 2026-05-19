---
name: repository-maintenance
description: Strukturierte Wartung und Verbesserung von Code-Repositories mit Fokus auf Dokumentation, Tests, Sicherheit und Patch-Qualität.
---

# Repository Maintenance

## Vorgehen
- Prüfe zuerst Git-Status, README, Lizenz, Sicherheitsdateien, Teststruktur und vorhandene Konventionen.
- Suche mit schnellen lokalen Suchwerkzeugen nach relevanten Dateien und Mustern.
- Halte Änderungen klein, nachvollziehbar und am Ziel orientiert.

## Analyse
- Benenne Dokumentationslücken, Testlücken, Sicherheitsrisiken und unklare Ownership.
- Trenne vorhandene Nutzeränderungen von eigenen Änderungen.
- Vermeide unaufgeforderte Refactors und Formatierungswellen.

## Patch-Qualität
- Neue Dateien klar benennen und in vorhandene Struktur integrieren.
- Tests oder Validierung passend zum Risiko ergänzen.
- Bei fehlender Laufzeitumgebung Syntax-, Import- oder statische Prüfungen durchführen.

## Abschluss
- Berichte geänderte Dateien, Verifikation, Restunsicherheiten und sinnvolle nächste Schritte.
