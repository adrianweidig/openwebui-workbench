# Air-Gapped Jupyter Python Tool

## Zweck

`air_gapped_jupyter_python` fuehrt kontrollierten Python-Code ueber einen vorhandenen lokalen oder intern erreichbaren Jupyter Server aus. Das Tool ist fuer OpenWebUI-Aufgabenmodelle gedacht, die offline Dateien analysieren, Tabellen verarbeiten, Code testen, Diagramme erzeugen oder Exporte vorbereiten muessen.

## Konfiguration

Bevorzugte Umgebungsvariablen:

```text
OPENWEBUI_JUPYTER_URL
OPENWEBUI_JUPYTER_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR
```

Alternativ koennen dieselben Werte in OpenWebUI als Tool-Valves gepflegt werden. Die Beispieldateien `.env.example` und `jupyter_config.example.json` enthalten keine echten Geheimnisse.

## Sicherheitsgrenzen

- Das Tool verbindet sich nur mit der konfigurierten Jupyter-Adresse.
- Python-Code wird vor der Ausfuehrung statisch geprueft.
- Shell-Magics, direkte Shell-Kommandos, Netzwerkbibliotheken, Prozessstarts und gefaehrliche Dateioperationen werden blockiert.
- Dateipfade werden standardmaessig auf `OPENWEBUI_JUPYTER_ALLOWED_WORKDIR` eingeschraenkt.
- Tokens werden in Fehlern und Ergebnissen maskiert.

Wichtig: Die tatsaechliche Sandbox-Grenze wird vom Jupyter Server, dessen Kernel, Benutzerrechten, Dateisystem und Netzwerkumgebung bestimmt. Dieses Tool ist eine zusaetzliche Schutzschicht, kein Ersatz fuer eine hart isolierte Jupyter-Umgebung.

## Lokaler Test

```text
python dist/tests/validate_artifacts.py
python dist/tests/test_jupyter_tool_static.py
```

Der statische Test benoetigt keinen laufenden Jupyter Server. Eine echte Ausfuehrungspruefung erfordert lokale Werte fuer `OPENWEBUI_JUPYTER_URL` und optional `OPENWEBUI_JUPYTER_TOKEN`.
