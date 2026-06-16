---
command: workbench-model-review
name: Workbench Model Review
description: Reviewt ein einzelnes Workbench-Modellpaket vor dem Import.
tags: workbench, modelle, review
---

Reviewe das bereitgestellte Workbench-Modellpaket.

Prüfe:

- kurzer deterministischer `systemprompt.md` mit Verweis auf die drei Pflichtdateien
- vorhandene und nicht leere `mainprompt.md`, `fachwissen.md` und genau eine `Golden_Example.<ext>`
- `beispiele/` nur als optionale Knowledge-/RAG-Beispiele
- passende Tool-, Function-/Filter- und Skill-Zuordnung
- keine Secrets, lokalen Infrastrukturverweise oder nicht belegten Versprechen

Antworte zuerst mit Befunden nach Schweregrad, danach mit einer kurzen Änderungsliste.
