using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;

namespace Product.UiTests.Shared.Infrastructure;

public sealed class AppLauncher
{
    public Application Launch(string executablePath, TimeSpan timeout)
    {
        if (!File.Exists(executablePath))
        {
            throw new FileNotFoundException("AUT wurde nicht gefunden.", executablePath);
        }

        var app = Application.Launch(executablePath);
        Retry.WhileFalse(() => app.HasExited == false, timeout: timeout, throwOnTimeout: true);
        return app;
    }

    public Window WaitForMainWindow(Application app, FlaUI.Core.AutomationBase automation, string automationId, TimeSpan timeout)
    {
        Window? result = null;

        Retry.WhileNull(
            () =>
            {
                result = app.GetAllTopLevelWindows(automation)
                    .FirstOrDefault(w =>
                        string.Equals(w.Properties.AutomationId.ValueOrDefault, automationId, StringComparison.Ordinal) ||
                        (w.Properties.Name.ValueOrDefault ?? string.Empty).Contains("Product", StringComparison.OrdinalIgnoreCase));

                return result;
            },
            timeout: timeout,
            interval: TimeSpan.FromMilliseconds(250),
            throwOnTimeout: true);

        return result ?? throw new InvalidOperationException($"Hauptfenster nicht gefunden: {automationId}");
    }
}
