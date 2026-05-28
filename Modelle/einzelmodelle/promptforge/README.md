# PromptForge

OpenWebUI-Modellumsetzung des Custom GPT `PromptForge` / `Promptgenerator` aus `adrianweidig/custom-gpts`.

## Zweck

Erstellt vollständige, direkt kopierbare Markdown-Promptvorlagen für ChatGPT, Custom GPTs, OpenWebUI, lokale LLMs und API-Workflows. Das Modell nutzt `beispielergebnis.md` als Goldstandard für fertige Promptvorlagen ohne Platzhalter und `beispiele/promptforge-goldstandard-briefing.md` als Few-Shot-Material.

## Referenz

Quelle: `https://github.com/adrianweidig/custom-gpts/tree/main/Promptgenerator`

## Vorgesehene Tools

- `ask_user`
- `tool_skill_overlay_planner`
- `json_csv_text_validator`
- `llm_council`
- `parallel_task_planner`

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`, `beispiele/` und `i18n/` werden beim API-Import als Knowledge für dieses Modell hinterlegt.
