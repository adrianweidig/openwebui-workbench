Golden Example – flaui-testassistent
Nutzeraufgabe

Analysiere den folgenden FlaUI-Test. Er ist in der CI instabil und schlägt besonders auf dem Azure-DevOps-Server-Agenten mit 125-%-DPI fehl.

C#
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.Input;
using FlaUI.UIA3;
using NUnit.Framework;

namespace Product.UiTests.Uia3.Smoke;

[TestFixture]
public sealed class FlakyCoordinateClickTest
{
    [Test]
    public void StartsWorkflow()
    {
        using var app = Application.Launch("C:\\Apps\\Product\\Product.Client.exe");
        using var automation = new UIA3Automation();

        var window = app.GetMainWindow(automation);
        Thread.Sleep(3000);

        Mouse.Click(window.BoundingRectangle.Left + 420, window.BoundingRectangle.Top + 280);

        Thread.Sleep(2000);

        var status = window.FindFirstDescendant(cf => cf.ByName("Bereit"));
        Assert.IsNotNull(status);
    }
}
Ideale Antwort
Kurzbewertung

Der Test prüft einen relevanten Smoke-Ablauf, ist aber für CI/CD nicht stabil genug. Die Hauptursachen sind der koordinatenbasierte Klick, feste Sleeps, ein nicht abgesicherter Zugriff auf das Hauptfenster und fehlende Fehlerartefakte. Für WPF ist FlaUI.UIA3 korrekt, die Teststruktur sollte aber auf Screen-Object, robuste Waits, Assert.That und Screenshot-/UIA-Dump-Artefakte umgestellt werden.

Findings
Schwere	Datei/Stelle	Problem	Empfehlung
Hoch	FlakyCoordinateClickTest.cs, Mouse.Click(...)	Klick auf absolute Koordinaten relativ zum Fenster. Das bricht bei DPI, Fensterposition, Skalierung und Layoutänderungen.	Button über stabile AutomationId suchen, z. B. StartWorkflowButton, und per FlaUI klicken.
Hoch	Thread.Sleep(3000) und Thread.Sleep(2000)	Statische Wartezeiten prüfen keinen fachlichen Zustand und verursachen Flakiness auf langsamen Agenten.	Waiter.UntilNotNull und zustandsbasierte Wartebedingungen verwenden.
Hoch	app.GetMainWindow(automation)	Hauptfenster wird ohne Timeout, Titelprüfung oder Fehlerdiagnose übernommen.	WindowFinder.WaitForMainWindow mit explizitem Timeout nutzen.
Mittel	Assert.IsNotNull(status)	MSTest-/klassischer NUnit-Stil und schwache Assertion ohne klare Fehlermeldung.	Assert.That(status, Is.Not.Null, "...") und fachlichen Statuswert prüfen.
Mittel	Gesamter Test	Keine Fehlerartefakte bei Rotlauf.	Im catch Screenshot, UIA-Dump und Metadaten über FailureArtifactCollector erzeugen.
Niedrig	Testdesign	UI-Bedienlogik liegt direkt im Test.	Screen-Object für den Hauptdialog ergänzen.
Niedrig	Konfiguration	AUT-Pfad ist hart codiert.	Pfad über ConfigurationLoader oder Umgebungsvariable laden.
Zielstack-Konformität
Regel	Status	Bewertung
NUnit	Teilweise OK	Test nutzt NUnit, sollte aber Assert.That verwenden.
FlaUI.UIA3 für WPF	OK	Backend passt für WPF.
FlaUI.UIA2 für WinForms	Nicht relevant	Kein WinForms-Dialog erkennbar.
Keine Koordinatenklicks	Nicht OK	Muss ersetzt werden.
Keine statischen Sleeps als Hauptwartebedingung	Nicht OK	Muss durch Wait/Retry mit Zustand ersetzt werden.
Artefakte bei Fehlern	Nicht OK	Screenshot, UIA-Dump und Metadaten fehlen.
Azure DevOps Server	Teilweise offen	Test selbst ist nicht agentenrobust; Pipeline muss TRX und Build-Artefakte veröffentlichen.
Keine xUnit, MSTest, Selenium, WinAppDriver, Playwright-Desktop	OK	Nicht vorhanden und nicht einzuführen.
Beispielpatch
Datei: tests/Product.UiTests.Shared/Screens/MainWindowScreen.cs
C#
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Shared.Screens;

public sealed class MainWindowScreen
{
    private readonly Window _window;
    private readonly TimeSpan _timeout;

    public MainWindowScreen(Window window, TimeSpan timeout)
    {
        _window = window ?? throw new ArgumentNullException(nameof(window));
        _timeout = timeout;
    }

    public void StartWorkflow()
    {
        var button = Waiter.UntilNotNull(
            () => _window.FindFirstDescendant(cf => cf.ByAutomationId("StartWorkflowButton"))?.AsButton(),
            _timeout,
            "Der Button mit AutomationId 'StartWorkflowButton' wurde nicht gefunden.");

        Waiter.Until(
            () => button.IsEnabled,
            _timeout,
            "Der Button mit AutomationId 'StartWorkflowButton' wurde nicht enabled.");

        button.Click();
    }

