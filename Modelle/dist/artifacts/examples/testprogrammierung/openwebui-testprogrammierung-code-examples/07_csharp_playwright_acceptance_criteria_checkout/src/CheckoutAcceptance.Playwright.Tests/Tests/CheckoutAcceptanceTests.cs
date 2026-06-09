using CheckoutAcceptance.Playwright.Tests.Pages;
using CheckoutAcceptance.Playwright.Tests.Support;
using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;

namespace CheckoutAcceptance.Playwright.Tests.Tests;

public sealed class CheckoutAcceptanceTests : PageTest
{
    private static readonly CheckoutSettings Settings = CheckoutSettings.FromEnvironment();

    public override BrowserNewContextOptions ContextOptions()
    {
        return new BrowserNewContextOptions
        {
            BaseURL = Settings.BaseUrl.ToString().TrimEnd('/'),
            ViewportSize = new ViewportSize { Width = 1366, Height = 768 }
        };
    }

    [Test]
    public async Task Checkout_WhenExpiredVoucherIsApplied_ShowsValidationAndKeepsOriginalTotal()
    {
        // Acceptance criterion covered by this test:
        // Given a customer has an item in the cart, when an expired voucher is applied,
        // then the voucher is rejected and the cart total remains unchanged.
        var cart = new CartPage(Page);

        await cart.OpenAsync(Settings.BaseUrl);
        await cart.AddKnownProductAsync(Settings.ProductSku);

        var originalTotal = await cart.ReadTotalTextAsync();

        await cart.ApplyVoucherAsync(Settings.ExpiredVoucherCode);

        await Expect(cart.VoucherError).ToHaveTextAsync("Voucher has expired");
        await Expect(cart.CartTotal).ToHaveTextAsync(originalTotal);
    }
}
