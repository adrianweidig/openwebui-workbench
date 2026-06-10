# fachwissen.md – Fachwissen für Eggplant-FlaUI-Skriptmigration

## 1. Zweck des Modells

Dieses Modell migriert bereitgestellte Eggplant-/SenseTalk-Skripte in den festgelegten C#-Zielstack:

- NUnit
- FlaUI.UIA3 für WPF
- FlaUI.UIA2 für WinForms
- OpenCvSharp4.Windows für Canvas-/Map-/Track-Line-Prüfungen
- Verify.NUnit für strukturierte Snapshots
- Serilog und eigene Artefaktinfrastruktur
- Azure DevOps Server mit self-hosted interaktiven Windows-Agenten

## 2. Kernprinzip

Migration bedeutet fachliche Rekonstruktion, nicht 1:1-Übersetzung.

Ein Eggplant-Schritt wie `Click "Customer.SaveButton"` wird nicht blind in einen Mausclick übersetzt, sondern in ein robustes UIA-Muster:

```csharp
window.FindFirstDescendant(cf.ByAutomationId("Customer.SaveButton"))
    ?.AsButton()
    .Invoke();
```

Ein Eggplant-Bildvergleich einer Track-Linie wird nicht durch einen Fullscreen-Pixelvergleich ersetzt, sondern durch ROI-Capture und OpenCV-Analyse.

## 3. Migrationsklassen

| Klasse | Eingang | Ziel |
|---|---|---|
| A | Standard-WPF-Workflow | `Product.UiTests.Uia3` |
| B | Standard-WinForms-Workflow | `Product.UiTests.Uia2` |
| C | gemischter Workflow | nach Startscreen trennen oder kombinierter UIA-Strang |
| D | Canvas/Map/Track-Line | FlaUI + OpenCvSharp VisualTrack |
| E | technische Smoke-Prüfung | UIA3 oder UIA2 nach Oberfläche |

## 4. Inventarisierungsfelder

Für jeden Eggplant-Test wird mindestens erfasst:

| Feld | Bedeutung |
|---|---|
| `EggplantSuite` | bisherige Suite |
| `EggplantTestName` | bisheriger Testname |
| `BusinessFlow` | fachlicher Ablauf |
| `SurfaceTechnology` | WPF, WinForms, gemischt, Canvas/Map |
| `PrimaryReplacement` | UIA3, UIA2, VisualTrack |
| `AutomationIdsAvailable` | ja/nein/teilweise |
| `VisualValidationRequired` | ja/nein |
| `TrackLineRequired` | ja/nein |
| `TestDataRequired` | ja/nein |
| `MigrationWave` | 0 bis 5 |
| `AcceptanceCriteria` | konkrete Zielassertions |

## 5. Eggplant → Zielstack-Mapping

| Eggplant-Muster | Interpretation | Zielmuster |
|---|---|---|
| `launchApp` | AUT starten | `Application.Launch` über `AppLauncher` |
| `waitFor "Image"` | Warten auf Zustand | `Waiter.UntilElement` oder fachliche UIA-Assertion |
| `Click "ButtonImage"` | Control bedienen | AutomationId + `Invoke()` |
| `TypeText` | Text setzen | TextBox `.Text = ""` + `.Enter(...)` |
| `AssertExists "Image"` | Zustand prüfen | UIA-Element vorhanden oder VisualTrack-Metrik |
| `AssertImagePresent "TrackLine..."` | visuelle Fachprüfung | ROI + `TrackLineDeviationAnalyzer` |
| `CaptureScreen` | Artefakt | Screenshot-Service / `Capture.Element` |

## 6. Selektorregeln

### WPF

- Primär `AutomationProperties.AutomationId`.
- `AutomationId` ist stabil, nicht lokalisiert, enthält keine Laufzeitdaten.
- Fachlich relevante Custom Controls brauchen AutomationPeers.

### WinForms

- Primär `Name` und `AccessibleName`.
- Dynamische Controls brauchen deterministische Namen.
- Für WinForms wird UIA2 bevorzugt.

### Verboten

- Button per Bildschirmkoordinate klicken.
- Textfeld per x/y fokussieren.
- Fullscreen-Pixelvergleich als fachliche Primärassertion.
- xUnit, MSTest, FluentAssertions als Zielstandard.
- ImageSharp für die initiale VisualTrack-Architektur.

## 7. VisualTrack-Fachwissen

VisualTrack ersetzt Eggplant-Bildvergleiche für dünne, bewegte Track-/Spurlinien.

### Pflichtmetriken

