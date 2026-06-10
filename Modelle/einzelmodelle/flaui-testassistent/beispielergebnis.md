# Beispielergebnis: FlaUI-Testassistent

## Annahmen

- Die Eingabe ist ein vorhandener FlaUI/NUnit-Test mit instabilem Koordinatenklick.
- Die Zielanwendung enthält einen WPF-Hauptdialog und optional einen Legacy-WinForms-Dialog.
- Der Zielstack bleibt `NUnit`, `FlaUI.UIA3`, `FlaUI.UIA2`, `OpenCvSharp4.Windows`, `Verify.NUnit`, `Serilog` und Azure DevOps Server.
- Es werden keine Secrets, internen URLs oder produktiven Zugangsdaten erzeugt.

## Kurzbewertung

Der Test ist fachlich relevant, aber in der aktuellen Form nicht stabil genug für CI/CD. Hauptproblem ist ein koordinatenbasierter Klick, der bei DPI, Fensterposition, Skalierung und langsamen UI-Zuständen bricht. Der Test sollte auf Screen-Objects, UIA-Suche, explizite Waits und Failure-Artefakte umgestellt werden.

## Findings

| Schwere | Datei/Stelle | Problem | Empfehlung |
| --- | --- | --- | --- |
| Hoch | `FlakyCoordinateClickTest.cs` | Klick auf feste Koordinaten statt auf UIA-Element | Button über `AutomationId` oder Name finden und per FlaUI klicken |
| Hoch | Testaufbau | Kein stabiler Wait auf sichtbares Hauptfenster | `WindowFinder.WaitForMainWindow` und kontrollierten Timeout verwenden |
| Mittel | Fehlerdiagnose | Kein Screenshot und kein UIA-Dump bei Fehlern | `FailureArtifactCollector` im `catch` ausführen |
| Mittel | Assertions | Nur indirekte Prüfung nach Aktion | Fachliche Bestätigung oder Zustandsänderung explizit assertieren |
| Niedrig | Wartbarkeit | UI-Logik direkt im Test | Screen-Object für Dialogaktion ergänzen |

## Zielstack-Konformität

| Regel | Status | Kommentar |
| --- | --- | --- |
| NUnit | OK | Beibehalten |
| FlaUI.UIA3 für WPF | Korrigieren | UIA3-Automation konsequent nutzen |
| FlaUI.UIA2 für WinForms | Offen | Nur verwenden, wenn der Dialog wirklich WinForms ist |
| Keine Koordinatenklicks | Nicht OK | Muss ersetzt werden |
| Keine xUnit/MSTest/ImageSharp/WinAppDriver | OK | Nicht einführen |
| Azure DevOps Server Artefakte | Korrigieren | TRX und Build-Artefakte veröffentlichen |

## Beispielpatch

```csharp
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Uia3.Smoke;

[TestFixture]
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
    public void StartWorkflow_ClicksPrimaryAction_ByAutomationId()
    {
        using var app = new AppLauncher(_config).StartApplication();
        using var automation = new UIA3Automation();

        try
        {
            var window = WindowFinder.WaitForMainWindow(app, automation, _config.DefaultTimeout);
            var primaryAction = Waiter.UntilNotNull(
                () => window.FindFirstDescendant(cf => cf.ByAutomationId("PrimaryActionButton"))?.AsButton(),
                _config.DefaultTimeout,
                "Primary action button was not visible.");

            primaryAction.Click();

            var status = Waiter.UntilNotNull(
                () => window.FindFirstDescendant(cf => cf.ByControlType(ControlType.Text).And(cf.ByName("Bereit"))),
                _config.DefaultTimeout,
                "Expected ready status was not visible.");

            Assert.That(status.Name, Is.EqualTo("Bereit"));
        }
        catch
        {
            _artifacts.Capture(app, automation, TestContext.CurrentContext.Test.Name);
            throw;
        }
    }
}
```

## Pipeline-Hinweise

```yaml
- task: DotNetCoreCLI@2
  displayName: Test FlaUI desktop suite
  inputs:
    command: test
    projects: '**/*UiTests*.csproj'
    arguments: '--configuration Release --logger trx --results-directory $(Build.SourcesDirectory)/TestResults'

- task: PublishTestResults@2
  inputs:
    testResultsFormat: VSTest
    testResultsFiles: 'TestResults/**/*.trx'
    failTaskOnFailedTests: true

- task: PublishBuildArtifacts@1
  inputs:
    PathtoPublish: 'TestResults'
    ArtifactName: 'flaui-test-artifacts'
```

## Akzeptanzkriterien

- Der Test enthält keine Koordinatenklicks.
- UI-Elemente werden über stabile UIA-Merkmale gesucht.
- Timeouts und Waits sind explizit und fachlich begründet.
- Bei Fehlern werden Screenshot, UIA-Dump und Logs als Artefakte erzeugt.
- Die Assertion prüft einen fachlichen Zustand statt nur den Ablauf.

## Offene Fragen

1. Welche `AutomationId` ist für den primären Button verbindlich?
2. Muss derselbe Ablauf zusätzlich für einen WinForms-Dialog mit UIA2 abgedeckt werden?
3. Welche Statusmeldung ist im Zielsystem der stabile fachliche Erfolgsnachweis?
