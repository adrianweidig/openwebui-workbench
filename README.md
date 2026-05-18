# OpenWebUI Workspace

Dieses Repository verwaltet den lokalen Arbeitsbereich unter `E:\OpenWebUI`.

## Struktur

- `OpenWebUI Model Builder/`: Quellvorgaben, Generatorlogik und erzeugte `dist`-Artefakte fuer OpenWebUI-Modelle und Tools.
- `Problemfaelle/`: Problemfall-Briefings, aus denen die Aufgabenmodelle erzeugt werden.
- `Modelle/`: Ablage fuer manuell gepflegte oder spaeter importierte Modellpakete ausserhalb des Builders.
- `Tools/`: Ablage fuer zusaetzliche lokale Tool-Implementierungen oder Hilfsskripte.
- `Weiteres/`: Sonstige referenzierbare Materialien, die nicht sauber in die anderen Bereiche passen.

## Arbeitsweise

- Primare operative Ergebnisse werden im Builder unter `OpenWebUI Model Builder/dist/` erzeugt.
- Original-Briefings in `Problemfaelle/` werden nicht destruktiv veraendert.
- Lokale Arbeits- und Sicherungsbereiche des Builders sind `.work/` und `.backup/`.
- Das Repository ist auf Offline-/Air-Gapped-Arbeit ausgelegt; keine externen Laufzeitabhaengigkeiten voraussetzen.

## Wichtige Einstiege

- `OpenWebUI Model Builder/README.md`
- `OpenWebUI Model Builder/dist/docs/ARCHITEKTUR.md`
- `OpenWebUI Model Builder/dist/reports/inventar.md`
