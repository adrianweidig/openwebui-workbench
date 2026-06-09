using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using SeleniumAutomation.Xunit.Tests.Support;

namespace SeleniumAutomation.Xunit.Tests.Pages;

public sealed class HomePage
{
    private static readonly By AppShell = By.CssSelector("[data-testid='app-shell']");
    private static readonly By Heading = By.CssSelector("[data-testid='home-heading']");
    private static readonly By PrimaryActionButton = By.CssSelector("[data-testid='primary-action']");
    private static readonly By ResultMessage = By.CssSelector("[data-testid='primary-action-result']");

    private readonly IWebDriver _driver;
    private readonly WebDriverWait _wait;

    public HomePage(IWebDriver driver, TimeSpan waitTimeout)
    {
        _driver = driver;
        _wait = new WebDriverWait(driver, waitTimeout);
    }

    public void Open(Uri baseUrl)
    {
        _driver.Navigate().GoToUrl(new Uri(baseUrl, "/").ToString());
        _wait.UntilVisible(AppShell);
    }

    public string ReadHeading()
    {
        return _wait.UntilVisible(Heading).Text.Trim();
    }

    public string ClickPrimaryActionAndReadResult()
    {
        _wait.UntilClickable(PrimaryActionButton).Click();
        return _wait.UntilVisible(ResultMessage).Text.Trim();
    }
}
