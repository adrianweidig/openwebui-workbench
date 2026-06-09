namespace ApiContract.Xunit.Tests.Support;

public sealed record ApiTestSettings(Uri BaseUrl, TimeSpan Timeout)
{
    public static ApiTestSettings FromEnvironment()
    {
        var rawBaseUrl = Environment.GetEnvironmentVariable("API_BASE_URL") ?? "https://example.test";
        if (!Uri.TryCreate(rawBaseUrl, UriKind.Absolute, out var baseUrl))
        {
            throw new InvalidOperationException("API_BASE_URL must be an absolute URL.");
        }

        return new ApiTestSettings(baseUrl, TimeSpan.FromSeconds(20));
    }
}
