using Microsoft.Playwright;

namespace LoginAutomation.Playwright.Tests.Pages;

public sealed class LoginPage
{
    private readonly IPage _page;

    public LoginPage(IPage page)
    {
        _page = page;
    }

    // Prefer accessibility-first selectors and stable test IDs over CSS classes that may change during styling work.
    public ILocator EmailInput => _page.GetByLabel("Email");
    public ILocator PasswordInput => _page.GetByLabel("Password");
    public ILocator SubmitButton => _page.GetByRole(AriaRole.Button, new() { Name = "Sign in" });
    public ILocator EmailRequiredError => _page.GetByTestId("login-email-required-error");
    public ILocator PasswordRequiredError => _page.GetByTestId("login-password-required-error");

    public async Task OpenAsync(Uri baseUrl)
    {
        // DOMContentLoaded is enough here; assertions below wait for user-visible state explicitly.
        await _page.GotoAsync(new Uri(baseUrl, "/login").ToString(), new PageGotoOptions
        {
            WaitUntil = WaitUntilState.DOMContentLoaded
        });
    }

    public async Task SubmitEmptyFormAsync()
    {
        await SubmitButton.ClickAsync();
    }
}
