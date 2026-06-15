Golden Example: Eggplant-FlaUI-Skriptmigration
Nutzeraufgabe

Migriere das folgende Eggplant-/SenseTalk-Skript in den Zielstack NUnit, FlaUI und OpenCvSharp. Erzeuge eine reviewfähige Migrationsantwort mit Klassifizierung, Zielentscheidung, Mapping, C#-Skizze, VisualTrack-Bewertung, Risiken und Akzeptanzkriterien.

sensetalk
put "C:\Program Files\Product\Product.exe" into autPath
LaunchApp autPath

WaitFor 30, "Login.Window"
Click "Login.UserName"
TypeText "qa.user"
Click "Login.Password"
TypeText the secureText "passwordFromSuite"
Click "Login.SignIn"

WaitFor 30, "Main.Navigation"
Click "Navigation.MapModule"
WaitFor 20, "Map.Canvas.Ready"

Click "Map.RouteSelector"
TypeText "AIRCRAFT-TRACK-BERLIN-01"
Click "Map.LoadRoute"

WaitFor 15, "Map.TrackLine.Visible"
CaptureScreen "artifacts/track-before-validation.png"

AssertImagePresent "TrackLine.Expected.Green"
AssertImagePresent "TrackLine.NoGap.AtWaypointBravo"

Click "Map.DetailsPanel"
AssertExists "Details.RouteName.AIRCRAFT-TRACK-BERLIN-01"
AssertExists "Details.Status.Active"
Erwartete Modellantwort
Annahmen

Das Eggplant-Skript startet eine WPF-Desktopanwendung und navigiert nach erfolgreichem Login in ein Karten-/Canvas-Modul.

Standarddialoge wie Login, Navigation, Routenauswahl und Detailpanel werden über FlaUI.UIA3 migriert.

Die fachliche Prüfung der grünen Track-Linie auf dem Karten-Canvas ist ein VisualTrack-Fall und wird nicht durch Fullscreen-Pixelvergleich ersetzt.

Die bisherigen Bildnamen sind als Hinweise auf erwartete AutomationId, ROI und fachliche Prüfabsicht zu behandeln.

Zugangsdaten werden nicht aus dem Eggplant-Skript übernommen, sondern aus Testkonfiguration oder Pipeline-Secret bereitgestellt.

1. Eingangsanalyse
Befund	Bewertung
Eggplant-Suite/Test	nicht angegeben; ableitbarer Testname: AIRCRAFT-TRACK-BERLIN-01
BusinessFlow	Login, Kartenmodul öffnen, Route laden, Track-Linie validieren, Detailstatus prüfen
SurfaceTechnology	WPF-Standardcontrols plus Canvas/Map
Primäre UI-Automation	FlaUI.UIA3
Visuelle Fachprüfung	ja, Track-Line-Prüfung über OpenCvSharp
TrackLineRequired	ja
Testdaten erforderlich	ja, Route AIRCRAFT-TRACK-BERLIN-01, erwartete Referenzroute, Displayprofil
MigrationWave	4, weil fachkritische VisualTrack-Prüfung
Nicht verwenden	Koordinatenklicks, Thread.Sleep, xUnit, MSTest, ImageSharp, WinAppDriver, Playwright-Desktop
2. Business Intent

Der Test prüft, ob ein berechtigter Nutzer eine definierte Flug-/Track-Route im Kartenmodul laden kann und ob die gerenderte Track-Linie fachlich korrekt dargestellt wird. Entscheidend sind nicht die Eggplant-Bildanker selbst, sondern folgende Zielaussagen:

Die Anwendung startet und der Login ist erfolgreich.

Das Kartenmodul wird geöffnet und ist renderbereit.

Die Route AIRCRAFT-TRACK-BERLIN-01 wird geladen.

Die Track-Linie wird im erwarteten ROI erkannt.

Die erkannte Linie deckt die erwartete Route ausreichend ab.

