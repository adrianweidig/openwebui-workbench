# Air-Gapped Jupyter Python Tool

## Zweck

`air_gapped_jupyter_python` führt kontrollierten Python-Code über einen vorhandenen lokalen oder intern erreichbaren Jupyter Server aus. Das Tool ist für OpenWebUI-Aufgabenmodelle gedacht, die offline Dateien analysieren, Tabellen verarbeiten, Code testen, Diagramme erzeugen oder Exporte vorbereiten müssen.

## Konfiguration

Für den Repo-Import werden die Werte zentral in `scripts/openwebui_workspace_config.yaml` gepflegt. Der API-Importer setzt sie danach als Tool-Valves für `air_gapped_jupyter_python`; die Jupyter-URL muss aus Sicht des OpenWebUI-Backends erreichbar sein, etwa `http://jupyter:8888` im Docker-Netz.

Relevante Valve-/Umgebungsnamen:

```text
OPENWEBUI_JUPYTER_URL
OPENWEBUI_JUPYTER_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR
```

Die Beispieldateien `.env.example`, `jupyter_config.example.json` und `scripts/openwebui_workspace_config.example.yaml` enthalten keine echten Geheimnisse. Für die produktive OpenWebUI-Integration ist die zentrale YAML der maßgebliche Pfad; direkte Tool-Valve- oder Env-Pflege ist nur ein Fallback, wenn der API-Importer nicht genutzt wird.

## Sicherheitsgrenzen

- Das Tool verbindet sich nur mit der konfigurierten Jupyter-Adresse.
- Python-Code wird vor der Ausführung statisch geprüft.
- Shell-Magics, direkte Shell-Kommandos, Netzwerkbibliotheken, Prozessstarts und gefährliche Dateioperationen werden blockiert.
- Dateipfade werden standardmäßig auf `OPENWEBUI_JUPYTER_ALLOWED_WORKDIR` eingeschränkt.
- Tokens werden in Fehlern und Ergebnissen maskiert.

Wichtig: Die tatsächliche Sandbox-Grenze wird vom Jupyter Server, dessen Kernel, Benutzerrechten, Dateisystem und Netzwerkumgebung bestimmt. Dieses Tool ist eine zusätzliche Schutzschicht, kein Ersatz für eine hart isolierte Jupyter-Umgebung.

## Lokaler Test

```text
python dist/tests/validate_artifacts.py
python dist/tests/test_jupyter_tool_static.py
```

Der statische Test benötigt keinen laufenden Jupyter Server. Eine echte Ausführungsprüfung erfordert lokale Werte in `scripts/openwebui_workspace_config.yaml` oder direkt gesetzte OpenWebUI-Tool-Valves für `OPENWEBUI_JUPYTER_URL` und optional `OPENWEBUI_JUPYTER_TOKEN`.
