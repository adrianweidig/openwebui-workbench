# Mistral Vision Workbench

Vision-faehiges OpenWebUI-Spezialmodell fuer Mistral-Medium-Workflows mit Bildern, Screenshots, Folien, Diagrammen, Scans und UI-Tests.

## Vorgesehene Tools

Das Modell kombiniert native Vision-Faehigkeit mit den Offline-Tools fuer Artefakte, Jupyter, Visuals, strukturierte Validierung, UI-/Code-Kontext und parallele QA-Planung.

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md` und `beispielergebnis.md` werden beim API-Import als Knowledge fuer dieses Modell hinterlegt. Dateien unter `beispiele/` werden zusaetzlich als nutzbare Beispielartefakte in die modellbezogene Knowledge Collection aufgenommen.
