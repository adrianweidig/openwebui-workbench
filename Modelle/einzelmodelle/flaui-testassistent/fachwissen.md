# fachwissen.md – Fachwissen für FlaUI-Testassistent

## 1. Zweck

Dieses Modell unterstützt die dauerhafte Implementierung und Pflege von FlaUI/NUnit-Desktop-UI-Tests für WPF, WinForms und VisualTrack-Szenarien.

Es analysiert, generiert, refaktoriert, diagnostiziert und reviewt Tests im Zielstack:

- NUnit
- FlaUI.Core
- FlaUI.UIA3 für WPF
- FlaUI.UIA2 für WinForms
- OpenCvSharp4.Windows für Canvas-/Track-Line-Prüfungen
- Verify.NUnit
- Serilog
- Azure DevOps Server mit self-hosted interaktiven Windows-Agenten

## 2. Grundbegriffe

| Begriff | Bedeutung |
|---|---|
| UIA3 | moderner UI-Automation-Backendpfad, Standard für WPF |
| UIA2 | alternativer UI-Automation-Backendpfad, Standard für WinForms |
| Screen Object | Kapselung eines Screens/Dialogbereichs mit stabilen Selektoren |
| AUT | Application Under Test |
| ROI | Region of Interest für visuelle Auswertung |
| VisualTrack | OpenCV-basierte Prüfung dünner Karten-/Spurlinien |
| Artifact Collector | Sammlung von Screenshots, Logs, UIA-Dumps, metadata.json |
| Flaky Test | Test mit wechselndem Ergebnis ohne Produktänderung |

## 3. Zielarchitektur für Testprojekte

```text
tests/
  Product.UiTests.Shared/
    Configuration/
    Diagnostics/
    Infrastructure/
    Screens/
    Visual/

  Product.UiTests.Uia3/
    Wpf/
    Smoke/
    VisualTrack/

  Product.UiTests.Uia2/
    WinForms/
    Smoke/
    VisualTrack/

  Product.UiTests.TestAssets/
    Scenarios/
    TrackRoutes/
    Calibration/
    Templates/
    SyntheticImages/
```

## 4. Pflichtklassen

| Klasse | Zweck |
|---|---|
| `AppLauncher` | AUT starten |
| `AutomationFactory` | UIA2/UIA3-Erzeugung, falls zentral gewünscht |
| `WindowFinder` | Hauptfenster/Dialog finden |
| `Waiter` | robuste Wartebedingungen |
| `ScreenBase` | gemeinsame Screen-Hilfen |
| `ArtifactPaths` | deterministische Artefaktordner |
| `ScreenshotService` | Fenster-/Element-Screenshots |
| `UiaTreeDumper` | UIA-Baum als XML |
| `FailureArtifactCollector` | Artefakte bei Fehlern |
| `TestEnvironmentGuard` | Auflösung/DPI prüfen |
| `TrackRouteDefinition` | VisualTrack-Szenario |
| `TrackLineDeviationAnalyzer` | OpenCV-Auswertung |
| `TrackLineArtifactWriter` | Masken, Overlay, JSON |

## 5. Selektor- und Warteprinzipien

### Gute Selektoren

- WPF: `AutomationProperties.AutomationId`
- WinForms: `Name`, `AccessibleName`, `AccessibleRole`
- stabile technische IDs
- keine Laufzeitdaten in IDs
- keine lokalisierte sichtbare Beschriftung als Primärselektor

### Schlechte Selektoren

- x/y-Koordinate
- Control-Index im UIA-Baum ohne fachliche Stabilität
- sichtbarer Text als einziger Selektor bei Mehrsprachigkeit
- Bildname als Control-Selektor für Standardcontrols

### Wartebedingungen

Gute Wartebedingungen prüfen fachliche Zustände:

- Element existiert.
- Element ist enabled.
- Dialog ist geschlossen.
- Text/Status entspricht Erwartung.
- RenderFrame wurde abgeschlossen.
- Track-Analyse hat Datei erzeugt.

Schlecht:

- `Thread.Sleep(...)` als Hauptlogik.
- fixe Wartezeit ohne Zustandsprüfung.
- retry ohne Fehlermeldung.

## 6. Reviewcheckliste für FlaUI-Tests

| Bereich | Prüffrage |
|---|---|
| Backend | UIA3 für WPF, UIA2 für WinForms? |
| Testframework | NUnit und `Assert.That`? |
| Parallelisierung | UI-Tests nonparallel? |
| Selektoren | stabile AutomationIds/AccessibleNames? |
| Bedienung | keine Koordinatenklicks für Standardcontrols? |
| Warten | robuste Waiter statt Sleep? |
| Assertions | fachlich und überprüfbar? |
| Artefakte | Screenshots, Logs, UIA-Dumps, metadata.json bei Fehler? |
| Konfiguration | AUT-Pfad und Testdaten per Config/Env? |
| VisualTrack | ROI, HSV, Masken, Overlay, `track-analysis.json`? |
| Pipeline | TRX + PublishBuildArtifacts@1? |

## 7. VisualTrack-Analyse

VisualTrack muss dünne Linien erkennen und fachlich bewerten.

### Ergebnisstruktur

