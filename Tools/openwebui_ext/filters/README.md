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
