---
name: flaui-eggplant-desktop-ui-testing
description: Produktionsnahe Migration und Qualitätssicherung von Eggplant-/SenseTalk-Workflows zu FlaUI/NUnit/OpenCV/Azure-DevOps-Server-Artefakten.
---

# FlaUI Eggplant Desktop UI Testing

## Zweck

Nutze diesen Skill für Eggplant-zu-FlaUI-Migrationen, FlaUI/NUnit-Testgenerierung, UI-Test-Reviews, VisualTrack-Analysen und Azure-DevOps-Server-Handover.

## Zielstack

- `NUnit` als Testframework.
- `FlaUI.UIA3` für WPF und moderne Windows-Desktopoberflächen.
- `FlaUI.UIA2` für WinForms- und Legacy-Flächen, wenn UIA3 nicht stabil sichtbar ist.
- `OpenCvSharp4.Windows` für VisualTrack-, Canvas-, Karten- und Track-Line-Prüfungen.
- `Verify.NUnit` nur für strukturierte Snapshots, nicht als Ersatz für fachliche Assertions.
- `PublishTestResults@2` für TRX und `PublishBuildArtifacts@1` für Screenshots, Logs, UIA-Dumps, OpenCV-Masken, Overlays und Analyse-JSON.

## Arbeitsweise

1. Trenne Business Intent, technische Eggplant-/SenseTalk-Aktion und fachlichen Zielnachweis.
2. Klassifiziere jeden Workflow als `UIA3`, `UIA2`, `VisualTrack`, `Mixed` oder `Nicht automatisierbar ohne Zusatzdaten`.
3. Erzeuge Ziel-Dateipfade und Projektstruktur, bevor du Code ausgibst.
4. Verwende Screen-Objects, `WindowFinder`, `Waiter`, `FailureArtifactCollector`, `UiaTreeDumper` und zentrale Konfiguration.
5. Prüfe mit FlaUInspect/UIA-Dump angenommene `AutomationId`, `Name`, `ControlType` und Fensterhierarchie.
6. Nutze VisualTrack nur für Bild-/Canvas-Zustände, nicht für normale Standardcontrols.
7. Lege offene Annahmen offen und nenne die konkret fehlenden Eingaben.

## Harte Grenzen

- Keine Koordinatenklicks für Standardcontrols.
- Keine hart kodierten Secrets, Passwörter, Tokens oder internen URLs.
- Keine `xUnit`-, `MSTest`-, `ImageSharp`-, `WinAppDriver`- oder Playwright-für-Desktop-Zielarchitektur.
- Keine Pipeline-Tasks voraussetzen, die in Azure DevOps Server nicht verfügbar sind.
- Keine Versionsstände behaupten, wenn sie weder aus Knowledge noch Nutzerkontext stammen.

## Ausgabeanker

Für Migration:

- Annahmen
- Eingangsanalyse
- Business Intent
- Klassifizierung und Zielentscheidung
- Eggplant zu FlaUI/OpenCV Mapping
- Ziel-Dateien
- C#-Code
- Testdaten / VisualTrack-Konfiguration
- Pipeline-/Artefakt-Hinweise
- Risiken und offene Punkte
- Akzeptanzkriterien

Für Review:

- Kurzbewertung
- Findings mit Schwere, Datei/Stelle, Problem und Empfehlung
- Zielstack-Konformität
- Beispielpatch
- Pipeline-Hinweise
- Offene Fragen

## Qualitätskriterien

- Tests sind reproduzierbar, wartbar und CI/CD-tauglich.
- Assertions prüfen fachliche Zustände, nicht nur erfolgreiche Klickabläufe.
- Failure-Artefakte sind pro Testlauf eindeutig auffindbar.
- UIA2/UIA3-Entscheidungen sind begründet.
- VisualTrack-Ergebnisse enthalten Metriken wie `TrackDetected`, `CoverageRatio`, `MaxDeviationPx`, `MaxDeviationNm` und `BrokenSegments`, wenn der Kontext diese Metriken hergibt.
