---
command: workbench-sync-check
name: Workbench Sync Check
description: Prüft, ob ein OpenWebUI-Workbench-Import vollständig und nachvollziehbar synchronisiert wurde.
tags: workbench, openwebui, audit
---

Prüfe den aktuellen OpenWebUI-Workbench-Import fachlich und technisch.

Berichte knapp in dieser Struktur:

1. Importstatus der Modelle, Tools, Functions/Filter, Skills und Promptvorlagen.
2. Nachweis, dass `mainprompt.md`, `fachwissen.md` und `Golden_Example.<ext>` als echte Dateien und nicht als Knowledge/RAG-Kernkontext genutzt werden.
3. Auffälligkeiten bei fehlenden Public-Read-Freigaben, inaktiven Functions, fehlenden Default-Filtern oder falschen Basismodellen.
4. Konkrete nächste Korrekturschritte.

Erfinde keine Zielsystemdaten. Wenn ein Nachweis fehlt, markiere ihn als nicht geprüft.
