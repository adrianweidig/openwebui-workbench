using System.Text.Json;
using OpenCvSharp;

namespace Product.UiTests.Shared.Visual;

public static class TrackLineDeviationAnalyzer
{
    public static TrackLineAnalysisResult Analyze(string roiImagePath, TrackRouteDefinition route, string artifactDirectory)
    {
        Directory.CreateDirectory(artifactDirectory);

        using var input = Cv2.ImRead(roiImagePath, ImreadModes.Color);
        if (input.Empty())
        {
            throw new InvalidOperationException($"ROI-Bild konnte nicht geladen werden: {roiImagePath}");
        }

        using var hsv = new Mat();
        Cv2.CvtColor(input, hsv, ColorConversionCodes.BGR2HSV);

        var lower = new Scalar(route.TrackColorHsvLower[0], route.TrackColorHsvLower[1], route.TrackColorHsvLower[2]);
        var upper = new Scalar(route.TrackColorHsvUpper[0], route.TrackColorHsvUpper[1], route.TrackColorHsvUpper[2]);

        using var actualMask = new Mat();
        Cv2.InRange(hsv, lower, upper, actualMask);

        using var kernel = Cv2.GetStructuringElement(MorphShapes.Rect, new Size(3, 3));
        Cv2.MorphologyEx(actualMask, actualMask, MorphTypes.Close, kernel);

        using var expectedMask = Mat.Zeros(input.Rows, input.Cols, MatType.CV_8UC1);
        for (var i = 1; i < route.ExpectedRoute.Length; i++)
        {
            var a = route.ExpectedRoute[i - 1];
            var b = route.ExpectedRoute[i];
            Cv2.Line(expectedMask, new Point(a.X, a.Y), new Point(b.X, b.Y), Scalar.White, 1);
        }

        using var invertedActual = new Mat();
        Cv2.BitwiseNot(actualMask, invertedActual);

        using var distance = new Mat();
        Cv2.DistanceTransform(invertedActual, distance, DistanceTypes.L2, DistanceTransformMasks.Mask3);

        var expectedPoints = Cv2.FindNonZero(expectedMask) ?? [];
        var deviations = new List<double>(expectedPoints.Length);
        var covered = 0;

        foreach (var point in expectedPoints)
        {
            var d = distance.At<float>(point.Y, point.X);
            deviations.Add(d);
            if (d <= 1.5)
            {
                covered++;
            }
        }

        var actualPixels = Cv2.CountNonZero(actualMask);
        var ordered = deviations.OrderBy(x => x).ToArray();

        var maxDeviationPx = ordered.Length == 0 ? double.PositiveInfinity : ordered[^1];
        var meanDeviationPx = ordered.Length == 0 ? double.PositiveInfinity : ordered.Average();
        var p95DeviationPx = ordered.Length == 0 ? double.PositiveInfinity : ordered[(int)Math.Clamp(Math.Ceiling(ordered.Length * 0.95) - 1, 0, ordered.Length - 1)];
        var coverageRatio = expectedPoints.Length == 0 ? 0 : (double)covered / expectedPoints.Length;
        var brokenSegments = EstimateBrokenSegments(actualMask, route.ExpectedRoute);

        var maskPath = Path.Combine(artifactDirectory, "track-mask.png");
        var expectedMaskPath = Path.Combine(artifactDirectory, "expected-route-mask.png");
        var overlayPath = Path.Combine(artifactDirectory, "track-deviation-overlay.png");

        Cv2.ImWrite(maskPath, actualMask);
        Cv2.ImWrite(expectedMaskPath, expectedMask);
        WriteOverlay(input, actualMask, expectedMask, overlayPath);

        var result = new TrackLineAnalysisResult
        {
            TrackDetected = actualPixels >= route.MinTrackPixels,
            CoverageRatio = coverageRatio,
            MaxDeviationPx = maxDeviationPx,
            MeanDeviationPx = meanDeviationPx,
            P95DeviationPx = p95DeviationPx,
            MaxDeviationNm = maxDeviationPx * route.NauticalMilesPerPixel,
            BrokenSegments = brokenSegments,
            ActualTrackPixels = actualPixels,
            MaskPath = maskPath,
            ExpectedMaskPath = expectedMaskPath,
            OverlayPath = overlayPath
        };

        File.WriteAllText(
            Path.Combine(artifactDirectory, "track-analysis.json"),
            JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }));

        return result;
    }

    private static int EstimateBrokenSegments(Mat actualMask, RoutePoint[] route)
    {
        var broken = 0;
        for (var i = 1; i < route.Length; i++)
        {
            var a = route[i - 1];
            var b = route[i];
            using var segmentMask = Mat.Zeros(actualMask.Rows, actualMask.Cols, MatType.CV_8UC1);
            Cv2.Line(segmentMask, new Point(a.X, a.Y), new Point(b.X, b.Y), Scalar.White, 3);
            using var intersection = new Mat();
            Cv2.BitwiseAnd(actualMask, segmentMask, intersection);
            if (Cv2.CountNonZero(intersection) == 0)
            {
                broken++;
            }
        }

        return broken;
    }

    private static void WriteOverlay(Mat input, Mat actualMask, Mat expectedMask, string path)
    {
        using var overlay = input.Clone();

        var actualPoints = Cv2.FindNonZero(actualMask) ?? [];
        foreach (var point in actualPoints)
        {
            overlay.Set(point.Y, point.X, new Vec3b(0, 255, 255));
        }

        var expectedPoints = Cv2.FindNonZero(expectedMask) ?? [];
        foreach (var point in expectedPoints)
        {
            overlay.Set(point.Y, point.X, new Vec3b(255, 0, 255));
        }

        Cv2.ImWrite(path, overlay);
    }
}
