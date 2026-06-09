using LoginAutomation.Playwright.Tests.Pages;
using LoginAutomation.Playwright.Tests.Support;
using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;
using NUnit.Framework.Interfaces;

namespace LoginAutomation.Playwright.Tests.Tests;

[Parallelizable(ParallelScope.Self)]
public sealed class LoginValidationTests : PageTest
{
    private static readonly TestSettings Settings = TestSettings.FromEnvironment();

    public override BrowserNewContextOptions ContextOptions()
    {
        return new BrowserNewContextOptions
        {
            BaseURL = Settings.BaseUrl.ToString().TrimEnd('/'),
            Locale = "en-US",
            ViewportSize = new ViewportSize { Width = 1280, Height = 720 },
            IgnoreHTTPSErrors = false,

            // Record video only when explicitly requested; artifacts can be large in CI.
            RecordVideoDir = Environment.GetEnvironmentVariable("PWVIDEO") == "1" ? "artifacts/videos" : null
        };
    }

    [SetUp]
    public void ConfigureTimeouts()
    {
        // A single explicit default timeout keeps waits deterministic and avoids Thread.Sleep.
        Page.SetDefaultTimeout((float)Settings.AssertionTimeout.TotalMilliseconds);
    }

    [Test]
    public async Task Login_WithEmptyRequiredFields_ShowsSpecificInlineValidationMessages()
    {
        var login = new LoginPage(Page);

        await login.OpenAsync(Settings.BaseUrl);

        await Expect(login.EmailInput).ToBeVisibleAsync();
        await Expect(login.PasswordInput).ToBeVisibleAsync();

        await login.SubmitEmptyFormAsync();

        // Assertions verify user-observable behavior rather than implementation details.
        await Expect(login.EmailRequiredError).ToHaveTextAsync("Email is required");
        await Expect(login.PasswordRequiredError).ToHaveTextAsync("Password is required");
    }

    [TearDown]
    public async Task CaptureFailureArtifactsAsync()
    {
        if (TestContext.CurrentContext.Result.Outcome.Status != TestStatus.Failed)
        {
            return;
        }

        var artifactsDirectory = Path.Combine(TestContext.CurrentContext.WorkDirectory, "artifacts");
        Directory.CreateDirectory(artifactsDirectory);

        var safeTestName = string.Concat(TestContext.CurrentContext.Test.Name.Select(ch => char.IsLetterOrDigit(ch) ? ch : '_'));
        var screenshotPath = Path.Combine(artifactsDirectory, $"{safeTestName}.png");

        await Page.ScreenshotAsync(new PageScreenshotOptions
        {
            Path = screenshotPath,
            FullPage = true
        });

        TestContext.AddTestAttachment(screenshotPath, "Failure screenshot captured by Playwright.");
    }
}
