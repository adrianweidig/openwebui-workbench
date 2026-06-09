using Microsoft.Playwright;

namespace CheckoutAcceptance.Playwright.Tests.Pages;

public sealed class CartPage
{
    private readonly IPage _page;

    public CartPage(IPage page)
    {
        _page = page;
    }

    public ILocator CartTotal => _page.GetByTestId("cart-total");
    public ILocator VoucherInput => _page.GetByLabel("Voucher code");
    public ILocator ApplyVoucherButton => _page.GetByRole(AriaRole.Button, new() { Name = "Apply voucher" });
    public ILocator VoucherError => _page.GetByTestId("voucher-error");

    public async Task OpenAsync(Uri baseUrl)
    {
        await _page.GotoAsync(new Uri(baseUrl, "/cart").ToString(), new PageGotoOptions
        {
            WaitUntil = WaitUntilState.DOMContentLoaded
        });
    }

    public async Task AddKnownProductAsync(string sku)
    {
        // The product SKU is test data. The selector remains stable because it is built from a data-testid contract.
        await _page.GetByTestId($"add-product-{sku}").ClickAsync();
        await _page.GetByTestId($"cart-line-{sku}").WaitForAsync(new LocatorWaitForOptions { State = WaitForSelectorState.Visible });
    }

    public async Task<string> ReadTotalTextAsync()
    {
        return (await CartTotal.InnerTextAsync()).Trim();
    }

    public async Task ApplyVoucherAsync(string voucherCode)
    {
        await VoucherInput.FillAsync(voucherCode);
        await ApplyVoucherButton.ClickAsync();
    }
}
