# Zusatzbeispiel 2: Offline Workbench Agent

Dieses Beispiel ist optionales Knowledge/RAG-Material für `offline-workbench-agent`. Es ersetzt nicht den Pflichtkontext aus `mainprompt.md`, `fachwissen.md` und `Golden_Example.<ext>`.

## Szenario

Unvollständige Eingabe mit Qualitätsgrenze

## Nutzeranfrage

Die Eingabe ist knapp, enthält aber genug Kontext für einen ersten sicheren Entwurf.

## Gute Antwort

Stelle höchstens drei gezielte Rückfragen, erfinde keine fehlenden Fakten und liefere eine konservative Arbeitsfassung mit klaren offenen Punkten.

Ergebnisziel: Komplexe Offline-Aufgaben routen, Tools kombinieren und HTML/PDF/ZIP/Tabellen/Code-Artefakte lokal erzeugen.

Qualitätskriterium: Der Plan muss Tool-Wellen, Offline-Artefakte, Validierung, Sicherheitsgrenzen und Übergabeformat enthalten.
