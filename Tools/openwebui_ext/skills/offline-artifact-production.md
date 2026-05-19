---
name: offline-artifact-production
description: Workflow für offline erzeugte HTML-, PDF-, Präsentations- und Download-Artefakte in OpenWebUI mit lokalem Jupyter.
---

# Offline Artifact Production

## Ziel
Erzeuge in OpenWebUI offline hochwertige, downloadfähige Arbeitsartefakte: HTML-Dokumente, druckfertige PDFs, HTML-Präsentationen, Tabellen, Diagramme und ZIP-Pakete.

## Grundprinzip
- Nutze lokale Nutzereingaben, hochgeladene Dateien und vorhandene Wissensquellen.
- Nutze den lokalen Jupyter-Server für Python-Berechnung, Datenanalyse, Diagramme und Validierung.
- Nutze das Artefakt-Tool für kontrollierte HTML-, PDF- und ZIP-Ausgaben.
- Keine Internetabhängigkeiten, keine externen CDNs, keine Webfonts, keine Remote-Bilder.

## HTML-Qualität
- HTML muss vollständig sein: `doctype`, `html`, `head`, `meta charset`, `title`, eingebettetes CSS.
- CSS muss druckfähig sein: `@page`, feste Seitenränder, kontrollierte Umbrüche, keine überlaufenden Tabellen.
- Für PDFs A4 oder 16:9-Landscape bewusst festlegen.
- Inhalte müssen ohne externe Assets lesbar bleiben.

## Präsentationen
- Folien als 16:9-HTML erzeugen.
- Jede Folie hat klare Headline, wenige starke Punkte und optional Notizen.
- Keine dekorativen Abhängigkeiten von externen Bildern oder Bibliotheken.
- Vor PDF-Export prüfen, dass Text nicht überläuft.

## Download-Workflow
1. Inhalt planen und fehlende Angaben mit maximal drei Rückfragen klären.
2. Bei Datenanalyse Jupyter nutzen und Ergebnisse knapp prüfen.
3. HTML oder Slides über das Artefakt-Tool schreiben.
4. Falls lokaler PDF-Konverter vorhanden ist, PDF erzeugen.
5. Bei mehreren Dateien ZIP-Paket erzeugen.
6. Im Chat Datei, Zweck, Grenzen und nächsten Prüfschritt nennen.

## Sicherheit
- Keine Secrets in Artefakte schreiben.
- Keine Pfade außerhalb des konfigurierten Artefaktverzeichnisses nutzen.
- Keine Shell- oder Netzwerkoperationen anfordern.
- Falls PDF-Konvertierung nicht verfügbar ist, klar die lokal bereitzustellende Abhängigkeit nennen.
