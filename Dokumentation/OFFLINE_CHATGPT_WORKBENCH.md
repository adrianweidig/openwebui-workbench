# Offline ChatGPT Workbench für OpenWebUI

## Ziel

Dieses Repository soll OpenWebUI so vorbereiten, dass Nutzer offline eine ChatGPT-ähnliche Arbeitsumgebung erhalten: Chat, Modelle, Skills, Tools, lokale Python-Ausführung, Datenanalyse, HTML-/PDF-Erzeugung, Präsentationen und Dateiübergabe.

## Komponenten

- `Modelle/`: direkt importierbare OpenWebUI-Modellprofile für die Problemfälle plus `Allgemein` als Fallbackmodell sowie Custom-GPT-nahe Modelle für `PromptForge`, `n8n Workflow Architect`, `OpenWebUI Model Builder` und den browserbasierten `Präsentationscreator`.
- `Tools/jupyter/`: kontrollierte Python-Ausführung über einen lokalen oder internen Jupyter-Server.
- `Tools/openwebui_ext/tools/`: zusätzliche direkt importierbare Tools.
- `Tools/openwebui_ext/skills/`: wiederverwendbare Arbeitsanweisungen für Modelle.
- `Artefakte/`: lokaler Bereich für erzeugte HTML-, PDF-, ZIP- und Datendateien.
- `Deployment/`: Vorlagen für Container-Volumes und Umgebungsvariablen.
- `F:\offline-ai-stack\openwebui-offline-addons`: lokaler Addon-Stack für OpenWebUI-Caches, Tiktoken, NLTK, Playwright/Chromium und zusätzliche Python-Pakete.

## Typischer Ablauf

1. Nutzer fragt im Chat nach Analyse, Dokument, Präsentation oder PDF.
2. Modell prüft OpenWebUI-Standardfunktionen, Builtins, Datei-/Knowledge-Kontext und passende Repo-Tools.
3. Für Berechnung, Tabellen, Diagramme oder Validierung nutzt das Modell das Jupyter-Tool.
4. Für fertige Dateien nutzt das Modell das Artefakt-Tool; für PDF-Konvertierung bevorzugt dieses den lokalen Playwright/Chromium-Cache aus den Offline-Addons.
5. Ergebnis wird als HTML, PDF oder ZIP im Artefaktvolume gespeichert.
6. OpenWebUI zeigt je nach Instanz Datei-Hinweise, Datei-Events oder gemountete Downloadpfade an.

## Präsentationen

Präsentationen werden als selbstständige 16:9-HTML-Dateien erzeugt. Das ist offline robust, versionierbar und kann bei lokal vorhandenem PDF-Konverter in PDF gewandelt werden. Externe CDNs, Fonts und Remote-Bilder sind nicht erlaubt.

## PDF-Dokumente

Der bevorzugte Weg ist: erst druckfähiges HTML erzeugen, dann lokal in PDF konvertieren. Das vermeidet proprietäre Office-Abhängigkeiten und funktioniert in Air-Gap-Umgebungen reproduzierbar.

Wenn `PLAYWRIGHT_BROWSERS_PATH=/app/backend/data/cache/ms-playwright` aus dem Offline-Addon-Stack gesetzt ist, nutzt `offline_artifact_workbench` Playwright/Chromium zuerst. Falls Playwright fehlt oder nicht starten kann, fällt es auf `weasyprint` und danach auf ein explizit erlaubtes `wkhtmltopdf` zurück.

## Agentische Features

Agentisches Verhalten entsteht durch Modellprofile, Skills und gezielte Tools:

- Skills definieren Arbeitsweise, Qualitätsregeln und Sicherheitsgrenzen.
- Tools liefern begrenzte Fähigkeiten wie Jupyter-Ausführung, Artefakterzeugung und Datenvalidierung.
- OpenWebUI-Builtins wie Code Interpreter, Datei-/Knowledge-Kontext, Citations und Statusmeldungen werden bevorzugt genutzt, wenn sie verfügbar sind.
- Modelle sollen maximal drei Rückfragen stellen und danach mit klaren Annahmen weiterarbeiten.
- Tool-Ergebnisse werden geprüft, nicht blind übernommen.

## Grenzen

Die tatsächliche Sandbox hängt von OpenWebUI, dem Jupyter-Server, Containerrechten und Volumes ab. Dieses Repository liefert sichere Defaults, ersetzt aber keine harte Laufzeitisolation.