Die maximale fachliche Abweichung bleibt innerhalb der erlaubten Toleranz.

Am Wegpunkt Bravo entsteht keine fachlich relevante Unterbrechung.

Das Detailpanel zeigt Route und Status Active.

3. Klassifizierung und Zielentscheidung
Kriterium	Entscheidung
Migrationsklasse	D – Canvas/Map/Track-Line VisualTrack
Zielprojekt UI	Product.UiTests.Uia3
Zielprojekt VisualTrack	Product.UiTests.Uia3/VisualTrack
UI-Technologie	WPF über UIA3
Visuelle Validierung	OpenCvSharp4.Windows
Testframework	NUnit
Assertions	Assert.That
Artefakte bei Fehler	Screenshot, UIA-Dump, Logs, metadata.json, OpenCV-Maske, Overlay, track-analysis.json
4. Eggplant → FlaUI/OpenCV Mapping
Eggplant-Schritt	Fachliche Bedeutung	Zielumsetzung
LaunchApp autPath	AUT starten	AppLauncher.StartApplication() mit Pfad aus appsettings.uitests.json
WaitFor "Login.Window"	Loginfenster bereit	WindowFinder.WaitForMainWindow(...) und LoginScreen.WaitFor(...)
Click "Login.UserName"	Benutzerfeld fokussieren	TextBox über AutomationId = Login.UserName finden
TypeText "qa.user"	Benutzer eingeben	Testkonto aus Konfiguration; kein hart kodiertes Secret
Click "Login.Password"	Passwortfeld fokussieren	PasswordBox über AutomationId = Login.Password
TypeText the secureText ...	Passwort eingeben	Pipeline-Secret oder lokale sichere Konfiguration
Click "Login.SignIn"	Anmeldung auslösen	Button über InvokePattern
WaitFor "Main.Navigation"	Hauptnavigation sichtbar	UIA-Assertion auf Navigation
Click "Navigation.MapModule"	Kartenmodul öffnen	Navigationseintrag über AutomationId aktivieren
WaitFor "Map.Canvas.Ready"	Karten-Canvas renderbereit	UIA-Element Map.Canvas sichtbar plus Ready-Indikator
Click "Map.RouteSelector"	Routeingabe öffnen	ComboBox/TextBox über UIA
TypeText "AIRCRAFT-TRACK-BERLIN-01"	Testroute auswählen	Routencode als Testdatenwert
Click "Map.LoadRoute"	Route laden	Button über Invoke()
WaitFor "Map.TrackLine.Visible"	Track gerendert	UIA-Ready-Status plus ROI-Capture
CaptureScreen ...	Diagnoseartefakt	Screenshot-/Element-Capture im Artefaktordner
AssertImagePresent "TrackLine.Expected.Green"	Track-Linie erkannt	HSV-Maske, CoverageRatio, Pixelanzahl
AssertImagePresent "TrackLine.NoGap.AtWaypointBravo"	keine Lücke am Wegpunkt Bravo	BrokenSegments und Waypoint-ROI prüfen
Click "Map.DetailsPanel"	Detailpanel öffnen	UIA-Element aktivieren
AssertExists "Details.RouteName..."	Routendetail korrekt	Text/Label über UIA prüfen
AssertExists "Details.Status.Active"	Status korrekt	Text/Label über UIA prüfen
5. Ziel-Dateien
Datei	Zweck
tests/Product.UiTests.Uia3/VisualTrack/AircraftTrackLineMigrationTests.cs	NUnit-Test für den migrierten End-to-End-Flow
tests/Product.UiTests.Shared/Screens/LoginScreen.cs	Screen-Object für Login
tests/Product.UiTests.Shared/Screens/MapScreen.cs	Screen-Object für Kartenmodul, Routeingabe und Canvas
tests/Product.UiTests.Shared/VisualTrack/TrackLineDeviationAnalyzer.cs	OpenCV-Analyse der Track-Linie
tests/Product.UiTests.Shared/VisualTrack/TrackLineAnalysisResult.cs	Ergebnisobjekt mit Pflichtmetriken
tests/Product.UiTests.Shared/Diagnostics/FailureArtifactCollector.cs	Fehlerartefakte
tests/Product.UiTests.Uia3/TestAssets/VisualTrack/aircraft-track-berlin-01.route.json	erwartete Referenzroute
tests/Product.UiTests.Uia3/appsettings.uitests.json	AUT-Pfad, Timeouts, Artefaktpfad und VisualTrack-Toleranzen
6. C#-Skizze
Datei: tests/Product.UiTests.Uia3/VisualTrack/AircraftTrackLineMigrationTests.cs
C#
using FlaUI.Core.AutomationElements;
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;
using Product.UiTests.Shared.VisualTrack;

