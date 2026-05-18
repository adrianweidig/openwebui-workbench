# Konfiguration

## Jupyter-Variablen

```text
OPENWEBUI_JUPYTER_URL=http://127.0.0.1:8888
OPENWEBUI_JUPYTER_TOKEN=REPLACE_WITH_LOCAL_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS=30
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR=/srv/openwebui-work
```

`OPENWEBUI_JUPYTER_TOKEN` darf nie in Modellantworten, Prompts, JSON-Profilen oder Logs ausgegeben werden.

## Modellparameter

Die Parameter stehen je Modell in `models/<modell-id>/model.json`. Analytische und technische Modelle verwenden niedrige Temperature-Werte, Schreib- und Kommunikationsmodelle moderate Werte.

## Capabilities

- Web Search: immer `false`
- Vision: `false`
- Image Generation: `false`
- File Upload/File Context: `true`, soweit OpenWebUI lokal verfuegbar
- Code Interpreter/Jupyter: je Problemfall `required`, `enabled`, `optional` oder `optional_disabled`
