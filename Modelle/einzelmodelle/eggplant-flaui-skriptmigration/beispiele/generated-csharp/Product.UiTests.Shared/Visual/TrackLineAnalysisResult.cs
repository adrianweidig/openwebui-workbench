namespace Product.UiTests.Shared.Visual;

public sealed class TrackLineAnalysisResult
{
    public bool TrackDetected { get; init; }
    public double CoverageRatio { get; init; }
    public double MaxDeviationPx { get; init; }
    public double MeanDeviationPx { get; init; }
    public double P95DeviationPx { get; init; }
    public double MaxDeviationNm { get; init; }
    public int BrokenSegments { get; init; }
    public int ActualTrackPixels { get; init; }
    public required string MaskPath { get; init; }
    public required string ExpectedMaskPath { get; init; }
    public required string OverlayPath { get; init; }
}
