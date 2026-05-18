# Validierung

## Automatische lokale Pruefung

```text
python dist/tests/validate_artifacts.py
```

Die Pruefung validiert JSON, Python-Syntax, Secret-Hinweise, Modellzuordnung, Web-Search-Deaktivierung, Prompt-Verweise, Tool-Zuordnung, Jupyter-Beispielkonfiguration und Berichtsvollstaendigkeit.

## Nicht automatisch pruefbar

- Echter Import in `openwebui:latest`
- Echte Ausfuehrung gegen einen Jupyter Server
- Fachliche Qualitaet mit realen Unternehmensdaten

Diese Punkte muessen lokal mit der Zielinstanz und Testdaten geprueft werden.
