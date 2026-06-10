# Recherchiertes Offline-Beispiel: Produktionsnaher FlaUI/NUnit-Testreview

## Quellenstand

Stand: 2026-06-10. Dieses Beispiel wurde mit öffentlichen Hersteller- und Projektdokumentationen abgeglichen und als Offline-Referenz für OpenWebUI verdichtet.

Verwendete Quellen:

- FlaUI Projekt: `https://github.com/FlaUI/FlaUI`
- FlaUInspect Projekt: `https://github.com/FlaUI/FlaUInspect`
- NUnit Apartment Attribute: `https://docs.nunit.org/articles/nunit/writing-tests/attributes/apartment.html`
- NUnit Attribute Reference: `https://docs.nunit.org/articles/nunit/writing-tests/attributes.html`
- OpenCvSharp Projekt: `https://github.com/shimat/opencvsharp`
- OpenCvSharp Dokumentation: `https://shimat.github.io/opencvsharp/`
- OpenCvSharp4.Windows NuGet: `https://www.nuget.org/packages/OpenCvSharp4.Windows`
- Azure DevOps `PublishTestResults@2`: `https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-test-results-v2`
- Azure DevOps `PublishBuildArtifacts@1`: `https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-build-artifacts-v1`

## Relevante Rechercheerkenntnisse

- FlaUI ist ein .NET-Wrapper um Microsoft UI Automation und eignet sich für Windows-Desktop-UI-Tests gegen Win32, WinForms, WPF und Store Apps.
- FlaUInspect unterstützt UIA2 und UIA3 und ist ein praktischer Referenzpfad, um stabile `AutomationId`, `Name`, `ControlType` und Baumpositionen zu prüfen.
- NUnit kann Tests per `ApartmentAttribute` in STA oder MTA ausführen; STA ist für Tests gegen WPF-, WinForms- oder COM-nahe UI-Komponenten relevant.
- OpenCvSharp liefert .NET-Zugriff auf OpenCV; unter Windows kann `OpenCvSharp4.Windows` als All-in-one-Paket genutzt werden.
- Azure Pipelines veröffentlicht Testresultate mit `PublishTestResults@2`; klassische Build-Artefakte, einschließlich TFS/Azure DevOps Server-Pfade, passen zu `PublishBuildArtifacts@1`.

## Nutzerauftrag

Reviewe diesen FlaUI-Test und liefere einen produktionsnahen Fix:

```csharp
using FlaUI.UIA3;
using NUnit.Framework;

[TestFixture]
public class OrderDialogTests
{
    [Test]
    public void SaveOrder()
    {
        var app = FlaUI.Core.Application.Launch("Product.exe");
        using var automation = new UIA3Automation();
        var window = app.GetMainWindow(automation);
        window.FindFirstDescendant(x => x.ByName("Orders")).Click();
        window.Mouse.Click(new System.Drawing.Point(920, 730));
        Assert.Pass();
    }
}
```

## Ideale Modellantwort

### Kurzbewertung

Der Test ist nicht produktionsreif. Er startet die Anwendung ohne kontrollierten Lebenszyklus, wartet nicht auf UI-Zustände, verwendet einen Koordinatenklick und enthält keine fachliche Assertion. Für CI/CD fehlen Failure-Artefakte und veröffentlichbare Testergebnisse. Der Test sollte in ein UIA3-WPF-Testprojekt mit STA-Apartment, Screen-Object, expliziten Waits und sauberem Artefaktpfad überführt werden.

### Findings

| Schwere | Datei/Stelle | Problem | Empfehlung |
| --- | --- | --- | --- |
| Hoch | `window.Mouse.Click(...)` | Koordinatenklick ist DPI-, Auflösungs- und Layout-anfällig | Button per UIA `AutomationId`/`Name` suchen |
| Hoch | `Assert.Pass()` | Keine fachliche Prüfung | Bestätigung, Status oder Datenzustand assertieren |
| Hoch | App-Lifecycle | Anwendung wird nicht zuverlässig beendet | `using var app` plus TearDown/Fallback verwenden |
| Mittel | Threading | Kein STA-Apartment | `[Apartment(ApartmentState.STA)]` ergänzen |
| Mittel | Diagnose | Keine Artefakte bei Fehlern | Screenshot, UIA-Dump und Log speichern |
| Mittel | Struktur | UI-Suche direkt im Test | Screen-Object für Order-Dialog verwenden |

