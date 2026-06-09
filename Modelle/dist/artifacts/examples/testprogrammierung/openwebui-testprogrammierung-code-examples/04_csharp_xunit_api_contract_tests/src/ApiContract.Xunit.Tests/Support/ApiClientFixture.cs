using System.Net.Http.Headers;

namespace ApiContract.Xunit.Tests.Support;

public sealed class ApiClientFixture : IDisposable
{
    public ApiTestSettings Settings { get; } = ApiTestSettings.FromEnvironment();
    public HttpClient Client { get; }

    public ApiClientFixture()
    {
        Client = new HttpClient
        {
            BaseAddress = Settings.BaseUrl,
            Timeout = Settings.Timeout
        };

        // Tests request JSON explicitly and do not rely on server defaults.
        Client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

        var bearerToken = Environment.GetEnvironmentVariable("API_BEARER_TOKEN");
        if (!string.IsNullOrWhiteSpace(bearerToken))
        {
            // Secrets are injected by CI/CD secret stores, never committed in source files.
            Client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", bearerToken);
        }
    }

    public void Dispose()
    {
        Client.Dispose();
    }
}
