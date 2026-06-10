using NUnit.Framework;
using OpenCvSharp;
using Product.UiTests.Shared.Visual;

namespace Product.UiTests.Uia3.VisualTrack;

[TestFixture]
public sealed class SyntheticTrackLineAnalyzerTests
{
    [Test]
    public void Synthetic_Pass_Track_Is_Detected()
    {
        using var temp = new TemporaryDirectory();
        var imagePath = Path.Combine(temp.Path, "expected-pass.png");
        WriteSyntheticTrackImage(imagePath, offsetY: 0, broken: false);

        var route = CreateRoute("SYNTHETIC_PASS", allowedDeviationNm: 5.0);
        var result = TrackLineDeviationAnalyzer.Analyze(imagePath, route, temp.Path);

        Assert.Multiple(() =>
        {
            Assert.That(result.TrackDetected, Is.True);
            Assert.That(result.CoverageRatio, Is.GreaterThanOrEqualTo(0.90));
            Assert.That(result.MaxDeviationNm, Is.LessThanOrEqualTo(route.AllowedDeviationNm));
        });
    }

    [Test]
    public void Synthetic_Offset_Track_Exceeds_Nautical_Mile_Threshold()
    {
        using var temp = new TemporaryDirectory();
        var imagePath = Path.Combine(temp.Path, "expected-fail-offset-3px.png");
        WriteSyntheticTrackImage(imagePath, offsetY: 3, broken: false);

        var route = CreateRoute("SYNTHETIC_OFFSET", allowedDeviationNm: 5.0);
        var result = TrackLineDeviationAnalyzer.Analyze(imagePath, route, temp.Path);

        Assert.That(result.MaxDeviationNm, Is.GreaterThan(route.AllowedDeviationNm));
    }

    [Test]
    public void Synthetic_Broken_Track_Is_Reportable()
    {
        using var temp = new TemporaryDirectory();
        var imagePath = Path.Combine(temp.Path, "expected-fail-broken.png");
        WriteSyntheticTrackImage(imagePath, offsetY: 0, broken: true);

        var route = CreateRoute("SYNTHETIC_BROKEN", allowedDeviationNm: 5.0);
        var result = TrackLineDeviationAnalyzer.Analyze(imagePath, route, temp.Path);

        Assert.That(result.BrokenSegments, Is.GreaterThan(route.AllowedBrokenSegments));
    }

    private static TrackRouteDefinition CreateRoute(string scenarioId, double allowedDeviationNm)
    {
        return new TrackRouteDefinition
        {
            ScenarioId = scenarioId,
            UiBackend = "UIA3",
            MapAutomationId = "AircraftMapCanvas",
            SimulationTimeUtc = DateTime.Parse("2026-06-10T12:00:00Z").ToUniversalTime(),
            DisplayProfile = "FHD_100DPI",
            ZoomLevel = "Z08",
            NauticalMilesPerPixel = 2.5,
            AllowedDeviationNm = allowedDeviationNm,
            CoverageThreshold = 0.90,
            AllowedBrokenSegments = 0,
            MinTrackPixels = 20,
            TrackColorHsvLower = [20, 80, 80],
            TrackColorHsvUpper = [45, 255, 255],
            ExpectedRoute =
            [
                new RoutePoint(120, 430),
                new RoutePoint(520, 220)
            ]
        };
    }

    private static void WriteSyntheticTrackImage(string path, int offsetY, bool broken)
    {
        using var image = Mat.Zeros(600, 800, MatType.CV_8UC3);
        var color = new Scalar(0, 220, 255); // BGR, ergibt gelbliche Track-Linie.
        if (broken)
        {
            Cv2.Line(image, new Point(120, 430 + offsetY), new Point(250, 362 + offsetY), color, 2);
            Cv2.Line(image, new Point(390, 288 + offsetY), new Point(520, 220 + offsetY), color, 2);
        }
        else
        {
            Cv2.Line(image, new Point(120, 430 + offsetY), new Point(520, 220 + offsetY), color, 2);
        }

        Cv2.ImWrite(path, image);
    }

    private sealed class TemporaryDirectory : IDisposable
    {
        public TemporaryDirectory()
        {
            Path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "trackline-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Path);
        }

        public string Path { get; }

        public void Dispose()
        {
            try { Directory.Delete(Path, recursive: true); }
            catch { /* Testcleanup darf Testergebnis nicht verdecken. */ }
        }
    }
}
