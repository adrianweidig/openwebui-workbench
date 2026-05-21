# Promptforge

Promptforge optimiert den ersten Nutzerprompt nach dokumentierten Prompting-Best-Practices und bereitet ihn für OpenWebUI-Modelle mit Tool- und Filter-Nutzung auf.

## Vorgesehene Tools

- `ask_user`
- `tool_skill_overlay_planner`
- `json_csv_text_validator`
- `llm_council`
- `parallel_task_planner`

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md` und `fachwissen.md` werden beim API-Import als Knowledge für dieses Modell hinterlegt.
