# Problemfall: Internetwissen

## Ziel

Das OpenWebUI-Modellpaket `internetwissen` ist integriert und wird offline-first gehärtet. Es soll für allgemeine Recherchefragen, Anleitungen, Erklärungen, Quellenkritik und Wissensstrukturierung nutzbar bleiben, ohne Live-Websuche vorzutäuschen.

Das initiale Modell funktioniert ohne große externe Datensätze. Die Wissensbasis liegt direkt im Repository, insbesondere in `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, Beispielen und i18n-Profilen.

## Nutzerproblem

Nutzer möchten im Offline-Betrieb ein Modell verwenden, das bei allgemeinen Internet- und Wissensfragen hilfreich bleibt, aber keine Live-Websuche vortäuscht. Es soll allgemeingültige Anleitungen, Recherchepläne und Quellenkritik liefern können.

## Anforderungen

- repo-interne KnowledgeBase statt externer GB-/TB-Daten
- keine Live-Websuche im Offline-Default
- klare Kennzeichnung von Aktualitätsgrenzen
- Antwortmuster für Erklärungen, Anleitungen, Recherchepläne und Quellenkritik
- keine großen Datenartefakte im Git-Repository
- späterer Ausbau über optionale KnowledgePacks statt Initialumfang
- maximal 10 GiB Gesamtbudget für KnowledgePacks und optionale Offline-Image-Artefakte

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
- Netzwerkfähige Tools sind nicht Teil des Offline-Profils.
- KnowledgePack-Struktur und Budgetprüfung sind validierbar.
