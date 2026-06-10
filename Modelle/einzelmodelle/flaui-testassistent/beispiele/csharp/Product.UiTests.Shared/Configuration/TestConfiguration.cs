namespace Product.UiTests.Shared.Configuration;

public sealed class TestConfiguration
{
    public required string AppUnderTestPath { get; init; }
    public required string ArtifactRoot { get; init; }
    public required string ScenarioRoot { get; init; }
    public required string CalibrationRoot { get; init; }
    public int MainWindowTimeoutSeconds { get; init; } = 60;
    public string DisplayProfile { get; init; } = "FHD_100DPI";
}
