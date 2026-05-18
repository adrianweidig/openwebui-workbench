# OpenWebUI Model Builder

Lokaler Projektordner fuer den oeffentlichen ChatGPT `OpenWebUI Model Builder`.

## ChatGPT-Link

https://chatgpt.com/g/g-6a070eda8fdc81918ab61d4c4f1aa136-openwebui-model-builder

## Zweck

Dieser GPT erstellt vollstaendige OpenWebUI-Modellpakete fuer konkrete Aufgabenmodelle. Neben einer plausiblen `model.json` erzeugt er die zugehoerigen Prompt- und Wissensdateien fuer reproduzierbare Modellkonfigurationen.

## Enthaltene Dateien

- `customgpt_infos.md`: Beschreibung, Zielgruppe, Einsatzgebiete und Konfigurationslogik.
- `fachwissen.md`: fachliche Regeln und Strukturwissen fuer OpenWebUI-Modelle.
- `systemprompt.md`: Steuerlogik fuer Erstellung, Grenzen und Entscheidungsregeln.
- `bootloader.md`: kompakte Einbindung der Kernlogik fuer GPT-Hinweise.
- `icon.png`: Symbolgrafik fuer die GPT-Darstellung.
- `Problemfälle/`: Beispielsammlung oder Sonderfaelle fuer problematische oder grenzwertige Modellkonstellationen.

## Typische Nutzung

Geeignet fuer interne Aufgabenmodelle, Dokumentenanalyse, Support, RAG, Code-Review und standardisierte OpenWebUI-Presets mit bewusst gewaehlten Capabilities und Parametern.

## Fuer Repo-Nutzer

Startpunkt ist `customgpt_infos.md`. Fuer die eigentliche Modell- und Promptlogik danach `systemprompt.md` und `fachwissen.md` lesen.