namespace Product.UiTests.Uia3.VisualTrack;

[TestFixture]
[NonParallelizable]
[Apartment(System.Threading.ApartmentState.STA)]
public sealed class AircraftTrackLineMigrationTests
{
    private TestConfiguration _config = null!;
    private AppLauncher _launcher = null!;
    private FailureArtifactCollector _artifacts = null!;
    private TrackLineDeviationAnalyzer _trackAnalyzer = null!;

    [SetUp]
    public void SetUp()
    {
        _config = ConfigurationLoader.Load();
        _launcher = new AppLauncher(_config);
        _artifacts = new FailureArtifactCollector(_config.ArtifactRoot);
        _trackAnalyzer = new TrackLineDeviationAnalyzer();
    }

    [Test]
    public void LoadAircraftTrackBerlin01_RendersExpectedTrackLine_AndShowsActiveDetails()
    {
        const string routeId = "AIRCRAFT-TRACK-BERLIN-01";

        using var app = _launcher.StartApplication();
        using var automation = new UIA3Automation();

        try
        {
            var mainWindow = WindowFinder.WaitForMainWindow(app, automation, _config.DefaultTimeout);

            var login = LoginScreen.WaitFor(mainWindow, _config.DefaultTimeout);
            login.SignIn(_config.UserName, _config.Password);

            var map = MapScreen.WaitFor(mainWindow, _config.DefaultTimeout);
            map.OpenMapModule();
            map.WaitUntilCanvasReady(_config.DefaultTimeout);
            map.LoadRoute(routeId);

            var canvas = map.WaitForTrackCanvas(_config.DefaultTimeout);
            var capturePath = _artifacts.CaptureElement(canvas, TestContext.CurrentContext.Test.Name, "map-canvas.png");

            var analysis = _trackAnalyzer.Analyze(
                actualImagePath: capturePath,
                expectedRoutePath: _config.VisualTrack.RouteFile("aircraft-track-berlin-01.route.json"),
                profile: _config.VisualTrack.DisplayProfile,
                outputDirectory: _artifacts.TestArtifactDirectory(TestContext.CurrentContext.Test.Name));

            Assert.That(analysis.TrackDetected, Is.True, "Die Track-Linie wurde im Karten-ROI nicht erkannt.");
            Assert.That(analysis.CoverageRatio, Is.GreaterThanOrEqualTo(0.90), "Die erkannte Linie deckt die erwartete Route nicht ausreichend ab.");
            Assert.That(analysis.MaxDeviationNm, Is.LessThanOrEqualTo(_config.VisualTrack.AllowedDeviationNm), "Die maximale fachliche Abweichung überschreitet die Toleranz.");
            Assert.That(analysis.BrokenSegments, Is.LessThanOrEqualTo(_config.VisualTrack.AllowedBrokenSegments), "Die Track-Linie enthält zu viele Unterbrechungen.");
            Assert.That(analysis.ActualTrackPixels, Is.GreaterThanOrEqualTo(_config.VisualTrack.MinTrackPixels), "Die erkannte Track-Pixelmenge ist zu gering.");

            map.OpenDetailsPanel();

            Assert.That(map.RouteNameText, Is.EqualTo(routeId));
            Assert.That(map.StatusText, Is.EqualTo("Active"));
        }
        catch
        {
            _artifacts.Capture(app, automation, TestContext.CurrentContext.Test.Name);
            throw;
        }
    }
}
Datei: tests/Product.UiTests.Shared/Screens/LoginScreen.cs
C#
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;

