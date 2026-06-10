using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Shared.Screens;

public sealed class CustomerScreen
{
    private readonly Window _window;
    private readonly ConditionFactory _cf;

    public CustomerScreen(Window window, ConditionFactory cf)
    {
        _window = window;
        _cf = cf;
    }

    public void SearchCustomer(string customerId)
    {
        var search = Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Dashboard.CustomerSearchBox")),
            TimeSpan.FromSeconds(20),
            "Dashboard.CustomerSearchBox").AsTextBox();

        search.Text = string.Empty;
        search.Enter(customerId);

        Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Dashboard.SearchButton")),
            TimeSpan.FromSeconds(10),
            "Dashboard.SearchButton").AsButton().Invoke();

        Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Customer.DetailView")),
            TimeSpan.FromSeconds(10),
            "Customer.DetailView");
    }

    public void UpdateNameAndSave(string customerName)
    {
        var name = Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Customer.NameTextBox")),
            TimeSpan.FromSeconds(10),
            "Customer.NameTextBox").AsTextBox();

        name.Text = string.Empty;
        name.Enter(customerName);

        Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Customer.SaveButton")),
            TimeSpan.FromSeconds(10),
            "Customer.SaveButton").AsButton().Invoke();
    }

    public bool SaveToastVisible()
    {
        return _window.FindFirstDescendant(_cf.ByAutomationId("Customer.SaveSuccessToast")) is not null;
    }
}
