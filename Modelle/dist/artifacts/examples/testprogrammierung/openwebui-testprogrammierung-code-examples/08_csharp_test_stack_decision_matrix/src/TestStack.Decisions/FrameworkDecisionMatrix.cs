namespace TestStack.Decisions;

public enum RecommendationLevel
{
    DirectlyRecommended,
    PossibleWithConstraints,
    NotRecommended,
    NotDerivable
}

public sealed record TestStackDecision(
    string Language,
    string Framework,
    string TestGoal,
    RecommendationLevel Recommendation,
    string Rationale,
    string PreferredCiPattern);

public static class FrameworkDecisionMatrix
{
    private static readonly IReadOnlyList<TestStackDecision> Decisions =
    [
        new("C#", "Playwright", "Browser E2E", RecommendationLevel.DirectlyRecommended,
            "Playwright has strong .NET support, auto-waiting, trace artifacts, and reliable headless CI execution.",
            "dotnet test plus Playwright browser installation and TRX publishing."),

        new("C#", "Selenium", "Browser E2E", RecommendationLevel.DirectlyRecommended,
            "Selenium WebDriver is established for cross-browser automation; explicit waits and stable selectors are mandatory.",
            "dotnet test with headless browser execution and TRX publishing."),

        new("Ada", "AUnit", "Unit tests", RecommendationLevel.DirectlyRecommended,
            "AUnit is suitable for Ada unit tests and can be executed with GNAT/gprbuild on a prepared agent.",
            "gprbuild test project, run AUnit harness, publish text or XML/JUnit artifacts when configured."),

        new("Ada", "GNATtest", "Generated unit-test skeletons", RecommendationLevel.DirectlyRecommended,
            "GNATtest generates AUnit-based skeletons and harnesses for visible Ada subprograms.",
            "gnattest -P project, build generated harness, run generated drivers on a self-hosted Ada agent."),

        new("Ada", "Playwright", "Browser E2E", RecommendationLevel.NotRecommended,
            "Playwright does not provide a native Ada binding suitable for direct browser E2E test authoring.",
            "Keep Ada tests in Ada; use a separate C# or supported-language browser E2E project if browser automation is required."),

        new("Ada", "Selenium", "Browser E2E", RecommendationLevel.PossibleWithConstraints,
            "A bridge or external process can be built, but it adds maintenance risk and is not a standard Selenium core-binding path.",
            "Prefer separate C# Selenium tests instead of mixing Ada production code with browser automation plumbing.")
    ];

    public static TestStackDecision Decide(string language, string framework, string testGoal)
    {
        var decision = Decisions.FirstOrDefault(item =>
            string.Equals(item.Language, language, StringComparison.OrdinalIgnoreCase) &&
            string.Equals(item.Framework, framework, StringComparison.OrdinalIgnoreCase) &&
            string.Equals(item.TestGoal, testGoal, StringComparison.OrdinalIgnoreCase));

        return decision ?? new TestStackDecision(
            language,
            framework,
            testGoal,
            RecommendationLevel.NotDerivable,
            "The combination cannot be assessed without more project context.",
            "Ask for language, framework, test type, target system, and CI environment; do not invent tool support.");
    }
}
