namespace Product.UiTests.Shared.Diagnostics;

public sealed class ArtifactPaths
{
    public ArtifactPaths(string artifactRoot, string testName)
    {
        Root = Path.Combine(artifactRoot, Sanitize(testName), DateTime.UtcNow.ToString("yyyyMMdd_HHmmss_fff"));
        Screenshots = Path.Combine(Root, "screenshots");
        OpenCv = Path.Combine(Root, "opencv");
        Logs = Path.Combine(Root, "logs");
        UiaDumps = Path.Combine(Root, "uia");
        Metadata = Path.Combine(Root, "metadata");

        Directory.CreateDirectory(Screenshots);
        Directory.CreateDirectory(OpenCv);
        Directory.CreateDirectory(Logs);
        Directory.CreateDirectory(UiaDumps);
        Directory.CreateDirectory(Metadata);
    }

    public string Root { get; }
    public string Screenshots { get; }
    public string OpenCv { get; }
    public string Logs { get; }
    public string UiaDumps { get; }
    public string Metadata { get; }

    private static string Sanitize(string value)
    {
        foreach (var invalid in Path.GetInvalidFileNameChars())
        {
            value = value.Replace(invalid, '_');
        }

        return value.Replace(' ', '_');
    }
}
