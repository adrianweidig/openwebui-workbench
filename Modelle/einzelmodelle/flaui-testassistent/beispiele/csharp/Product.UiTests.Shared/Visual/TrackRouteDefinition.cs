namespace Product.UiTests.Shared.Visual;

public sealed record RoutePoint(int X, int Y);

public sealed class TrackRouteDefinition
{
    public required string ScenarioId { get; init; }
    public required string UiBackend { get; init; }
    public required string MapAutomationId { get; init; }
    public required DateTime SimulationTimeUtc { get; init; }
    public required string DisplayProfile { get; init; }
    public required string ZoomLevel { get; init; }
    public double NauticalMilesPerPixel { get; init; }
    public double AllowedDeviationNm { get; init; }
    public double CoverageThreshold { get; init; } = 0.90;
    public int AllowedBrokenSegments { get; init; }
    public int MinTrackPixels { get; init; } = 20;
    public int[] TrackColorHsvLower { get; init; } = [20, 80, 80];
    public int[] TrackColorHsvUpper { get; init; } = [45, 255, 255];
    public required RoutePoint[] ExpectedRoute { get; init; }
}
