# Beispielergebnis: Eggplant-FlaUI-Skriptmigration

## Annahmen

- Das Eingabeartefakt ist ein Eggplant-/SenseTalk-Skript aus `beispiele/eggplant/wpf_login_customer_save.script`.
- Die Zielanwendung ist eine WPF-Desktopanwendung; Standardpfad ist daher `FlaUI.UIA3`.
- Element-IDs, `AutomationId` und Testdaten sind aus dem Skript nicht vollständig ableitbar und müssen gegen UIA-Dump oder laufende Anwendung verifiziert werden.
- Secrets, interne URLs und produktive Zugangsdaten werden nicht erzeugt.

## 1. Eingangsanalyse

| Befund | Bewertung |
| --- | --- |
| UI-Technologie | WPF-nahe Interaktion mit Login- und Kundendialog |
| Eggplant-Muster | `Click`, `TypeText`, visuelle Prüfung und fachlicher Save-Flow |
| Zielpfad | `Product.UiTests.Uia3/Wpf/CustomerWorkflowTests.cs` |
| Benötigte Zusatzdaten | UIA-Dump, stabile `AutomationId`, Testkonto, erwartete Bestätigung |

## 2. Business Intent

Der Test prüft, ob ein berechtigter Nutzer nach erfolgreichem Login einen Kundendatensatz öffnet, Pflichtfelder ändert, speichert und eine fachlich erkennbare Bestätigung erhält. Entscheidend ist nicht die pixelgenaue Eggplant-Aktion, sondern der stabile fachliche Ablauf mit wartbaren Screen-Objects.

## 3. Klassifizierung und Zielentscheidung

| Kriterium | Entscheidung |
| --- | --- |
| Standardcontrols erreichbar | Ja, bevorzugt UIA3 |
| Visueller Sonderfall | Nur für ergänzende Bestätigung, kein primärer Klickpfad |
| Zielarchitektur | NUnit + FlaUI.UIA3 + Screen-Objects + Failure-Artefakte |
| Nicht verwenden | Koordinatenklicks, WinAppDriver, MSTest, xUnit, ImageSharp |

## 4. Eggplant zu FlaUI/OpenCV Mapping

| Eggplant-Aktion | Zielumsetzung |
| --- | --- |
| `Click "LoginButton"` | `LoginScreen.LoginButton.Click()` über `AutomationId` |
| `TypeText userName` | `LoginScreen.UserName.Enter(...)` |
| `TypeText password` | Secret nur aus Testkonfiguration, nie hart kodieren |
| `WaitFor "CustomerWindow"` | `Waiter.UntilVisible(window.FindFirstDescendant(...))` |
| `ImageFound "SavedToast"` | Primär UIA-Text prüfen, optional Screenshot-Artefakt speichern |

## 5. Ziel-Dateien

| Datei | Zweck |
| --- | --- |
| `Product.UiTests.Shared/Screens/LoginScreen.cs` | Kapselt Login-Elemente und Login-Aktion |
| `Product.UiTests.Shared/Screens/CustomerScreen.cs` | Kapselt Kundendialog und Save-Bestätigung |
| `Product.UiTests.Uia3/Wpf/CustomerWorkflowTests.cs` | NUnit-Test für den migrierten Workflow |
| `Product.UiTests.Shared/Diagnostics/FailureArtifactCollector.cs` | Screenshot, UIA-Dump und Log bei Fehlern |

## 6. C#-Code

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
public sealed class CustomerWorkflowTests
{
    private TestConfiguration _config = null!;
    private AppLauncher _launcher = null!;
    private FailureArtifactCollector _artifacts = null!;

    [SetUp]
    public void SetUp()
    {
        _config = ConfigurationLoader.Load();
        _launcher = new AppLauncher(_config);
        _artifacts = new FailureArtifactCollector(_config.ArtifactRoot);
    }

    [Test]
    public void Login_EditCustomer_Save_ShowsConfirmation()
    {
        using var app = _launcher.StartApplication();
        using var automation = new UIA3Automation();

        try
        {
            var mainWindow = WindowFinder.WaitForMainWindow(app, automation, _config.DefaultTimeout);
            var login = new LoginScreen(mainWindow);
            login.SignIn(_config.UserName, _config.Password);

            var customer = CustomerScreen.WaitFor(mainWindow, _config.DefaultTimeout);
            customer.OpenCustomer("CUST-10001");
            customer.SetCity("Berlin");
            customer.Save();

            Assert.That(customer.SuccessMessageText, Does.Contain("gespeichert"));
        }
        catch
        {
            _artifacts.Capture(app, automation, TestContext.CurrentContext.Test.Name);
            throw;
        }
    }
}
```

## 7. Testdaten / VisualTrack-Konfiguration

- Testdaten gehören in `appsettings.local.json` oder eine Pipeline-Variable, nicht in den Testcode.
- Für Standard-WPF-Controls reicht UIA3; VisualTrack wird nur benötigt, wenn die Bestätigung ausschließlich als Canvas, Karte oder Bildspur sichtbar ist.
- Falls VisualTrack nötig ist, nutze `OpenCvSharp4.Windows`, Referenzrouten aus `beispiele/test-assets/TrackRoutes/` und speichere Metriken als JSON-Artefakt.

## 8. Pipeline-/Artefakt-Hinweise

- Azure DevOps Server: `PublishTestResults@2` für TRX und `PublishBuildArtifacts@1` für Screenshots, UIA-Dumps und VisualTrack-JSON.
- Kein `PublishPipelineArtifact@1`, wenn die Zielumgebung klassischer Azure DevOps Server ohne diesen Task ist.
- Fehlerartefakte müssen pro Testlauf eindeutig unter `TestResults/<RunId>/<TestName>/` liegen.

## 9. Risiken und offene Punkte

- Ohne UIA-Dump bleiben `AutomationId` und Window-Titel Annahmen.
- Wenn Eggplant-Bildanker bisher verdeckte Geschäftslogik prüfen, muss der fachliche Sollzustand separat beschrieben werden.
- Legacy-WinForms-Dialoge im selben Flow müssen in ein getrenntes UIA2-Testprojekt ausgelagert werden.

## 10. Akzeptanzkriterien

- Der migrierte Test nutzt `NUnit` und `FlaUI.UIA3`.
- Der Login verwendet keine hart kodierten Credentials.
- Standardcontrols werden über UIA gesucht, nicht per Koordinatenklick.
- Failure-Artefakte entstehen reproduzierbar bei Fehlern.
- Offene Annahmen sind sichtbar markiert und fachlich prüfbar.
