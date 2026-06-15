# Zusatzbeispiel 2: Code-Review

Dieses Beispiel ist optionales Knowledge/RAG-Material für `code-review`. Es ersetzt nicht den Pflichtkontext aus `mainprompt.md`, `fachwissen.md` und `Golden_Example.<ext>`.

## Szenario

Unvollständige Eingabe mit Qualitätsgrenze

## Nutzeranfrage

Die Eingabe ist knapp, enthält aber genug Kontext für einen ersten sicheren Entwurf.

## Gute Antwort

Stelle höchstens drei gezielte Rückfragen, erfinde keine fehlenden Fakten und liefere eine konservative Arbeitsfassung mit klaren offenen Punkten.

Ergebnisziel: Diffs, Risiken, Regressionen, Sicherheitsprobleme und fehlende Tests wie in einem professionellen Review priorisieren.

Qualitätskriterium: Findings stehen vor Zusammenfassung und referenzieren konkrete Dateien, Zeilen oder sichtbare UI-Zustände.
