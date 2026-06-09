using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;

namespace SeleniumAutomation.Xunit.Tests.Support;

public static class WaitExtensions
{
    public static IWebElement UntilVisible(this WebDriverWait wait, By locator)
    {
        wait.IgnoreExceptionTypes(typeof(NoSuchElementException), typeof(StaleElementReferenceException));

        return wait.Until(driver =>
        {
            var element = driver.FindElement(locator);
            return element.Displayed ? element : null;
        })!;
    }

    public static IWebElement UntilClickable(this WebDriverWait wait, By locator)
    {
        wait.IgnoreExceptionTypes(typeof(NoSuchElementException), typeof(StaleElementReferenceException));

        return wait.Until(driver =>
        {
            var element = driver.FindElement(locator);
            return element.Displayed && element.Enabled ? element : null;
        })!;
    }
}
