# Allgemein

Allgemeines OpenWebUI-Fallbackmodell für freie oder gemischte Nutzerprobleme, die nicht eindeutig zu einem spezialisierten Problemfallmodell passen.

## Vorgesehene Tools

Alle Offline-Default-Tools sind aktiviert. Das Modell entscheidet anhand der Aufgabe, welche davon genutzt werden.

## Import

`model.json` ist ein OpenWebUI-kompatibles JSON-Array mit genau einem Modellobjekt. `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md` und Dateien unter `beispiele/` werden beim API-Import als Knowledge für dieses Modell hinterlegt.
