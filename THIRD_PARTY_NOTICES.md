# Third-Party Notices

Abrufdatum: 2026-05-19

## Quellen geprüft

### Open WebUI Dokumentation

- Quelle: https://docs.openwebui.com/features/extensibility/plugin/tools/development/
- Zweck: Abgleich der Tool-Struktur, `Tools`-Klasse, Typannotationen, Valves/UserValves und Security-Hinweise.
- Ergebnis: Als Implementierungsreferenz genutzt, kein Code übernommen.

### Open WebUI Skills Dokumentation

- Quelle: https://docs.openwebui.com/features/workspace/skills/
- Zweck: Abgleich von Markdown-Skills, YAML-Frontmatter und Importverhalten.
- Ergebnis: Als Implementierungsreferenz genutzt, kein Code übernommen.

### gitjfmd/open-webui-tools

- Quelle: https://github.com/gitjfmd/open-webui-tools
- Lizenz laut Repository-Ansicht: MIT
- Zweck: Externer OpenWebUI-Tool-Kandidat.
- Entscheidung: Nicht integriert. Das Repository ist klein, ohne Releases, die GitHub-Webansicht lieferte keine belastbare Einzeldatei-Prüfung im aktuellen Lauf und mehrere gelistete Kategorien wie Code Interpreter oder UI-Erweiterungen erfordern eine strengere Detailprüfung vor Übernahme.

### Haervwe/open-webui-tools

- Quelle: https://github.com/Haervwe/open-webui-tools
- Lizenz laut Such- und Repository-Ansicht: MIT
- Zweck: Umfangreiche Community-Sammlung für OpenWebUI-Tools, Functions, Filter und Workflows.
- Geprüfte Kategorien: arXiv, Perplexica, Pexels, YouTube, native Image Generation, Hugging Face/Cloudflare Image, ComfyUI Image/Audio/Video, OpenWeatherMap, X-Daten, Planner Agent v3, Multi-Model Conversations, Resume Analyzer, Letta, Mopidy, Filter.
- Entscheidung: Kein ausführbarer Drittanbieter-Code übernommen. Stattdessen wurden offline-taugliche eigene Tools/Skills ergänzt, die die relevanten Muster sicher kapseln: Visuals, ComfyUI-Workflow-Prüfung, parallele Tool-/Subagent-Planung und Tool-/Skill-Overlays. Externe API- und Dienst-Tools bleiben bewusste lokale Integrationen, nicht globale Defaults.

### Classic298/open-webui-plugins

- Quelle: https://github.com/Classic298/open-webui-plugins
- Lizenz laut Repository-Datei: BSD-3-Clause
- Zweck: Inline Visualizer v1/v2, MCP App Bridge und weitere OpenWebUI-Plugins für Rich UI.
- Geprüfte Kategorien: `inline-visualizer`, `inline-visualizer-v2`, `mcp-app-bridge`.
- Entscheidung: Kein ausführbarer Drittanbieter-Code übernommen. Inline Visualizer v2 benötigt Same-Origin-Iframe-Zugriff für Streaming und erlaubt je nach CSP-Modus Inline-Skripte/CDN-Bibliotheken. Für Air-Gap-Betrieb wurde stattdessen `inline_visuals_toolkit_v3.py` als offline-fähiger, statischer SVG/HTML/Mermaid-Fallback ergänzt. Wer die Original-Plugins nutzen will, sollte sie separat in einem Testmodell prüfen und nicht global aktivieren.

### iChristGit/OpenWebui-Tools

- Quelle: https://github.com/iChristGit/OpenWebui-Tools
- Zweck: Community-Tool-Sammlung aus dem OpenWebUI-Ökosystem.
- Entscheidung: Nicht integriert. Im aktuellen Lauf wurde keine belastbare Lizenz- und Einzeldatei-Prüfung abgeschlossen. Ohne klare lokale Review-Basis wird kein serverseitig ausführbarer Drittanbieter-Code übernommen.

### Öffentliche OpenWebUI-Tool-Exports aus lokalem Download

- Quelle: `C:\Users\adrian.TOP\Downloads\öffentliche tools`
- Abruf-/Übernahmedatum: 2026-05-20
- Enthaltene Exports: Ask User, OpenUI, LLM Council, Parallel Tools, Sub Agent, Visuals Toolkit V4, Web Search and Crawl.
- Lizenzangaben laut Tool-Metadaten: `llm_council`, `parallel_tools`, `sub_agent`, `visuals_toolkit_v4` und `web_search_and_crawl` nennen MIT; `ask_user`, `openui` und `markdown_normalizer` nennen keine explizite Lizenz im Export.
- Entscheidung: Integriert, aber nicht roh als Produktivdefault. Original-Exports liegen unverändert unter `Tools/openwebui_ext/third_party/public_openwebui_tools/`. Produktive Kopien liegen unter `Tools/openwebui_ext/tools/` und enthalten Air-Gap-Anpassungen.

## Übernommener Drittanbieter-Code

- `Tools/openwebui_ext/tools/openui_generative_ui.py`: aus `generative_ui_plugin_for_open_webui.json`, optionales Rich-UI-Tool. Nicht Offline-Default; CDN-Default auf lokalen Pfad `/static/openui/dist` geändert.
- `Tools/openwebui_ext/tools/ask_user.py`: aus `ask_user_tool🧩_—_smart_follow-up_questions_before_the_ai_responds.json`. Keine öffentlichen Dienste; blockierendes Warten durch `asyncio.sleep` ersetzt und Event-Emitter defensiv geprüft.
- `Tools/openwebui_ext/tools/llm_council.py`: aus `llm_council.json`, MIT laut Export. Öffentliche OpenAI-/OpenRouter-Fallbacks deaktiviert; Default-Modell auf lokal `coder` gesetzt.
- `Tools/openwebui_ext/tools/parallel_tools.py`: aus `parallel_tools.json`, MIT laut Export. Keine öffentlichen Defaults ergänzt; Reichweite bleibt durch aktivierte OpenWebUI-Tools begrenzt.
- `Tools/openwebui_ext/tools/sub_agent.py`: aus `sub_agent_tool.json`, MIT laut Export. Web-, Image-, Automation- und Calendar-Builtin-Kategorien standardmäßig deaktiviert.
- `Tools/openwebui_ext/tools/visuals_toolkit_v4.py`: aus `visuals_toolkit_v4.json`, MIT laut Export. Public-CDN-Default deaktiviert; Auto-Modus fällt auf Text/ASCII zurück.
- `Tools/openwebui_ext/tools/web_search_and_crawl.py`: aus `web_search_and_crawl_tool.json`, MIT laut Export. Nicht Offline-Default; Public-Network-Guard ergänzt, lokale/private/allowlistete Hosts erlaubt, OpenRouter-Default entfernt, optionale `orjson`/`loguru`-Fallbacks ergänzt.
- `Tools/openwebui_ext/filters/markdown_normalizer.py`: aus `markdown_normalizer.json`. Der Export nennt `type: action`, der Code implementiert aber eine `Filter`-Klasse mit `outlet`; im Repo wird er als Filter importiert. Keine externen Netzaufrufe.
