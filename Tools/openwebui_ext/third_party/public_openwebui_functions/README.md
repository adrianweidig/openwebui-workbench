# Public OpenWebUI Function Exports

Diese JSON-Dateien sind unveränderte öffentliche OpenWebUI-Function-Exports aus einem lokalen Downloadordner.

Die produktiven Kopien liegen unter `Tools/openwebui_ext/filters/` oder künftig unter passenden Function-Unterordnern und wurden für Air-Gap-Betrieb geprüft.

- `markdown_normalizer.json` -> `Tools/openwebui_ext/filters/markdown_normalizer.py`
- `auto_tool_selector__automatically_enables_the_right_mcp_tools_per_message.json` -> `Tools/openwebui_ext/filters/auto_tool_selector.py`

Der Original-Export deklariert `type: action`, enthält aber eine `Filter`-Klasse mit `outlet`-Hook. Die produktive Repo-Version wird deshalb als Filter behandelt.

Der öffentliche `auto_tool_selector` nutzt OpenWebUI-Interna und Modellaufrufe,
um MCP-Server zu wählen. Die produktive Repo-Version bleibt bewusst ein
offlinefähiger Filter: Sie nutzt keine externen Dienste, importiert keine
OpenWebUI-Module auf Top-Level und ergänzt nur Tool-IDs, die im Modell- oder
Request-Kontext verfügbar sind.
