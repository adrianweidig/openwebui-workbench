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
- `openwebui_ext/tools/ask_user.py`: interaktive Rückfragen über OpenWebUI-Pop-ups stellen.
- `openwebui_ext/tools/offline_artifact_workbench.py`: HTML-, Präsentations-, PDF- und ZIP-Artefakte im erlaubten Artefaktverzeichnis erzeugen.
- `openwebui_ext/tools/json_csv_text_validator.py`: Daten vor Artefakterzeugung validieren.
- `openwebui_ext/tools/inline_visuals_toolkit_v3.py`: offline SVG-Charts, HTML-Dashboards und Mermaid-Blöcke erzeugen.
- `openwebui_ext/tools/parallel_task_planner.py`: komplexe Arbeit in sichere Parallelwellen und Subagent-Aufgaben zerlegen.
- `openwebui_ext/tools/parallel_tools.py`: bereits aktivierte OpenWebUI-Tools parallel ausführen.
- `openwebui_ext/tools/sub_agent.py`: direkte OpenWebUI-Subagenten mit Air-Gap-sicheren Builtin-Defaults ausführen.
- `openwebui_ext/tools/llm_council.py`: lokale Modellratsantworten über die OpenWebUI-API erzeugen.
- `openwebui_ext/tools/subagent_orchestrator.py`: Subagent-Roster, delegierbare Arbeitspakete und Ergebnis-Merges für agentische Workflows erzeugen.
- `openwebui_ext/tools/tool_skill_overlay_planner.py`: Tools und Skills redundant auf Modellprofile verteilen.
- `openwebui_ext/tools/comfyui_workflow_inspector.py`: ComfyUI-Workflows offline prüfen und Setup-Checklisten erzeugen.
- `openwebui_ext/tools/mediawiki_legacy_crawler.py`: interne alte MediaWiki-Server per API und Legacy-Login crawlen.
- `openwebui_ext/filters/auto_tool_selector.py`: passende lokale Tools und optional konfigurierte MCP-Server vor dem Modellaufruf aktivieren.
- `openwebui_ext/filters/markdown_normalizer.py`: Markdown-, Tabellen-, Mermaid- und Codeblock-Ausgaben nach dem Modellaufruf normalisieren.
- `openwebui_ext/filters/context_compressor_filter.py`: lange Chats vor dem Modellaufruf lokal komprimieren.

Optionale, nicht im Offline-Standard aktivierte Drittanbieter-Tools:

- `openwebui_ext/tools/openui_generative_ui.py`: Rich UI nur mit lokal bereitgestelltem OpenUI-Browser-Bundle.
- `openwebui_ext/tools/web_search_and_crawl.py`: lokale/self-hosted SearXNG-/Crawl4AI-Suche mit Public-Network-Guard.
- `openwebui_ext/tools/safe_http_fetcher.py` und `openwebui_ext/tools/github_repo_inspector.py`: bewusste Netzwerkprofile, nicht Air-Gap-Default.

## API-Import

Der bevorzugte Weg ist der Generator mit anschließendem API-Import. Er schreibt zuerst die Registries, Modellprofile, ZIPs und Prüfübersichten und ruft danach den Importer auf:

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

Die Konfigurationsdatei trennt die extern erreichbare OpenWebUI-Adresse von der Docker-internen Jupyter-Adresse. `openwebui.base_url` muss von der Maschine erreichbar sein, auf der das Python-Skript läuft; `jupyter.url` muss aus Sicht des OpenWebUI-Backends erreichbar sein, z. B. `http://jupyter:8888`.

`import_openwebui_workspace.py` bleibt als Fallback direkt ausführbar und nutzt die erzeugten Registries. Es importiert Tools, Functions/Filter und Skills, setzt Jupyter-/Artefakt-Valves, lädt `mainprompt.md` und `fachwissen.md` je Modell als Knowledge hoch und importiert anschließend die Modellprofile inklusive eingebetteter Icons. Vor einem echten Import kann `python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.yaml` die lokalen Payloads prüfen.
Es wird auch in `dist/openwebui-tools-skills-offline.zip` mit ausgeliefert.

## Codex-Testprovider

`codex_openai_bridge.py` ist nur für lokale Tests gedacht. Das Skript speichert keine OpenAI- oder Codex-Secrets, sondern nutzt die bereits lokal authentifizierte Codex-CLI. Es stellt bevorzugt `/v1/responses` bereit und bietet `/v1/chat/completions` nur als Kompatibilitätsfallback an. In einer WSL-/Docker-Umgebung, in der OpenWebUI im Container läuft und Codex unter Windows angemeldet ist, kann der Bridge-Server so gestartet werden:

```bash
cd /mnt/e/OpenWebUI
python3 Tools/codex_openai_bridge.py --host 0.0.0.0 --port 4010 --windows-codex
```

Danach in OpenWebUI einen OpenAI-kompatiblen Provider auf `http://172.23.0.1:4010/v1` konfigurieren und `api_type` auf `responses` setzen. Der Bridge-Provider stellt `coder`, `codex`, `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex` und `gpt-5.3-codex-spark` bereit; `coder` und `codex` werden intern auf `gpt-5.5` abgebildet. Die Gateway-IP kann je Docker-Netz abweichen und muss bei Bedarf mit `docker network inspect <netz>` geprüft werden.
