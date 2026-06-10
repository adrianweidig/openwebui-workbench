using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Shared.Screens;

public sealed class AircraftMapScreen
{
    private readonly Window _window;
    private readonly ConditionFactory _cf;

    public AircraftMapScreen(Window window, ConditionFactory cf)
    {
        _window = window;
        _cf = cf;
    }

    public AutomationElement MapCanvas => Waiter.UntilElement(
        () => _window.FindFirstDescendant(_cf.ByAutomationId("AircraftMapCanvas")),
        TimeSpan.FromSeconds(10),
        "AircraftMapCanvas");

    public void LoadScenario(string scenarioId)
    {
        var scenarioBox = Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.ScenarioIdTextBox")),
            TimeSpan.FromSeconds(10),
            "TestHooks.ScenarioIdTextBox").AsTextBox();

        scenarioBox.Text = string.Empty;
        scenarioBox.Enter(scenarioId);

        Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.LoadScenarioButton")),
            TimeSpan.FromSeconds(10),
            "TestHooks.LoadScenarioButton").AsButton().Invoke();
    }

    public void SetSimulationTime(DateTime utc)
    {
        var timeBox = Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.SimulationTimeTextBox")),
            TimeSpan.FromSeconds(10),
            "TestHooks.SimulationTimeTextBox").AsTextBox();

        timeBox.Text = string.Empty;
        timeBox.Enter(utc.ToString("O"));
    }

    public void SetZoom(string zoomLevel)
    {
        var zoomBox = Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.MapZoomTextBox")),
            TimeSpan.FromSeconds(10),
            "TestHooks.MapZoomTextBox").AsTextBox();

        zoomBox.Text = string.Empty;
        zoomBox.Enter(zoomLevel);
    }

    public void RenderFrame()
    {
        Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.RenderFrameButton")),
            TimeSpan.FromSeconds(10),
            "TestHooks.RenderFrameButton").AsButton().Invoke();
    }
}
