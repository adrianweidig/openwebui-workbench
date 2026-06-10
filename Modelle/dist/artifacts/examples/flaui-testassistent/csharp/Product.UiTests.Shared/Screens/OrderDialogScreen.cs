using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Shared.Screens;

public sealed class OrderDialogScreen
{
    private readonly Window _window;
    private readonly ConditionFactory _cf;

    public OrderDialogScreen(Window window, ConditionFactory cf)
    {
        _window = window;
        _cf = cf;
    }

    public void OpenOrder(string orderNumber)
    {
        Waiter.UntilElement(() => _window.FindFirstDescendant(_cf.ByAutomationId("Menu.Orders")), TimeSpan.FromSeconds(10), "Menu.Orders").AsButton().Invoke();
        Waiter.UntilElement(() => _window.FindFirstDescendant(_cf.ByAutomationId("Orders.OpenByNumber")), TimeSpan.FromSeconds(10), "Orders.OpenByNumber").AsButton().Invoke();

        var orderBox = Waiter.UntilElement(() => _window.FindFirstDescendant(_cf.ByAutomationId("Orders.OrderNumberTextBox")), TimeSpan.FromSeconds(10), "Orders.OrderNumberTextBox").AsTextBox();
        orderBox.Text = string.Empty;
        orderBox.Enter(orderNumber);

        Waiter.UntilElement(() => _window.FindFirstDescendant(_cf.ByAutomationId("Orders.Search")), TimeSpan.FromSeconds(10), "Orders.Search").AsButton().Invoke();
        Waiter.UntilElement(() => _window.FindFirstDescendant(_cf.ByAutomationId("OrderDialog")), TimeSpan.FromSeconds(10), "OrderDialog");
    }

    public string StatusText()
    {
        return Waiter.UntilElement(() => _window.FindFirstDescendant(_cf.ByAutomationId("OrderDialog.StatusLabel")), TimeSpan.FromSeconds(10), "OrderDialog.StatusLabel").Name;
    }

    public void Close()
    {
        Waiter.UntilElement(() => _window.FindFirstDescendant(_cf.ByAutomationId("OrderDialog.CloseButton")), TimeSpan.FromSeconds(10), "OrderDialog.CloseButton").AsButton().Invoke();
    }
}
