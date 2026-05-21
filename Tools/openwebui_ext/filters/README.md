# OpenWebUI Filters

Importierbare OpenWebUI-Filter-Functions für modellübergreifende Middleware.

## context_compressor_filter.py

Zählt vor jedem Modellaufruf die geschätzten Chat-Kontexttokens. Sobald der
konfigurierte Schwellwert erreicht wird, werden ältere Chatnachrichten in eine
kompakte System-Zusammenfassung überführt und die jüngsten Nachrichten
unverändert behalten.

Der Filter ist als togglebarer OpenWebUI-Filter gebaut, wird aber durch die
Generatorlogik in `meta.defaultFilterIds` für alle Chat-Modelle standardmäßig
aktiviert.

## auto_tool_selector.py

Aktiviert vor jedem Modellaufruf passende, bereits verfügbare Tool-IDs für den
aktuellen Prompt. Die produktive Version ist aus dem öffentlichen
`auto_tool_selector`-Export abgeleitet, arbeitet aber air-gap-sicher ohne
LLM-Aufruf, ohne externe Netzwerke und ohne harte OpenWebUI-Imports.

Der Filter erkennt lokale Repo-Tools wie `ask_user`, `parallel_tools`,
`sub_agent`, `llm_council`, `visuals_toolkit_v4`, Jupyter, Artefakt-Tools,
Validatoren und optionale MCP-Server nur dann, wenn sie in der Zielinstanz
verfügbar sind. Alle aktivierten Functions bleiben dadurch echte
OpenWebUI-Filter mit `inlet`/`outlet`-Hooks.

## markdown_normalizer.py

Normalisiert Assistant-Ausgaben nach der Modellantwort: Codeblöcke, LaTeX,
Mermaid-Syntax, Tabellen, Überschriften und ausgewählte XML-Artefakte. Der
Filter arbeitet lokal ohne Netzwerkzugriff und überspringt HTML-Inhalte, damit
Rich-UI-Toolausgaben nicht nachträglich umgeschrieben werden.

Der öffentliche Export deklarierte `type: action`, enthält aber eine
`Filter`-Klasse mit `outlet`-Hook. Die Generatorlogik importiert ihn daher
korrekt als OpenWebUI-Filter.
