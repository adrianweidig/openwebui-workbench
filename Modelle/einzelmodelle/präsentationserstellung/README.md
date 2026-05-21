# Präsentationserstellung

## Zweck

OpenWebUI-Modellumsetzung des Custom GPT `Präsentationscreator` aus `adrianweidig/custom-gpts`.

Das Ziel ist nicht mehr eine langweilige PDF- oder PPTX-Folienausgabe, sondern eine hochwertige browserbasierte Web-Keynote als `präsentation.html`: 16:9, modern gestaltet, animiert, interaktiv, PowerPoint-ähnlich bedienbar und direkt im Browser lauffähig.

## Quelle

Referenz: `https://github.com/adrianweidig/custom-gpts/tree/main/Pr%C3%A4sentationscreator`

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: enabled

## Dateien

- `model.json`: direkt importierbare OpenWebUI-JSON-Datei im Exportschema, als Array mit genau einem Modellobjekt
- `systemprompt.md`: Custom-GPT-Systemprompt des Präsentationscreator
- `mainprompt.md`: Bootloader-/Operationslogik für OpenWebUI
- `fachwissen.md`: verbindliche Präsentations-, Design-, HTML-/CSS-/JS- und Qualitätsregeln
- `customgpt_infos.md`: Referenzinformationen zum ursprünglichen Custom GPT

## Hinweis

Für den eigentlichen OpenWebUI-Import ist `model.json` die primäre Datei. Die Markdown-Dateien sind für Durchsicht, Pflege und manuelle Nacharbeit im Repository gedacht.
