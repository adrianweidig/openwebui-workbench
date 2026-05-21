# Third-Party OpenWebUI Tools

Dieses Verzeichnis enthält Original-Exports geprüfter Drittanbieter-Tools als Referenzmaterial.

Produktiv importierbare, air-gap-angepasste Kopien liegen unter `Tools/openwebui_ext/tools/` und `Tools/openwebui_ext/filters/`. Die Originaldateien bleiben hier unverändert nachvollziehbar, damit Herkunft, Lizenzangaben und lokale Änderungen prüfbar bleiben.

Übernommene Exports:

- `public_openwebui_tools/ask_user_tool🧩_—_smart_follow-up_questions_before_the_ai_responds.json` -> `ask_user.py`
- `public_openwebui_tools/generative_ui_plugin_for_open_webui.json` -> `openui_generative_ui.py`
- `public_openwebui_tools/llm_council.json` -> `llm_council.py`
- `public_openwebui_tools/parallel_tools.json` -> `parallel_tools.py`
- `public_openwebui_tools/sub_agent_tool.json` -> `sub_agent.py`
- `public_openwebui_tools/visuals_toolkit_v4.json` -> `visuals_toolkit_v4.py`
- `public_openwebui_tools/web_search_and_crawl_tool.json` -> `web_search_and_crawl.py`
- `public_openwebui_functions/auto_tool_selector__automatically_enables_the_right_mcp_tools_per_message.json` -> `filters/auto_tool_selector.py`
- `public_openwebui_functions/markdown_normalizer.json` -> `filters/markdown_normalizer.py`

Air-Gap-Änderungen sind in den produktiven Tool-/Filter-Dateien dokumentiert. Insbesondere wurden öffentliche API-Fallbacks deaktiviert, CDN-Defaults entfernt oder zu lokalen Pfaden geändert, Public-Web-Crawling auf lokale/private/allowlistete Hosts begrenzt und der Auto-Tool-Selector ohne OpenWebUI-Top-Level-Imports, externen Modellaufruf oder Netzwerkzugriff umgesetzt.
