# OpenWebUI Model Builder

OpenWebUI-Modellumsetzung des Custom GPT `OpenWebUI Model Builder` aus `adrianweidig/custom-gpts`.

## Zweck

Erstellt vollständige OpenWebUI-Modellpakete mit `model.json`, kurzem Bootloader-`systemprompt.md`, `mainprompt.md`, `fachwissen.md`, passendem `beispielergebnis` und Importcheckliste.

## Referenz

Quelle: `https://github.com/adrianweidig/custom-gpts/tree/main/OpenWebUI%20Model%20Builder`

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, `beispiele/` und `i18n/` werden beim API-Import als Knowledge für dieses Modell hinterlegt.
