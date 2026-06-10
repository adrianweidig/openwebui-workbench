using FlaUI.Core;
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Uia3.Smoke;

[TestFixture]
[NonParallelizable]
public sealed class MainWindowSmokeTests
{
    private Application? _app;

    [TearDown]
    public void TearDown()
    {
        _app?.Close();
        _app?.Dispose();
    }

    [Test]
    public void MainWindow_Is_Visible_With_Uia3()
    {
        var config = ConfigurationLoader.Load();
        var artifacts = new ArtifactPaths(config.ArtifactRoot, TestContext.CurrentContext.Test.Name);

        using var automation = new UIA3Automation();
        var launcher = new AppLauncher();

        try
        {
            TestEnvironmentGuard.AssertDeterministicDesktop();

            _app = launcher.Launch(config.AppUnderTestPath, TimeSpan.FromSeconds(config.MainWindowTimeoutSeconds));
            var window = launcher.WaitForMainWindow(_app, automation, "ProductMainWindow", TimeSpan.FromSeconds(config.MainWindowTimeoutSeconds));

            Assert.That(window, Is.Not.Null);
            Assert.That(window.Properties.Name.ValueOrDefault, Is.Not.Null.And.Not.Empty);
        }
        catch (Exception ex)
        {
            FailureArtifactCollector.Collect(null, artifacts, TestContext.CurrentContext.Test.Name, ex);
            throw;
        }
    }
}
