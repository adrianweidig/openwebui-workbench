using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Shared.Screens;

public abstract class ScreenBase
{
    protected ScreenBase(Window window, ConditionFactory cf)
    {
        Window = window;
        Cf = cf;
    }

    protected Window Window { get; }
    protected ConditionFactory Cf { get; }

    protected AutomationElement ByAutomationId(string automationId, TimeSpan? timeout = null)
    {
        return Waiter.UntilElement(
            () => Window.FindFirstDescendant(Cf.ByAutomationId(automationId)),
            timeout ?? TimeSpan.FromSeconds(10),
            automationId);
    }
}