namespace Product.UiTests.Shared.Screens;

public sealed class LoginScreen
{
    private readonly Window _window;

    private LoginScreen(Window window)
    {
        _window = window;
    }

    public static LoginScreen WaitFor(Window window, TimeSpan timeout)
    {
        var end = DateTime.UtcNow.Add(timeout);

        while (DateTime.UtcNow < end)
        {
            var loginRoot = window.FindFirstDescendant(cf => cf.ByAutomationId("Login.Window"));
            if (loginRoot is not null && !loginRoot.Properties.IsOffscreen.ValueOrDefault)
            {
                return new LoginScreen(window);
            }
        }

        throw new TimeoutException("Login.Window wurde nicht innerhalb des Timeouts sichtbar.");
    }

    public void SignIn(string userName, string password)
    {
        var userNameBox = Required("Login.UserName").AsTextBox();
        userNameBox.Text = string.Empty;
        userNameBox.Enter(userName);

        var passwordBox = Required("Login.Password").AsTextBox();
        passwordBox.Text = string.Empty;
        passwordBox.Enter(password);

        Required("Login.SignIn").AsButton().Invoke();
    }

    private AutomationElement Required(string automationId)
    {
        return _window.FindFirstDescendant(cf => cf.ByAutomationId(automationId))
            ?? throw new InvalidOperationException($"UI-Element mit AutomationId '{automationId}' wurde nicht gefunden.");
    }
}
Datei: tests/Product.UiTests.Shared/Screens/MapScreen.cs
C#
using FlaUI.Core.AutomationElements;

namespace Product.UiTests.Shared.Screens;

public sealed class MapScreen
{
    private readonly Window _window;

    private MapScreen(Window window)
    {
        _window = window;
    }

    public string RouteNameText => Required("Details.RouteName").AsLabel().Text;
    public string StatusText => Required("Details.Status").AsLabel().Text;

    public static MapScreen WaitFor(Window window, TimeSpan timeout)
    {
        var end = DateTime.UtcNow.Add(timeout);

        while (DateTime.UtcNow < end)
        {
            var navigation = window.FindFirstDescendant(cf => cf.ByAutomationId("Main.Navigation"));
            if (navigation is not null && !navigation.Properties.IsOffscreen.ValueOrDefault)
            {
                return new MapScreen(window);
            }
        }

        throw new TimeoutException("Main.Navigation wurde nicht innerhalb des Timeouts sichtbar.");
    }

    public void OpenMapModule()
    {
        Required("Navigation.MapModule").AsButton().Invoke();
    }

    public void WaitUntilCanvasReady(TimeSpan timeout)
    {
        var end = DateTime.UtcNow.Add(timeout);

        while (DateTime.UtcNow < end)
        {
            var ready = _window.FindFirstDescendant(cf => cf.ByAutomationId("Map.Canvas.Ready"));
            var canvas = _window.FindFirstDescendant(cf => cf.ByAutomationId("Map.Canvas"));

            if (ready is not null && canvas is not null && !canvas.Properties.IsOffscreen.ValueOrDefault)
            {
                return;
            }
        }

        throw new TimeoutException("Map.Canvas.Ready wurde nicht innerhalb des Timeouts erreicht.");
    }

    public void LoadRoute(string routeId)
    {
        var selector = Required("Map.RouteSelector").AsTextBox();
        selector.Text = string.Empty;
        selector.Enter(routeId);

        Required("Map.LoadRoute").AsButton().Invoke();
    }

