---
name: offline-creative-media-workflows
description: Plant lokale Bild-, Audio-, Video- und Präsentations-Workflows mit ComfyUI, Inline-Visuals und Artefakt-Fallbacks.
---

# Offline Creative Media Workflows

Nutze diesen Skill für Bildgenerierung, Bildbearbeitung, Audio/TTS, Video, Präsentationsgrafiken und Medien-Artefakte in einer Offline-OpenWebUI-Umgebung.

## Workflow

1. Zielmedium bestimmen: SVG/Diagramm, HTML, Präsentation, Bild, Audio, Video oder ZIP-Artefakt.
2. Für einfache Visualisierung `inline_visuals_toolkit_v3` nutzen.
3. Für lokale generative Medien ComfyUI-Workflow-JSON prüfen, Modell-/Node-Bedarf listen und eine Setup-Checkliste erzeugen.
4. Für exportierbare Ergebnisse `offline_artifact_workbench` verwenden.
5. Bei fehlender Rendering- oder Medienpipeline reproduzierbare Prompts, Parameter und Akzeptanzkriterien liefern.

## Grenzen

- Keine externen Asset-CDNs in Offline-Artefakten voraussetzen.
- Keine urheberrechtlich problematischen Vollkopien externer Medien in Artefakte einbauen.
- Keine absoluten Hostpfade, Tokens oder internen URLs in Nutzerantworten ausgeben.

## Qualität

Medienausgaben brauchen Format, Auflösung oder Seitenverhältnis, Zielgruppe, Stilgrenzen, Dateinamenkonzept und Fallback.