| Metrik | Zweck |
|---|---|
| `TrackDetected` | Spur überhaupt gefunden |
| `CoverageRatio` | Anteil der erwarteten Route mit erkannter Linie |
| `MaxDeviationPx` | maximale Pixelabweichung |
| `MeanDeviationPx` | mittlere Pixelabweichung |
| `P95DeviationPx` | robustes hohes Quantil |
| `MaxDeviationNm` | fachliche Abweichung in nautischen Meilen |
| `BrokenSegments` | Unterbrechungen |
| `ActualTrackPixels` | erkannte Pixelzahl |

### Default-Schwellwerte

- `TrackDetected == true`
- `CoverageRatio >= 0.90`
- `MaxDeviationNm <= AllowedDeviationNm`
- `BrokenSegments <= AllowedBrokenSegments`
- `ActualTrackPixels >= MinTrackPixels`

### Algorithmus

1. FlaUI lädt deterministisches Szenario.
2. FlaUI setzt Simulationszeit und Zoom.
3. FlaUI rendert einen Frame.
4. FlaUI ermittelt die ROI über `BoundingRectangle`/Element-Capture.
5. OpenCV konvertiert BGR zu HSV.
6. `InRange` extrahiert Track-Pixel.
7. Morphological Closing schließt kleine Lücken.
8. Erwartete Route wird als Maske gerendert.
9. Distance Transform misst Abweichung.
10. Ergebnis wird als JSON, Maske und Overlay gespeichert.

## 8. Codekonventionen

- Namespaces beginnen mit `Product.UiTests`.
- UI-Tests sind `[NonParallelizable]`.
- Assemblies setzen `LevelOfParallelism(1)`.
- `Assert.That` ist Standard.
- Testdaten stehen in JSON/CSV, nicht hart verteilt im Code.
- Konfiguration erfolgt über `appsettings.uitests.json` und `UI_TEST_`-Umgebungsvariablen.
- Testfehler sammeln Screenshots, UIA-Dumps, Logs und metadata.json.

## 9. Migrationswellen

| Welle | Inhalt |
|---|---|
| 0 | Testinfrastruktur und Pipeline |
| 1 | Smoke Tests und Login/Startpfade |
| 2 | fachliche WPF-Standarddialoge |
| 3 | fachliche WinForms-Standarddialoge |
| 4 | VisualTrack und fachkritische Canvas-/Map-Prüfungen |
| 5 | restliche Regressionen und Stabilisierung |

Track-Line-Tests sind Gate-Kandidaten und dürfen nicht pauschal ans Ende verschoben werden, wenn sie fachlich entscheidend sind.

## 10. Gute Antwort

Eine gute Migrationsantwort enthält:

- Business Intent.
- Zielklasse.
- Eggplant-zu-FlaUI-Mapping.
- konkrete Ziel-Dateien.
- C#-Code mit Screen Objects.
- VisualTrack-Konfiguration bei Bild-/Track-Prüfungen.
- Akzeptanzkriterien.
- offene AutomationId-/Testhook-Punkte.

## 11. Schlechte Antwort

Eine schlechte Antwort:

- übersetzt Clicks in Koordinaten.
- ersetzt Bildvergleich durch Fullscreen-Screenshotvergleich.
- schlägt xUnit/MSTest vor.
- ignoriert WinForms/UIA2.
- generiert Code ohne Artefakte.
- verwechselt Screenshot-Artefakt mit fachlicher Assertion.
- behauptet eine Migration sei vollständig, obwohl AutomationIds oder Testhooks fehlen.

## 12. Beispielpfade

Siehe `beispiele/`:

- `eggplant/wpf_login_customer_save.script`
- `eggplant/winforms_legacy_order_dialog.script`
- `eggplant/aircraft_track_line_visual.script`
- `generated-csharp/Product.UiTests.Uia3/Wpf/CustomerWorkflowTests.cs`
- `generated-csharp/Product.UiTests.Uia3/VisualTrack/AircraftTrackLineMigrationTests.cs`
- `generated-csharp/Product.UiTests.Uia2/WinForms/LegacyOrderDialogMigrationTests.cs`

## 13. Sicherheitsregeln

- Keine echten Zugangsdaten in Testcode.
- Keine PATs, API Keys oder Passwörter in Dateien.
- Produktive AUTs nicht mutierend testen, sofern keine isolierte Testumgebung vorhanden ist.
- KI-generierte Migrationen sind reviewpflichtig.
- Datenschutzrelevante Testdaten pseudonymisieren.

## 14. Ausgabevorlage für Codeblöcke

Wenn C# erzeugt wird, nenne vor jedem Codeblock den Zielpfad:

```md
### Datei: tests/Product.UiTests.Uia3/Wpf/CustomerWorkflowTests.cs

```csharp
...
```
```

Wenn mehrere Dateien erzeugt werden, füge eine kurze Zielstruktur voran.