    public AutomationElement WaitForTrackCanvas(TimeSpan timeout)
    {
        var end = DateTime.UtcNow.Add(timeout);

        while (DateTime.UtcNow < end)
        {
            var canvas = _window.FindFirstDescendant(cf => cf.ByAutomationId("Map.Canvas"));
            var trackVisible = _window.FindFirstDescendant(cf => cf.ByAutomationId("Map.TrackLine.Visible"));

            if (canvas is not null && trackVisible is not null && !canvas.Properties.IsOffscreen.ValueOrDefault)
            {
                return canvas;
            }
        }

        throw new TimeoutException("Map.TrackLine.Visible wurde nicht innerhalb des Timeouts erreicht.");
    }

    public void OpenDetailsPanel()
    {
        Required("Map.DetailsPanel").AsButton().Invoke();
    }

    private AutomationElement Required(string automationId)
    {
        return _window.FindFirstDescendant(cf => cf.ByAutomationId(automationId))
            ?? throw new InvalidOperationException($"UI-Element mit AutomationId '{automationId}' wurde nicht gefunden.");
    }
}
Datei: tests/Product.UiTests.Shared/VisualTrack/TrackLineAnalysisResult.cs
C#
namespace Product.UiTests.Shared.VisualTrack;

public sealed record TrackLineAnalysisResult(
    bool TrackDetected,
    double CoverageRatio,
    double MaxDeviationPx,
    double MeanDeviationPx,
    double P95DeviationPx,
    double MaxDeviationNm,
    int BrokenSegments,
    int ActualTrackPixels,
    string MaskPath,
    string OverlayPath,
    string JsonPath);
Datei: tests/Product.UiTests.Shared/VisualTrack/TrackLineDeviationAnalyzer.cs
C#
using System.Text.Json;
using OpenCvSharp;

namespace Product.UiTests.Shared.VisualTrack;

