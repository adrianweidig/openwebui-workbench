# KI-Kontext fuer E:\OpenWebUI

## Zweck der Umgebung

Dieser Workspace dient zum Erstellen, Pflegen, Sortieren und Ausliefern von OpenWebUI-Aufgabenmodellen und zugehoerigen Offline-Tools fuer eine interne oder air-gapped Umgebung.

## Was hier moeglich ist

- Problemfaelle als fachliche Briefings lesen und daraus OpenWebUI-Modelle ableiten
- vorhandene Modellpakete pruefen, erweitern und neu strukturieren
- OpenWebUI-kompatible Modellartefakte fuer verschiedene Aufgabenfaelle pflegen
- Offline-Tools fuer OpenWebUI bereitstellen, insbesondere das Jupyter-Python-Tool
- Air-Gap-Handover-Artefakte erzeugen oder aktualisieren
- Dokumentation fuer GUI-Import, Volume-Mount und lokalen Betrieb pflegen
- den Root-Workspace als versioniertes Projekt weiterentwickeln

## Ordnerbedeutung

- `OpenWebUI Model Builder/`
  Nur Quelle, Vorgaben, Generatorlogik und Builder-interne Arbeitsbereiche.
  Nicht als primaere Ablage fuer operative Modelle oder Tools verwenden.

- `Problemfaelle/`
  Fachliche Briefings. Neue Anwendungsfaelle zuerst hier sauber beschreiben.

- `Modelle/einzelmodelle/`
  Primaere operative Modellablage.
  Jedes Unterverzeichnis entspricht einem Aufgabenmodell.

- `Modelle/dist/`
  Air-Gap-Handover-Bereich.
  Verwenden fuer ZIP-Transfer, Copy/Paste oder volumenbasierte Bereitstellung.

- `Tools/jupyter/`
  Operatives OpenWebUI-Tool fuer kontrollierte Python-Ausfuehrung ueber Jupyter.

- `Weiteres/`
  Reserve fuer sonstige Referenzen, die nicht klar zugeordnet sind.

## Empfohlene Nutzung

1. Neue oder geaenderte Anforderungen zuerst in `Problemfaelle/` formulieren.
2. Den Builder nur als Ausgangspunkt fuer Regeln, Generatorlogik und Regenerierung verwenden.
3. Operative Ergebnisse immer in `Modelle/` und `Tools/` ablegen, nicht nur im Builder.
4. Modelle fuer Menschen unter `Modelle/einzelmodelle/` lesbar halten.
5. Fuer Zielsysteme oder Transport `Modelle/dist/` verwenden.
6. Tools unter `Tools/` so ablegen, dass sie direkt fuer OpenWebUI uebernehmbar sind.
7. Root-Dokumentation aktuell halten, wenn sich Importwege oder Betriebsannahmen aendern.

## OpenWebUI-Nutzung

### Modelle per GUI

- passendes Modellpaket unter `Modelle/einzelmodelle/<modell-id>/` auswaehlen
- `systemprompt.md` als System Prompt verwenden
- `model.json` fuer Name, Parameter und Features heranziehen
- `mainprompt.md` und `fachwissen.md` nach OpenWebUI-Kontext zusaetzlich hinterlegen, falls moeglich

### Modelle per Container oder Volume

- `Modelle/dist/` ist der vorgesehene Uebergabeordner
- je nach OpenWebUI-Setup den Ordner in den Container mounten
- wenn keine direkte Dateierkennung existiert, Inhalte aus `dist/` oder `einzelmodelle/` manuell uebernehmen

### Tools

- produktive Tool-Datei: `Tools/jupyter/jupyter_tool.py`
- Konfiguration ueber:
  - `OPENWEBUI_JUPYTER_URL`
  - `OPENWEBUI_JUPYTER_TOKEN`
  - `OPENWEBUI_JUPYTER_TIMEOUT_SECONDS`
  - `OPENWEBUI_JUPYTER_ALLOWED_WORKDIR`

## Arbeitsregeln fuer KI

- keine destruktiven Aenderungen an Briefings oder Quellen ohne klare Notwendigkeit
- operative Artefakte nicht nur im Builder pflegen, sondern unter `Modelle/` und `Tools/`
- Builder und operative Ausgabe logisch trennen
- keine Internetabhaengigkeit in Modelle oder Tools einbauen, wenn Air-Gap-Ziel gilt
- keine Secrets, Tokens oder produktiven Zugangsdaten in Dateien schreiben
- bei Unsicherheit zur OpenWebUI-Importstruktur dokumentierte Fallback-Strukturen beibehalten
- menschenlesbare Sortierung vor technischer Bequemlichkeit priorisieren
