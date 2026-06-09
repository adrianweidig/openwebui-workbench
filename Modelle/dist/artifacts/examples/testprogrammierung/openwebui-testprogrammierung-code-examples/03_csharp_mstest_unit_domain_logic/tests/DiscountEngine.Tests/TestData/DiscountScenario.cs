using DiscountEngine;

namespace DiscountEngine.Tests.TestData;

public sealed record DiscountScenario(
    decimal GrossAmount,
    CustomerSegment Segment,
    DateOnly PurchaseDate,
    decimal ExpectedNetAmount,
    string RuleDescription);
