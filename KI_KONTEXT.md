# KI-Kontext für E:\OpenWebUI

## Zweck der Umgebung

Dieser Workspace dient zum Erstellen, Pflegen, Sortieren und Ausliefern von OpenWebUI-Aufgabenmodellen und zugehörigen Offline-Tools für eine interne oder air-gapped Umgebung.

## Was hier möglich ist

- Problemfälle als fachliche Briefings lesen und daraus OpenWebUI-Modelle ableiten
- vorhandene Modellpakete prüfen, erweitern und neu strukturieren
- OpenWebUI-kompatible Modellartefakte für verschiedene Aufgabenfälle pflegen
- Offline-Tools für OpenWebUI bereitstellen, insbesondere das Jupyter-Python-Tool
- Air-Gap-Handover-Artefakte erzeugen oder aktualisieren
- Dokumentation für GUI-Import, Volume-Mount und lokalen Betrieb pflegen
- den Root-Workspace als versioniertes Projekt weiterentwickeln

## Ordnerbedeutung

- `OpenWebUI Model Builder/`
  Nur Quelle, Vorgaben, Generatorlogik und Builder-interne Arbeitsbereiche.
  Nicht als primäre Ablage für operative Modelle oder Tools verwenden.

- `Problemfälle/`
  Fachliche Briefings. Neue Anwendungsfälle zuerst hier sauber beschreiben.

- `Modelle/einzelmodelle/`
  Primäre operative Modellablage.
  Jedes Unterverzeichnis entspricht einem Aufgabenmodell.

- `Modelle/dist/`
  Air-Gap-Handover-Bereich.
  Verwenden für ZIP-Transfer, Copy/Paste oder volumenbasierte Bereitstellung.

- `Tools/jupyter/`
  Operatives OpenWebUI-Tool für kontrollierte Python-Ausführung über Jupyter.

- `Weiteres/`
  Reserve für sonstige Referenzen, die nicht klar zugeordnet sind.

## Empfohlene Nutzung

1. Neue oder geänderte Anforderungen zuerst in `Problemfälle/` formulieren.
2. Den Builder nur als Ausgangspunkt für Regeln, Generatorlogik und Regenerierung verwenden.
3. Operative Ergebnisse immer in `Modelle/` und `Tools/` ablegen, nicht nur im Builder.
4. Modelle für Menschen unter `Modelle/einzelmodelle/` lesbar halten.
5. Für Zielsysteme oder Transport `Modelle/dist/` verwenden.
6. Tools unter `Tools/` so ablegen, dass sie direkt für OpenWebUI übernehmbar sind.
7. Root-Dokumentation aktuell halten, wenn sich Importwege oder Betriebsannahmen ändern.

## OpenWebUI-Nutzung

### Modelle per GUI

- passendes Modellpaket unter `Modelle/einzelmodelle/<modell-id>/` auswählen
- `systemprompt.md` als System Prompt verwenden
- `model.json` für Import, Name, Parameter und Features heranziehen
- `mainprompt.md` und `fachwissen.md` nach OpenWebUI-Kontext zusätzlich hinterlegen, falls möglich

### Modelle per Container oder Volume

- `Modelle/dist/` ist der vorgesehene Übergabeordner
- je nach OpenWebUI-Setup den Ordner in den Container mounten
- wenn keine direkte Dateierkennung existiert, `openwebui-models-import.json` oder einzelne `model.json`-Dateien manuell über die GUI importieren

### Tools

- produktive Tool-Datei: `Tools/jupyter/jupyter_tool.py`
- Konfiguration über:
  - `OPENWEBUI_JUPYTER_URL`
  - `OPENWEBUI_JUPYTER_TOKEN`
  - `OPENWEBUI_JUPYTER_TIMEOUT_SECONDS`
  - `OPENWEBUI_JUPYTER_ALLOWED_WORKDIR`

## Arbeitsregeln für KI

- keine destruktiven Änderungen an Briefings oder Quellen ohne klare Notwendigkeit
- operative Artefakte nicht nur im Builder pflegen, sondern unter `Modelle/` und `Tools/`
- Builder und operative Ausgabe logisch trennen
- keine Internetabhängigkeit in Modelle oder Tools einbauen, wenn Air-Gap-Ziel gilt
- keine Secrets, Tokens oder produktiven Zugangsdaten in Dateien schreiben
- bei Unsicherheit zur OpenWebUI-Importstruktur dokumentierte Fallback-Strukturen beibehalten
- menschenlesbare Sortierung vor technischer Bequemlichkeit priorisieren
