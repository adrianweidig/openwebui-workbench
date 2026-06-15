Golden Example: Testprogrammierung
Nutzeranfrage

Erstelle automatisierte UI-Tests für eine Login-Maske mit C#, Playwright und NUnit. Es gibt folgende Akzeptanzkriterien:

Bei gültigen Zugangsdaten wird nach dem Absenden das Dashboard angezeigt.

Bei leerem Passwort erscheint die Meldung „Passwort ist erforderlich“.

Bei falschen Zugangsdaten erscheint die Meldung „Anmeldung fehlgeschlagen“.

Die Tests sollen lokal und in Azure DevOps ausführbar sein.

Es dürfen keine echten Zugangsdaten im Code stehen.

Musterantwort
Kurzentscheidung

Sprache: C#
Framework: Playwright mit NUnit
Testart: UI-/E2E-Test
Bewertung: Direkt empfohlen

Annahmen

Die Login-Seite ist über die Umgebungsvariable SHOP_BASE_URL erreichbar.

Gültige Testzugangsdaten werden über SHOP_TEST_USER und SHOP_TEST_PASSWORD bereitgestellt.

Die Anwendung stellt stabile Testselektoren über data-testid bereit.

Die Tests laufen gegen eine isolierte Testumgebung, nicht gegen Produktion.

Geheimnisse werden ausschließlich über lokale Umgebungsvariablen oder Pipeline-Variablen gesetzt.

Empfehlung

Für diese Login-Szenarien ist C# mit Playwright und NUnit direkt geeignet. Playwright bringt robuste automatische Wartebedingungen, gute Headless-Fähigkeit und eine saubere Integration in dotnet test mit. Die Tests werden als unabhängige E2E-Tests umgesetzt, die Konfiguration wird aus Umgebungsvariablen gelesen und Testergebnisse werden als TRX-Dateien für Azure DevOps ausgegeben.

Projektstruktur
Shop.Login.Tests/
├─ Shop.Login.Tests.csproj
├─ Pages/
│  ├─ LoginPage.cs
│  └─ DashboardPage.cs
├─ Tests/
│  └─ LoginTests.cs
└─ TestConfiguration.cs
Abhängigkeiten
XML
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.10.0" />
    <PackageReference Include="Microsoft.Playwright.NUnit" Version="1.44.0" />
    <PackageReference Include="NUnit" Version="4.1.0" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
  </ItemGroup>

</Project>
Testcode
TestConfiguration.cs
C#
namespace Shop.Login.Tests;

public sealed class TestConfiguration
{
    public string BaseUrl { get; }
    public string ValidUser { get; }
    public string ValidPassword { get; }

    private TestConfiguration(string baseUrl, string validUser, string validPassword)
    {
        BaseUrl = baseUrl.TrimEnd('/');
        ValidUser = validUser;
        ValidPassword = validPassword;
    }

    public static TestConfiguration FromEnvironment()
    {
        string baseUrl = ReadRequired("SHOP_BASE_URL");
        string validUser = ReadRequired("SHOP_TEST_USER");
        string validPassword = ReadRequired("SHOP_TEST_PASSWORD");

        return new TestConfiguration(baseUrl, validUser, validPassword);
    }

    private static string ReadRequired(string name)
    {
        string? value = Environment.GetEnvironmentVariable(name);

        if (string.IsNullOrWhiteSpace(value))
        {
            throw new InvalidOperationException(
                $"Die erforderliche Umgebungsvariable '{name}' ist nicht gesetzt.");
        }

        return value;
    }
}
Pages/LoginPage.cs
C#
using Microsoft.Playwright;

namespace Shop.Login.Tests.Pages;

public sealed class LoginPage
{
    private readonly IPage _page;

    public LoginPage(IPage page)
    {
        _page = page;
    }

