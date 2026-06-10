# Recherchiertes Offline-Beispiel: Eggplant-/SenseTalk-Workflow nach FlaUI/NUnit migrieren

## Quellenstand

Stand: 2026-06-10. Dieses Beispiel wurde aus öffentlich verfügbaren Hersteller- und Projektdokumentationen verdichtet, damit das Modell später offline realitätsnahe Entscheidungen trifft.

Verwendete Quellen:

- Eggplant Functional / SenseTalk: `https://docs.eggplantsoftware.com/epf/stk-sensetalk-reference/`
- Eggplant Basic SenseTalk Scripting: `https://docs.eggplantsoftware.com/epf/epf-basic-sensetalk/`
- Eggplant Handlers: `https://docs.eggplantsoftware.com/epf/stk-handlers/`
- FlaUI Projekt: `https://github.com/FlaUI/FlaUI`
- FlaUInspect Projekt: `https://github.com/FlaUI/FlaUInspect`
- NUnit Apartment Attribute: `https://docs.nunit.org/articles/nunit/writing-tests/attributes/apartment.html`
- OpenCvSharp Projekt: `https://github.com/shimat/opencvsharp`
- OpenCvSharp4.Windows NuGet: `https://www.nuget.org/packages/OpenCvSharp4.Windows`
- Azure DevOps `PublishTestResults@2`: `https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-test-results-v2`
- Azure DevOps `PublishBuildArtifacts@1`: `https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-build-artifacts-v1`

## Relevante Rechercheerkenntnisse

- SenseTalk ist die englischnahe Skriptsprache von Eggplant Functional; Migration muss daher Absicht, Handler-Struktur und GUI-Aktionssemantik erfassen, nicht nur Zeilen übersetzen.
- FlaUI automatisiert Windows-Anwendungen über Microsoft UI Automation und ist für Win32, WinForms, WPF und Store Apps geeignet. UIA3 ist der Standardpfad für moderne WPF-Anwendungen; UIA2 bleibt für ältere oder problematische Legacy-Controls relevant.
- Für WPF-/WinForms-nahe UI-Tests ist bei NUnit ein STA-Apartment relevant, weil diese UI-Technologien häufig einen bestimmten COM-/Threading-Apartment-Zustand benötigen.
- OpenCvSharp4.Windows ist ein Windows-All-in-one-Paket für OpenCV aus .NET heraus und passt zu visuellen Map-/Canvas-/Track-Prüfungen, wenn UIA keine semantischen Controls liefern kann.
- Für Azure DevOps Server sind TRX-Ergebnisse über `PublishTestResults@2` und klassische Build-Artefakte über `PublishBuildArtifacts@1` robuste Handover-Pfade.

## Nutzerauftrag

Migriere folgendes Eggplant-/SenseTalk-Skript in einen wartbaren FlaUI/NUnit-Zielstand:

```text
on RunCustomerSaveWorkflow
  Click "Login_User"
  TypeText "qa.user"
  Click "Login_Password"
  TypeText the PasswordFor("CustomerWorkflow")
  Click "Login_Submit"
  WaitFor 20, "CustomerSearch"
  Click "CustomerSearch"
  TypeText "CUST-10001"
  Click "OpenCustomer"
  WaitFor 10, "CustomerWindow"
  Click "CityField"
  TypeText "Berlin"
  Click "SaveCustomer"
  WaitFor 10, "SavedToast"
end RunCustomerSaveWorkflow
```

## Ideale Modellantwort

### Annahmen

- Die Zielanwendung ist eine WPF-Anwendung; daher wird `FlaUI.UIA3` verwendet.
- Das Eggplant-Bild `SavedToast` steht fachlich für eine sichtbare Speicherbestätigung. Primär wird versucht, diese Bestätigung über UIA-Text oder `AutomationId` zu prüfen.
- `PasswordFor("CustomerWorkflow")` wird nicht in Code übertragen. Das Passwort kommt aus lokaler Testkonfiguration oder Pipeline-Secret.
- Falls einzelne Controls nicht per UIA sichtbar sind, wird zunächst mit FlaUInspect und UIA-Dump nach `AutomationId`, `Name`, `ControlType` und Hierarchie gesucht.

### 1. Eingangsanalyse

| Skriptteil | Bedeutung | Migrationsrisiko |
| --- | --- | --- |
| Login-Felder | Standard-Formularinteraktion | Niedrig, falls `AutomationId` vorhanden |
| Kundensuche | Suchfeld plus Aktion | Mittel, da Ergebniszustand geprüft werden muss |
| Kundendialog | fachlicher Zielzustand | Mittel, wenn Dialog modal oder verzögert öffnet |
| `SavedToast` | visuelle Erfolgsmeldung | Mittel bis hoch, wenn nur als Bild gerendert |

### 2. Business Intent

