# Tools

Dieser Ordner enthält die operativ relevanten Tool-Artefakte.

## Unterstruktur

- `jupyter/`: Offline-Jupyter-Tool für OpenWebUI
- `openwebui_ext/`: zusätzliche direkt importierbare OpenWebUI-Tools, Skills, Doku und Tests
- `dist/`: portables Offline-Paket für Tools und Skills
- `index.json`: Tool-Index für die lokale Übersicht
- `import_openwebui_workspace.py`: API-Importer für Tools, Functions/Filter, Skills, Knowledge und Modelle
- `codex_openai_bridge.py`: lokaler Test-Provider, der Codex CLI als minimale OpenAI-kompatible Responses-/Chat-API bereitstellt

## Nutzung

Die produktive Tool-Datei für OpenWebUI liegt unter `jupyter/jupyter_tool.py`.

Weitere produktive Tools liegen unter `openwebui_ext/tools/`. Für den Offline-ChatGPT-ähnlichen Betrieb sind besonders wichtig:

- `jupyter/jupyter_tool.py`: kontrollierte Python-Ausführung über den lokalen Jupyter-Server.
- `openwebui_ext/tools/offline_artifact_workbench.py`: HTML-, Präsentations-, PDF- und ZIP-Artefakte im erlaubten Artefaktverzeichnis erzeugen.
- `openwebui_ext/tools/json_csv_text_validator.py`: Daten vor Artefakterzeugung validieren.
- `openwebui_ext/tools/inline_visuals_toolkit_v3.py`: offline SVG-Charts, HTML-Dashboards und Mermaid-Blöcke erzeugen.
- `openwebui_ext/tools/parallel_task_planner.py`: komplexe Arbeit in sichere Parallelwellen und Subagent-Aufgaben zerlegen.
- `openwebui_ext/tools/subagent_orchestrator.py`: Subagent-Roster, delegierbare Arbeitspakete und Ergebnis-Merges für agentische Workflows erzeugen.
- `openwebui_ext/tools/tool_skill_overlay_planner.py`: Tools und Skills redundant auf Modellprofile verteilen.
- `openwebui_ext/tools/comfyui_workflow_inspector.py`: ComfyUI-Workflows offline prüfen und Setup-Checklisten erzeugen.
- `openwebui_ext/tools/mediawiki_legacy_crawler.py`: interne alte MediaWiki-Server per API und Legacy-Login crawlen.

## API-Import

`import_openwebui_workspace.py` importiert den Workspace in eine laufende OpenWebUI-Instanz. Es reicht, einen Admin-API-Token per Umgebungsvariable oder im Skript-Platzhalter zu setzen:

```powershell
$env:OPENWEBUI_ADMIN_TOKEN="YOUR_OPEN_WEBUI_API_KEY"
python Tools/import_openwebui_workspace.py --base-url http://localhost:3000
```

Das Skript nutzt die erzeugten Registries, importiert Tools, Functions/Filter und Skills, lädt `mainprompt.md` und `fachwissen.md` je Modell als Knowledge hoch und importiert anschließend die Modellprofile inklusive eingebetteter Icons.
Es wird auch in `dist/openwebui-tools-skills-offline.zip` mit ausgeliefert.

## Codex-Testprovider

`codex_openai_bridge.py` ist nur für lokale Tests gedacht. Das Skript speichert keine OpenAI- oder Codex-Secrets, sondern nutzt die bereits lokal authentifizierte Codex-CLI. Es stellt bevorzugt `/v1/responses` bereit und bietet `/v1/chat/completions` nur als Kompatibilitätsfallback an. In einer WSL-/Docker-Umgebung, in der OpenWebUI im Container läuft und Codex unter Windows angemeldet ist, kann der Bridge-Server so gestartet werden:

```bash
cd /mnt/e/OpenWebUI
python3 Tools/codex_openai_bridge.py --host 0.0.0.0 --port 4010 --windows-codex
```

Danach in OpenWebUI einen OpenAI-kompatiblen Provider auf `http://172.23.0.1:4010/v1` konfigurieren und `api_type` auf `responses` setzen. Der Bridge-Provider stellt `coder`, `codex`, `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex` und `gpt-5.3-codex-spark` bereit; `coder` und `codex` werden intern auf `gpt-5.5` abgebildet. Die Gateway-IP kann je Docker-Netz abweichen und muss bei Bedarf mit `docker network inspect <netz>` geprüft werden.
