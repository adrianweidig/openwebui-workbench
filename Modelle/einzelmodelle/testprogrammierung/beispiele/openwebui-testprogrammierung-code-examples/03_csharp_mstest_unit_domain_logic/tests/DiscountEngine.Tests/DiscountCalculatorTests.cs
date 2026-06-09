using DiscountEngine.Tests.TestData;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace DiscountEngine.Tests;

[TestClass]
public sealed class DiscountCalculatorTests
{
    public static IEnumerable<object[]> SupportedDiscountScenarios
    {
        get
        {
            yield return Scenario(100.00m, CustomerSegment.Standard, new DateOnly(2026, 1, 15), 100.00m, "Standard customers receive no default discount.");
            yield return Scenario(100.00m, CustomerSegment.Loyalty, new DateOnly(2026, 1, 15), 90.00m, "Loyalty customers receive a 10 percent discount.");
            yield return Scenario(100.00m, CustomerSegment.Employee, new DateOnly(2026, 1, 15), 70.00m, "Employees receive a 30 percent discount.");
            yield return Scenario(100.00m, CustomerSegment.Loyalty, new DateOnly(2026, 11, 29), 85.00m, "Loyalty and seasonal discounts are cumulative.");
            yield return Scenario(100.00m, CustomerSegment.Employee, new DateOnly(2026, 11, 29), 65.00m, "Combined discounts are capped at 35 percent.");
        }
    }

    [DataTestMethod]
    [DynamicData(nameof(SupportedDiscountScenarios), DynamicDataSourceType.Property)]
    public void CalculateNetAmount_ForSupportedScenario_ReturnsExpectedAmount(DiscountScenario scenario)
    {
        var calculator = new DiscountCalculator();

        var actual = calculator.CalculateNetAmount(scenario.GrossAmount, scenario.Segment, scenario.PurchaseDate);

        Assert.AreEqual(scenario.ExpectedNetAmount, actual, scenario.RuleDescription);
    }

    [TestMethod]
    public void CalculateNetAmount_WhenGrossAmountIsNegative_ThrowsClearException()
    {
        var calculator = new DiscountCalculator();

        var exception = Assert.ThrowsExactly<ArgumentOutOfRangeException>(() =>
            calculator.CalculateNetAmount(-0.01m, CustomerSegment.Standard, new DateOnly(2026, 1, 15)));

        StringAssert.Contains(exception.Message, "Gross amount must not be negative");
    }

    private static object[] Scenario(decimal grossAmount, CustomerSegment segment, DateOnly purchaseDate, decimal expectedNetAmount, string ruleDescription)
    {
        return
        [
            new DiscountScenario(grossAmount, segment, purchaseDate, expectedNetAmount, ruleDescription)
        ];
    }
}
