using OpenQA.Selenium;
using SeleniumAutomation.Xunit.Tests.Pages;
using SeleniumAutomation.Xunit.Tests.Support;
using Xunit;

namespace SeleniumAutomation.Xunit.Tests.Tests;

public sealed class HomeInteractionTests : IDisposable
{
    private readonly SeleniumTestSettings _settings = SeleniumTestSettings.FromEnvironment();
    private readonly IWebDriver _driver;

    public HomeInteractionTests()
    {
        _driver = WebDriverFactory.CreateChrome(_settings);
    }

    [Fact]
    public void HomePage_PrimaryAction_ShowsExpectedResultMessage()
    {
        try
        {
            var page = new HomePage(_driver, _settings.WaitTimeout);

            page.Open(_settings.BaseUrl);

            Assert.Equal("Welcome", page.ReadHeading());
            Assert.Equal("Action completed", page.ClickPrimaryActionAndReadResult());
        }
        catch
        {
            ArtifactWriter.TryCaptureScreenshot(_driver, _settings.ArtifactDirectory, nameof(HomePage_PrimaryAction_ShowsExpectedResultMessage));
            throw;
        }
    }

    public void Dispose()
    {
        _driver.Quit();
        _driver.Dispose();
    }
}
