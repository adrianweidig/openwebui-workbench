---
name: native-tool-calling-rollout
description: Rollout-Checkliste für Native Tool Calling und modellbezogene Tool-Freigaben in OpenWebUI.
---

# Native Tool Calling Rollout

Nutze diesen Skill, wenn Tool Calling in OpenWebUI stabil für mehrere Modelle ausgerollt werden soll.

## Rollout

1. Globalen Zielmodus festlegen: Native Tool Calling für geeignete Modelle.
2. Pro Modell testen: einfaches Tool, strukturiertes JSON, mehrstufige Tool-Kette, Fehlerfall.
3. Kleine oder schwache lokale Modelle nur mit einfachen, read-only Tools kombinieren.
4. Komplexe Tool-Ketten auf stärkere lokale Modelle oder ein dediziertes Agent-Modell legen.
5. Tool-Zugriff nicht nur am Modell, sondern auch über Nutzer-/Gruppenrechte prüfen.
6. Fallback-Skills an Modelle binden, damit Workflows ohne Tool-Aufruf verständlich weiterlaufen.

## Abnahmetests

- Tool wird im Chat angeboten.
- Modell erzeugt gültige Tool-Argumente.
- Fehlende Berechtigung wird als erwarteter Ausfall erkannt.
- Ein alternativer Skill-/Tool-Pfad ist dokumentiert.

## Betrieb

Änderungen an Toolsets zuerst in einem Testmodell prüfen, dann auf produktive Modellprofile übertragen.
