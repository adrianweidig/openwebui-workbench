using FlaUI.Core;
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;

namespace Product.UiTests.Uia3.Wpf;

[TestFixture]
[NonParallelizable]
public sealed class CustomerWorkflowTests
{
    private Application? _app;

    [TearDown]
    public void TearDown()
    {
        _app?.Close();
        _app?.Dispose();
    }

    [Test]
    public void Migrated_Eggplant_Wpf_Login_And_Customer_Save()
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
            var cf = automation.ConditionFactory;

            new LoginScreen(window, cf).Login(
                Environment.GetEnvironmentVariable("UI_TEST_UserName") ?? "test.operator",
                Environment.GetEnvironmentVariable("UI_TEST_Password") ?? "not-a-real-password");

            var customer = new CustomerScreen(window, cf);
            customer.SearchCustomer("CUST-4711");
            customer.UpdateNameAndSave("Musterkunde GmbH");

            Assert.That(customer.SaveToastVisible(), Is.True, "Customer.SaveSuccessToast muss erscheinen.");
        }
        catch (Exception ex)
        {
            FailureArtifactCollector.Collect(null, artifacts, TestContext.CurrentContext.Test.Name, ex);
            throw;
        }
    }
}
