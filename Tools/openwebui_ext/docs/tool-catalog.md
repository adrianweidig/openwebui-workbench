# Tool Catalog

## safe_http_fetcher.py

Sichere öffentliche HTTP-GET/HEAD-Abfragen mit Timeout, Größenlimit, Redirect-Limit, Header-Redaktion und SSRF-Schutz. Nicht für interne Netzwerkdiagnose gedacht.

## internet_research_tool.py

Öffentliche Websuche, Recherchebriefs und Seitenabrufe mit Timeout, Größenlimit, Citation-Events und SSRF-Schutz. Das Tool nutzt einen konfigurierbaren öffentlichen HTML-Suchendpunkt und blockiert private, lokale oder reservierte Netzwerkziele standardmäßig.

## openapi_schema_inspector.py

Analysiert eingefügtes OpenAPI-JSON lokal. Führt keine API-Aufrufe aus und verarbeitet keine Tokens.

## json_csv_text_validator.py

Validiert JSON, CSV und Text. Markiert sensible Feldnamen und redigiert offensichtliche Secret-Werte.

## github_repo_inspector.py

Liest GitHub-Repository-Metadaten read-only über die GitHub-API. Optionaler Token kommt aus Valves oder OAuth und wird nie ausgegeben.

## docker_compose_triage.py

Analysiert eingefügte Compose-Dateien und Fehlertexte. Startet keine Container und führt keine Shell-Befehle aus.

## repo_tree_analyzer.py

Analysiert vom Nutzer eingefügte Dateibäume. Öffnet keine lokalen Pfade und liest keine Dateien.

## markdown_skill_builder.py

Erzeugt sichere importierbare Skill-Markdown-Dateien aus Nutzerzielen und lehnt missbräuchliche Zielsetzungen ab.

## mediawiki_legacy_crawler.py

Crawlt interne MediaWiki-Instanzen über `api.php`. Das Tool unterstützt moderne Login-Token und den alten `NeedToken`-Loginflow sehr alter MediaWiki-Versionen. Zugangsdaten gehören in Valves (`base_url`, `username`, `password`) und werden in Ausgaben redigiert. Es schreibt keine Dateien und ruft nur die konfigurierte Wiki-API auf.

## offline_artifact_workbench.py

Erzeugt offline HTML-Dokumente, 16:9-HTML-Präsentationen, optionale PDFs und ZIP-Pakete unterhalb des konfigurierten Artefaktverzeichnisses. PDF-Konvertierung nutzt lokal vorhandenes `weasyprint` oder optional `wkhtmltopdf`; fehlt ein Konverter, bleibt das HTML-Artefakt nutzbar und der Fehler nennt die lokal bereitzustellende Abhängigkeit.

## inline_visuals_toolkit_v3.py

Erzeugt offline nutzbare SVG-Charts, HTML-Dashboards, Mermaid-Blöcke und Visual-Briefs. Das Tool lädt keine Skripte, Bilder oder Fonts aus dem Netz und eignet sich als robuster Fallback zu ComfyUI- oder CDN-gestützten Visual-Tools.

## parallel_task_planner.py

Zerlegt komplexe Aufgaben in dependency-sichere Parallelwellen, Subagent-Arbeitspakete und konsolidierte Ergebnisberichte. Das Tool führt selbst keine Subagenten oder externen Tools aus; es verhindert damit Race Conditions durch Planung statt verdeckter Ausführung.

## subagent_orchestrator.py

Erzeugt OpenWebUI-fähige Subagent-Roster, Delegationsprompts und Ergebnis-Merges. Es führt keine Modelle selbst aus, sondern macht agentische Arbeitsschritte reproduzierbar, damit Nutzer Subagent-Jobs mit den importierten Modellprofilen und Tools ausführen können.

## tool_skill_overlay_planner.py

Plant modellbezogene Tool-/Skill-Overlays mit Redundanz, Use-Case-Abdeckung und Fallback-Stacks. Nützlich, um gleiche Fähigkeiten bewusst mehrfach abzudecken, ohne riskante Tools global zu aktivieren.

## comfyui_workflow_inspector.py

Analysiert ComfyUI-Workflow-JSON lokal, listet Knotentypen, Modellreferenzen, Ein-/Ausgabe-Kandidaten und Setup-Prüfpunkte. Es verbindet sich nicht mit ComfyUI und ist daher für Air-Gap-Vorprüfung geeignet.
