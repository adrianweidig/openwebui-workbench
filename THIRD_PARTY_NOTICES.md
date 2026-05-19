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

## Übernommener Drittanbieter-Code

Keiner.
