# OpenWebUI Filters

Importierbare OpenWebUI-Filter-Functions fuer modelluebergreifende Middleware.

## context_compressor_filter.py

Zaehlt vor jedem Modellaufruf die geschaetzten Chat-Kontexttokens. Sobald der
konfigurierte Schwellwert erreicht wird, werden aeltere Chatnachrichten in eine
kompakte System-Zusammenfassung ueberfuehrt und die juengsten Nachrichten
unveraendert behalten.

Der Filter ist als togglebarer OpenWebUI-Filter gebaut, wird aber durch die
Generatorlogik in `meta.defaultFilterIds` fuer alle Chat-Modelle standardmaessig
aktiviert.
