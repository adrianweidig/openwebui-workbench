using TestStack.Decisions;
using Xunit;

namespace TestStack.Decisions.Tests;

public sealed class FrameworkDecisionMatrixTests
{
    [Fact]
    public void Decide_ForCSharpPlaywrightBrowserE2E_ReturnsDirectRecommendation()
    {
        var decision = FrameworkDecisionMatrix.Decide("C#", "Playwright", "Browser E2E");

        Assert.Equal(RecommendationLevel.DirectlyRecommended, decision.Recommendation);
        Assert.Contains("TRX", decision.PreferredCiPattern);
    }

    [Fact]
    public void Decide_ForAdaPlaywrightBrowserE2E_DoesNotInventNativeSupport()
    {
        var decision = FrameworkDecisionMatrix.Decide("Ada", "Playwright", "Browser E2E");

        Assert.Equal(RecommendationLevel.NotRecommended, decision.Recommendation);
        Assert.Contains("does not provide a native Ada binding", decision.Rationale);
    }

    [Fact]
    public void Decide_ForUnknownCombination_ReturnsNotDerivable()
    {
        var decision = FrameworkDecisionMatrix.Decide("Rust", "UnknownTool", "Browser E2E");

        Assert.Equal(RecommendationLevel.NotDerivable, decision.Recommendation);
        Assert.Contains("do not invent tool support", decision.PreferredCiPattern);
    }
}
