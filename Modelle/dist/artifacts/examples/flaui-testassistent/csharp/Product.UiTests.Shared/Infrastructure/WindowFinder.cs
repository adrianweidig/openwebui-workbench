using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;

namespace Product.UiTests.Shared.Infrastructure;

public static class WindowFinder
{
    public static Window ByAutomationId(Application app, FlaUI.Core.AutomationBase automation, string automationId, TimeSpan timeout)
    {
        Window? window = null;

        Retry.WhileNull(
            () =>
            {
                window = app.GetAllTopLevelWindows(automation)
                    .FirstOrDefault(w => string.Equals(w.Properties.AutomationId.ValueOrDefault, automationId, StringComparison.Ordinal));
                return window;
            },
            timeout: timeout,
            interval: TimeSpan.FromMilliseconds(250),
            throwOnTimeout: false);

        return window ?? throw new TimeoutException($"Fenster mit AutomationId '{automationId}' wurde nicht gefunden.");
    }
}