public sealed class TrackLineDeviationAnalyzer
{
    public TrackLineAnalysisResult Analyze(
        string actualImagePath,
        string expectedRoutePath,
        VisualTrackDisplayProfile profile,
        string outputDirectory)
    {
        Directory.CreateDirectory(outputDirectory);

        using var actual = Cv2.ImRead(actualImagePath, ImreadModes.Color);
        if (actual.Empty())
        {
            throw new InvalidOperationException($"Canvas-Capture konnte nicht gelesen werden: {actualImagePath}");
        }

        using var hsv = new Mat();
        Cv2.CvtColor(actual, hsv, ColorConversionCodes.BGR2HSV);

        using var trackMask = new Mat();
        Cv2.InRange(
            hsv,
            new Scalar(profile.TrackHueMin, profile.TrackSaturationMin, profile.TrackValueMin),
            new Scalar(profile.TrackHueMax, profile.TrackSaturationMax, profile.TrackValueMax),
            trackMask);

        using var kernel = Cv2.GetStructuringElement(MorphShapes.Rect, new Size(3, 3));
        Cv2.MorphologyEx(trackMask, trackMask, MorphTypes.Close, kernel);

        using var expectedMask = ExpectedRouteMaskRenderer.Render(expectedRoutePath, actual.Size(), profile);
        using var distanceInput = new Mat();
        Cv2.BitwiseNot(trackMask, distanceInput);

        using var distance = new Mat();
        Cv2.DistanceTransform(distanceInput, distance, DistanceTypes.L2, DistanceTransformMasks.Mask3);

        var expectedPixels = Cv2.FindNonZero(expectedMask);
        var actualPixels = Cv2.CountNonZero(trackMask);

        var deviations = expectedPixels
            .Select(point => distance.At<float>(point.Y, point.X))
            .OrderBy(value => value)
            .ToArray();

        var maxDeviationPx = deviations.Length == 0 ? double.MaxValue : deviations[^1];
        var meanDeviationPx = deviations.Length == 0 ? double.MaxValue : deviations.Average();
        var p95DeviationPx = deviations.Length == 0 ? double.MaxValue : deviations[(int)Math.Floor((deviations.Length - 1) * 0.95)];

        var coveragePixels = expectedPixels.Count(point => trackMask.At<byte>(point.Y, point.X) > 0);
        var coverageRatio = expectedPixels.Length == 0 ? 0.0 : (double)coveragePixels / expectedPixels.Length;

        var brokenSegments = TrackGapCounter.Count(expectedMask, trackMask, profile.MaxGapPixels);

        var maskPath = Path.Combine(outputDirectory, "track-mask.png");
        var overlayPath = Path.Combine(outputDirectory, "track-overlay.png");
        var jsonPath = Path.Combine(outputDirectory, "track-analysis.json");

        Cv2.ImWrite(maskPath, trackMask);
        Cv2.ImWrite(overlayPath, TrackOverlayRenderer.Render(actual, expectedMask, trackMask));

        var result = new TrackLineAnalysisResult(
            TrackDetected: actualPixels >= profile.MinTrackPixels,
            CoverageRatio: coverageRatio,
            MaxDeviationPx: maxDeviationPx,
            MeanDeviationPx: meanDeviationPx,
            P95DeviationPx: p95DeviationPx,
            MaxDeviationNm: maxDeviationPx * profile.NauticalMilesPerPixel,
            BrokenSegments: brokenSegments,
            ActualTrackPixels: actualPixels,
            MaskPath: maskPath,
            OverlayPath: overlayPath,
            JsonPath: jsonPath);

        File.WriteAllText(jsonPath, JsonSerializer.Serialize(result, new JsonSerializerOptions
        {
            WriteIndented = true
        }));

        return result;
    }
}
7. Testdaten / VisualTrack-Konfiguration
Datei: tests/Product.UiTests.Uia3/TestAssets/VisualTrack/aircraft-track-berlin-01.route.json
JSON
{
  "routeId": "AIRCRAFT-TRACK-BERLIN-01",
  "coordinateSystem": "canvas-pixels",
  "waypoints": [
    {
      "name": "Alpha",
      "x": 128,
      "y": 412
    },
    {
      "name": "Bravo",
      "x": 318,
      "y": 336
    },
    {
      "name": "Charlie",
      "x": 506,
      "y": 289
    },
    {
      "name": "Delta",
      "x": 694,
      "y": 224
    }
  ],
  "expectedSegments": [
    {
      "from": "Alpha",
      "to": "Bravo"
    },
    {
      "from": "Bravo",
      "to": "Charlie"
    },
    {
      "from": "Charlie",
      "to": "Delta"
    }
  ],
  "criticalWaypoints": [
    {
      "name": "Bravo",
      "maxGapPixels": 4
    }
  ]
}
Datei: tests/Product.UiTests.Uia3/appsettings.uitests.json
JSON
{
  "Application": {
    "ExecutablePath": "C:\\Program Files\\Product\\Product.exe"
  },
  "Timeouts": {
    "DefaultSeconds": 30
  },
  "Artifacts": {
    "Root": "TestResults"
  },
  "Credentials": {
    "UserNameEnvironmentVariable": "UI_TEST_USERNAME",
    "PasswordEnvironmentVariable": "UI_TEST_PASSWORD"
  },
  "VisualTrack": {
    "AssetRoot": "TestAssets\\VisualTrack",
    "AllowedDeviationNm": 0.15,
    "AllowedBrokenSegments": 0,
    "MinTrackPixels": 250,
    "DisplayProfile": {
      "TrackHueMin": 35,
      "TrackHueMax": 95,
      "TrackSaturationMin": 80,
      "TrackValueMin": 80,
      "TrackSaturationMax": 255,
      "TrackValueMax": 255,
      "NauticalMilesPerPixel": 0.003,
      "MaxGapPixels": 4,
      "MinTrackPixels": 250
    }
  }
}
8. Pipeline-/Artefakt-Hinweise
YAML
steps:
- task: DotNetCoreCLI@2
  displayName: 'Restore UI test projects'
  inputs:
    command: 'restore'
    projects: 'tests/**/*.csproj'

