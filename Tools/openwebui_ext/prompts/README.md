# OpenWebUI Promptvorlagen

Dieses Verzeichnis enthält importierbare OpenWebUI-Promptvorlagen für die Workbench.
Jede Vorlage ist eine Markdown-Datei mit einfachem Frontmatter:

```markdown
---
command: workbench-sync-check
name: Workbench Sync Check
description: Kurze Beschreibung.
tags: workbench, audit
---

Promptinhalt.
```

Der Generator schreibt daraus `Tools/dist/openwebui-prompt-registry.json` und
`Tools/dist/openwebui-prompts-import.json`. Die Dashboard-Ressourcenverwaltung
kann Promptvorlagen einzeln bearbeiten, lokal löschen oder aus OpenWebUI entfernen.