### Zielstack-Konformität

| Regel | Bewertung |
| --- | --- |
| NUnit | Beibehalten |
| FlaUI.UIA3 für WPF | Beibehalten und strukturieren |
| UIA2 nur für Legacy-WinForms | Nicht nötig, solange Dialog WPF/UIA3-sichtbar ist |
| OpenCvSharp | Nur für Canvas-/Bildprüfungen nötig, hier nicht primär |
| Keine Koordinatenklicks | Muss korrigiert werden |
| Azure DevOps Server | TRX und Build-Artefakte vorbereiten |

### Beispielpatch

```csharp
using System.Threading;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;

namespace Product.UiTests.Uia3.Orders;

[TestFixture]
[Apartment(ApartmentState.STA)]
public sealed class OrderDialogTests
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
    public void SaveOrder_WithValidOrder_ShowsSavedStatus()
    {
        using var app = new AppLauncher(_config).StartApplication();
        using var automation = new UIA3Automation();

        try
        {
            var window = WindowFinder.WaitForMainWindow(app, automation, _config.DefaultTimeout);
            var ordersTab = Waiter.UntilNotNull(
                () => window.FindFirstDescendant(cf => cf.ByName("Orders"))?.AsTabItem(),
                _config.DefaultTimeout,
                "Orders tab was not visible.");

            ordersTab.Select();

            var saveButton = Waiter.UntilNotNull(
                () => window.FindFirstDescendant(cf => cf.ByAutomationId("SaveOrderButton"))?.AsButton(),
                _config.DefaultTimeout,
                "Save order button was not visible.");

            saveButton.Click();

            var status = Waiter.UntilNotNull(
                () => window.FindFirstDescendant(cf =>
                    cf.ByControlType(ControlType.Text).And(cf.ByAutomationId("OrderStatusText"))),
                _config.DefaultTimeout,
                "Order status text was not visible.");

            Assert.That(status.Name, Does.Contain("gespeichert").Or.Contain("saved"));
        }
        catch
        {
            _artifacts.Capture(app, automation, TestContext.CurrentContext.Test.Name);
            throw;
        }
    }
}
```

### Ergänzende Ziel-Dateien

| Datei | Zweck |
| --- | --- |
| `Product.UiTests.Shared/Infrastructure/WindowFinder.cs` | Hauptfenster mit Timeout suchen |
| `Product.UiTests.Shared/Infrastructure/Waiter.cs` | Polling und kontrollierte Fehlermeldungen |
| `Product.UiTests.Shared/Diagnostics/FailureArtifactCollector.cs` | Screenshot und UIA-Dump bei Fehlern |
| `Product.UiTests.Shared/Configuration/TestConfiguration.cs` | App-Pfad, Timeout, Artefaktpfad und Testdaten |

### Pipeline-Hinweise

```yaml
- task: DotNetCoreCLI@2
  displayName: Run FlaUI smoke tests
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
    ArtifactName: 'flaui-order-dialog-artifacts'
```

### Offene Fragen

1. Ist `SaveOrderButton` die tatsächliche `AutomationId` oder muss sie per FlaUInspect/UIA-Dump verifiziert werden?
2. Ist der Order-Dialog WPF/UIA3-sichtbar oder ein Legacy-WinForms-Dialog, der UIA2 benötigt?
3. Ist die Erfolgsbestätigung lokalisiert, und gibt es eine stabile Status-`AutomationId`?

### Akzeptanzkriterien

- Kein Koordinatenklick bleibt im Test.
- Der Test läuft im STA-Apartment.
- Der Test prüft einen fachlichen Erfolg.
- Fehlerfälle erzeugen lokale Artefakte.
- Der Pipelinepfad veröffentlicht TRX und Build-Artefakte ohne vorausgesetzte Cloud-only Tasks.
