using FlaUI.Core.AutomationElements;
using FlaUI.Core.Capturing;

namespace Product.UiTests.Shared.Diagnostics;

public static class ScreenshotService
{
    public static string CaptureWindow(Window window, string directory, string fileName)
    {
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, fileName);
        Capture.Element(window).ToFile(path);
        return path;
    }

    public static string CaptureElement(AutomationElement element, string directory, string fileName)
    {
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, fileName);
        Capture.Element(element).ToFile(path);
        return path;
    }
}