    private ILocator UserNameInput => _page.GetByTestId("login-username");
    private ILocator PasswordInput => _page.GetByTestId("login-password");
    private ILocator SubmitButton => _page.GetByTestId("login-submit");
    private ILocator ErrorMessage => _page.GetByTestId("login-error");

    public async Task OpenAsync(string baseUrl)
    {
        await _page.GotoAsync($"{baseUrl}/login");
    }

    public async Task LoginAsync(string userName, string password)
    {
        await UserNameInput.FillAsync(userName);
        await PasswordInput.FillAsync(password);
        await SubmitButton.ClickAsync();
    }

    public async Task SubmitWithEmptyPasswordAsync(string userName)
    {
        await UserNameInput.FillAsync(userName);
        await PasswordInput.FillAsync(string.Empty);
        await SubmitButton.ClickAsync();
    }

    public ILocator VisibleErrorMessage()
    {
        return ErrorMessage;
    }
}
Pages/DashboardPage.cs
C#
using Microsoft.Playwright;

namespace Shop.Login.Tests.Pages;

public sealed class DashboardPage
{
    private readonly IPage _page;

    public DashboardPage(IPage page)
    {
        _page = page;
    }

    public ILocator Heading => _page.GetByTestId("dashboard-heading");
}
Tests/LoginTests.cs
C#
using Microsoft.Playwright.NUnit;
using NUnit.Framework;
using Shop.Login.Tests.Pages;

namespace Shop.Login.Tests.Tests;

[Parallelizable(ParallelScope.Self)]
[TestFixture]
public sealed class LoginTests : PageTest
{
    private TestConfiguration _configuration = null!;

    [SetUp]
    public void ReadConfiguration()
    {
        _configuration = TestConfiguration.FromEnvironment();
    }

    [Test]
    public async Task Login_WithValidCredentials_ShouldShowDashboard()
    {
        var loginPage = new LoginPage(Page);
        var dashboardPage = new DashboardPage(Page);

        await loginPage.OpenAsync(_configuration.BaseUrl);
        await loginPage.LoginAsync(
            _configuration.ValidUser,
            _configuration.ValidPassword);

        await Expect(dashboardPage.Heading).ToBeVisibleAsync();
        await Expect(dashboardPage.Heading).ToContainTextAsync("Dashboard");
    }

    [Test]
    public async Task Login_WithEmptyPassword_ShouldShowPasswordRequiredMessage()
    {
        var loginPage = new LoginPage(Page);

        await loginPage.OpenAsync(_configuration.BaseUrl);
        await loginPage.SubmitWithEmptyPasswordAsync(_configuration.ValidUser);

        await Expect(loginPage.VisibleErrorMessage()).ToBeVisibleAsync();
        await Expect(loginPage.VisibleErrorMessage()).ToHaveTextAsync("Passwort ist erforderlich");
    }

    [Test]
    public async Task Login_WithInvalidCredentials_ShouldShowLoginFailedMessage()
    {
        var loginPage = new LoginPage(Page);

        await loginPage.OpenAsync(_configuration.BaseUrl);
        await loginPage.LoginAsync(_configuration.ValidUser, "ungültiges-passwort-für-negativtest");

        await Expect(loginPage.VisibleErrorMessage()).ToBeVisibleAsync();
        await Expect(loginPage.VisibleErrorMessage()).ToHaveTextAsync("Anmeldung fehlgeschlagen");
    }
}
Lokale Ausführung
Bash
dotnet restore
dotnet build
pwsh bin/Debug/net8.0/playwright.ps1 install
dotnet test --logger "trx;LogFileName=login-tests.trx" --results-directory TestResults

Erforderliche lokale Umgebungsvariablen:

Bash
export SHOP_BASE_URL="https://testumgebung.shop.local"
export SHOP_TEST_USER="login-test-user"
# SHOP_TEST_PASSWORD im lokalen Secret-Store oder temporär in der Shell setzen.

Unter PowerShell:

