# Problemfall: Internetwissen

## Ziel

Ein neues OpenWebUI-Modellpaket `internetwissen` soll offline für allgemeine Recherchefragen, Anleitungen, Erklärungen, Quellenkritik und Wissensstrukturierung nutzbar sein.

Das initiale Modell funktioniert ohne große externe Datensätze. Die Wissensbasis liegt direkt im Repository, insbesondere in `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, Beispielen und i18n-Profilen.

## Nutzerproblem

Nutzer möchten im Offline-Betrieb ein Modell verwenden, das bei allgemeinen Internet- und Wissensfragen hilfreich bleibt, aber keine Live-Websuche vortäuscht. Es soll allgemeingültige Anleitungen, Recherchepläne und Quellenkritik liefern können.

## Anforderungen

- repo-interne KnowledgeBase statt externer GB-/TB-Daten
- keine Live-Websuche im Offline-Default
- klare Kennzeichnung von Aktualitätsgrenzen
- Antwortmuster für Erklärungen, Anleitungen, Recherchepläne und Quellenkritik
- keine großen Datenartefakte im Git-Repository
- späterer Ausbau über Roadmap statt Initialumfang

## Nicht-Ziele

- kein FineWeb
- kein Common Crawl
- kein Wikipedia-Dump
- kein Kiwix/ZIM
- kein externer Vektorindex
- keine automatische Webarchiv-Pipeline
- keine versteckte Online-Abhängigkeit

## Erfolgskriterien

- Das Modell `internetwissen` ist importierbar.
- `web_search` ist im Modellprofil deaktiviert.
- Das Modell kann allgemeine Anleitungen, Recherchepläne, Quellenkritik und Wissensstrukturierung liefern.
- Das Modell sagt klar, wenn aktuelle Quellen nötig sind.
- Die Roadmap beschreibt große Offline-Webkorpora nur als spätere Option.
