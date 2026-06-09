namespace CheckoutAcceptance.Playwright.Tests.Support;

public sealed record CheckoutSettings(Uri BaseUrl, string ProductSku, string ExpiredVoucherCode)
{
    public static CheckoutSettings FromEnvironment()
    {
        var baseUrl = Environment.GetEnvironmentVariable("APP_BASE_URL") ?? "https://example.test";

        return new CheckoutSettings(
            new Uri(baseUrl, UriKind.Absolute),
            Environment.GetEnvironmentVariable("CHECKOUT_PRODUCT_SKU") ?? "SKU-TEST-001",
            Environment.GetEnvironmentVariable("EXPIRED_VOUCHER_CODE") ?? "EXPIRED-TEST-VOUCHER");
    }
}
