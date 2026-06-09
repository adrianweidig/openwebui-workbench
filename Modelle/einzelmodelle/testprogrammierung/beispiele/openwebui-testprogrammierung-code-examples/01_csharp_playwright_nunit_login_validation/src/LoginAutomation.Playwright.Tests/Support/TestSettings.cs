namespace LoginAutomation.Playwright.Tests.Support;

public sealed record TestSettings(Uri BaseUrl, TimeSpan AssertionTimeout)
{
    public static TestSettings FromEnvironment()
    {
        // The example uses environment variables so no URL, token, user name, or password is hard-coded.
        var rawBaseUrl = Environment.GetEnvironmentVariable("APP_BASE_URL") ?? "https://example.test";
        if (!Uri.TryCreate(rawBaseUrl, UriKind.Absolute, out var baseUrl))
        {
            throw new InvalidOperationException("APP_BASE_URL must be an absolute URL, for example https://test.example.com.");
        }

        var rawTimeoutSeconds = Environment.GetEnvironmentVariable("ASSERTION_TIMEOUT_SECONDS") ?? "10";
        if (!double.TryParse(rawTimeoutSeconds, out var timeoutSeconds) || timeoutSeconds <= 0)
        {
            throw new InvalidOperationException("ASSERTION_TIMEOUT_SECONDS must be a positive number.");
        }

        return new TestSettings(baseUrl, TimeSpan.FromSeconds(timeoutSeconds));
    }
}
