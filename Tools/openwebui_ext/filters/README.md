# OpenWebUI Filters

Importierbare OpenWebUI-Filter-Functions für modellübergreifende Middleware.

## workbench_required_file_context_filter.py

Injiziert pro Workbench-Modell die drei Pflichtdateien `mainprompt.md`,
`fachwissen.md` und `Golden_Example.<ext>` als geschützten
Full-Context-Systemblock und hängt ihre OpenWebUI-File-IDs an den Request an.
Beispiele bleiben Knowledge/RAG und werden nicht pauschal injiziert.

## context_compressor_filter.py

Zählt vor jedem Modellaufruf die geschätzten Chat-Kontexttokens. Sobald der
konfigurierte Schwellwert erreicht wird, werden ältere Chatnachrichten in eine
kompakte System-Zusammenfassung überführt und die jüngsten Nachrichten
bevorzugt erhalten.

Zusätzlich entfernt der Filter problematische 0-Ausgabewerte wie
`max_tokens: 0` oder `num_predict: 0` aus dem Request. Wenn der Request danach
immer noch über dem sicheren Eingabebudget liegt, greift ein harter Context
Budget Guard: Systemnachrichten bleiben geschützt, die jüngste Nutzeranweisung
bleibt priorisiert, sehr große Einzelprompts oder Toolausgaben werden
struktur-aware mit Anfang, Ende, wichtigen Fehler-/Code-/JSON-/CSV-Zeilen und
einem sichtbaren Kürzungshinweis verdichtet. Das verhindert Providerfehler wie
`maximum context length is 131072 tokens ... requested 0 output tokens`.

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
