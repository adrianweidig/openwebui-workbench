using Microsoft.Extensions.Configuration;

namespace Product.UiTests.Shared.Configuration;

public static class ConfigurationLoader
{
    public static TestConfiguration Load()
    {
        var config = new ConfigurationBuilder()
            .AddJsonFile("appsettings.uitests.json", optional: true)
            .AddEnvironmentVariables(prefix: "UI_TEST_")
            .Build();

        var result = config.Get<TestConfiguration>();
        if (result is null)
        {
            throw new InvalidOperationException("UI-Testkonfiguration konnte nicht geladen werden.");
        }

        if (string.IsNullOrWhiteSpace(result.AppUnderTestPath))
        {
            throw new InvalidOperationException("AppUnderTestPath fehlt. Setze UI_TEST_AppUnderTestPath.");
        }

        if (string.IsNullOrWhiteSpace(result.ArtifactRoot))
        {
            result = result.WithFallbackArtifactRoot();
        }

        return result;
    }

    private static TestConfiguration WithFallbackArtifactRoot(this TestConfiguration input)
    {
        return new TestConfiguration
        {
            AppUnderTestPath = input.AppUnderTestPath,
            ArtifactRoot = Path.Combine(Path.GetTempPath(), "Product.UiTests.Artifacts"),
            ScenarioRoot = input.ScenarioRoot,
            CalibrationRoot = input.CalibrationRoot,
            MainWindowTimeoutSeconds = input.MainWindowTimeoutSeconds,
            DisplayProfile = input.DisplayProfile
        };
    }
}
