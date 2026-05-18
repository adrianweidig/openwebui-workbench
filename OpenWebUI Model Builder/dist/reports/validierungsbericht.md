# Validierungsbericht

Status: ERFOLGREICH

| Pruefung | Ergebnis | Detail |
|---|---:|---|
| JSON-Dateien syntaktisch valide | OK |  |
| Python-Dateien kompilierbar | OK |  |
| Keine echten Tokens/Passwoerter/Secrets gefunden | OK |  |
| Jedes Index-Modell hat ein Modellverzeichnis | OK | [] |
| Jedes Modell ist einem Problemfall zugeordnet | OK |  |
| Keine Modellbeschreibung aktiviert Web Search | OK |  |
| Systemprompts verweisen auf mainprompt.md | OK |  |
| Mainprompts verweisen auf fachwissen.md | OK |  |
| Jedes Tool ist einem Modell oder Utility-Kontext zugeordnet | OK | tool_ids=['air_gapped_jupyter_python'], assigned=['air_gapped_jupyter_python'] |
| Jupyter-Beispielkonfiguration enthaelt keine echten Zugangsdaten | OK |  |
| Pflichtdokumentation vorhanden | OK |  |
| Abschlussberichte vorhanden | OK |  |
| Jupyter-Tool-Static-Test bestanden | OK | static security policy checks passed |

Nicht ausgefuehrt: echter Import in `openwebui:latest` und echte Jupyter-Codeausfuehrung, weil dafuer eine laufende Zielinstanz mit lokaler Konfiguration erforderlich ist.