    public AutomationElement WaitForReadyStatus()
    {
        return Waiter.UntilNotNull(
            () => _window.FindFirstDescendant(cf =>
                cf.ByAutomationId("WorkflowStatusText")
                  .And(cf.ByControlType(ControlType.Text))),
            _timeout,
            "Der Status mit AutomationId 'WorkflowStatusText' wurde nicht gefunden.");
    }

    public string ReadyStatusText()
    {
        return WaitForReadyStatus().Name;
    }
}
Datei: tests/Product.UiTests.Uia3/Smoke/MainWindowSmokeTests.cs
C#
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;

namespace Product.UiTests.Uia3.Smoke;

[TestFixture]
[NonParallelizable]
[Apartment(System.Threading.ApartmentState.STA)]
public sealed class MainWindowSmokeTests
{
    private TestConfiguration _config = null!;
    private FailureArtifactCollector _artifacts = null!;

    [SetUp]
    public void SetUp()
    {
        _config = ConfigurationLoader.Load();
        _artifacts = new FailureArtifactCollector(_config.ArtifactRoot);
    }

    [Test]
    public void StartsWorkflow_UsesAutomationIdAndShowsReadyStatus()
    {
        using var app = new AppLauncher(_config).StartApplication();
        using var automation = new UIA3Automation();

        try
        {
            var window = WindowFinder.WaitForMainWindow(
                app,
                automation,
                _config.DefaultTimeout,
                expectedAutomationId: "MainWindow");

            var screen = new MainWindowScreen(window, _config.DefaultTimeout);

            screen.StartWorkflow();

            Assert.That(
                screen.ReadyStatusText(),
                Is.EqualTo("Bereit"),
                "Nach dem Start des Workflows muss der fachliche Status 'Bereit' angezeigt werden.");
        }
        catch
        {
            _artifacts.Capture(app, automation, TestContext.CurrentContext.Test.Name);
            throw;
        }
    }
}
Datei: azure-pipelines-ui-tests.yml
YAML
pool:
  name: WIN-UI-DESKTOP
  demands:
    - Agent.OS -equals Windows_NT

steps:
- task: DotNetCoreCLI@2
  displayName: Restore UI test solution
  inputs:
    command: restore
    projects: 'Product.UiTests.sln'
    arguments: '--locked-mode'

- task: DotNetCoreCLI@2
  displayName: Build UI test solution
  inputs:
    command: build
    projects: 'Product.UiTests.sln'
    arguments: '--configuration Release --no-restore'

- task: DotNetCoreCLI@2
  displayName: Run FlaUI UIA3 smoke tests
  inputs:
    command: test
    projects: 'tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj'
    arguments: '--configuration Release --no-build --logger trx --results-directory $(Build.SourcesDirectory)/TestResults'

- task: PublishTestResults@2
  displayName: Publish TRX results
  condition: succeededOrFailed()
  inputs:
    testResultsFormat: VSTest
    testResultsFiles: 'TestResults/**/*.trx'
    failTaskOnFailedTests: true

- task: PublishBuildArtifacts@1
  displayName: Publish FlaUI failure artifacts
  condition: succeededOrFailed()
  inputs:
    PathtoPublish: 'TestResults'
    ArtifactName: 'flaui-test-artifacts'
Stabiler Fix

In der WPF-AUT muss der Start-Button eine stabile technische ID erhalten:

XML
<Button
    x:Name="StartWorkflowButton"
    AutomationProperties.AutomationId="StartWorkflowButton"
    Content="Start" />

Der Status sollte ebenfalls technisch adressierbar sein:

XML
<TextBlock
    x:Name="WorkflowStatusText"
    AutomationProperties.AutomationId="WorkflowStatusText"
    Text="{Binding WorkflowStatus}" />

Der Test darf nicht über sichtbaren Text als Primärselektor steuern. Der Text Bereit ist als fachliche Assertion zulässig, aber nicht als alleiniger Elementselektor.

Der Azure-DevOps-Server-Agent muss als interaktiver Windows-Agent laufen. Ein gesperrter Desktop, RDP-Abmeldung oder abweichende DPI kann UI-Tests weiterhin beeinflussen, auch wenn der Koordinatenklick entfernt wurde.

Akzeptanzkriterien

Der Test enthält keinen Mouse.Click(x, y)-Aufruf.

Der Test enthält keinen Thread.Sleep(...) als Hauptwartebedingung.

WPF wird über FlaUI.UIA3 automatisiert.

Der Start-Button wird über AutomationId gefunden.

Der Status wird über AutomationId gefunden und fachlich auf Bereit geprüft.

Assertions verwenden Assert.That.

Bei Fehlern werden mindestens Screenshot, UIA-Dump und Metadaten als Artefakte gesammelt.

Die Pipeline veröffentlicht TRX über PublishTestResults@2.

Die Pipeline veröffentlicht Diagnoseartefakte über PublishBuildArtifacts@1.

Es werden keine Secrets, externen SaaS-Abhängigkeiten oder produktiven Änderungen eingeführt.

Zusätzlich benötigte Daten

Bestätigung, dass die Zielanwendung WPF ist und der Dialog nicht aus WinForms gehostet wird.

Verbindliche AutomationId für den Start-Button.

Verbindliche AutomationId für das Statusfeld.

Speicherort für ArtifactRoot im Agent-Workspace.

Screenshot und UIA-Dump eines aktuellen Rotlaufs, falls der Test nach dem Umbau weiterhin flakyt.
