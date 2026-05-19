# Validierungsbericht

Status: ERFOLGREICH

| Prüfung | Ergebnis | Detail |
|---|---:|---|
| JSON-Dateien syntaktisch valide | OK |  |
| Python-Dateien kompilierbar | OK |  |
| Keine echten Tokens/Passwörter/Secrets gefunden | OK |  |
| Jedes Index-Modell hat ein Modellverzeichnis | OK | [] |
| Jedes Modell ist einem Problemfall zugeordnet | OK |  |
| Keine Modellbeschreibung aktiviert Web Search | OK |  |
| Modell-JSON folgt dem OpenWebUI-Importschema | OK |  |
| Systemprompts verweisen auf mainprompt.md | OK |  |
| Mainprompts verweisen auf fachwissen.md | OK |  |
| Jedes Tool ist einem Modell oder Utility-Kontext zugeordnet | OK | tool_ids=['air_gapped_jupyter_python'], assigned=[] |
| Jupyter-Beispielkonfiguration enthält keine echten Zugangsdaten | OK |  |
| Sammelimport ist OpenWebUI-kompatibles JSON-Array | OK | bundled=25, expected=25 |
| Pflichtdokumentation vorhanden | OK |  |
| Abschlussberichte vorhanden | OK |  |
| Jupyter-Tool-Static-Test bestanden | OK | static security policy checks passed |

Nicht ausgeführt: echter Import in `openwebui:latest` und echte Jupyter-Codeausführung, weil dafür eine laufende Zielinstanz mit lokaler Konfiguration erforderlich ist.
