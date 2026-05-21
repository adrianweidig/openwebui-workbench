# Modelle

Dieser Ordner enthält die operativ relevanten Modellartefakte.

## Unterstruktur

- `einzelmodelle/`: menschenlesbar sortierte Modellpakete mit importierbarem `model.json`, `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, `beispiele/`, `README.md` und dem kanonischen Index `index.md`/`index.json`
- `icons/`: generische schwarz-weiße SVG-/PNG-Profilicons mit weißem Hintergrund für OpenWebUI-Modellprofile
- `dist/`: Air-Gap-Handover für Copy/Paste, ZIP und OpenWebUI-Import

## Nutzung

- Für inhaltliche Prüfung und manuelle Bearbeitung `einzelmodelle/` verwenden.
- Für Modellprofilbilder einfache Icons aus `icons/generic/` verwenden; die vorgeschlagene Modellzuordnung steht in `icons/openwebui-generic-icons.json`.
- Für Transport in die Zielumgebung oder gebündelte Übergabe `dist/` verwenden.
- Die Einzelmodell-Indizes liegen nur unter `einzelmodelle/`; direkte Kopien im Ordner `Modelle/` werden nicht versioniert.
- Für die ChatGPT-ähnliche Offline-Gesamterfahrung zuerst `einzelmodelle/offline-workbench-agent/model.json` importieren und mit Jupyter- sowie Artefakt-Tools koppeln.
- Modellprofile werden über `scripts/configure_openwebui_tool_models.py` vereinheitlicht: natives Tool-Calling, Vision-Fähigkeit für Mistral-Medium-VL, eingebettete Icons, use-case-spezifische `temperature`-/`top_p`-Werte und ein kurzer Bootstrap-Systemprompt. Die Detailsteuerung liegt bewusst in `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und `beispiele/`; der Systemprompt verpflichtet das Modell, diese Knowledge vor der Antwort zu laden und zu analysieren. `max_tokens` wird bewusst nicht gesetzt; die Zielinstanz nutzt ihre Kontext- und Antwortlimits.
