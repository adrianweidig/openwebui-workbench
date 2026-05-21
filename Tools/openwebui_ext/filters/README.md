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

## markdown_normalizer.py

Normalisiert Assistant-Ausgaben nach der Modellantwort: Codeblöcke, LaTeX,
Mermaid-Syntax, Tabellen, Überschriften und ausgewählte XML-Artefakte. Der
Filter arbeitet lokal ohne Netzwerkzugriff und überspringt HTML-Inhalte, damit
Rich-UI-Toolausgaben nicht nachträglich umgeschrieben werden.

Der öffentliche Export deklarierte `type: action`, enthält aber eine
`Filter`-Klasse mit `outlet`-Hook. Die Generatorlogik importiert ihn daher
korrekt als OpenWebUI-Filter.