```json
{
  "TrackDetected": true,
  "CoverageRatio": 0.97,
  "MaxDeviationPx": 1.2,
  "MeanDeviationPx": 0.3,
  "P95DeviationPx": 0.9,
  "MaxDeviationNm": 3.0,
  "BrokenSegments": 0,
  "ActualTrackPixels": 822
}
```

### Häufige Ursachen für VisualTrack-Fehler

| Symptom | Ursache | Fix |
|---|---|---|
| `TrackDetected=false` | HSV-Schwellen falsch oder Linie nicht gerendert | Trackfarbe/Kalibrierung prüfen |
| `CoverageRatio` niedrig | erwartete Route passt nicht zur Projektion | MapCalibration und Route prüfen |
| `MaxDeviationNm` hoch | tatsächliche Linie versetzt | fachlicher Fehler oder falscher nm/px-Faktor |
| Overlay leer | falsche ROI oder falsches Element | `AircraftMapCanvas`/BoundingRectangle prüfen |
| BrokenSegments > 0 | Rendering-Lücke oder Maskenparameter | Morphology/Schwellwerte kalibrieren |

## 8. Fehlerdiagnose bei UI-Tests

### Reihenfolge

1. TRX/Stacktrace lesen.
2. Screenshot ansehen.
3. UIA-Dump prüfen.
4. Log/metadata.json prüfen.
5. Agent-DPI/Auflösung prüfen.
6. Testdatenzustand prüfen.
7. Selektor und Waiter prüfen.
8. AUT-/Backend-spezifische Besonderheiten prüfen.

### Wahrscheinlichkeitsmuster

| Fehler | Typische Ursache |
|---|---|
| Element not found | AutomationId fehlt, falscher Dialog, Timing |
| Element disabled | fachlicher Zustand nicht erreicht |
| Falscher Text | Testdaten oder Lokalisierung |
| Test nur auf Agent rot | DPI, Desktop gesperrt, Auto-Logon, Auflösung |
| VisualTrack nur manchmal rot | Antialiasing, nicht deterministische Simulation, fehlender Testhook |
| Restore hängt | externer Feed, fehlende Lockfiles, Paketdrift |

## 9. Codegenerierungsmuster

### Screen Object

- enthält keine Testassertions außer defensiven NotFound-Fehlern.
- kapselt UIA-Suche und Bedienung.
- nutzt `Waiter`.
- enthält sprechende fachliche Methoden: `Login`, `SearchCustomer`, `RenderFrame`.

### Test

- arrangiert Konfiguration.
- startet AUT.
- nutzt Screen Object.
- assertet fachlich.
- sammelt Artefakte bei Fehlern.
- ist nonparallel.

## 10. Azure-DevOps-Server-Regeln

- `PublishTestResults@2` für TRX.
- `PublishBuildArtifacts@1` für Screenshots, Logs, UIA-Dumps, OpenCV.
- Keine `PublishPipelineArtifact@1` in Azure DevOps Server.
- UI-Agenten im Pool `WIN-UI-DESKTOP`.
- VisualTrack-Agent mit Demand `VisualTrack -equals true`.
- Build-Agenten ohne UI im Pool `WIN-BUILD`.
- Restore mit `--locked-mode`.

## 11. Gute Antwortmuster

Gute Antwort auf „Analysiere diesen Test“:

- Kurzbewertung.
- Findings mit Schweregrad.
- Zielstack-Konformität.
- konkreter Patch.
- offene Fragen.
- Artefakt-/Diagnosehinweise.

Gute Antwort auf „Generiere Test“:

- Annahmen.
- Zielprojekt.
- Screen Object.
- Testdatei.
- Akzeptanz.
- notwendige AutomationIds/Testhooks.

## 12. Schlechte Antwortmuster

- Nur Code ohne Annahmen und Akzeptanz.
- Koordinatenklicks.
- `Thread.Sleep` als Standard.
- xUnit/MSTest.
- ImageSharp.
- Keine Fehlerartefakte.
- Kein Unterschied zwischen UIA2 und UIA3.
- VisualTrack ohne JSON/Overlay/Metriken.
- „Der Test ist garantiert stabil“ ohne Ausführung.

## 13. Beispiele

Das Paket enthält:

- `beispiele/csharp/Product.UiTests.Shared/Infrastructure/*.cs`
- `beispiele/csharp/Product.UiTests.Shared/Screens/*.cs`
- `beispiele/csharp/Product.UiTests.Shared/Visual/*.cs`
- `beispiele/csharp/Product.UiTests.Uia3/Smoke/*.cs`
- `beispiele/csharp/Product.UiTests.Uia3/VisualTrack/*.cs`
- `beispiele/csharp/Product.UiTests.Uia2/WinForms/*.cs`
- `beispiele/legacy-eggplant-reference/*.script`
- `beispiele/review-input/FlakyCoordinateClickTest.cs`
- `beispiele/review-output/flaky-coordinate-click-review.md`

## 14. Sicherheits- und Datenschutzregeln

- Keine echten Passwörter.
- Keine PATs/API Keys.
- Testdaten pseudonymisieren.
- Keine produktiven Änderungen.
- Keine Exfiltration über externe Tools.
- Reviewpflicht für generierte Tests.
