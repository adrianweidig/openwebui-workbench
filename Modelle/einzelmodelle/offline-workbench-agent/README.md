# Offline Workbench Agent

Zentraler Offline-Arbeitsagent für OpenWebUI mit lokalem Jupyter und Artefakt-Workflow.

Das Goldstandard-Beispiel `beispielergebnis.md` zeigt ein vollständiges Offline-Handover mit Tool-Wellen, Artefaktmanifest, HTML-/JSON-/ZIP-Regeln, Validierung und Grenzen. Ergänzende Few-Shot-Beispiele liegen unter `beispiele/offline-workbench-auftrag-goldstandard.md`.

## Vorgesehene Tools

- `air_gapped_jupyter_python`
- `offline_artifact_workbench`
- `json_csv_text_validator`
- optional weitere Tools aus `Tools/openwebui_ext/tools/`

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, `beispiele/` und `i18n/` werden beim API-Import als Knowledge für dieses Modell hinterlegt.
