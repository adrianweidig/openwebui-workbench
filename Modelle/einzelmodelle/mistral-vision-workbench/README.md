# Mistral Vision Workbench

Vision-fähiges OpenWebUI-Spezialmodell für Mistral-Medium-Workflows mit Bildern, Screenshots, Folien, Diagrammen, Scans und UI-Tests.

## Vorgesehene Tools

Das Modell kombiniert native Vision-Fähigkeit mit den Offline-Tools für Artefakte, Jupyter, Visuals, strukturierte Validierung, UI-/Code-Kontext und parallele QA-Planung.

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md` und `beispielergebnis.md` werden beim API-Import als Knowledge für dieses Modell hinterlegt. Dateien unter `beispiele/` werden zusätzlich als nutzbare Beispielartefakte in die modellbezogene Knowledge Collection aufgenommen.
