---
name: visual-toolkit-v3-offline
description: Offline-Workflow für OpenWebUI-Visuals mit Inline-SVG, Mermaid, HTML-Dashboards und ComfyUI-Fallbacks.
---

# Visual Toolkit V3 Offline

Nutze diesen Skill, wenn ein Nutzer Diagramme, Dashboards, visuelle Zusammenfassungen, Präsentationsgrafiken, Mermaid-Diagramme oder ComfyUI-nahe Medien-Workflows möchte.

## Arbeitsweise

1. Kläre das Ziel des Visuals: Entscheidung, Analyse, Status, Architektur, Prozess oder Story.
2. Nutze zuerst lokale, robuste Formate: Tabelle, SVG, Mermaid oder HTML ohne externe Skripte.
3. Wenn echte Bild-, Audio- oder Video-Generierung gewünscht ist, prüfe zuerst die lokale ComfyUI-Verfügbarkeit und erstelle eine reproduzierbare Workflow-Checkliste.
4. Verwende `inline_visuals_toolkit_v3` für Charts, Dashboards, Mermaid-Blöcke und Visual-Briefs.
5. Verwende `comfyui_workflow_inspector`, wenn ein ComfyUI-Workflow-JSON vorliegt oder ein lokaler Mediengenerator angebunden werden soll.

## Fallback-Regeln

- Wenn SVG nicht ausreicht, liefere Mermaid plus tabellarische Datenbasis.
- Wenn Mermaid nicht gerendert wird, liefere den Diagrammcode und eine Textbeschreibung.
- Wenn ComfyUI nicht verfügbar ist, liefere Prompt, Parameter, Modell-/Node-Liste und erwartete Artefakte.
- Keine CDN-Abhängigkeiten, keine externen Bilder, keine Secrets und keine absoluten Hostpfade in Ausgaben verwenden.

## Ergebnisqualität

Jedes Visual muss Titel, Datenquelle oder Annahme, beschriftete Achsen/Legende und einen klaren nächsten Schritt enthalten. Bei unklaren Daten keine Scheingenauigkeit erzeugen.