Der Test validiert, dass ein berechtigter Nutzer einen bekannten Kunden öffnet, den Ort ändert, speichert und eine fachliche Bestätigung erhält. Die Zielmigration muss einen stabilen fachlichen Ablauf erzeugen, nicht die Eggplant-Klickreihenfolge unverändert kopieren.

### 3. Klassifizierung und Zielentscheidung

| Entscheidung | Ziel |
| --- | --- |
| UIA3-Testprojekt | `Product.UiTests.Uia3/Wpf/CustomerSaveWorkflowTests.cs` |
| Shared Screen-Objects | `LoginScreen`, `CustomerSearchScreen`, `CustomerScreen` |
| Failure-Artefakte | Screenshot, UIA-Dump, optional UI-Log |
| VisualTrack | Nur Fallback für Canvas-/Bildzustände, nicht für normale Controls |

### 4. Eggplant zu FlaUI/OpenCV Mapping

| Eggplant/SenseTalk | FlaUI-Ziel |
| --- | --- |
| `Click "Login_User"` | `LoginScreen.UserNameTextBox.Enter(...)` |
| `TypeText the PasswordFor(...)` | Secret aus `TestConfiguration.Password` |
| `WaitFor 20, "CustomerSearch"` | expliziter Wait auf UIA-Element |
| `Click "SaveCustomer"` | Button über `AutomationId("SaveCustomerButton")` |
| `WaitFor 10, "SavedToast"` | UIA-Text `Saved` oder lokalisierte Bestätigung; optional Screenshot-Artefakt |

### 5. Ziel-Dateien

```text
tests/
  Directory.Build.props
  Directory.Packages.props
  Product.UiTests.Shared/
    Configuration/TestConfiguration.cs
    Diagnostics/FailureArtifactCollector.cs
    Infrastructure/AppLauncher.cs
    Infrastructure/Waiter.cs
    Infrastructure/WindowFinder.cs
    Screens/LoginScreen.cs
    Screens/CustomerSearchScreen.cs
    Screens/CustomerScreen.cs
  Product.UiTests.Uia3/
    Wpf/CustomerSaveWorkflowTests.cs
```

### 6. C#-Code

```csharp
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;

namespace Product.UiTests.Uia3.Wpf;

[TestFixture]
[Apartment(System.Threading.ApartmentState.STA)]
public sealed class CustomerSaveWorkflowTests
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
    public void CustomerCityChange_Save_ShowsConfirmation()
    {
        using var app = new AppLauncher(_config).StartApplication();
        using var automation = new UIA3Automation();

        try
        {
            var window = WindowFinder.WaitForMainWindow(app, automation, _config.DefaultTimeout);

            var login = new LoginScreen(window);
            login.SignIn(_config.UserName, _config.Password);

            var search = CustomerSearchScreen.WaitFor(window, _config.DefaultTimeout);
            search.SearchAndOpen("CUST-10001");

            var customer = CustomerScreen.WaitFor(window, _config.DefaultTimeout);
            customer.SetCity("Berlin");
            customer.Save();

            Assert.That(customer.SuccessMessage, Does.Contain("gespeichert").Or.Contain("saved"));
        }
        catch
        {
            _artifacts.Capture(app, automation, TestContext.CurrentContext.Test.Name);
            throw;
        }
    }
}
```

### 7. Testdaten / VisualTrack-Konfiguration

- `CustomerWorkflow`-Credentials werden nur über lokale Konfiguration oder Pipeline-Secret eingelesen.
- `CUST-10001` muss ein stabiler Testdatensatz sein, der zurücksetzbar ist.
- VisualTrack wird nur aktiviert, wenn `SavedToast` nicht als UIA-Text oder Statusbar erscheint.
- Für VisualTrack-Artefakte werden Referenzbild, Maske, Thresholds und Ergebnis-JSON versioniert; tatsächliche Screenshots bleiben Laufzeitartefakte.

### 8. Pipeline-/Artefakt-Hinweise

```yaml
- task: DotNetCoreCLI@2
  displayName: Run migrated FlaUI tests
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
    ArtifactName: 'flaui-migration-artifacts'
```

### 9. Risiken und offene Punkte

- Ohne UIA-Dump sind konkrete `AutomationId`-Werte Platzhalter.
- Wenn die Anwendung als Administrator läuft, muss die Testausführung mit passender Integritätsstufe geplant werden.
- Lokalisierte Bestätigungstexte müssen entweder über Ressourcen oder tolerante fachliche Matcher abgebildet werden.

### 10. Akzeptanzkriterien

- Keine Koordinatenklicks.
- Keine hart kodierten Secrets.
- `coder` bleibt nur Basismodell; das Aufgabenmodell liefert Zielartefakte und Migrationsentscheidungen.
- UIA3 ist Standard für WPF; UIA2 wird nur für belegte Legacy-WinForms-Flächen verwendet.
- TRX und Failure-Artefakte sind in Azure DevOps Server veröffentlichbar.
