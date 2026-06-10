using FlaUI.Core;
using FlaUI.UIA2;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;

namespace Product.UiTests.Uia2.WinForms;

[TestFixture]
[NonParallelizable]
public sealed class LegacyOrderDialogMigrationTests
{
    private Application? _app;

    [TearDown]
    public void TearDown()
    {
        _app?.Close();
        _app?.Dispose();
    }

    [Test]
    public void Migrated_Eggplant_WinForms_Order_Dialog()
    {
        var config = ConfigurationLoader.Load();
        var artifacts = new ArtifactPaths(config.ArtifactRoot, TestContext.CurrentContext.Test.Name);

        using var automation = new UIA2Automation();
        var launcher = new AppLauncher();

        try
        {
            TestEnvironmentGuard.AssertDeterministicDesktop();

            _app = launcher.Launch(config.AppUnderTestPath, TimeSpan.FromSeconds(config.MainWindowTimeoutSeconds));
            var window = launcher.WaitForMainWindow(_app, automation, "LegacyShell", TimeSpan.FromSeconds(config.MainWindowTimeoutSeconds));
            var screen = new OrderDialogScreen(window, automation.ConditionFactory);

            screen.OpenOrder("ORD-2026-00042");

            Assert.That(screen.StatusText(), Does.Contain("Freigegeben"));

            screen.Close();
        }
        catch (Exception ex)
        {
            FailureArtifactCollector.Collect(null, artifacts, TestContext.CurrentContext.Test.Name, ex);
            throw;
        }
    }
}
