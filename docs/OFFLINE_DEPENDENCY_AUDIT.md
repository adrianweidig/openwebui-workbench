# Offline-Dependency-Audit

Stand: 2026-06-01

Dieses Audit klassifiziert Netzwerkindikatoren im Repository. Ziel ist nicht, jede Dokumentations-URL zu entfernen, sondern echte Runtime-Netzwerkabhängigkeiten vom Offline-Default zu trennen.

## Kategorien

| Kategorie | Bedeutung |
|---|---|
| 0 | lokale oder Intra-Stack-Kommunikation, für Air-Gap-Default zulässig |
| 1 | reine Dokumentation, Quellenangabe oder Beispieltext |
| 2 | README-Badge oder Bildreferenz |
| 3 | optionales Netzwerktool, nicht Offline-Default |
| 4 | Runtime-Abhängigkeit, für Offline-Default unzulässig |
| 5 | Container-/Release-Abhängigkeit, als Offline-Image-Artefakt zu spiegeln |

## Befunde

| Datei | Fundstelle | Kategorie | Risiko | Offline-Status | Maßnahme |
|---|---:|---:|---|---|---|
| `README.md`, `README.de.md` | GitHub- und shields.io-Badges | 2 | Badges laden nur in der GitHub-/Webansicht nach | kein Runtime-Effekt | Lokale Hero- und Screenshot-Bilder bleiben versioniert; externe Badges sind Komfortanzeige |
| `Tools/import_openwebui_workspace.py` | `urllib`, `OPENWEBUI_BASE_URL` | 3 | API-Import spricht bewusst eine Zielinstanz an | nicht Teil des Offline-Modellbetriebs | Import nur mit lokaler Konfiguration und Admin-Token ausführen |
| `Tools/openwebui_ext/tools/llm_council.py` | `requests`, lokale OpenWebUI-API | 0 | Modellrat braucht eine erreichbare lokale OpenWebUI-API und lokale Modell-IDs | Offline-Default mit lokaler API | Öffentliche Provider-Fallbacks bleiben im Air-Gap-Build deaktiviert; `OPENWEBUI_BASE_URL` auf lokale oder Intra-Stack-API setzen |
| `Tools/openwebui_ext/tools/safe_http_fetcher.py` | `urllib.request` | 3 | öffentliches HTTP-Fetching möglich | nicht Offline-Default | Nicht im Offline-Import und nicht im `internetwissen`-Profil verwenden |
| `Tools/openwebui_ext/tools/github_repo_inspector.py` | `api.github.com` | 3 | GitHub-API-Zugriff möglich | nicht Offline-Default | Optionales Netzwerktool; nicht `internetwissen` zuweisen |
| `Tools/openwebui_ext/tools/web_search_and_crawl.py` | `aiohttp`, SearXNG, Crawl4AI, OpenAI-kompatible URL | 3 | Suche/Crawl/LLM-Aufrufe über lokale oder externe Dienste möglich | nicht Offline-Default | Nur bewusst in Online-/Intranetprofilen aktivieren |
| `Tools/openwebui_ext/tools/openui_generative_ui.py` | lokaler OpenUI-Bundle-Pfad `/static/openui` | 3 | optionales Rich-UI-Tool rendert nur mit lokal bereitgestelltem Bundle; kein öffentlicher CDN-Default | nicht Offline-Default | OpenUI-Browser-Bundle vorab air-gapped unter `/static/openui/dist` bereitstellen oder `inline_visuals_toolkit_v3.py` bevorzugen |
| `Tools/openwebui_ext/tools/mediawiki_legacy_crawler.py` | MediaWiki `http://`/`https://`-Endpunkt | 3 | Live-Wiki-Endpunkt nötig | nicht Offline-Default für `internetwissen` | Nur als internes Snapshot-/Intranet-Werkzeug dokumentieren, nicht als allgemeines Offline-Wissenstool |
| `Tools/openwebui_ext/tools/visuals_toolkit_v4.py` | optionales Plotly-CDN | 3 | CDN nur bei aktivierter Valve | kein Offline-Default, wenn CDN deaktiviert bleibt | Für Offline-Beispiele `inline_visuals_toolkit_v3` bevorzugen |
| `Tools/jupyter/jupyter_tool.py` | Jupyter-HTTP-URL | 3 | lokaler Jupyter-Server erforderlich | optionales lokales Tool | Nur mit lokaler URL und ohne externe Datenquellen verwenden |
| `Deployment/docker-compose*.yml` und README-Hinweise | GHCR-/Image-Referenzen | 5 | `docker pull` benötigt Netz | kein Runtime-Nachladen nach Air-Gap-Import | Offline-Image-Export unter `Deployment/images/README.md` dokumentieren |
| `Tools/openwebui_ext/third_party/*` | upstream URLs und Funktionsmetadata | 1 | Provenienz- und Lizenzhinweise | kein Runtime-Effekt | Hinweise beibehalten; Third-Party-Notices pflegen |
| `Modelle/icons/generic/*.svg` | SVG namespace `http://www.w3.org/2000/svg` | 1 | Namespace ist keine Netzwerkabhängigkeit | offline sauber | Keine Maßnahme |

## Ergebnis

Der Offline-Default bleibt ohne öffentliche Runtime-Websuche und ohne öffentliche CDN-Pflicht. Lokale Intra-Stack-API-Kommunikation wie der Modellrat über OpenWebUI bleibt zulässig, solange sie auf die lokale oder intern bereitgestellte Zielinstanz zeigt. Netzwerkfähige Tools sind optional, dokumentiert und dürfen nicht automatisch Modellprofilen wie `internetwissen` zugewiesen werden. Externe Container-Images werden als Release-/Deployment-Thema behandelt; für Air-Gap-Nutzung sind lokale Image-Tars mit Hashes vorgesehen.