- task: DotNetCoreCLI@2
  displayName: 'Run FlaUI VisualTrack tests'
  inputs:
    command: 'test'
    projects: 'tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj'
    arguments: '--configuration Release --logger trx --results-directory $(Build.SourcesDirectory)\TestResults'
  env:
    UI_TEST_USERNAME: $(UiTestUserName)
    UI_TEST_PASSWORD: $(UiTestPassword)

- task: PublishTestResults@2
  displayName: 'Publish TRX results'
  inputs:
    testResultsFormat: 'VSTest'
    testResultsFiles: 'TestResults/**/*.trx'
    failTaskOnFailedTests: true

- task: PublishBuildArtifacts@1
  displayName: 'Publish UI test artifacts'
  inputs:
    PathtoPublish: '$(Build.SourcesDirectory)\TestResults'
    ArtifactName: 'ui-test-artifacts'
    publishLocation: 'Container'

Hinweise:

Der Agent muss ein self-hosted interaktiver Windows-Agent sein.

Die AUT darf nicht in einer reinen Service-Session ohne Desktop gestartet werden.

Für Azure DevOps Server wird PublishBuildArtifacts@1 verwendet.

VisualTrack-Artefakte müssen pro Testlauf track-mask.png, track-overlay.png und track-analysis.json enthalten.

9. Risiken und offene Punkte
Risiko/offener Punkt	Bewertung	Erforderliche Aktion
AutomationId nicht verifiziert	mittel	UIA-Dump mit Login.*, Map.*, Details.* gegen Zielanwendung prüfen
Karten-Canvas semantisch nicht über UIA prüfbar	erwartet	ROI-Capture über Canvas-BoundingRectangle verwenden
HSV-Farbgrenzen abhängig vom Theme	mittel	Displayprofil gegen Testumgebung kalibrieren
Route im Beispiel aus Bildnamen abgeleitet	mittel	Referenzroute fachlich gegen Produktdaten verifizieren
Wegpunkt-Bravo-Lückenprüfung	hoch	criticalWaypoints mit Produkt-/Fachteam validieren
Zugangsdaten im Eggplant-Skript	kritisch	nur Secret-Variablen verwenden, keine Klartextwerte übernehmen
UI-Rendering abhängig von Zoom/Skalierung	hoch	deterministisches Displayprofil und feste Zoomstufe erzwingen
10. Akzeptanzkriterien

Der migrierte Test verwendet NUnit, FlaUI.UIA3 und OpenCvSharp4.Windows.

Standardcontrols werden ausschließlich über AutomationId, UIA-Pattern oder stabile Accessible-Metadaten bedient.

Es gibt keine Koordinatenklicks und kein Thread.Sleep.

Die Track-Line-Prüfung nutzt ROI-Capture und OpenCV-Metriken statt Fullscreen-Pixelvergleich.

Die Pflichtmetriken TrackDetected, CoverageRatio, MaxDeviationPx, MeanDeviationPx, P95DeviationPx, MaxDeviationNm, BrokenSegments und ActualTrackPixels werden erzeugt.

CoverageRatio >= 0.90.

MaxDeviationNm <= AllowedDeviationNm.

BrokenSegments <= AllowedBrokenSegments.

ActualTrackPixels >= MinTrackPixels.

Route und Status werden zusätzlich über UIA im Detailpanel geprüft.

Bei Fehlern werden Screenshot, UIA-Dump, Logs, metadata.json, OpenCV-Maske, Overlay und track-analysis.json abgelegt.

Zugangsdaten stehen nicht im Testcode und nicht im Repository.

Offene Annahmen sind reviewfähig ausgewiesen.
