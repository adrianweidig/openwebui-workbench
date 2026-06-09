using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;

namespace SeleniumAutomation.Xunit.Tests.Support;

public static class WebDriverFactory
{
    public static IWebDriver CreateChrome(SeleniumTestSettings settings)
    {
        var options = new ChromeOptions();

        if (settings.Headless)
        {
            options.AddArgument("--headless=new");
        }

        // These arguments improve reliability on Linux build agents without changing test intent.
        options.AddArgument("--window-size=1280,720");
        options.AddArgument("--disable-dev-shm-usage");
        options.AddArgument("--no-sandbox");

        var driver = new ChromeDriver(options);

        // Use explicit waits only. Mixing implicit and explicit waits makes timing failures harder to diagnose.
        driver.Manage().Timeouts().ImplicitWait = TimeSpan.Zero;
        driver.Manage().Timeouts().PageLoad = TimeSpan.FromSeconds(30);

        return driver;
    }
}
