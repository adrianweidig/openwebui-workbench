namespace DiscountEngine;

public enum CustomerSegment
{
    Standard,
    Loyalty,
    Employee
}

public sealed class DiscountCalculator
{
    public decimal CalculateNetAmount(decimal grossAmount, CustomerSegment segment, DateOnly purchaseDate)
    {
        if (grossAmount < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(grossAmount), "Gross amount must not be negative.");
        }

        var segmentDiscount = segment switch
        {
            CustomerSegment.Standard => 0.00m,
            CustomerSegment.Loyalty => 0.10m,
            CustomerSegment.Employee => 0.30m,
            _ => throw new ArgumentOutOfRangeException(nameof(segment), segment, "Unknown customer segment.")
        };

        var seasonalDiscount = purchaseDate.Month == 11 && purchaseDate.Day == 29 ? 0.05m : 0.00m;

        // The cap keeps combined discounts predictable and protects against accidental over-discounting.
        var totalDiscount = Math.Min(segmentDiscount + seasonalDiscount, 0.35m);
        var netAmount = grossAmount * (1 - totalDiscount);

        return decimal.Round(netAmount, 2, MidpointRounding.AwayFromZero);
    }
}
