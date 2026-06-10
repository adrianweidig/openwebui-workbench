using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;

namespace Product.UiTests.Shared.Infrastructure;

public static class Waiter
{
    public static T UntilNotNull<T>(Func<T?> producer, TimeSpan timeout, string description) where T : class
    {
        T? value = null;
        Retry.WhileNull(
            () =>
            {
                value = producer();
                return value;
            },
            timeout: timeout,
            interval: TimeSpan.FromMilliseconds(200),
            throwOnTimeout: false);

        return value ?? throw new TimeoutException($"Timeout beim Warten auf: {description}");
    }

    public static AutomationElement UntilElement(Func<AutomationElement?> producer, TimeSpan timeout, string automationId)
    {
        return UntilNotNull(producer, timeout, $"AutomationElement '{automationId}'");
    }
}
