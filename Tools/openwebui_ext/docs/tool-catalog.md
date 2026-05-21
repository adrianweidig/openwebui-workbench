# Tool Catalog

## safe_http_fetcher.py

Optionales Netzwerktool für explizit erlaubte HTTP-GET/HEAD-Abfragen mit Timeout, Größenlimit, Redirect-Limit, Header-Redaktion und SSRF-Schutz. Nicht Teil des Offline-Standardimports und keinem Modellprofil standardmäßig zugewiesen.

## openapi_schema_inspector.py

Analysiert eingefügtes OpenAPI-JSON lokal. Führt keine API-Aufrufe aus und verarbeitet keine Tokens.

## json_csv_text_validator.py

Validiert JSON, CSV und Text. Markiert sensible Feldnamen und redigiert offensichtliche Secret-Werte.

## github_repo_inspector.py

Optionales Netzwerktool für GitHub-Repository-Metadaten read-only über die GitHub-API. Optionaler Token kommt aus Valves oder OAuth und wird nie ausgegeben. Nicht Teil des Offline-Standardimports und keinem Modellprofil standardmäßig zugewiesen.

## ask_user.py

Drittanbieter-Tool für interaktive Rückfragen über OpenWebUI-Pop-up-Events. Es ruft keine externen Dienste auf und ist im Offline-Standardimport enthalten. Die Air-Gap-Variante nutzt `asyncio.sleep`, damit der Event-Loop nicht durch blockierendes Warten angehalten wird.

## llm_council.py

Drittanbieter-Tool für lokale Multi-Modell-Abstimmungen über die OpenWebUI-API. Die Air-Gap-Variante nutzt standardmäßig nur lokale Modell-IDs (`coder`) und deaktiviert öffentliche OpenAI-/OpenRouter-Fallbacks vollständig.

## parallel_tools.py

Drittanbieter-Tool zum parallelen Ausführen bereits in OpenWebUI aktivierter Tools. Es ruft keine öffentlichen Dienste direkt auf; die tatsächliche Reichweite wird durch die im Chat aktivierten Tools und die OpenWebUI-Instanz begrenzt.

## sub_agent.py

Drittanbieter-Tool für isolierte OpenWebUI-Subagenten. Die Air-Gap-Variante deaktiviert Web-, Image-, Automation- und Calendar-Builtin-Kategorien standardmäßig; lokale Knowledge-, Memory-, Notes-, Chat- und Tool-Funktionen bleiben nutzbar, sofern OpenWebUI sie bereitstellt.

## visuals_toolkit_v4.py

Drittanbieter-Visualisierungstool mit Tabellen, Charts, Dashboards und Diagrammen. Die Air-Gap-Variante lädt Plotly nicht aus einem CDN und fällt standardmäßig auf Text-/ASCII-Ausgaben zurück; für vollständig offline-interaktive Visuals bleibt `inline_visuals_toolkit_v3.py` der robuste Default.

## openui_generative_ui.py

Optionales Drittanbieter-Rich-UI-Tool. Nicht Teil des Offline-Standardimports, weil das benötigte OpenUI-Browser-Bundle lokal als statische OpenWebUI-Datei bereitgestellt werden muss. Der Default zeigt auf `/static/openui/dist` statt auf ein öffentliches CDN.

## web_search_and_crawl.py

Optionales Drittanbieter-Such- und Crawl-Tool für lokale/self-hosted SearXNG- und Crawl4AI-Setups. Nicht Teil des Offline-Standardimports. Öffentliche Netzwerke sind per `ALLOW_PUBLIC_NETWORK=false` blockiert; erlaubt sind nur lokale/private/allowlistete Hosts.

## docker_compose_triage.py

Analysiert eingefügte Compose-Dateien und Fehlertexte. Startet keine Container und führt keine Shell-Befehle aus.

## repo_tree_analyzer.py

Analysiert vom Nutzer eingefügte Dateibäume. Öffnet keine lokalen Pfade und liest keine Dateien.

## markdown_skill_builder.py

Erzeugt sichere importierbare Skill-Markdown-Dateien aus Nutzerzielen und lehnt missbräuchliche Zielsetzungen ab.

## mediawiki_legacy_crawler.py

Crawlt interne MediaWiki-Instanzen über `api.php`. Das Tool unterstützt moderne Login-Token und den alten `NeedToken`-Loginflow sehr alter MediaWiki-Versionen. Zugangsdaten gehören in Valves (`base_url`, `username`, `password`) und werden in Ausgaben redigiert. Es schreibt keine Dateien und ruft nur die konfigurierte Wiki-API auf.

## offline_artifact_workbench.py

Erzeugt offline HTML-Dokumente, 16:9-HTML-Präsentationen, optionale PDFs und ZIP-Pakete unterhalb des konfigurierten Artefaktverzeichnisses. PDF-Konvertierung nutzt bevorzugt lokales Playwright/Chromium aus `F:\offline-ai-stack\openwebui-offline-addons`, danach lokal vorhandenes `weasyprint` oder optional `wkhtmltopdf`; fehlt ein Konverter, bleibt das HTML-Artefakt nutzbar und der Fehler nennt die lokal bereitzustellende Abhängigkeit. Für Präsentationen dient `Modelle/einzelmodelle/präsentationserstellung/beispiele/praesentation-premium-demo.html` als Offline-Referenz für Navigation, Hover-Toolbar, Dark Mode und Effekte.

## inline_visuals_toolkit_v3.py

Erzeugt offline nutzbare SVG-Charts, HTML-Dashboards, Mermaid-Blöcke und Visual-Briefs. Das Tool lädt keine Skripte, Bilder oder Fonts aus dem Netz und eignet sich als robuster Fallback zu ComfyUI- oder CDN-gestützten Visual-Tools.

## parallel_task_planner.py

Zerlegt komplexe Aufgaben in dependency-sichere Parallelwellen, Subagent-Arbeitspakete und konsolidierte Ergebnisberichte. Das Tool führt selbst keine Subagenten oder externen Tools aus; es verhindert damit Race Conditions durch Planung statt verdeckter Ausführung.

## subagent_orchestrator.py

Erzeugt OpenWebUI-fähige Subagent-Roster, Delegationsprompts und Ergebnis-Merges für lokale/offline Arbeitspakete. Es führt keine Modelle selbst aus, sondern macht agentische Arbeitsschritte reproduzierbar, damit Nutzer Subagent-Jobs mit den importierten Modellprofilen und Offline-Tools ausführen können.

## tool_skill_overlay_planner.py

Plant modellbezogene Tool-/Skill-Overlays mit Redundanz, Use-Case-Abdeckung und Fallback-Stacks. Nützlich, um gleiche Fähigkeiten bewusst mehrfach abzudecken, ohne riskante Tools global zu aktivieren.

## comfyui_workflow_inspector.py

Analysiert ComfyUI-Workflow-JSON lokal, listet Knotentypen, Modellreferenzen, Ein-/Ausgabe-Kandidaten und Setup-Prüfpunkte. Es verbindet sich nicht mit ComfyUI und ist daher für Air-Gap-Vorprüfung geeignet.
