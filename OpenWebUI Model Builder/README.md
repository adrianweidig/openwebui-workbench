# OpenWebUI Model Builder

Lokaler Projektordner für den öffentlichen ChatGPT `OpenWebUI Model Builder`.

## ChatGPT-Link

https://chatgpt.com/g/g-6a070eda8fdc81918ab61d4c4f1aa136-openwebui-model-builder

## Zweck

Dieser GPT erstellt vollständige OpenWebUI-Modellpakete für konkrete Aufgabenmodelle. Neben einer plausiblen `model.json` erzeugt er die zugehörigen Prompt- und Wissensdateien für reproduzierbare Modellkonfigurationen.

## Enthaltene Dateien

- `customgpt_infos.md`: Beschreibung, Zielgruppe, Einsatzgebiete und Konfigurationslogik.
- `fachwissen.md`: fachliche Regeln und Strukturwissen für OpenWebUI-Modelle.
- `systemprompt.md`: Steuerlogik für Erstellung, Grenzen und Entscheidungsregeln.
- `bootloader.md`: kompakte Einbindung der Kernlogik für GPT-Hinweise.
- `icon.png`: Symbolgrafik für die GPT-Darstellung.
- `Problemfälle/`: Beispielsammlung oder Sonderfälle für problematische oder grenzwertige Modellkonstellationen.

## Typische Nutzung

Geeignet für interne Aufgabenmodelle, Dokumentenanalyse, Support, RAG, Code-Review und standardisierte OpenWebUI-Presets mit bewusst gewählten Capabilities und Parametern.

## Für Repo-Nutzer

Startpunkt ist `customgpt_infos.md`. Für die eigentliche Modell- und Promptlogik danach `systemprompt.md` und `fachwissen.md` lesen.
