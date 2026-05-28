# OpenWebUI Import Guide

## Tools importieren

1. In OpenWebUI mit einem vertrauenswürdigen Administrator anmelden.
2. `Workspace > Tools` öffnen.
3. `Import` wählen.
4. `Tools/dist/openwebui-tools-offline-import.json` auswählen.
5. Optional mit Netzwerk-/Rich-UI-/lokalen Crawl-Tools: `Tools/dist/openwebui-tools-import.json` auswählen.
6. Speichern und Tools nur für passende Modelle aktivieren.
7. Für den vollständigen Repo-Import bevorzugt `scripts/openwebui_workspace_config.yaml` nutzen; dort liegen OpenWebUI-Adresse, Admin-Token, Backend-Pfade, `tool_valves` und `function_valves` zentral.

Fallback: Einzelne `.py`-Dateien aus `Tools/openwebui_ext/tools/*.py` oder `Tools/jupyter/jupyter_tool.py` über `Create Tool` einfügen.

Der reproduzierbare API-Pfad ist:

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --config scripts/openwebui_workspace_config.yaml
```

## Skills importieren

1. `Workspace > Skills` öffnen.
2. `Import` wählen.
3. Eine `.md`-Datei aus `Tools/openwebui_ext/skills/` auswählen.
4. Name und Beschreibung aus dem YAML-Frontmatter prüfen.
5. Skill bei Bedarf direkt per `$skill-name` nutzen oder im Modell binden.

## Aktivierung in Modellen

- Tools nur Modellen zuordnen, deren Aufgabe den Tool-Zweck benötigt.
- Skills können modellgebunden werden, wenn sie regelmäßig gebraucht werden.
- Für Tools Native Function Calling bevorzugen und Status-/Citation-Events nutzen.
- Der Standard-Workflow ist der API-Import mit zentraler YAML, weil dabei Tool-Valves, Function-/Filter-Valves, Skills, modellbezogene Knowledge inklusive `mainprompt.md`, `fachwissen.md`, modellseitig definierter Beispielergebnis-Datei und `beispiele/` sowie Modellprofile in der richtigen Reihenfolge gesetzt werden. Der manuelle Offline-Fallback ist: zuerst `Tools/dist/openwebui-tools-offline-import.json` importieren, danach `Tools/dist/openwebui-functions-import.json` und Skills importieren, anschließend `Modelle/dist/openwebui-models-import.json` als Sammelimport laden.
- Öffentliche Netzwerktools wie `safe_http_fetcher.py` und `github_repo_inspector.py` sowie optionale Rich-UI-/Crawl-Tools wie `openui_generative_ui.py` und `web_search_and_crawl.py` sind nicht Teil des Offline-Standardimports und werden keinem Modellprofil standardmäßig zugewiesen.

## Rechtevergabe

- Tool-Import entspricht serverseitiger Python-Ausführung und gehört nur in Admin-Hände.
- Skills sind Textanweisungen, können aber sensible Arbeitsweisen enthalten; Zugriff bewusst setzen.

## Troubleshooting

- Importfehler: `python scripts/validate_openwebui_extensions.py` ausführen; zusätzlich Python-Syntax mit `python -m py_compile Tools/openwebui_ext/tools/<tool>.py` prüfen.
- `401 Unauthorized` vor dem Import: zuerst `python Tools/import_openwebui_workspace.py --auth-check --config scripts/openwebui_workspace_config.yaml` ausführen. Danach prüfen, ob `openwebui.base_url` auf die WebUI-Root zeigt, z. B. `http://127.0.0.1:3000`, nicht auf `/api` oder `/api/v1`. Der Importer normalisiert diese Suffixe, aber die Root-URL ist die erwartete Konfiguration. Der Token muss ein API-Key oder JWT eines Admin-Users aus OpenWebUI sein, nicht `WEBUI_SECRET_KEY`, ein Docker-Secret oder ein Jupyter-Token.
- Wenn `/api/version` erreichbar ist, aber `/api/models` 401 liefert, ist die URL korrekt und der Fehler liegt bei Authentifizierung oder Endpoint-Rechten: API Keys in OpenWebUI aktivieren, API-Key im Admin-Account neu erzeugen, Endpoint-Restrictions für `/api/models` und die genutzten `/api/v1/...`-Routen freigeben. Nur bei Gateway/SSO/Proxy-Problemen `openwebui.auth_header: "x-api-key"` und `openwebui.auth_scheme: ""` setzen beziehungsweise an `CUSTOM_API_KEY_HEADER` der OpenWebUI-Instanz anpassen.
- Meldungen wie `Tool nicht importierbar` im Generator sollten mit aktuellem Stand nicht mehr durch lokal fehlende Python-Pakete entstehen. `configure_openwebui_tool_models.py` prüft Tools und Filter strukturell per AST und braucht auf der Import-Maschine keine optionalen Tool-Abhängigkeiten wie `fastapi`, `pydantic`, `requests`, `aiohttp`, `tiktoken`, `starlette` oder `playwright`, solange nur Bundles gebaut oder ein Dry-Run ausgeführt wird.
- Wenn OpenWebUI selbst beim echten Import ein Tool ablehnt, liegt der Fehler im Zielcontainer. Dann den Tool-Namen aus der OpenWebUI-Fehlermeldung nehmen und dort prüfen, ob die Zielinstanz die benötigten Runtime-Pakete aus `openwebui-offline-addons` beziehungsweise dem OpenWebUI-Backend-Pythonpfad laden kann.
- Reimports dürfen bei unveränderten Modell-Knowledge-Dateien nicht erneut alle Dateien einbetten. Der Importer schreibt einen `Import-Fingerprint` in die Knowledge-Beschreibung, überspringt unveränderte Sammlungen und meldet sie als `model_knowledge_collections: skipped`. Wenn ein Reimport trotzdem sehr lange läuft, zuerst hängende alte Importprozesse und die Lockdatei `Artefakte/temp/openwebui_workspace_import.lock` prüfen, danach OpenWebUI-Logs auf erneute Datei-Uploads oder Embedding-Läufe kontrollieren.
- Tool wird nicht aufgerufen: Modell-Tool-Zuordnung und Function-Calling-Einstellung prüfen.
- Skill nicht sichtbar: Skill aktivieren und Zugriffsrechte prüfen.
- Unerwartete Toolfehler: `scripts/openwebui_workspace_config.yaml`, importierte Tool-/Function-Valves, Netzwerkzugriff und Größenlimits prüfen.
