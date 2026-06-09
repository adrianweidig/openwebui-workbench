using OpenQA.Selenium;

namespace SeleniumAutomation.Xunit.Tests.Support;

public static class ArtifactWriter
{
    public static void TryCaptureScreenshot(IWebDriver driver, string artifactDirectory, string testName)
    {
        if (driver is not ITakesScreenshot screenshotDriver)
        {
            return;
        }

        Directory.CreateDirectory(artifactDirectory);
        var safeName = string.Concat(testName.Select(ch => char.IsLetterOrDigit(ch) ? ch : '_'));
        var path = Path.Combine(artifactDirectory, $"{safeName}.png");

        // Writing bytes avoids Selenium API differences around Screenshot.SaveAsFile overloads.
        File.WriteAllBytes(path, screenshotDriver.GetScreenshot().AsByteArray);
    }
}
