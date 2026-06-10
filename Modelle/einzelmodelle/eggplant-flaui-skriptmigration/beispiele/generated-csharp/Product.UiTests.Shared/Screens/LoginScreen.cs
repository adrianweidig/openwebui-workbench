using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Shared.Screens;

public sealed class LoginScreen
{
    private readonly Window _window;
    private readonly ConditionFactory _cf;

    public LoginScreen(Window window, ConditionFactory cf)
    {
        _window = window;
        _cf = cf;
    }

    public void Login(string userName, string password)
    {
        var userNameBox = Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Login.UserNameField")),
            TimeSpan.FromSeconds(10),
            "Login.UserNameField").AsTextBox();

        userNameBox.Text = string.Empty;
        userNameBox.Enter(userName);

        var passwordBox = Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Login.PasswordField")),
            TimeSpan.FromSeconds(10),
            "Login.PasswordField").AsTextBox();

        passwordBox.Text = string.Empty;
        passwordBox.Enter(password);

        Waiter.UntilElement(
            () => _window.FindFirstDescendant(_cf.ByAutomationId("Login.SubmitButton")),
            TimeSpan.FromSeconds(10),
            "Login.SubmitButton").AsButton().Invoke();
    }
}
