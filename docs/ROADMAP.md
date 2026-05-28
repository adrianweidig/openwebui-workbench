# Roadmap

Diese Roadmap ist nicht als Release-Zusage zu verstehen. Sie beschreibt eine vorsichtige Wartungsrichtung, die aus der aktuellen Repository-Struktur und den vorhandenen Prüfpfaden ableitbar ist.

## Stabil halten

- `scripts/verify_openwebui_workspace.py` als zentrale nicht-mutierende Prüfung erhalten.
- Generator-Check ohne erkannte Änderungen halten, solange keine Artefakte bewusst regeneriert werden.
- Offline-Default ohne öffentliche Netzwerkabhängigkeiten bewahren.
- `Modelle/dist/` und `Tools/dist/` als kanonische Handover-Bereiche pflegen.

## Internetwissen-Modell

Das Modellpaket `internetwissen` ist integriert. Es unterstützt allgemeine Recherchefragen, Anleitungen, Erklärungen, Quellenkritik und Wissensstrukturierung offline.

### Phase 1: Initiales Internetwissenmodell

Ziel der ersten Phase ist ein sofort nutzbares Modell ohne große externe Datenbestände.

Umgesetzt:

- Modellpaket `Modelle/einzelmodelle/internetwissen/`.
- Problemfall-Briefing `Problemfälle/27_internetwissen.md`.
- `model.json`, `systemprompt.md`, `mainprompt.md`, `fachwissen.md` und `beispielergebnis.md`.
- Kompakte, selbst geschriebene Wissensbasis in `fachwissen.md` pflegen.
- Beispiele für Recherchefragen, Anleitungen, Quellenkritik und Aktualitätsgrenzen.
- Produkt-i18n-Dateien für die unterstützten Locales.
- Websuche im Modellprofil deaktiviert lassen.
- Keine externen GB-/TB-Daten in das Repository aufnehmen.
- Generator- und Verify-Prüfung für das neue Modell erfolgreich halten.

Nicht Bestandteil von Phase 1:

- FineWeb
- Common Crawl
- Wikipedia-Dumps
- Kiwix-/ZIM-Dateien
- externe Vektorindizes
- automatische Webarchiv-Pipelines
- Live-Websuche

### Phase 2: Kleine optionale Knowledge-Erweiterungen

Nach dem initialen Modell können kleine, repo-taugliche Knowledge-Erweiterungen geprüft werden.

Mögliche Ergänzungen:

- zusätzliche selbst geschriebene Kompaktmodule für Recherchemethodik, Web-Grundlagen, technische Grundbegriffe und Anleitungsmuster
- kleine lizenzklare Beispielquellen
- Quellen- und Lizenztemplates
- Importbeispiele für lokale KnowledgeBases
- Smoke-Tests für Knowledge-Nutzung im Modell

Grenze:

- keine großen externen Datensätze im Git-Repository
- keine unklare Übernahme fremder Webinhalte

### Phase 3: Optionale lokale KnowledgePacks

Für größere Installationen kann ein KnowledgePack-Konzept vorbereitet werden. Das Repository soll dabei nur Manifeste, Skripte und Dokumentation enthalten. Die eigentlichen Daten liegen lokal beim Nutzer und bleiben unversioniert.

Mögliche KnowledgePacks:

- technische Dokumentationssammlungen
- lokale Markdown-/Textsammlungen
- exportierte OpenWebUI-KnowledgeBases
- lokale Wiki- oder Dokumentationsarchive
- lizenzklar kuratierte Fachkorpora

Geplante Artefakte:

- `KnowledgePacks/internetwissen/README.md`
- Manifestformat für lokale Wissenspakete
- Beispielkonfiguration für lokale Pfade
- Lizenz- und Snapshot-Report
- Import-Dry-Run ohne produktive Tokens

### Phase 4: Web-Scale-Ausbau als spätere Option

Langfristig kann geprüft werden, ob sehr große Offline-Webkorpora angebunden werden sollen. Diese Ausbaustufe ist bewusst nicht Teil des initialen Modells.

Denkbare spätere Themen:

- FineWeb
- FineWeb-Edu
- Common Crawl
- Wikimedia-/Kiwix-Dumps
- lokale Such- und Retrieval-Indizes
- Qdrant, OpenSearch, PGVector oder vergleichbare lokale Indexdienste
- dedizierte Import-, Chunking-, Deduplizierungs- und Lizenzprüfpfade
- lokale Web-Korpus-Suche als optionales OpenWebUI-Tool

Grundsatz:

Große Webkorpora werden nicht in dieses Repository eingecheckt. Das Repository darf dafür nur reproduzierbare Manifeste, Importskripte, Sicherheitsregeln, Lizenzhinweise und Deployment-Beispiele enthalten.

## Naheliegende Verbesserungen

- Weitere Unit-Tests für Tools mit komplexerer Valve- oder Dateisystemlogik ergänzen.
- Dokumentierte Importfehler und OpenWebUI-Versionseigenheiten in `docs/FAQ.md` sammeln.
- Optionalen Docker-Compose-Check in CI prüfen, wenn ein stabiler, nicht produktiver Docker-Pfad verfügbar ist.
- Beispielartefakte ohne vertrauliche Daten ausbauen, wenn sie direkt aus vorhandenen Modellpaketen ableitbar sind.
- Security-Review für optionale Netzwerktools regelmäßig wiederholen.

## Maintainer-Entscheidungen

- GitHub Topics, Repository Description und Social Preview setzen.
- Private Vulnerability Reporting oder einen privaten Sicherheitskontakt aktivieren.
- Release- und Tagging-Strategie festlegen, falls Artefaktstände versioniert werden sollen.
- Entscheiden, ob GitHub Pages oder ein separates Docs-Hosting genutzt werden soll.
- Entscheiden, ob `internetwissen` langfristig ein einzelnes Modell bleibt oder in zusätzliche Profile wie `internetwissen-kurator` oder `internetwissen-max` aufgeteilt wird.

## Nicht-Ziele im aktuellen Stand

- Kein automatischer produktiver OpenWebUI-Import ohne ausdrücklichen Auftrag.
- Keine versteckten Online-Abhängigkeiten für Offline-Default-Tools.
- Keine Änderung öffentlicher Tool- oder Import-Schnittstellen ohne klare Validierung.
- Keine großen externen Webkorpora im Git-Repository.
- Keine ungeprüfte Übernahme fremder Webinhalte ohne Lizenz- und Attributionsprüfung.
