# OpenWebUI Import Guide

## Tools importieren

1. In OpenWebUI mit einem vertrauenswürdigen Administrator anmelden.
2. `Workspace > Tools` öffnen.
3. `Create Tool` wählen.
4. Inhalt einer Datei aus `Tools/openwebui_ext/tools/*.py` vollständig einfügen.
5. Speichern und Tool nur für passende Modelle aktivieren.
6. Valves prüfen und Secrets ausschließlich lokal in OpenWebUI konfigurieren, nicht im Repository.

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

## Rechtevergabe

- Tool-Import entspricht serverseitiger Python-Ausführung und gehört nur in Admin-Hände.
- Skills sind Textanweisungen, können aber sensible Arbeitsweisen enthalten; Zugriff bewusst setzen.

## Troubleshooting

- Importfehler: Python-Syntax mit `python -m py_compile Tools/openwebui_ext/tools/<tool>.py` prüfen.
- Tool wird nicht aufgerufen: Modell-Tool-Zuordnung und Function-Calling-Einstellung prüfen.
- Skill nicht sichtbar: Skill aktivieren und Zugriffsrechte prüfen.
- Unerwartete Toolfehler: Valves, Netzwerkzugriff und Größenlimits prüfen.
