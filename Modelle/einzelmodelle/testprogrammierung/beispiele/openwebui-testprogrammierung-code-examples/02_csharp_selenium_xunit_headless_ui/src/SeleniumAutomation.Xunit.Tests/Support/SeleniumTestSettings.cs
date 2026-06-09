namespace SeleniumAutomation.Xunit.Tests.Support;

public sealed record SeleniumTestSettings(Uri BaseUrl, bool Headless, TimeSpan WaitTimeout, string ArtifactDirectory)
{
    public static SeleniumTestSettings FromEnvironment()
    {
        var rawBaseUrl = Environment.GetEnvironmentVariable("APP_BASE_URL") ?? "https://example.test";
        if (!Uri.TryCreate(rawBaseUrl, UriKind.Absolute, out var baseUrl))
        {
            throw new InvalidOperationException("APP_BASE_URL must be an absolute URL.");
        }

        var headless = !string.Equals(Environment.GetEnvironmentVariable("HEADLESS"), "0", StringComparison.OrdinalIgnoreCase);
        var artifactDirectory = Environment.GetEnvironmentVariable("TEST_ARTIFACT_DIR") ?? Path.Combine(Environment.CurrentDirectory, "artifacts");

        return new SeleniumTestSettings(baseUrl, headless, TimeSpan.FromSeconds(15), artifactDirectory);
    }
}
