using System.Runtime.InteropServices;

namespace Product.UiTests.Shared.Infrastructure;

public static class TestEnvironmentGuard
{
    public static void AssertDeterministicDesktop()
    {
        var width = GetSystemMetrics(0);
        var height = GetSystemMetrics(1);

        if (width != 1920 || height != 1080)
        {
            throw new InvalidOperationException($"Falsche Auflösung: {width}x{height}. Erwartet: 1920x1080.");
        }

        using var graphics = System.Drawing.Graphics.FromHwnd(IntPtr.Zero);
        if (Math.Round(graphics.DpiX) != 96 || Math.Round(graphics.DpiY) != 96)
        {
            throw new InvalidOperationException($"Falsche DPI: {graphics.DpiX}x{graphics.DpiY}. Erwartet: 96x96.");
        }
    }

    [DllImport("user32.dll")]
    private static extern int GetSystemMetrics(int nIndex);
}
