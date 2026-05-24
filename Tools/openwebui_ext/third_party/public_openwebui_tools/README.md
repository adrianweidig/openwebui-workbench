# Public OpenWebUI Tool Exports

Diese JSON-Dateien sind die unveränderten öffentlichen OpenWebUI-Tool-Exports aus einem lokalen Downloadordner.

Die produktiven Kopien liegen als einzelne Python-Tools unter `Tools/openwebui_ext/tools/` und wurden für Air-Gap-Betrieb angepasst:

- `generative_ui_plugin_for_open_webui.json` -> `openui_generative_ui.py`
- `ask_user_tool🧩_—_smart_follow-up_questions_before_the_ai_responds.json` -> `ask_user.py`
- `llm_council.json` -> `llm_council.py`
- `parallel_tools.json` -> `parallel_tools.py`
- `sub_agent_tool.json` -> `sub_agent.py`
- `visuals_toolkit_v4.json` -> `visuals_toolkit_v4.py`
- `web_search_and_crawl_tool.json` -> `web_search_and_crawl.py`

Die Original-Exports sind Referenzartefakte und nicht der Importpfad für die Air-Gap-Instanz. Importiert werden die generierten Bundles unter `Tools/dist/`.
