# Zusatzbeispiel 1: Code-Review

Dieses Beispiel ist optionales Knowledge/RAG-Material für `code-review`. Es ersetzt nicht den Pflichtkontext aus `mainprompt.md`, `fachwissen.md` und `Golden_Example.<ext>`.

## Szenario

Fokussierter Standardauftrag

## Nutzeranfrage

Ein Patch soll mit Findings, Schweregrad, Repro-Hinweis und Testlücken bewertet werden.

## Gute Antwort

Arbeite mit sichtbaren Quellen, markiere Annahmen und liefere ein direkt prüfbares Zwischenergebnis. Nutze die Pflichtdateien als Qualitätsanker; dieses Beispiel ist nur zusätzliches RAG-Material.

Ergebnisziel: Diffs, Risiken, Regressionen, Sicherheitsprobleme und fehlende Tests wie in einem professionellen Review priorisieren.

Qualitätskriterium: Findings stehen vor Zusammenfassung und referenzieren konkrete Dateien, Zeilen oder sichtbare UI-Zustände.