PowerShell
$env:SHOP_BASE_URL = "https://testumgebung.shop.local"
$env:SHOP_TEST_USER = "login-test-user"
# SHOP_TEST_PASSWORD im lokalen Secret-Store oder temporär in der Shell setzen.
CI/CD-Ausführung
YAML
trigger:
  branches:
    include:
      - main

pool:
  vmImage: ubuntu-latest

variables:
  DOTNET_CLI_TELEMETRY_OPTOUT: '1'
  DOTNET_NOLOGO: '1'

steps:
  - task: UseDotNet@2
    displayName: Install .NET SDK
    inputs:
      packageType: sdk
      version: 8.x

  - script: dotnet restore Shop.Login.Tests/Shop.Login.Tests.csproj
    displayName: Restore test project

  - script: dotnet build Shop.Login.Tests/Shop.Login.Tests.csproj --configuration Release --no-restore
    displayName: Build test project

  - script: pwsh Shop.Login.Tests/bin/Release/net8.0/playwright.ps1 install --with-deps
    displayName: Install Playwright browsers

  - script: >
      dotnet test Shop.Login.Tests/Shop.Login.Tests.csproj
      --configuration Release
      --no-build
      --logger "trx;LogFileName=login-tests.trx"
      --results-directory "$(Agent.TempDirectory)/TestResults"
    displayName: Run Playwright login tests
    env:
      SHOP_BASE_URL: $(SHOP_BASE_URL)
      SHOP_TEST_USER: $(SHOP_TEST_USER)
      SHOP_TEST_PASSWORD: $(SHOP_TEST_PASSWORD)

  - task: PublishTestResults@2
    displayName: Publish TRX test results
    condition: succeededOrFailed()
    inputs:
      testResultsFormat: VSTest
      testResultsFiles: '$(Agent.TempDirectory)/TestResults/*.trx'
      failTaskOnFailedTests: true

  - task: PublishPipelineArtifact@1
    displayName: Publish test artifacts
    condition: succeededOrFailed()
    inputs:
      targetPath: '$(Agent.TempDirectory)/TestResults'
      artifact: login-test-results
Testergebnisse und Artefakte

dotnet test liefert einen fehlerhaften Exit-Code, wenn mindestens ein Test fehlschlägt.

TRX-Dateien werden in TestResults erzeugt.

Azure DevOps veröffentlicht die Testergebnisse über PublishTestResults@2.

Testartefakte werden zusätzlich als Pipeline-Artefakt gespeichert.

Screenshots oder Traces können ergänzt werden, wenn die bestehende Fehleranalyse mehr Diagnostik benötigt.

Qualitätsregeln

Keine echten Zugangsdaten im Testcode.

Keine harten Sleeps wie Thread.Sleep.

Selektoren bevorzugt über data-testid.

Assertions prüfen sichtbares Verhalten, nicht nur technische Zustände.

Tests sind unabhängig voneinander ausführbar.

Testdaten werden über Umgebung oder dedizierte Testdatenbereitstellung konfiguriert.

Parallelisierung bleibt auf Fixture-Ebene begrenzt, solange die Testumgebung parallele Logins stabil unterstützt.

Browser laufen in CI headless.

Fehlende Konfiguration führt zu klaren Fehlermeldungen.

Grenzen und Alternativen

Die konkrete URL der Testumgebung und gültige Testzugangsdaten müssen aus der Projektumgebung kommen.

Die Selektoren login-username, login-password, login-submit, login-error und dashboard-heading müssen in der Anwendung vorhanden sein oder entsprechend angepasst werden.

Wenn bereits Selenium Grid vorhanden ist, ist Selenium mit C# ebenfalls möglich; für neue C#-UI-Tests ist Playwright hier jedoch wartungsärmer.

Für Ada-Code wären AUnit oder GNATtest sinnvoll, aber Ada ist für direkte Browserautomation mit Playwright nicht als primärer Weg zu empfehlen.
