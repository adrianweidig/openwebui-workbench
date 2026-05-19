# Validierung

## Automatische lokale Prüfung

```text
python dist/tests/validate_artifacts.py
```

Die Prüfung validiert JSON, Python-Syntax, Secret-Hinweise, Modellzuordnung, Web-Search-Deaktivierung, Prompt-Verweise, Tool-Zuordnung, Jupyter-Beispielkonfiguration, das OpenWebUI-Importschema und Berichtsvollständigkeit.

## Nicht automatisch prüfbar

- Echter Import in `openwebui:latest`
- Echte Ausführung gegen einen Jupyter Server
- Fachliche Qualität mit realen Unternehmensdaten

Diese Punkte müssen lokal mit der Zielinstanz und Testdaten geprüft werden.
