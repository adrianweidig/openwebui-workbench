using System.Text.Json;
using FlaUI.Core;
using FlaUI.Core.Capturing;
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;
using Product.UiTests.Shared.Visual;

namespace Product.UiTests.Uia3.VisualTrack;

[TestFixture]
[NonParallelizable]
public sealed class AircraftTrackLineMigrationTests
{
    private Application? _app;

    [TearDown]
    public void TearDown()
    {
        _app?.Close();
        _app?.Dispose();
    }

    [Test]
    public void Migrated_Eggplant_Aircraft_Track_Line_Visual_Check()
    {
        var config = ConfigurationLoader.Load();
        var artifacts = new ArtifactPaths(config.ArtifactRoot, TestContext.CurrentContext.Test.Name);
        var routePath = Path.Combine(config.ScenarioRoot, "TrackRoutes", "TRACK_ROUTE_001.json");
        var route = JsonSerializer.Deserialize<TrackRouteDefinition>(File.ReadAllText(routePath))
            ?? throw new InvalidOperationException($"Route konnte nicht geladen werden: {routePath}");

        using var automation = new UIA3Automation();
        var launcher = new AppLauncher();

        try
        {
            TestEnvironmentGuard.AssertDeterministicDesktop();

            _app = launcher.Launch(config.AppUnderTestPath, TimeSpan.FromSeconds(config.MainWindowTimeoutSeconds));
            var window = launcher.WaitForMainWindow(_app, automation, "ProductMainWindow", TimeSpan.FromSeconds(config.MainWindowTimeoutSeconds));

            var map = new AircraftMapScreen(window, automation.ConditionFactory);
            map.LoadScenario(route.ScenarioId);
            map.SetSimulationTime(route.SimulationTimeUtc);
            map.SetZoom(route.ZoomLevel);
            map.RenderFrame();

            var roiPath = Path.Combine(artifacts.Screenshots, $"{route.ScenarioId}-roi.png");
            Capture.Element(map.MapCanvas).ToFile(roiPath);

            var result = TrackLineDeviationAnalyzer.Analyze(roiPath, route, artifacts.OpenCv);

            Assert.Multiple(() =>
            {
                Assert.That(result.TrackDetected, Is.True, "TrackDetected");
                Assert.That(result.CoverageRatio, Is.GreaterThanOrEqualTo(route.CoverageThreshold), "CoverageRatio");
                Assert.That(result.MaxDeviationNm, Is.LessThanOrEqualTo(route.AllowedDeviationNm), "MaxDeviationNm");
                Assert.That(result.BrokenSegments, Is.LessThanOrEqualTo(route.AllowedBrokenSegments), "BrokenSegments");
                Assert.That(result.ActualTrackPixels, Is.GreaterThanOrEqualTo(route.MinTrackPixels), "ActualTrackPixels");
            });
        }
        catch (Exception ex)
        {
            FailureArtifactCollector.Collect(null, artifacts, TestContext.CurrentContext.Test.Name, ex);
            throw;
        }
    }
}
