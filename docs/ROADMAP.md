# Roadmap

Diese Roadmap ist nicht als Release-Zusage zu verstehen. Sie beschreibt eine vorsichtige Wartungsrichtung, die aus der aktuellen Repository-Struktur und den vorhandenen Prüfpfaden ableitbar ist.

## Stabil halten

- `scripts/verify_openwebui_workspace.py` als zentrale nicht-mutierende Prüfung erhalten.
- Generator-Check ohne erkannte Änderungen halten, solange keine Artefakte bewusst regeneriert werden.
- Offline-Default ohne öffentliche Netzwerkabhängigkeiten bewahren.
- `Modelle/dist/` und `Tools/dist/` als kanonische Handover-Bereiche pflegen.

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

## Nicht-Ziele im aktuellen Stand

- Kein automatischer produktiver OpenWebUI-Import ohne ausdrücklichen Auftrag.
- Keine versteckten Online-Abhängigkeiten für Offline-Default-Tools.
- Keine Änderung öffentlicher Tool- oder Import-Schnittstellen ohne klare Validierung.
