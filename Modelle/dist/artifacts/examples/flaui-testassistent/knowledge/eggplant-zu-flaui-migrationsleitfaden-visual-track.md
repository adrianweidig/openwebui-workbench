# Migrationsleitfaden: Eggplant → FlaUI/NUnit/OpenCV/Azure-DevOps-Server

**Stand:** 10.06.2026
**Ziel:** vollständige technische Ablösung der betrachteten Eggplant-Nutzung für eine interne C#-Desktopanwendung mit WPF/WinForms.
**Zielarchitektur:** Azure DevOps Server + self-hosted interaktive Windows-VM-Agenten + NUnit + FlaUI.UIA3/FlaUI.UIA2 + OpenCvSharp + Verify.NUnit + strukturierte Artefakte.
**Besondere Pflichtanforderung:** visuelle Prüfung dünner, bewegter Track-/Spurlinien, z. B. Flugzeugspur mit wenigen Pixeln Breite und fachlich relevanter Abweichung in nautischen Meilen.

---

## 0. Verbindliche Zielentscheidung

Eggplant wird nicht durch ein einzelnes Tool ersetzt, sondern durch folgenden Stack:

```text
Azure DevOps Server
  + Azure Repos Git
  + Azure Artifacts NuGet-Feed
  + Azure Pipelines YAML
  + self-hosted Windows-VM-Agenten im interaktiven Auto-Logon-Modus
  + NUnit
  + FlaUI.UIA3 für WPF
  + FlaUI.UIA2 für WinForms
  + OpenCvSharp für visuelle Track-/Linien-/Canvas-Prüfungen
  + Verify.NUnit für strukturierte Snapshots
  + Serilog für strukturierte Diagnose
  + eigene Testinfrastruktur für Screens, Artefakte, UIA-Dumps und Visual Validation
```

Die Migration hat ein eindeutiges Ziel:

```text
WPF-Dialog-/Workflowtests      → Product.UiTests.Uia3
WinForms-Dialog-/Workflowtests → Product.UiTests.Uia2
visuelle Track-Line-Prüfungen  → OpenCV-Analyzer im jeweiligen UIA-Teststrang
Pipeline-Orchestrierung        → Azure DevOps Server
Artefakte und Testresultate    → TRX + Build-Artefakte
```

Nicht Bestandteil des Zielstacks:

```text
xUnit
MSTest
ImageSharp
WinAppDriver
Playwright für Desktop
pixelbasierte Steuerung normaler Standardcontrols
VLM als Pass/Fail-Entscheider
unreviewte KI-generierte Tests
mehrere interaktive UI-Agenten auf derselben VM
Microsoft-hosted Agents
PublishPipelineArtifact@1 auf Azure DevOps Server
```

---

## 1. Zielbild der Ersatzarchitektur

```text
Online-Migrationslabor
  ├─ Azure DevOps Server, gleicher Patchstand wie Zielumgebung
  ├─ SQL Server, gleicher Hauptversions- und CU-Stand wie Zielumgebung
  ├─ Azure Artifacts Feed mit allen NuGet-Paketen
  ├─ optionale lokal importierte Marketplace-VSIX-Erweiterungen
  ├─ Build-VMs
  ├─ UI-Test-VMs für WPF/UIA3
  ├─ UI-Test-VMs für WinForms/UIA2
  └─ Export-Bundle für Airgap

Airgap-Zielumgebung
  ├─ Azure DevOps Server, identischer Patchstand
  ├─ SQL Server, identischer Stand
  ├─ Azure Artifacts Feed ohne externe Upstreams
  ├─ identische Agent-Pools
  ├─ identische VM-Baselines
  ├─ identische NuGet-Paketversionen
  ├─ identische VSIX-Erweiterungen
  ├─ identische Pipeline-YAML-Dateien
  └─ identische Testausführung ohne Internetzugriff
```

### 1.1 Spiegelungsregel

Alles, was in der Airgap-Umgebung laufen soll, wird zuerst im Online-Migrationslabor mit denselben Versionen, Pfaden, VM-Einstellungen und Pipeline-Demands validiert.

Verbindliche Gleichheitskriterien:

| Bereich | Online-Migrationslabor | Airgap-Zielumgebung |
|---|---|---|
| Azure DevOps Server | gleicher RTW-/Patchstand | gleicher RTW-/Patchstand |
| SQL Server | gleiche Hauptversion und gleicher CU-Stand | gleiche Hauptversion und gleicher CU-Stand |
| .NET SDK | gleiche SDK-Version | gleiche SDK-Version |
| NuGet-Pakete | gleiche `Directory.Packages.props` + `packages.lock.json` | gleiche Dateien |
| Agent-Software | gleiche ZIP-Version | gleiche ZIP-Version |
| Windows-VM-Image | gleiche Windows-Version | gleiche Windows-Version |
| DPI/Auflösung | identisch | identisch |
| Pipeline-YAML | identisch | identisch |
| Testdaten | identisch versioniert | identisch versioniert |
| Visual-Track-Kalibrierung | identisch | identisch |

---

## 2. Verbindliche Server- und VM-Topologie

### 2.1 Azure-DevOps-Server-Ebene

| Komponente | Vorgabe |
|---|---|
| Produkt | Azure DevOps Server, RTW vom 09.12.2025, Stand mindestens Patch 4 vom 14.05.2026 |
| Datenbank | SQL Server 2022 oder SQL Server 2025; für Online und Airgap exakt gleich festlegen |
| Repository | Azure Repos Git |
| Paketverwaltung | Azure Artifacts Feed `nuget-offline` |
| Pipeline-Typ | YAML |
| Testresultate | `PublishTestResults@2`, Format `VSTest`/TRX |
| Build-Artefakte | `PublishBuildArtifacts@1` |
| Pipeline-Artefakte | nicht verwenden |
| Agent-Modell | self-hosted Windows Agents |
| Agent-Version | Azure Pipelines Agent 4.x |

### 2.2 Servernamen

Für Online-Migrationslabor:

```text
MIG-ADO-01        Azure DevOps Server Application Tier
MIG-SQL-01        SQL Server Data Tier
MIG-BUILD-01      Build-Agent-VM
MIG-UI-WPF-01     WPF/UIA3-Agent-VM
MIG-UI-WF-01      WinForms/UIA2-Agent-VM
MIG-UI-VIS-01     reservierte Visual-Track-Agent-VM für empfindliche OpenCV-Prüfungen
```

Für Airgap-Zielumgebung:

```text
AG-ADO-01         Azure DevOps Server Application Tier
AG-SQL-01         SQL Server Data Tier
AG-BUILD-01       Build-Agent-VM
AG-UI-WPF-01      WPF/UIA3-Agent-VM
AG-UI-WF-01       WinForms/UIA2-Agent-VM
AG-UI-VIS-01      reservierte Visual-Track-Agent-VM
```

### 2.3 Agent-Pools

```text
WIN-BUILD
WIN-UI-DESKTOP
```

`WIN-BUILD` enthält nur Build-Agenten ohne sichtbare UI-Anforderung.

`WIN-UI-DESKTOP` enthält nur interaktive Desktop-UI-Agenten.

### 2.4 Agent-Capabilities

Jeder UI-Agent erhält explizite User Capabilities:

| Agent | Pool | User Capabilities |
|---|---|---|
| `MIG-UI-WPF-01` / `AG-UI-WPF-01` | `WIN-UI-DESKTOP` | `UiBackend=UIA3`, `UiProfile=WPF`, `DisplayProfile=FHD_100DPI`, `VisualTrack=false` |
| `MIG-UI-WF-01` / `AG-UI-WF-01` | `WIN-UI-DESKTOP` | `UiBackend=UIA2`, `UiProfile=WinForms`, `DisplayProfile=FHD_100DPI`, `VisualTrack=false` |
| `MIG-UI-VIS-01` / `AG-UI-VIS-01` | `WIN-UI-DESKTOP` | `UiBackend=UIA3`, `UiProfile=WPF`, `DisplayProfile=FHD_100DPI`, `VisualTrack=true` |

Die Pipeline steuert die Zuweisung über `demands`.

---

## 3. Online-Migrationslabor als exakter Spiegel der Airgap-Umgebung

### 3.1 Zweck

Das Online-Migrationslabor erzeugt, validiert und versioniert alles, was später in die Airgap-Umgebung importiert wird:

```text
Installationsmedien
Azure-DevOps-Patches
Agent-ZIP-Dateien
VSIX-Erweiterungen
NuGet-Pakete
NuGet-Lockfiles
Pipeline-YAML
PowerShell-Provisioning-Skripte
VM-Baseline-Skripte
Testdaten
Track-Line-Referenzdaten
OpenCV-Kalibrierdateien
```

### 3.2 Export-Bundle-Struktur

```text
MigrationBundle/
  00-manifest/
    migration.manifest.json
    sha256sums.txt
    package-inventory.csv
    vsix-inventory.csv
    agent-inventory.txt
    dotnet-inventory.txt

  01-installers/
    azure-devops-server/
    sql-server/
    dotnet-sdk/
    vc-redist/
    azure-pipelines-agent/
    windows-sdk-tools/

  02-azure-devops-extensions/
    *.vsix
    vsix-lock.json

  03-nuget/
    packages/
      *.nupkg
    nuget.config
    Directory.Packages.props
    packages-lock/
      Product.UiTests.Uia3.packages.lock.json
      Product.UiTests.Uia2.packages.lock.json
      Product.UiTests.Shared.packages.lock.json

  04-repo-bootstrap/
    azure-pipelines.yml
    Directory.Build.props
    Directory.Packages.props
    NuGet.config
    tests/
    scripts/
    docs/

  05-vm-baseline/
    Configure-UiTestVm.ps1
    Configure-Agent.ps1
    Set-DisplayProfile.ps1
    Disable-DesktopNoise.ps1
    Verify-UiTestEnvironment.ps1

  06-trackline-validation/
    scenarios/
      TRACK_ROUTE_001.json
      TRACK_ROUTE_002.json
    calibration/
      display-profile-FHD_100DPI.json
      map-calibration.json
    templates/
      aircraft-marker.png
    synthetic-tests/
      expected-pass.png
      expected-fail-offset-3px.png

  07-validation-results/
    online-lab-smoke/
    online-lab-trackline/
    import-dryrun/
```

### 3.3 Manifest

`migration.manifest.json` wird im Online-Migrationslabor erzeugt und in der Airgap-Umgebung vor Import geprüft.

```json
{
  "createdUtc": "2026-06-10T00:00:00Z",
  "azureDevOpsServer": {
    "release": "Azure DevOps Server RTW",
    "rtwDate": "2025-12-09",
    "patch": "Patch 4",
    "patchDate": "2026-05-14"
  },
  "sqlServer": {
    "majorVersion": "SQL Server 2022 or SQL Server 2025",
    "rule": "Online and Airgap must match exactly"
  },
  "dotnet": {
    "sdk": "10.0.9",
    "targetFramework": "net10.0-windows"
  },
  "windowsAgentVm": {
    "os": "Windows 11 Enterprise 25H2 x64",
    "resolution": "1920x1080",
    "dpi": "100%",
    "language": "de-DE",
    "timeZone": "W. Europe Standard Time"
  },
  "nuget": {
    "centralPackageManagement": true,
    "lockedMode": true,
    "externalFeedsInAirgap": false
  },
  "excluded": [
    "xUnit",
    "MSTest",
    "ImageSharp",
    "PublishPipelineArtifact@1",
    "Microsoft-hosted agents"
  ]
}
```

### 3.4 SHA-256-Erzeugung

```powershell
$bundleRoot = "D:\MigrationBundle"
Get-ChildItem $bundleRoot -Recurse -File |
  Sort-Object FullName |
  ForEach-Object {
    $hash = Get-FileHash -Algorithm SHA256 -Path $_.FullName
    [PSCustomObject]@{
      Sha256 = $hash.Hash
      Path   = $_.FullName.Replace($bundleRoot, '').TrimStart('\')
    }
  } |
  ConvertTo-Csv -NoTypeInformation |
  Set-Content "$bundleRoot\00-manifest\sha256sums.csv" -Encoding UTF8
```

---

## 4. Installations- und Softwarevorgaben

### 4.1 Azure DevOps Server

Vorgabe:

```text
Azure DevOps Server RTW, veröffentlicht 09.12.2025
mindestens Patch 4, veröffentlicht 14.05.2026
```

Installation:

```text
1. SQL Server bereitstellen.
2. Azure DevOps Server installieren.
3. Collection anlegen: DefaultCollection oder projektspezifische Collection.
4. Azure Repos, Pipelines, Artifacts aktivieren.
5. Agent Pools anlegen: WIN-BUILD, WIN-UI-DESKTOP.
6. Azure Artifacts Feed `nuget-offline` anlegen.
7. Pipeline-Tasks nur aus integrierten Tasks und freigegebenen VSIX-Erweiterungen verwenden.
```

### 4.2 SQL Server

Verbindlich:

```text
SQL Server Standard oder Enterprise
SQL Server 2022 oder SQL Server 2025
Online und Airgap exakt gleicher Hauptversions- und CU-Stand
SQL Server auf Linux nicht verwenden
SQL Express nicht für produktionsnahe Migration verwenden
```

Feature-Mindestumfang:

```text
Database Engine
Full-Text and Semantic Extractions for Search
```

### 4.3 .NET SDK

Vorgabe für neue UI-Testprojekte:

```text
.NET SDK 10.0.9
TargetFramework: net10.0-windows
RuntimeIdentifier: win-x64
```

Begründung für die Zielvorgabe:

```text
.NET 10 ist LTS und bis 14.11.2028 unterstützt.
.NET 8 läuft am 10.11.2026 aus und wird für neue Testprojekte nicht als Zielstandard festgelegt.
```

Installation auf allen Build- und UI-Test-VMs:

```powershell
# Beispielpfad; Installer liegt im MigrationBundle.
Start-Process -FilePath "D:\MigrationBundle\01-installers\dotnet-sdk\dotnet-sdk-10.0.9-win-x64.exe" `
  -ArgumentList "/install", "/quiet", "/norestart" `
  -Wait

dotnet --info
```

### 4.4 Visual C++ Redistributable

Pflicht für OpenCvSharp auf Windows:

```text
Microsoft Visual C++ 2022 Redistributable x64
```

Installation auf allen UI-Test-VMs:

```powershell
Start-Process -FilePath "D:\MigrationBundle\01-installers\vc-redist\VC_redist.x64.exe" `
  -ArgumentList "/install", "/quiet", "/norestart" `
  -Wait
```

### 4.5 Windows SDK Tools

Pflichtwerkzeuge für Analyse und Entwicklung:

```text
Inspect.exe
FlaUInspect
```

Verwendung:

```text
Inspect.exe     zur Gegenprüfung des UIA-Baums
FlaUInspect     zur FlaUI-nahen Kontrolle von UIA2/UIA3
```

Beide Tools werden im Online-Migrationslabor und auf Entwicklerarbeitsplätzen bereitgestellt. Auf den UI-Agent-VMs sind sie optional, aber für Fehlersuche empfohlen.

---

## 5. Azure-DevOps-Erweiterungen im Offlinebetrieb

Marketplace-Erweiterungen sind zulässig, aber keine harte Laufzeitvoraussetzung für die Eggplant-Ablösung.

### 5.1 VSIX-Prozess

```text
1. Im Online-Migrationslabor VSIX-Datei herunterladen.
2. Publisher, Extension-ID, Version, Quelle und SHA-256 erfassen.
3. VSIX im Online-Azure-DevOps-Server testweise importieren.
4. Pipeline mit VSIX-Erweiterung ausführen.
5. VSIX in `MigrationBundle/02-azure-devops-extensions/` aufnehmen.
6. In Airgap-Azure-DevOps-Server über lokale Extension-Verwaltung hochladen.
7. Kompatibilität mit Azure DevOps Server prüfen.
8. Nach Import dieselbe Pipeline ausführen.
```

### 5.2 VSIX-Lockdatei

`vsix-lock.json`:

```json
{
  "extensions": [
    {
      "publisher": "examplePublisher",
      "id": "exampleExtension",
      "version": "1.0.0",
      "file": "examplePublisher.exampleExtension-1.0.0.vsix",
      "sha256": "<SHA256>",
      "required": false,
      "purpose": "optional helper task; not required for UI test execution"
    }
  ]
}
```

### 5.3 Nicht zulässig als kritische Abhängigkeit

```text
Tasks, die zur Laufzeit Internetzugriff benötigen
Tasks, die nur Azure DevOps Services unterstützen
Tasks, die auf externe SaaS-Endpunkte angewiesen sind
Tasks, die Testresultate oder Artefakte außerhalb des Servers speichern
```

---

## 6. VM-Baseline für Desktop-UI-Tests

### 6.1 UI-Test-VM-Spezifikation

| Merkmal | Vorgabe |
|---|---|
| Betriebssystem | Windows 11 Enterprise 25H2 x64 |
| vCPU | mindestens 4, für Visual-Track-Tests 8 empfohlen |
| RAM | mindestens 16 GB, für Visual-Track-Tests 32 GB empfohlen |
| Systemdisk | SSD, mindestens 120 GB |
| Bildschirm | 1920×1080 |
| DPI | 100 % |
| Farbe | 32 Bit |
| Sprache | de-DE |
| Zeitzone | W. Europe Standard Time |
| Energiesparen | aus |
| Monitor-Timeout | aus |
| Sperrbildschirm | aus |
| Windows-Animationen | aus |
| Agent-Modus | interaktiv mit Auto-Logon |
| Agenten pro VM | genau 1 |

### 6.2 Baseline-Skript

`Configure-UiTestVm.ps1`:

```powershell
param(
  [string]$TimeZone = "W. Europe Standard Time"
)

Set-TimeZone -Id $TimeZone

powercfg /change monitor-timeout-ac 0
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /hibernate off

# Animationen reduzieren.
New-Item -Path "HKCU:\Control Panel\Desktop" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "UserPreferencesMask" -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00)) -Type Binary

# Explorer-/Desktoprauschen reduzieren.
New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Type DWord -Value 0

# Testverzeichnisse.
New-Item -ItemType Directory -Force -Path "C:\TestRuntime" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\TestRuntime\Artifacts" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\TestRuntime\Screenshots" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\TestRuntime\Logs" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\TestRuntime\UiaDumps" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\TestRuntime\OpenCv" | Out-Null

Write-Host "UI-Test-VM-Baseline angewendet. Neustart empfohlen."
```

### 6.3 RDP-Regel

RDP-Sitzungen dürfen UI-Testläufe nicht sperren. Beim Trennen ist `tscon` zu verwenden.

`Disconnect-RdpKeepConsole.cmd`:

```bat
@echo off
for /f "skip=1 tokens=3" %%s in ('query user %USERNAME%') do (
  %windir%\System32\tscon.exe %%s /dest:console
)
```

---

## 7. Azure-Pipelines-Agenten

### 7.1 Agent-Installation

Agenten werden nicht als Service installiert. Sie laufen interaktiv mit Auto-Logon.

Beispiel für `AG-UI-WPF-01`:

```powershell
$agentRoot = "C:\azagent"
New-Item -ItemType Directory -Force -Path $agentRoot | Out-Null
Expand-Archive -Path "D:\MigrationBundle\01-installers\azure-pipelines-agent\vsts-agent-win-x64.zip" -DestinationPath $agentRoot -Force
Set-Location $agentRoot

$env:ADO_PAT = "<PAT nur für Agent-Registrierung>"
$env:AGENT_PASSWORD = "<Windows-Passwort des Testbenutzers>"

.\config.cmd --unattended `
  --url "https://AG-ADO-01/tfs/DefaultCollection" `
  --auth pat `
  --token $env:ADO_PAT `
  --pool "WIN-UI-DESKTOP" `
  --agent "AG-UI-WPF-01" `
  --work "C:\azagent\_work" `
  --runAsAutoLogon `
  --windowsLogonAccount "DOMAIN\svc-ui-wpf-01" `
  --windowsLogonPassword $env:AGENT_PASSWORD `
  --overwriteAutoLogon `
  --replace
```

Nach Konfiguration:

```powershell
Restart-Computer
```

Der Agent startet nach Auto-Logon automatisch. Manuell kann er mit folgendem Befehl gestartet werden:

```powershell
C:\azagent\run.cmd
```

### 7.2 Agent-Capabilities setzen

Capabilities werden in Azure DevOps Server gesetzt:

```text
Collection Settings
  → Agent Pools
  → WIN-UI-DESKTOP
  → Agents
  → AG-UI-WPF-01
  → Capabilities
  → User capabilities
```

Für `AG-UI-WPF-01`:

```text
UiBackend=UIA3
UiProfile=WPF
DisplayProfile=FHD_100DPI
VisualTrack=false
```

Für `AG-UI-WF-01`:

```text
UiBackend=UIA2
UiProfile=WinForms
DisplayProfile=FHD_100DPI
VisualTrack=false
```

Für `AG-UI-VIS-01`:

```text
UiBackend=UIA3
UiProfile=WPF
DisplayProfile=FHD_100DPI
VisualTrack=true
```

### 7.3 Pipeline-Demands

```yaml
pool:
  name: WIN-UI-DESKTOP
  demands:
    - UiBackend -equals UIA3
    - DisplayProfile -equals FHD_100DPI
```

Visual-Track-Tests:

```yaml
pool:
  name: WIN-UI-DESKTOP
  demands:
    - VisualTrack -equals true
    - DisplayProfile -equals FHD_100DPI
```

---

## 8. NuGet- und Paketstrategie

### 8.1 Grundsatz

```text
Keine Paketversionen mit Wildcards.
Keine Floating Versions.
Keine externen Feeds in Airgap.
Central Package Management verwenden.
packages.lock.json einchecken.
dotnet restore immer mit --locked-mode.
```

### 8.2 Feed-Aufbau

Online-Migrationslabor:

```text
Feed: nuget-offline
Upstream: nuget.org nur während Paketaufbau aktiv
Ziel: alle benötigten Pakete und Transitiven einmalig cachen/exportieren
```

Airgap:

```text
Feed: nuget-offline
Upstream: keiner
Paketimport: ausschließlich aus MigrationBundle/03-nuget/packages
```

### 8.3 NuGet.config

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="nuget-offline" value="https://AG-ADO-01/tfs/DefaultCollection/_packaging/nuget-offline/nuget/v3/index.json" />
  </packageSources>
  <packageSourceMapping>
    <packageSource key="nuget-offline">
      <package pattern="*" />
    </packageSource>
  </packageSourceMapping>
</configuration>
```

Für das Online-Migrationslabor wird derselbe Feedname verwendet; nur die Server-URL unterscheidet sich.

### 8.4 Paketimport in Azure Artifacts

```powershell
$feedUrl = "https://AG-ADO-01/tfs/DefaultCollection/_packaging/nuget-offline/nuget/v3/index.json"
$packages = Get-ChildItem "D:\MigrationBundle\03-nuget\packages" -Filter *.nupkg

foreach ($pkg in $packages) {
  dotnet nuget push $pkg.FullName `
    --source $feedUrl `
    --api-key az `
    --skip-duplicate
}
```

### 8.5 Exakte Paketliste

| Paket | Version | Verwendung |
|---|---:|---|
| `FlaUI.Core` | `5.0.0` | Basisbibliothek für FlaUI |
| `FlaUI.UIA3` | `5.0.0` | WPF/UIA3-Teststrang |
| `FlaUI.UIA2` | `5.0.0` | WinForms/UIA2-Teststrang |
| `NUnit` | `4.6.1` | Testframework |
| `NUnit3TestAdapter` | `6.2.0` | Testadapter für `dotnet test`/VSTest |
| `NUnit.Analyzers` | `4.14.0` | statische Prüfung von NUnit-Testcode |
| `Microsoft.NET.Test.Sdk` | `18.0.0` | .NET-Testausführung |
| `OpenCvSharp4.Windows` | `4.13.0.20260531` | OpenCV unter Windows inklusive Runtime-Paket |
| `Verify.NUnit` | `31.19.1` | strukturierte Snapshots |
| `Serilog` | `4.3.1` | Logging |
| `Serilog.Sinks.File` | `7.0.0` | Logdateien |
| `Serilog.Sinks.Console` | `6.1.1` | Konsolenlogs |
| `Serilog.Formatting.Compact` | `3.0.0` | kompakte JSON-Logs |
| `Serilog.Enrichers.Environment` | `3.0.1` | Agent-/Maschineninformationen im Log |
| `Microsoft.Extensions.Configuration.Json` | `10.0.9` | Testkonfiguration aus JSON |
| `Microsoft.Extensions.Configuration.EnvironmentVariables` | `10.0.9` | Pipeline-Overrides per Environment Variables |
| `Microsoft.Extensions.Configuration.Binder` | `10.0.9` | strongly typed Testkonfiguration |

---

## 9. Repository-Struktur

```text
repo-root/
  azure-pipelines.yml
  Directory.Build.props
  Directory.Packages.props
  NuGet.config
  global.json

  src/
    Product/
      Product.csproj

  tests/
    Product.UiTests.Shared/
      Product.UiTests.Shared.csproj
      Configuration/
      Diagnostics/
      Infrastructure/
      Screens/
      Visual/

    Product.UiTests.Uia3/
      Product.UiTests.Uia3.csproj
      AssemblyInfo.cs
      Wpf/
      Smoke/
      VisualTrack/

    Product.UiTests.Uia2/
      Product.UiTests.Uia2.csproj
      AssemblyInfo.cs
      WinForms/
      Smoke/
      VisualTrack/

    Product.UiTests.TestAssets/
      Scenarios/
      TrackRoutes/
      Calibration/
      Templates/
      SyntheticImages/

  scripts/
    Build/
    AzureDevOps/
    Agents/
    VmBaseline/
    NuGet/
    Diagnostics/

  docs/
    migration/
      eggplant-to-flaui.md
      testability-rules.md
      visual-track-validation.md
```

### 9.1 global.json

```json
{
  "sdk": {
    "version": "10.0.9",
    "rollForward": "latestFeature"
  }
}
```

### 9.2 Directory.Build.props

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0-windows</TargetFramework>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <WarningsAsErrors />
    <AnalysisLevel>latest</AnalysisLevel>
    <IsPackable>false</IsPackable>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode Condition="'$(ContinuousIntegrationBuild)' == 'true'">true</RestoreLockedMode>
  </PropertyGroup>
</Project>
```

### 9.3 Directory.Packages.props

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <PackageVersion Include="FlaUI.Core" Version="5.0.0" />
    <PackageVersion Include="FlaUI.UIA3" Version="5.0.0" />
    <PackageVersion Include="FlaUI.UIA2" Version="5.0.0" />

    <PackageVersion Include="NUnit" Version="4.6.1" />
    <PackageVersion Include="NUnit3TestAdapter" Version="6.2.0" />
    <PackageVersion Include="NUnit.Analyzers" Version="4.14.0" />
    <PackageVersion Include="Microsoft.NET.Test.Sdk" Version="18.0.0" />

    <PackageVersion Include="OpenCvSharp4.Windows" Version="4.13.0.20260531" />
    <PackageVersion Include="Verify.NUnit" Version="31.19.1" />

    <PackageVersion Include="Serilog" Version="4.3.1" />
    <PackageVersion Include="Serilog.Sinks.File" Version="7.0.0" />
    <PackageVersion Include="Serilog.Sinks.Console" Version="6.1.1" />
    <PackageVersion Include="Serilog.Formatting.Compact" Version="3.0.0" />
    <PackageVersion Include="Serilog.Enrichers.Environment" Version="3.0.1" />

    <PackageVersion Include="Microsoft.Extensions.Configuration.Json" Version="10.0.9" />
    <PackageVersion Include="Microsoft.Extensions.Configuration.EnvironmentVariables" Version="10.0.9" />
    <PackageVersion Include="Microsoft.Extensions.Configuration.Binder" Version="10.0.9" />
  </ItemGroup>
</Project>
```

### 9.4 Shared-Projekt

`tests/Product.UiTests.Shared/Product.UiTests.Shared.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="FlaUI.Core" />
    <PackageReference Include="OpenCvSharp4.Windows" />
    <PackageReference Include="Serilog" />
    <PackageReference Include="Serilog.Sinks.File" />
    <PackageReference Include="Serilog.Sinks.Console" />
    <PackageReference Include="Serilog.Formatting.Compact" />
    <PackageReference Include="Serilog.Enrichers.Environment" />
    <PackageReference Include="Microsoft.Extensions.Configuration.Json" />
    <PackageReference Include="Microsoft.Extensions.Configuration.EnvironmentVariables" />
    <PackageReference Include="Microsoft.Extensions.Configuration.Binder" />
  </ItemGroup>
</Project>
```

### 9.5 WPF/UIA3-Testprojekt

`tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <ProjectReference Include="..\Product.UiTests.Shared\Product.UiTests.Shared.csproj" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="FlaUI.UIA3" />
    <PackageReference Include="NUnit" />
    <PackageReference Include="NUnit3TestAdapter" />
    <PackageReference Include="NUnit.Analyzers" PrivateAssets="all" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" />
    <PackageReference Include="Verify.NUnit" />
  </ItemGroup>
</Project>
```

### 9.6 WinForms/UIA2-Testprojekt

`tests/Product.UiTests.Uia2/Product.UiTests.Uia2.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <ProjectReference Include="..\Product.UiTests.Shared\Product.UiTests.Shared.csproj" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="FlaUI.UIA2" />
    <PackageReference Include="NUnit" />
    <PackageReference Include="NUnit3TestAdapter" />
    <PackageReference Include="NUnit.Analyzers" PrivateAssets="all" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" />
    <PackageReference Include="Verify.NUnit" />
  </ItemGroup>
</Project>
```

### 9.7 AssemblyInfo für nicht parallele UI-Tests

`tests/Product.UiTests.Uia3/AssemblyInfo.cs`:

```csharp
using NUnit.Framework;

[assembly: LevelOfParallelism(1)]
[assembly: NonParallelizable]
```

`tests/Product.UiTests.Uia2/AssemblyInfo.cs`:

```csharp
using NUnit.Framework;

[assembly: LevelOfParallelism(1)]
[assembly: NonParallelizable]
```

---

## 10. Testbarkeitsanforderungen an die Anwendung

### 10.1 WPF

Jedes fachlich relevante Control erhält eine stabile AutomationId.

```xml
<Button
    Content="Speichern"
    AutomationProperties.AutomationId="Customer.SaveButton"
    AutomationProperties.Name="Speichern" />
```

Regeln:

```text
AutomationId ist technisch stabil und nicht lokalisiert.
AutomationId enthält keine dynamischen IDs.
AutomationId enthält keine Laufzeitdaten.
AutomationId ist innerhalb des Containers eindeutig.
Fachlich relevante Custom Controls bekommen AutomationPeers.
```

### 10.2 WinForms

WinForms-Controls erhalten stabile technische Namen und Accessibility-Eigenschaften.

```csharp
var saveButton = new Button
{
    Name = "Customer_SaveButton",
    AccessibleName = "Customer.SaveButton",
    AccessibleDescription = "Speichert den aktuellen Kunden",
    Text = "Speichern"
};
```

Regeln:

```text
Name und AccessibleName sind stabil.
Visible Text ist nicht Primärselektor.
Dynamisch erzeugte Controls bekommen deterministische Namen.
Custom Controls liefern sinnvolle AccessibleRole-/AccessibleName-Informationen.
```

### 10.3 Testhooks für deterministische Visual-Track-Tests

Für Flugzeug-/Track-Line-Tests ist ein Testmodus der Anwendung Pflicht.

Mindestfunktionen:

```text
LoadScenario(scenarioId)
SetSimulationTime(utcTimestamp)
RenderFrame()
SetMapZoom(zoomLevel)
SetMapViewport(centerLat, centerLon, widthNm, heightNm)
GetMapCalibration()
GetExpectedRoute(scenarioId, timestamp)
```

Diese Funktionen können über eine der folgenden technischen Schnittstellen bereitgestellt werden:

```text
verstecktes Testmenü mit AutomationIds
lokale Test-API innerhalb der Anwendung
Command-Line-Parameter beim Start
Testkonfigurationsdatei
interner Debug-/Test-Service
```

Für die neue Architektur wird folgender UIA-basierter Mindestpfad festgelegt:

| Funktion | UIA-Element |
|---|---|
| Szenario laden | `TestHooks.LoadScenarioButton` |
| Szenario-ID setzen | `TestHooks.ScenarioIdTextBox` |
| Simulationszeit setzen | `TestHooks.SimulationTimeTextBox` |
| Zoom setzen | `TestHooks.MapZoomTextBox` |
| Frame rendern | `TestHooks.RenderFrameButton` |
| Karten-/Canvas-Region | `AircraftMapCanvas` |

---

## 11. Testinfrastruktur im C#-Stack

### 11.1 Pflichtklassen

```text
AppLauncher
AutomationFactory
WindowFinder
Waiter
ScreenBase
ArtifactPaths
ScreenshotService
UiaTreeDumper
FailureArtifactCollector
TestEnvironmentGuard
TestConfiguration
TrackRouteDefinition
TrackLineDeviationAnalyzer
TrackLineArtifactWriter
```

### 11.2 TestConfiguration

```csharp
namespace Product.UiTests.Shared.Configuration;

public sealed class TestConfiguration
{
    public required string AppUnderTestPath { get; init; }
    public required string ArtifactRoot { get; init; }
    public required string ScenarioRoot { get; init; }
    public required string CalibrationRoot { get; init; }
    public int MainWindowTimeoutSeconds { get; init; } = 60;
    public string DisplayProfile { get; init; } = "FHD_100DPI";
}
```

### 11.3 ConfigurationLoader

```csharp
using Microsoft.Extensions.Configuration;

namespace Product.UiTests.Shared.Configuration;

public static class ConfigurationLoader
{
    public static TestConfiguration Load()
    {
        var config = new ConfigurationBuilder()
            .AddJsonFile("appsettings.uitests.json", optional: true)
            .AddEnvironmentVariables(prefix: "UI_TEST_")
            .Build();

        var result = config.Get<TestConfiguration>();
        if (result is null)
        {
            throw new InvalidOperationException("UI-Testkonfiguration konnte nicht geladen werden.");
        }

        if (string.IsNullOrWhiteSpace(result.AppUnderTestPath))
        {
            throw new InvalidOperationException("AppUnderTestPath fehlt.");
        }

        return result;
    }
}
```

### 11.4 ArtifactPaths

```csharp
namespace Product.UiTests.Shared.Diagnostics;

public sealed class ArtifactPaths
{
    public ArtifactPaths(string artifactRoot, string testName)
    {
        Root = Path.Combine(artifactRoot, Sanitize(testName), DateTime.UtcNow.ToString("yyyyMMdd_HHmmss_fff"));
        Screenshots = Path.Combine(Root, "screenshots");
        OpenCv = Path.Combine(Root, "opencv");
        Logs = Path.Combine(Root, "logs");
        UiaDumps = Path.Combine(Root, "uia");
        Metadata = Path.Combine(Root, "metadata");

        Directory.CreateDirectory(Screenshots);
        Directory.CreateDirectory(OpenCv);
        Directory.CreateDirectory(Logs);
        Directory.CreateDirectory(UiaDumps);
        Directory.CreateDirectory(Metadata);
    }

    public string Root { get; }
    public string Screenshots { get; }
    public string OpenCv { get; }
    public string Logs { get; }
    public string UiaDumps { get; }
    public string Metadata { get; }

    private static string Sanitize(string value)
    {
        foreach (var invalid in Path.GetInvalidFileNameChars())
        {
            value = value.Replace(invalid, '_');
        }

        return value.Replace(' ', '_');
    }
}
```

### 11.5 TestEnvironmentGuard

```csharp
using System.Runtime.InteropServices;

namespace Product.UiTests.Shared.Infrastructure;

public static class TestEnvironmentGuard
{
    public static void AssertDeterministicDesktop()
    {
        var width = GetSystemMetrics(0);
        var height = GetSystemMetrics(1);

        if (width != 1920 || height != 1080)
        {
            throw new InvalidOperationException($"Falsche Auflösung: {width}x{height}. Erwartet: 1920x1080.");
        }

        using var g = System.Drawing.Graphics.FromHwnd(IntPtr.Zero);
        if (Math.Round(g.DpiX) != 96 || Math.Round(g.DpiY) != 96)
        {
            throw new InvalidOperationException($"Falsche DPI: {g.DpiX}x{g.DpiY}. Erwartet: 96x96.");
        }
    }

    [DllImport("user32.dll")]
    private static extern int GetSystemMetrics(int nIndex);
}
```

---

## 12. Screen-Object-Struktur

### 12.1 WPF-Screen-Object

```csharp
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using FlaUI.Core.Definitions;

namespace Product.UiTests.Shared.Screens;

public sealed class AircraftMapScreen
{
    private readonly Window _window;
    private readonly ConditionFactory _cf;

    public AircraftMapScreen(Window window, ConditionFactory cf)
    {
        _window = window;
        _cf = cf;
    }

    public AutomationElement MapCanvas => _window.FindFirstDescendant(_cf.ByAutomationId("AircraftMapCanvas"))
        ?? throw new InvalidOperationException("AircraftMapCanvas nicht gefunden.");

    public void LoadScenario(string scenarioId)
    {
        _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.LoadScenarioButton"))
            ?.AsButton()
            .Invoke();

        var textBox = _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.ScenarioIdTextBox"))
            ?.AsTextBox()
            ?? throw new InvalidOperationException("ScenarioIdTextBox nicht gefunden.");

        textBox.Text = string.Empty;
        textBox.Enter(scenarioId);

        _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.ConfirmScenarioButton"))
            ?.AsButton()
            .Invoke();
    }

    public void SetSimulationTime(DateTime utc)
    {
        var textBox = _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.SimulationTimeTextBox"))
            ?.AsTextBox()
            ?? throw new InvalidOperationException("SimulationTimeTextBox nicht gefunden.");

        textBox.Text = string.Empty;
        textBox.Enter(utc.ToString("O"));
    }

    public void RenderFrame()
    {
        _window.FindFirstDescendant(_cf.ByAutomationId("TestHooks.RenderFrameButton"))
            ?.AsButton()
            .Invoke();
    }
}
```

### 12.2 Kein Koordinatenstandard

Koordinaten werden nicht zum Bedienen normaler Controls verwendet.

Zulässig:

```text
ROI-Ermittlung über BoundingRectangle
OpenCV-Auswertung innerhalb der ROI
Overlay-Artefakte mit Pixelkoordinaten
fachliche Abweichungsmessung in Pixel und nautischen Meilen
```

Nicht zulässig:

```text
Button per x/y klicken
Textfeld per x/y fokussieren
Dialog per Bildschirmkoordinate bedienen
Full-Screen-Pixelvergleich als primäre fachliche Assertion
```

---

## 13. Visual-Track-Line-Validierung als Pflichtbestandteil

### 13.1 Testziel

Die neue Lösung muss dünne, wenige Pixel breite Linien erkennen und fachlich bewerten können. Beispiel:

```text
Ein Flugzeug bewegt sich über eine Karte.
Die Anwendung rendert eine Spur-/Track-Linie hinter dem Flugzeug.
Eine Abweichung von wenigen Pixeln entspricht mehreren nautischen Meilen.
Der Test muss die Abweichung erkennen, quantifizieren und bei Überschreitung fehlschlagen.
```

### 13.2 Messgrößen

| Metrik | Bedeutung |
|---|---|
| `TrackDetected` | Es wurde überhaupt eine Spur erkannt |
| `CoverageRatio` | Anteil der erwarteten Route, der durch erkannte Spur abgedeckt ist |
| `MaxDeviationPx` | maximale Pixelabweichung des Ist-Tracks zur Sollroute |
| `MeanDeviationPx` | mittlere Pixelabweichung |
| `P95DeviationPx` | 95%-Quantil der Pixelabweichung |
| `MaxDeviationNm` | maximale Abweichung in nautischen Meilen |
| `BrokenSegments` | erkannte Unterbrechungen in der Spur |
| `ActualTrackPixels` | Anzahl erkannter Track-Pixel |

### 13.3 Harte Default-Schwellwerte

Diese Werte werden initial verwendet und je Szenario versioniert überschrieben:

```text
TrackDetected muss true sein.
CoverageRatio muss >= 0.90 sein.
MaxDeviationNm muss <= allowedDeviationNm sein.
BrokenSegments muss <= allowedBrokenSegments sein.
ActualTrackPixels muss >= minTrackPixels sein.
```

### 13.4 Algorithmus

```text
1. FlaUI öffnet deterministisches Szenario.
2. FlaUI setzt Simulationszeitpunkt und Zoom.
3. FlaUI rendert exakt einen Frame.
4. FlaUI ermittelt BoundingRectangle der Karten-/Canvas-ROI.
5. Screenshot nur der ROI wird gespeichert.
6. OpenCV lädt ROI als Mat.
7. OpenCV konvertiert BGR → HSV.
8. OpenCV extrahiert Track-Pixel per InRange.
9. Morphological Closing schließt kleine Antialiasing-/Rendering-Lücken.
10. Erwartete Route wird als 1-px-Maske gerendert.
11. Toleranzkorridor wird per Dilate aus der Sollroute erzeugt.
12. Distance Transform misst Abstände vom Ist-Track zur Sollroute.
13. Abweichung wird von Pixeln in nautische Meilen umgerechnet.
14. NUnit assertet TrackDetected, CoverageRatio, MaxDeviationNm und BrokenSegments.
15. Artefakte werden geschrieben: ROI, Masken, Overlay, JSON-Ergebnis.
```

### 13.5 Artefakte pro Visual-Track-Test

```text
track-source.png
track-actual-mask.png
track-actual-mask-closed.png
track-expected-mask.png
track-tolerance-mask.png
track-deviation-overlay.png
track-deviation-heatmap.png
track-analysis.json
track-route-definition.json
metadata.json
```

---

## 14. Track-Route-Dateiformat

`tests/Product.UiTests.TestAssets/TrackRoutes/TRACK_ROUTE_001.json`:

```json
{
  "scenarioId": "TRACK_ROUTE_001",
  "uiBackend": "UIA3",
  "mapAutomationId": "AircraftMapCanvas",
  "simulationTimeUtc": "2026-06-10T10:15:00Z",
  "displayProfile": "FHD_100DPI",
  "zoomLevel": "Z08",
  "nauticalMilesPerPixel": 2.5,
  "allowedDeviationNm": 5.0,
  "coverageThreshold": 0.90,
  "allowedBrokenSegments": 0,
  "minTrackPixels": 120,
  "trackColorHsvLower": [20, 120, 120],
  "trackColorHsvUpper": [45, 255, 255],
  "expectedRoute": [
    { "x": 120.0, "y": 430.0 },
    { "x": 180.0, "y": 398.0 },
    { "x": 245.0, "y": 360.0 },
    { "x": 320.0, "y": 310.0 },
    { "x": 410.0, "y": 260.0 },
    { "x": 520.0, "y": 220.0 }
  ],
  "maskedRegions": [
    { "name": "clock", "x": 0, "y": 0, "width": 160, "height": 40 }
  ]
}
```

Regel:

```text
Alle Pixelkoordinaten beziehen sich auf die ROI, nicht auf den gesamten Bildschirm.
```

---

## 15. C#-Implementierung: Track-Line-Analyzer

### 15.1 Datenmodelle

`tests/Product.UiTests.Shared/Visual/TrackRouteDefinition.cs`:

```csharp
using System.Text.Json.Serialization;
using OpenCvSharp;

namespace Product.UiTests.Shared.Visual;

public sealed class TrackRouteDefinition
{
    public required string ScenarioId { get; init; }
    public required string UiBackend { get; init; }
    public required string MapAutomationId { get; init; }
    public required DateTime SimulationTimeUtc { get; init; }
    public required string DisplayProfile { get; init; }
    public required string ZoomLevel { get; init; }
    public required double NauticalMilesPerPixel { get; init; }
    public required double AllowedDeviationNm { get; init; }
    public required double CoverageThreshold { get; init; }
    public required int AllowedBrokenSegments { get; init; }
    public required int MinTrackPixels { get; init; }
    public required int[] TrackColorHsvLower { get; init; }
    public required int[] TrackColorHsvUpper { get; init; }
    public required List<RoutePoint> ExpectedRoute { get; init; }
    public List<MaskedRegion> MaskedRegions { get; init; } = [];

    [JsonIgnore]
    public Scalar LowerHsv => ToScalar(TrackColorHsvLower);

    [JsonIgnore]
    public Scalar UpperHsv => ToScalar(TrackColorHsvUpper);

    private static Scalar ToScalar(IReadOnlyList<int> values)
    {
        if (values.Count != 3)
        {
            throw new InvalidOperationException("HSV-Grenze muss exakt drei Werte enthalten.");
        }

        return new Scalar(values[0], values[1], values[2]);
    }
}

public sealed record RoutePoint(double X, double Y)
{
    public Point2f ToPoint2f() => new((float)X, (float)Y);
}

public sealed record MaskedRegion(string Name, int X, int Y, int Width, int Height);
```

`tests/Product.UiTests.Shared/Visual/TrackLineAnalysisResult.cs`:

```csharp
namespace Product.UiTests.Shared.Visual;

public sealed record TrackLineAnalysisResult(
    bool TrackDetected,
    int ActualTrackPixels,
    double CoverageRatio,
    double MaxDeviationPx,
    double MeanDeviationPx,
    double P95DeviationPx,
    double MaxDeviationNm,
    int BrokenSegments,
    string SourceImagePath,
    string ActualMaskPath,
    string ExpectedMaskPath,
    string ToleranceMaskPath,
    string OverlayPath,
    string AnalysisJsonPath);
```

### 15.2 Analyzer

`tests/Product.UiTests.Shared/Visual/TrackLineDeviationAnalyzer.cs`:

```csharp
using System.Text.Json;
using OpenCvSharp;

namespace Product.UiTests.Shared.Visual;

public static class TrackLineDeviationAnalyzer
{
    public static TrackLineAnalysisResult Analyze(
        string roiImagePath,
        TrackRouteDefinition route,
        string artifactDirectory)
    {
        Directory.CreateDirectory(artifactDirectory);

        using var source = Cv2.ImRead(roiImagePath, ImreadModes.Color);
        if (source.Empty())
        {
            throw new InvalidOperationException($"ROI-Screenshot konnte nicht geladen werden: {roiImagePath}");
        }

        ValidateRoute(route, source.Width, source.Height);

        using var preprocessed = source.Clone();
        ApplyMasks(preprocessed, route.MaskedRegions);

        using var hsv = new Mat();
        Cv2.CvtColor(preprocessed, hsv, ColorConversionCodes.BGR2HSV);

        using var actualMaskRaw = new Mat();
        Cv2.InRange(hsv, route.LowerHsv, route.UpperHsv, actualMaskRaw);

        using var closeKernel = Cv2.GetStructuringElement(MorphShapes.Rect, new Size(3, 3));
        using var actualMaskClosed = new Mat();
        Cv2.MorphologyEx(actualMaskRaw, actualMaskClosed, MorphTypes.Close, closeKernel);

        using var expectedMask = CreateExpectedRouteMask(source.Size(), route.ExpectedRoute.Select(p => p.ToPoint2f()).ToList());
        using var toleranceMask = CreateToleranceMask(expectedMask, route.AllowedDeviationNm / route.NauticalMilesPerPixel);

        var actualTrackPixels = Cv2.CountNonZero(actualMaskClosed);
        if (actualTrackPixels < route.MinTrackPixels)
        {
            var emptyResult = WriteResult(
                trackDetected: false,
                actualTrackPixels: actualTrackPixels,
                coverageRatio: 0,
                maxDeviationPx: double.PositiveInfinity,
                meanDeviationPx: double.PositiveInfinity,
                p95DeviationPx: double.PositiveInfinity,
                nauticalMilesPerPixel: route.NauticalMilesPerPixel,
                brokenSegments: int.MaxValue,
                source: preprocessed,
                actualMask: actualMaskClosed,
                expectedMask: expectedMask,
                toleranceMask: toleranceMask,
                route: route,
                artifactDirectory: artifactDirectory);

            return emptyResult;
        }

        var coverageRatio = CalculateCoverageRatio(expectedMask, actualMaskClosed, route.AllowedDeviationNm / route.NauticalMilesPerPixel);
        var deviationsPx = CalculateActualPixelDeviations(actualMaskClosed, expectedMask);
        var brokenSegments = CountBrokenExpectedSegments(expectedMask, actualMaskClosed, route.AllowedDeviationNm / route.NauticalMilesPerPixel);

        var maxDeviationPx = deviationsPx.Count == 0 ? double.PositiveInfinity : deviationsPx.Max();
        var meanDeviationPx = deviationsPx.Count == 0 ? double.PositiveInfinity : deviationsPx.Average();
        var p95DeviationPx = deviationsPx.Count == 0 ? double.PositiveInfinity : Percentile(deviationsPx, 0.95);

        return WriteResult(
            trackDetected: true,
            actualTrackPixels: actualTrackPixels,
            coverageRatio: coverageRatio,
            maxDeviationPx: maxDeviationPx,
            meanDeviationPx: meanDeviationPx,
            p95DeviationPx: p95DeviationPx,
            nauticalMilesPerPixel: route.NauticalMilesPerPixel,
            brokenSegments: brokenSegments,
            source: preprocessed,
            actualMask: actualMaskClosed,
            expectedMask: expectedMask,
            toleranceMask: toleranceMask,
            route: route,
            artifactDirectory: artifactDirectory);
    }

    private static void ValidateRoute(TrackRouteDefinition route, int width, int height)
    {
        if (route.NauticalMilesPerPixel <= 0)
        {
            throw new InvalidOperationException("NauticalMilesPerPixel muss > 0 sein.");
        }

        if (route.ExpectedRoute.Count < 2)
        {
            throw new InvalidOperationException("ExpectedRoute benötigt mindestens zwei Punkte.");
        }

        foreach (var point in route.ExpectedRoute)
        {
            if (point.X < 0 || point.Y < 0 || point.X >= width || point.Y >= height)
            {
                throw new InvalidOperationException($"Routenpunkt außerhalb ROI: {point.X},{point.Y}; ROI={width}x{height}");
            }
        }
    }

    private static void ApplyMasks(Mat image, IReadOnlyList<MaskedRegion> regions)
    {
        foreach (var region in regions)
        {
            var rect = new Rect(region.X, region.Y, region.Width, region.Height);
            Cv2.Rectangle(image, rect, Scalar.Black, thickness: -1);
        }
    }

    private static Mat CreateExpectedRouteMask(Size size, IReadOnlyList<Point2f> route)
    {
        var mask = Mat.Zeros(size.Height, size.Width, MatType.CV_8UC1);

        for (var i = 0; i < route.Count - 1; i++)
        {
            Cv2.Line(
                mask,
                ToPoint(route[i]),
                ToPoint(route[i + 1]),
                Scalar.White,
                thickness: 1,
                lineType: LineTypes.AntiAlias);
        }

        Cv2.Threshold(mask, mask, 1, 255, ThresholdTypes.Binary);
        return mask;
    }

    private static Mat CreateToleranceMask(Mat expectedMask, double allowedDeviationPx)
    {
        var kernelSize = ToOddKernelSize(allowedDeviationPx * 2 + 1);
        using var kernel = Cv2.GetStructuringElement(MorphShapes.Ellipse, new Size(kernelSize, kernelSize));
        var toleranceMask = new Mat();
        Cv2.Dilate(expectedMask, toleranceMask, kernel);
        return toleranceMask;
    }

    private static double CalculateCoverageRatio(Mat expectedMask, Mat actualMask, double allowedDeviationPx)
    {
        var kernelSize = ToOddKernelSize(allowedDeviationPx * 2 + 1);
        using var kernel = Cv2.GetStructuringElement(MorphShapes.Ellipse, new Size(kernelSize, kernelSize));
        using var actualDilated = new Mat();
        Cv2.Dilate(actualMask, actualDilated, kernel);

        using var coveredExpected = new Mat();
        Cv2.BitwiseAnd(expectedMask, actualDilated, coveredExpected);

        var expectedPixels = Cv2.CountNonZero(expectedMask);
        if (expectedPixels == 0)
        {
            return 0;
        }

        return Cv2.CountNonZero(coveredExpected) / (double)expectedPixels;
    }

    private static List<double> CalculateActualPixelDeviations(Mat actualMask, Mat expectedMask)
    {
        using var invertedExpected = new Mat();
        Cv2.BitwiseNot(expectedMask, invertedExpected);

        using var distance = new Mat();
        Cv2.DistanceTransform(invertedExpected, distance, DistanceTypes.L2, DistanceTransformMasks.Mask3);

        var deviations = new List<double>(capacity: Math.Max(128, Cv2.CountNonZero(actualMask)));

        for (var y = 0; y < actualMask.Rows; y++)
        {
            for (var x = 0; x < actualMask.Cols; x++)
            {
                if (actualMask.At<byte>(y, x) == 0)
                {
                    continue;
                }

                deviations.Add(distance.At<float>(y, x));
            }
        }

        return deviations;
    }

    private static int CountBrokenExpectedSegments(Mat expectedMask, Mat actualMask, double allowedDeviationPx)
    {
        var kernelSize = ToOddKernelSize(allowedDeviationPx * 2 + 1);
        using var kernel = Cv2.GetStructuringElement(MorphShapes.Ellipse, new Size(kernelSize, kernelSize));
        using var actualDilated = new Mat();
        Cv2.Dilate(actualMask, actualDilated, kernel);

        using var uncoveredExpected = new Mat();
        Cv2.BitwiseAnd(expectedMask, ~actualDilated, uncoveredExpected);

        Cv2.ConnectedComponentsWithStats(
            uncoveredExpected,
            out var labels,
            out var stats,
            out _,
            PixelConnectivity.Connectivity8,
            MatType.CV_32S);

        using (labels)
        using (stats)
        {
            var brokenSegments = 0;
            for (var label = 1; label < stats.Rows; label++)
            {
                var area = stats.At<int>(label, (int)ConnectedComponentsTypes.Area);
                if (area >= 4)
                {
                    brokenSegments++;
                }
            }

            return brokenSegments;
        }
    }

    private static TrackLineAnalysisResult WriteResult(
        bool trackDetected,
        int actualTrackPixels,
        double coverageRatio,
        double maxDeviationPx,
        double meanDeviationPx,
        double p95DeviationPx,
        double nauticalMilesPerPixel,
        int brokenSegments,
        Mat source,
        Mat actualMask,
        Mat expectedMask,
        Mat toleranceMask,
        TrackRouteDefinition route,
        string artifactDirectory)
    {
        var sourcePath = Path.Combine(artifactDirectory, "track-source.png");
        var actualMaskPath = Path.Combine(artifactDirectory, "track-actual-mask.png");
        var expectedMaskPath = Path.Combine(artifactDirectory, "track-expected-mask.png");
        var toleranceMaskPath = Path.Combine(artifactDirectory, "track-tolerance-mask.png");
        var overlayPath = Path.Combine(artifactDirectory, "track-deviation-overlay.png");
        var analysisPath = Path.Combine(artifactDirectory, "track-analysis.json");

        using var overlay = CreateOverlay(source, actualMask, expectedMask, toleranceMask);

        Cv2.ImWrite(sourcePath, source);
        Cv2.ImWrite(actualMaskPath, actualMask);
        Cv2.ImWrite(expectedMaskPath, expectedMask);
        Cv2.ImWrite(toleranceMaskPath, toleranceMask);
        Cv2.ImWrite(overlayPath, overlay);

        var result = new TrackLineAnalysisResult(
            TrackDetected: trackDetected,
            ActualTrackPixels: actualTrackPixels,
            CoverageRatio: coverageRatio,
            MaxDeviationPx: maxDeviationPx,
            MeanDeviationPx: meanDeviationPx,
            P95DeviationPx: p95DeviationPx,
            MaxDeviationNm: maxDeviationPx * nauticalMilesPerPixel,
            BrokenSegments: brokenSegments,
            SourceImagePath: sourcePath,
            ActualMaskPath: actualMaskPath,
            ExpectedMaskPath: expectedMaskPath,
            ToleranceMaskPath: toleranceMaskPath,
            OverlayPath: overlayPath,
            AnalysisJsonPath: analysisPath);

        var json = JsonSerializer.Serialize(new
        {
            route.ScenarioId,
            route.DisplayProfile,
            route.ZoomLevel,
            route.NauticalMilesPerPixel,
            route.AllowedDeviationNm,
            result.TrackDetected,
            result.ActualTrackPixels,
            result.CoverageRatio,
            result.MaxDeviationPx,
            result.MeanDeviationPx,
            result.P95DeviationPx,
            result.MaxDeviationNm,
            result.BrokenSegments,
            result.SourceImagePath,
            result.ActualMaskPath,
            result.ExpectedMaskPath,
            result.ToleranceMaskPath,
            result.OverlayPath
        }, new JsonSerializerOptions { WriteIndented = true });

        File.WriteAllText(analysisPath, json);
        return result;
    }

    private static Mat CreateOverlay(Mat source, Mat actualMask, Mat expectedMask, Mat toleranceMask)
    {
        var overlay = source.Clone();

        using var toleranceEdges = new Mat();
        Cv2.Canny(toleranceMask, toleranceEdges, 50, 150);

        overlay.SetTo(new Scalar(255, 0, 0), toleranceEdges);   // Blau: Toleranzrand
        overlay.SetTo(new Scalar(0, 0, 255), expectedMask);     // Rot: Sollroute
        overlay.SetTo(new Scalar(0, 255, 0), actualMask);       // Grün: erkannter Track

        return overlay;
    }

    private static int ToOddKernelSize(double value)
    {
        var size = (int)Math.Ceiling(value);
        if (size % 2 == 0)
        {
            size++;
        }

        return Math.Max(size, 3);
    }

    private static Point ToPoint(Point2f point)
        => new((int)Math.Round(point.X), (int)Math.Round(point.Y));

    private static double Percentile(List<double> values, double percentile)
    {
        values.Sort();
        var index = (int)Math.Ceiling(percentile * values.Count) - 1;
        index = Math.Clamp(index, 0, values.Count - 1);
        return values[index];
    }
}
```

### 15.3 NUnit-Test für WPF/UIA3

`tests/Product.UiTests.Uia3/VisualTrack/AircraftTrackLineTests.cs`:

```csharp
using System.Text.Json;
using FlaUI.Core;
using FlaUI.Core.Capturing;
using FlaUI.Core.Conditions;
using FlaUI.UIA3;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;
using Product.UiTests.Shared.Visual;

namespace Product.UiTests.Uia3.VisualTrack;

[TestFixture]
[NonParallelizable]
[Category("VisualTrack")]
[Category("UIA3")]
public sealed class AircraftTrackLineTests
{
    private Application? _app;
    private UIA3Automation? _automation;
    private TestConfiguration? _config;
    private ArtifactPaths? _artifacts;

    [SetUp]
    public void SetUp()
    {
        TestEnvironmentGuard.AssertDeterministicDesktop();

        _config = ConfigurationLoader.Load();
        _artifacts = new ArtifactPaths(_config.ArtifactRoot, TestContext.CurrentContext.Test.Name);

        _app = Application.Launch(_config.AppUnderTestPath);
        _automation = new UIA3Automation();
    }

    [TearDown]
    public void TearDown()
    {
        if (TestContext.CurrentContext.Result.Outcome.Status == NUnit.Framework.Interfaces.TestStatus.Failed)
        {
            TestContext.AddTestAttachment(_artifacts!.Root, "UI-Test-Artefakte");
        }

        _automation?.Dispose();
        _app?.Close();
        _app?.Dispose();
    }

    [Test]
    public void Aircraft_track_line_must_follow_expected_route_within_nautical_mile_tolerance()
    {
        var routePath = Path.Combine(_config!.ScenarioRoot, "TrackRoutes", "TRACK_ROUTE_001.json");
        var route = JsonSerializer.Deserialize<TrackRouteDefinition>(File.ReadAllText(routePath))
            ?? throw new InvalidOperationException($"TrackRouteDefinition konnte nicht geladen werden: {routePath}");

        Assert.That(route.UiBackend, Is.EqualTo("UIA3"));

        var mainWindow = _app!.GetMainWindow(_automation!, TimeSpan.FromSeconds(_config.MainWindowTimeoutSeconds));
        Assert.That(mainWindow, Is.Not.Null, "Hauptfenster wurde nicht gefunden.");

        var cf = new ConditionFactory(new UIA3PropertyLibrary());
        var screen = new AircraftMapScreen(mainWindow, cf);

        screen.LoadScenario(route.ScenarioId);
        screen.SetSimulationTime(route.SimulationTimeUtc);
        screen.RenderFrame();

        var mapCanvas = screen.MapCanvas;
        var bounds = mapCanvas.BoundingRectangle;
        var screenshot = Capture.Rectangle(bounds);

        var roiPath = Path.Combine(_artifacts!.Screenshots, "track-roi.png");
        screenshot.ToFile(roiPath);

        var result = TrackLineDeviationAnalyzer.Analyze(
            roiImagePath: roiPath,
            route: route,
            artifactDirectory: _artifacts.OpenCv);

        TestContext.AddTestAttachment(result.SourceImagePath, "ROI-Screenshot");
        TestContext.AddTestAttachment(result.ActualMaskPath, "erkannte Track-Maske");
        TestContext.AddTestAttachment(result.ExpectedMaskPath, "Sollroute-Maske");
        TestContext.AddTestAttachment(result.ToleranceMaskPath, "Toleranzmaske");
        TestContext.AddTestAttachment(result.OverlayPath, "Abweichungs-Overlay");
        TestContext.AddTestAttachment(result.AnalysisJsonPath, "Track-Analyse JSON");

        Assert.Multiple(() =>
        {
            Assert.That(result.TrackDetected, Is.True, "Die Flugzeugspur muss sichtbar und detektierbar sein.");
            Assert.That(result.ActualTrackPixels, Is.GreaterThanOrEqualTo(route.MinTrackPixels), "Zu wenige Track-Pixel erkannt.");
            Assert.That(result.CoverageRatio, Is.GreaterThanOrEqualTo(route.CoverageThreshold), "Die Sollroute ist nicht ausreichend durch den Track abgedeckt.");
            Assert.That(result.BrokenSegments, Is.LessThanOrEqualTo(route.AllowedBrokenSegments), "Die Track-Linie hat nicht zulässige Unterbrechungen.");
            Assert.That(result.MaxDeviationNm, Is.LessThanOrEqualTo(route.AllowedDeviationNm), "Die maximale Track-Abweichung überschreitet die fachliche NM-Toleranz.");
        });
    }
}
```

### 15.4 WinForms/UIA2-Variante

Im WinForms-Projekt ist derselbe Analyzer zu verwenden. Der Unterschied liegt nur im Automation-Backend und in der Property Library.

`tests/Product.UiTests.Uia2/VisualTrack/AircraftTrackLineWinFormsTests.cs`:

```csharp
using System.Text.Json;
using FlaUI.Core;
using FlaUI.Core.Capturing;
using FlaUI.Core.Conditions;
using FlaUI.UIA2;
using NUnit.Framework;
using Product.UiTests.Shared.Configuration;
using Product.UiTests.Shared.Diagnostics;
using Product.UiTests.Shared.Infrastructure;
using Product.UiTests.Shared.Screens;
using Product.UiTests.Shared.Visual;

namespace Product.UiTests.Uia2.VisualTrack;

[TestFixture]
[NonParallelizable]
[Category("VisualTrack")]
[Category("UIA2")]
public sealed class AircraftTrackLineWinFormsTests
{
    private Application? _app;
    private UIA2Automation? _automation;
    private TestConfiguration? _config;
    private ArtifactPaths? _artifacts;

    [SetUp]
    public void SetUp()
    {
        TestEnvironmentGuard.AssertDeterministicDesktop();

        _config = ConfigurationLoader.Load();
        _artifacts = new ArtifactPaths(_config.ArtifactRoot, TestContext.CurrentContext.Test.Name);

        _app = Application.Launch(_config.AppUnderTestPath);
        _automation = new UIA2Automation();
    }

    [TearDown]
    public void TearDown()
    {
        _automation?.Dispose();
        _app?.Close();
        _app?.Dispose();
    }

    [Test]
    public void WinForms_aircraft_track_line_must_follow_expected_route_within_nautical_mile_tolerance()
    {
        var routePath = Path.Combine(_config!.ScenarioRoot, "TrackRoutes", "TRACK_ROUTE_001_WINFORMS.json");
        var route = JsonSerializer.Deserialize<TrackRouteDefinition>(File.ReadAllText(routePath))
            ?? throw new InvalidOperationException($"TrackRouteDefinition konnte nicht geladen werden: {routePath}");

        Assert.That(route.UiBackend, Is.EqualTo("UIA2"));

        var mainWindow = _app!.GetMainWindow(_automation!, TimeSpan.FromSeconds(_config.MainWindowTimeoutSeconds));
        var cf = new ConditionFactory(new UIA2PropertyLibrary());
        var screen = new AircraftMapScreen(mainWindow, cf);

        screen.LoadScenario(route.ScenarioId);
        screen.SetSimulationTime(route.SimulationTimeUtc);
        screen.RenderFrame();

        var bounds = screen.MapCanvas.BoundingRectangle;
        var screenshot = Capture.Rectangle(bounds);
        var roiPath = Path.Combine(_artifacts!.Screenshots, "track-roi.png");
        screenshot.ToFile(roiPath);

        var result = TrackLineDeviationAnalyzer.Analyze(roiPath, route, _artifacts.OpenCv);

        Assert.Multiple(() =>
        {
            Assert.That(result.TrackDetected, Is.True);
            Assert.That(result.CoverageRatio, Is.GreaterThanOrEqualTo(route.CoverageThreshold));
            Assert.That(result.MaxDeviationNm, Is.LessThanOrEqualTo(route.AllowedDeviationNm));
            Assert.That(result.BrokenSegments, Is.LessThanOrEqualTo(route.AllowedBrokenSegments));
        });
    }
}
```

---

## 16. Synthetische Analyzer-Tests

Vor der Migration echter Eggplant-Visual-Tests wird der OpenCV-Analyzer mit synthetischen Bildern validiert.

Ziel:

```text
Bild mit exakt erwarteter Linie         → Test grün
Bild mit 1 px Abweichung innerhalb Limit → Test grün
Bild mit 3 px Abweichung über Limit      → Test rot
Bild ohne Linie                          → Test rot
Bild mit unterbrochener Linie             → Test rot
```

Beispiel:

```csharp
using NUnit.Framework;
using OpenCvSharp;
using Product.UiTests.Shared.Visual;

namespace Product.UiTests.Uia3.VisualTrack;

[TestFixture]
[Category("VisualAnalyzerUnit")]
public sealed class TrackLineDeviationAnalyzerSyntheticTests
{
    [Test]
    public void Analyzer_must_fail_when_line_is_offset_by_more_than_allowed_pixels()
    {
        var temp = Path.Combine(TestContext.CurrentContext.WorkDirectory, Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(temp);

        var imagePath = Path.Combine(temp, "offset.png");
        using var image = Mat.Zeros(600, 800, MatType.CV_8UC3);

        // HSV-Zielfarbe ungefähr gelb, hier direkt BGR für Zeichnung.
        Cv2.Line(image, new Point(120, 434), new Point(520, 224), new Scalar(0, 220, 220), 2, LineTypes.AntiAlias);
        Cv2.ImWrite(imagePath, image);

        var route = new TrackRouteDefinition
        {
            ScenarioId = "SYNTHETIC_OFFSET",
            UiBackend = "UIA3",
            MapAutomationId = "AircraftMapCanvas",
            SimulationTimeUtc = DateTime.UtcNow,
            DisplayProfile = "FHD_100DPI",
            ZoomLevel = "Z08",
            NauticalMilesPerPixel = 2.5,
            AllowedDeviationNm = 5.0,
            CoverageThreshold = 0.90,
            AllowedBrokenSegments = 0,
            MinTrackPixels = 20,
            TrackColorHsvLower = [20, 80, 80],
            TrackColorHsvUpper = [45, 255, 255],
            ExpectedRoute =
            [
                new RoutePoint(120, 430),
                new RoutePoint(520, 220)
            ]
        };

        var result = TrackLineDeviationAnalyzer.Analyze(imagePath, route, temp);

        Assert.That(result.TrackDetected, Is.True);
        Assert.That(result.MaxDeviationNm, Is.GreaterThan(route.AllowedDeviationNm));
    }
}
```

Diese synthetischen Tests sind Pflicht, weil sie beweisen, dass der Ersatzstack die kritische Eggplant-Fähigkeit der pixelgenauen Linienabweichung technisch abbildet.

---

## 17. Pipeline-YAML

### 17.1 Vollständige Pipeline

`azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pr:
  branches:
    include:
      - main
      - develop

variables:
  buildConfiguration: 'Release'
  solution: 'Product.sln'
  artifactRoot: '$(Build.ArtifactStagingDirectory)\ui-test-artifacts'
  testResultsRoot: '$(Build.ArtifactStagingDirectory)\test-results'
  autPublishDir: '$(Build.ArtifactStagingDirectory)\aut'
  ContinuousIntegrationBuild: 'true'
  AZP_AGENT_CLEANUP_PSMODULES_IN_POWERSHELL: 'true'

stages:
  - stage: Build
    displayName: 'Build and package AUT'
    jobs:
      - job: Build_AUT
        displayName: 'Build AUT and tests'
        pool:
          name: WIN-BUILD
        steps:
          - checkout: self
            clean: true

          - powershell: |
              dotnet --info
              dotnet nuget locals all --list
            displayName: 'Show .NET and NuGet info'

          - powershell: |
              dotnet restore $(solution) --configfile NuGet.config --locked-mode
            displayName: 'Restore locked NuGet packages'

          - powershell: |
              dotnet build $(solution) --configuration $(buildConfiguration) --no-restore
            displayName: 'Build solution'

          - powershell: |
              dotnet publish src/Product/Product.csproj `
                --configuration $(buildConfiguration) `
                --no-build `
                --output "$(autPublishDir)"
            displayName: 'Publish AUT'

          - task: PublishBuildArtifacts@1
            displayName: 'Publish AUT artifact'
            inputs:
              PathtoPublish: '$(autPublishDir)'
              ArtifactName: 'aut'
              publishLocation: 'Container'

  - stage: UIA3_WPF
    displayName: 'Run WPF UIA3 UI tests'
    dependsOn: Build
    jobs:
      - job: Run_Uia3
        displayName: 'NUnit + FlaUI.UIA3'
        timeoutInMinutes: 120
        pool:
          name: WIN-UI-DESKTOP
          demands:
            - UiBackend -equals UIA3
            - UiProfile -equals WPF
            - DisplayProfile -equals FHD_100DPI
        steps:
          - checkout: self
            clean: true

          - task: DownloadBuildArtifacts@0
            displayName: 'Download AUT artifact'
            inputs:
              buildType: 'current'
              downloadType: 'single'
              artifactName: 'aut'
              downloadPath: '$(Pipeline.Workspace)'

          - powershell: |
              New-Item -ItemType Directory -Force -Path "$(artifactRoot)" | Out-Null
              New-Item -ItemType Directory -Force -Path "$(testResultsRoot)" | Out-Null
              Get-Process Product -ErrorAction SilentlyContinue | Stop-Process -Force
            displayName: 'Prepare UIA3 runtime directories'
            condition: always()

          - powershell: |
              dotnet restore tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj --configfile NuGet.config --locked-mode
              dotnet build tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj --configuration $(buildConfiguration) --no-restore
            displayName: 'Build UIA3 tests'

          - powershell: |
              dotnet test tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj `
                --configuration $(buildConfiguration) `
                --no-build `
                --logger "trx;LogFileName=uia3-wpf.trx" `
                --results-directory "$(testResultsRoot)" `
                -- NUnit.NumberOfTestWorkers=1
            displayName: 'Run UIA3 tests'
            env:
              UI_TEST_AppUnderTestPath: '$(Pipeline.Workspace)\aut\Product.exe'
              UI_TEST_ArtifactRoot: '$(artifactRoot)\uia3'
              UI_TEST_ScenarioRoot: '$(Build.SourcesDirectory)\tests\Product.UiTests.TestAssets'
              UI_TEST_CalibrationRoot: '$(Build.SourcesDirectory)\tests\Product.UiTests.TestAssets\Calibration'

          - task: PublishTestResults@2
            displayName: 'Publish UIA3 TRX'
            condition: always()
            inputs:
              testResultsFormat: 'VSTest'
              testResultsFiles: '$(testResultsRoot)\*.trx'
              failTaskOnFailedTests: true

          - task: PublishBuildArtifacts@1
            displayName: 'Publish UIA3 artifacts'
            condition: always()
            inputs:
              PathtoPublish: '$(artifactRoot)'
              ArtifactName: 'ui-artifacts-uia3'
              publishLocation: 'Container'

  - stage: UIA2_WinForms
    displayName: 'Run WinForms UIA2 UI tests'
    dependsOn: Build
    jobs:
      - job: Run_Uia2
        displayName: 'NUnit + FlaUI.UIA2'
        timeoutInMinutes: 120
        pool:
          name: WIN-UI-DESKTOP
          demands:
            - UiBackend -equals UIA2
            - UiProfile -equals WinForms
            - DisplayProfile -equals FHD_100DPI
        steps:
          - checkout: self
            clean: true

          - task: DownloadBuildArtifacts@0
            displayName: 'Download AUT artifact'
            inputs:
              buildType: 'current'
              downloadType: 'single'
              artifactName: 'aut'
              downloadPath: '$(Pipeline.Workspace)'

          - powershell: |
              New-Item -ItemType Directory -Force -Path "$(artifactRoot)" | Out-Null
              New-Item -ItemType Directory -Force -Path "$(testResultsRoot)" | Out-Null
              Get-Process Product -ErrorAction SilentlyContinue | Stop-Process -Force
            displayName: 'Prepare UIA2 runtime directories'
            condition: always()

          - powershell: |
              dotnet restore tests/Product.UiTests.Uia2/Product.UiTests.Uia2.csproj --configfile NuGet.config --locked-mode
              dotnet build tests/Product.UiTests.Uia2/Product.UiTests.Uia2.csproj --configuration $(buildConfiguration) --no-restore
            displayName: 'Build UIA2 tests'

          - powershell: |
              dotnet test tests/Product.UiTests.Uia2/Product.UiTests.Uia2.csproj `
                --configuration $(buildConfiguration) `
                --no-build `
                --logger "trx;LogFileName=uia2-winforms.trx" `
                --results-directory "$(testResultsRoot)" `
                -- NUnit.NumberOfTestWorkers=1
            displayName: 'Run UIA2 tests'
            env:
              UI_TEST_AppUnderTestPath: '$(Pipeline.Workspace)\aut\Product.exe'
              UI_TEST_ArtifactRoot: '$(artifactRoot)\uia2'
              UI_TEST_ScenarioRoot: '$(Build.SourcesDirectory)\tests\Product.UiTests.TestAssets'
              UI_TEST_CalibrationRoot: '$(Build.SourcesDirectory)\tests\Product.UiTests.TestAssets\Calibration'

          - task: PublishTestResults@2
            displayName: 'Publish UIA2 TRX'
            condition: always()
            inputs:
              testResultsFormat: 'VSTest'
              testResultsFiles: '$(testResultsRoot)\*.trx'
              failTaskOnFailedTests: true

          - task: PublishBuildArtifacts@1
            displayName: 'Publish UIA2 artifacts'
            condition: always()
            inputs:
              PathtoPublish: '$(artifactRoot)'
              ArtifactName: 'ui-artifacts-uia2'
              publishLocation: 'Container'

  - stage: VisualTrack
    displayName: 'Run deterministic visual track-line tests'
    dependsOn: Build
    jobs:
      - job: Run_VisualTrack
        displayName: 'OpenCV Track-Line Validation'
        timeoutInMinutes: 120
        pool:
          name: WIN-UI-DESKTOP
          demands:
            - VisualTrack -equals true
            - DisplayProfile -equals FHD_100DPI
        steps:
          - checkout: self
            clean: true

          - task: DownloadBuildArtifacts@0
            displayName: 'Download AUT artifact'
            inputs:
              buildType: 'current'
              downloadType: 'single'
              artifactName: 'aut'
              downloadPath: '$(Pipeline.Workspace)'

          - powershell: |
              New-Item -ItemType Directory -Force -Path "$(artifactRoot)" | Out-Null
              New-Item -ItemType Directory -Force -Path "$(testResultsRoot)" | Out-Null
              Get-Process Product -ErrorAction SilentlyContinue | Stop-Process -Force
            displayName: 'Prepare VisualTrack runtime directories'
            condition: always()

          - powershell: |
              dotnet restore tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj --configfile NuGet.config --locked-mode
              dotnet build tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj --configuration $(buildConfiguration) --no-restore
            displayName: 'Build VisualTrack tests'

          - powershell: |
              dotnet test tests/Product.UiTests.Uia3/Product.UiTests.Uia3.csproj `
                --configuration $(buildConfiguration) `
                --no-build `
                --filter "TestCategory=VisualTrack" `
                --logger "trx;LogFileName=visual-track.trx" `
                --results-directory "$(testResultsRoot)" `
                -- NUnit.NumberOfTestWorkers=1
            displayName: 'Run VisualTrack tests'
            env:
              UI_TEST_AppUnderTestPath: '$(Pipeline.Workspace)\aut\Product.exe'
              UI_TEST_ArtifactRoot: '$(artifactRoot)\visual-track'
              UI_TEST_ScenarioRoot: '$(Build.SourcesDirectory)\tests\Product.UiTests.TestAssets'
              UI_TEST_CalibrationRoot: '$(Build.SourcesDirectory)\tests\Product.UiTests.TestAssets\Calibration'

          - task: PublishTestResults@2
            displayName: 'Publish VisualTrack TRX'
            condition: always()
            inputs:
              testResultsFormat: 'VSTest'
              testResultsFiles: '$(testResultsRoot)\*.trx'
              failTaskOnFailedTests: true

          - task: PublishBuildArtifacts@1
            displayName: 'Publish VisualTrack artifacts'
            condition: always()
            inputs:
              PathtoPublish: '$(artifactRoot)'
              ArtifactName: 'ui-artifacts-visual-track'
              publishLocation: 'Container'
```

---

## 18. Migrationsvorgehen Eggplant → Zielstack

### 18.1 Inventarisierung

Für jeden Eggplant-Test wird eine Zeile erfasst:

| Feld | Inhalt |
|---|---|
| `EggplantSuite` | bisherige Suite |
| `EggplantTestName` | bisheriger Testname |
| `BusinessFlow` | fachlicher Ablauf |
| `SurfaceTechnology` | WPF, WinForms, gemischt, Canvas/Map |
| `PrimaryReplacement` | UIA3, UIA2, VisualTrack |
| `AutomationIdsAvailable` | ja/nein |
| `VisualValidationRequired` | ja/nein |
| `TrackLineRequired` | ja/nein |
| `TestDataRequired` | ja/nein |
| `MigrationWave` | 0, 1, 2, 3 |
| `AcceptanceCriteria` | konkrete Zielassertions |

### 18.2 Klassifizierung

```text
Klasse A: Standard-WPF-Workflow        → UIA3
Klasse B: Standard-WinForms-Workflow   → UIA2
Klasse C: gemischter Workflow          → nach Startscreen, ggf. getrennte Tests
Klasse D: Canvas-/Map-/Track-Line      → FlaUI + OpenCV VisualTrack
Klasse E: nur technische Smoke-Prüfung → UIA3 oder UIA2 nach Oberfläche
```

### 18.3 Migrationswellen

```text
Welle 0: Testinfrastruktur und Pipeline
Welle 1: Smoke Tests und Login/Startpfade
Welle 2: fachliche Standarddialoge WPF/UIA3
Welle 3: fachliche Standarddialoge WinForms/UIA2
Welle 4: visuelle Track-Line-Prüfungen
Welle 5: restliche Regressionen und Stabilisierung
```

### 18.4 Priorität

Die Track-Line-Prüfung wird in Welle 4 nicht nach hinten verschoben, wenn sie fachlich entscheidend ist. Sie wird als Ablösungs-Gate behandelt.

Gate-Kriterium:

```text
Mindestens ein echter bisheriger Eggplant-Track-Line-Test muss mit OpenCvSharp reproduzierbar fehlschlagen, wenn die Linie um die fachlich relevante Pixelabweichung versetzt ist.
```

---

## 19. Codex-Arbeitsanweisungen für die Migration

Diese Datei kann als Steuerdatei für Codex verwendet werden.

### 19.1 Harte Codex-Regeln

```text
Verwende NUnit, nicht xUnit.
Verwende NUnit Assert.That, nicht FluentAssertions.
Verwende FlaUI.UIA3 für WPF.
Verwende FlaUI.UIA2 für WinForms.
Verwende OpenCvSharp4.Windows für Bildanalyse.
Verwende kein ImageSharp.
Verwende keine Koordinatenklicks für Standardcontrols.
Erzeuge bei jedem fehlgeschlagenen UI-Test Screenshots, Logs, UIA-Dumps und metadata.json.
Erzeuge bei jedem VisualTrack-Test OpenCV-Masken, Overlay und track-analysis.json.
Neue Testprojekte targeten net10.0-windows.
Alle Pakete werden über Directory.Packages.props versioniert.
Alle Restores laufen locked.
Pipeline-Artefakte verwenden PublishBuildArtifacts@1.
```

### 19.2 Codex-Task 1: Repository-Grundstruktur

Prompt:

```text
Erzeuge die Repository-Struktur aus Abschnitt 9. Verwende .NET SDK 10, Central Package Management, NUnit, FlaUI.UIA3, FlaUI.UIA2, OpenCvSharp4.Windows und Verify.NUnit. Erzeuge keine xUnit-, MSTest- oder ImageSharp-Referenzen. Erzeuge Directory.Build.props, Directory.Packages.props, NuGet.config und die drei Testprojekte Product.UiTests.Shared, Product.UiTests.Uia3 und Product.UiTests.Uia2.
```

Akzeptanz:

```text
dotnet restore --locked-mode funktioniert.
dotnet build funktioniert.
Keine xUnit-/MSTest-/ImageSharp-Pakete vorhanden.
```

### 19.3 Codex-Task 2: FlaUI-Infrastruktur

Prompt:

```text
Implementiere AppLauncher, WindowFinder, Waiter, ScreenBase, ArtifactPaths, ScreenshotService, UiaTreeDumper, FailureArtifactCollector und TestEnvironmentGuard gemäß Migrationsleitfaden. Verwende AutomationId-basierte Selektoren. Keine Koordinatensteuerung.
```

Akzeptanz:

```text
Ein UIA3-Smoke-Test startet die Anwendung und findet das Hauptfenster.
Ein UIA2-Smoke-Test startet die Anwendung und findet einen WinForms-Screen.
Fehlschlag erzeugt Artefaktordner.
```

### 19.4 Codex-Task 3: VisualTrack-Analyzer

Prompt:

```text
Implementiere TrackRouteDefinition, TrackLineAnalysisResult und TrackLineDeviationAnalyzer exakt nach Abschnitt 15. Ergänze synthetische NUnit-Tests, die Pass, Offset-Fail, Missing-Line-Fail und Broken-Line-Fail prüfen. Verwende OpenCvSharp4.Windows. Verwende keine ImageSharp-Abhängigkeit.
```

Akzeptanz:

```text
Synthetischer Pass-Test ist grün.
Synthetischer 3-px-Offset-Test ist rot bzw. assertet eine Überschreitung.
Missing-Line-Test ist rot.
Broken-Line-Test ist rot.
Alle Tests schreiben OpenCV-Artefakte.
```

### 19.5 Codex-Task 4: Erster echter Track-Line-Test

Prompt:

```text
Migriere den vorhandenen Eggplant-Test für Flugzeugspur/Track-Line nach Product.UiTests.Uia3.VisualTrack. Verwende FlaUI nur zum Starten, Navigieren, Szenario-Laden, Rendern und ROI-Capture. Verwende TrackLineDeviationAnalyzer für die fachliche Linienabweichung. Das Ergebnis muss MaxDeviationPx und MaxDeviationNm ausgeben und bei Überschreitung der NM-Toleranz fehlschlagen.
```

Akzeptanz:

```text
Test läuft auf AG-UI-VIS-01.
Test erzeugt track-analysis.json.
Test erzeugt track-deviation-overlay.png.
Bewusst versetzte Linie führt zu rotem Test.
Korrekte Linie führt zu grünem Test.
```

### 19.6 Codex-Task 5: Azure Pipeline

Prompt:

```text
Implementiere azure-pipelines.yml gemäß Abschnitt 17. Verwende Build Stage, UIA3_WPF Stage, UIA2_WinForms Stage und VisualTrack Stage. Nutze DownloadBuildArtifacts@0, PublishBuildArtifacts@1 und PublishTestResults@2. Verwende keine PublishPipelineArtifact-Tasks.
```

Akzeptanz:

```text
Pipeline läuft auf Azure DevOps Server.
UIA3-Job landet auf UIA3-Agent.
UIA2-Job landet auf UIA2-Agent.
VisualTrack-Job landet auf VisualTrack-Agent.
TRX-Dateien werden veröffentlicht.
Artefakte werden veröffentlicht.
```

---

## 20. Definition of Done für die Eggplant-Ablösung

### 20.1 Technische DoD

```text
Azure DevOps Server läuft online und airgap mit gleichem Patchstand.
Agent-Pools WIN-BUILD und WIN-UI-DESKTOP existieren.
Mindestens je ein UIA3-, UIA2- und VisualTrack-Agent ist registriert.
Agenten laufen interaktiv mit Auto-Logon.
Alle UI-Test-VMs haben 1920×1080 und 100 % DPI.
NuGet-Feed enthält alle Pakete.
Restore läuft in Airgap ohne externen Feed.
Pipeline läuft komplett in Airgap.
TRX-Ergebnisse erscheinen in Azure DevOps Server.
Build-Artefakte enthalten Screenshots, Logs, UIA-Dumps und OpenCV-Overlays.
```

### 20.2 Test-DoD

```text
Alle migrierten Smoke Tests laufen stabil.
WPF-Tests laufen im UIA3-Projekt.
WinForms-Tests laufen im UIA2-Projekt.
Track-Line-Tests laufen mit OpenCV-Analyzer.
Track-Line-Test erkennt fachlich relevante Pixelabweichung.
Track-Line-Test berechnet Abweichung in nautischen Meilen.
Fehlschläge sind anhand von Overlay und JSON nachvollziehbar.
```

### 20.3 Stabilitäts-DoD

```text
50 aufeinanderfolgende Pipeline-Läufe im Online-Migrationslabor.
50 aufeinanderfolgende Pipeline-Läufe in Airgap-Staging.
Flaky-Rate für Standard-UI-Tests < 2 %.
Flaky-Rate für VisualTrack-Tests < 3 % nach Kalibrierung.
Kein Test verwendet normale Koordinatenklicks.
Kein Test hängt von Fullscreen-Pixelvergleich ab.
```

---

## 21. Häufige Fehler und festgelegte Gegenmaßnahmen

| Fehler | Gegenmaßnahme |
|---|---|
| UI-Test läuft auf Service-Agent | Agent neu mit `--runAsAutoLogon` konfigurieren |
| RDP trennt Session und Tests schlagen fehl | `tscon` verwenden |
| VisualTrack-Test flackert | AG-UI-VIS-01 reservieren, keine parallelen UI-Jobs, Renderingzeit deterministisch setzen |
| Linie wird nicht erkannt | HSV-Grenzen kalibrieren, ROI prüfen, Maskenartefakte vergleichen |
| Linie wird erkannt, aber Abweichung falsch | `nauticalMilesPerPixel`, Zoom und ROI-Ursprung prüfen |
| WPF-Control nicht auffindbar | AutomationId setzen oder AutomationPeer implementieren |
| WinForms-Control nicht auffindbar | Name/AccessibleName/AccessibleRole setzen, UIA2 verwenden |
| Pipeline publiziert keine Artefakte | `PublishBuildArtifacts@1` verwenden |
| Restore greift ins Internet | `NuGet.config` mit `<clear />`, internen Feed prüfen, `--locked-mode` erzwingen |
| Package Drift | `Directory.Packages.props` und `packages.lock.json` prüfen |

---

## 22. Quellenstand für technische Festlegungen

Diese Quellen wurden für die Festlegungen geprüft:

| Thema | Quelle |
|---|---|
| Azure DevOps Server Release/Patches | https://learn.microsoft.com/en-us/azure/devops/server/release-notes/azuredevopsserver |
| Azure DevOps Server Anforderungen | https://learn.microsoft.com/en-us/azure/devops/server/requirements |
| Self-hosted Windows Agents | https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/windows-agent |
| UI-Testing mit interaktivem Auto-Logon-Agent | https://learn.microsoft.com/en-us/azure/devops/pipelines/test/ui-testing-considerations |
| Agent Capabilities/Demands | https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agents |
| PublishBuildArtifacts@1 | https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-build-artifacts-v1 |
| PublishPipelineArtifact@1 nicht on-prem | https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-pipeline-artifact-v1 |
| Azure DevOps Extensions | https://learn.microsoft.com/en-us/azure/devops/marketplace/install-extension |
| Azure Artifacts Upstreams | https://learn.microsoft.com/en-us/azure/devops/artifacts/concepts/upstream-sources |
| dotnet restore | https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-restore |
| dotnet nuget push | https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-nuget-push |
| .NET Support Policy | https://dotnet.microsoft.com/en-us/platform/support/policy |
| Windows 11 Enterprise Lifecycle | https://learn.microsoft.com/en-us/lifecycle/products/windows-11-enterprise-and-education |
| FlaUI GitHub | https://github.com/FlaUI/FlaUI |
| FlaUI.Core NuGet | https://www.nuget.org/packages/FlaUI.Core |
| FlaUI.UIA3 NuGet | https://www.nuget.org/packages/FlaUI.UIA3 |
| FlaUI.UIA2 NuGet | https://www.nuget.org/packages/FlaUI.UIA2 |
| NUnit Downloads | https://nunit.org/download/ |
| NUnit NonParallelizable | https://docs.nunit.org/articles/nunit/writing-tests/attributes/nonparallelizable.html |
| NUnit LevelOfParallelism | https://docs.nunit.org/articles/nunit/writing-tests/attributes/levelofparallelism.html |
| OpenCvSharp4.Windows NuGet | https://www.nuget.org/packages/OpenCvSharp4.Windows |
| OpenCvSharp GitHub | https://github.com/shimat/opencvsharp |
| OpenCV inRange | https://docs.opencv.org/4.x/da/d97/tutorial_threshold_inRange.html |
| OpenCV Distance Transform | https://docs.opencv.org/4.x/d2/dbd/tutorial_distance_transform.html |
| OpenCV Morphological Transformations | https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html |
| OpenCV Hough Lines | https://docs.opencv.org/4.x/d9/db0/tutorial_hough_lines.html |
| WPF AutomationId | https://learn.microsoft.com/en-us/dotnet/api/system.windows.automation.automationproperties.automationid |
| UI Automation Standard Controls | https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-support-for-standard-controls |
| WPF Custom Control Automation | https://learn.microsoft.com/en-us/dotnet/desktop/wpf/controls/ui-automation-of-a-wpf-custom-control |
| AutomationId Usage | https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/use-the-automationid-property |
| Verify.NUnit NuGet | https://www.nuget.org/packages/Verify.NUnit |
| Serilog NuGet | https://www.nuget.org/packages/Serilog |

---

## 23. Selbstprüfung dieser Migrationsfassung

Prüfpunkte:

```text
NUnit ist als einziges Testframework festgelegt.
FlaUI.UIA3 ist als WPF-Strang festgelegt.
FlaUI.UIA2 ist als WinForms-Strang festgelegt.
OpenCvSharp ist Pflicht für Track-Line-/Canvas-Prüfungen.
ImageSharp ist nicht Bestandteil des Initialstacks.
Azure DevOps Server nutzt PublishBuildArtifacts@1.
Pipeline verwendet keine PublishPipelineArtifact-Tasks.
Self-hosted UI-Agenten laufen interaktiv mit Auto-Logon.
Online-Migrationslabor und Airgap-Zielumgebung werden als Spiegel betrieben.
Track-Line-Tests messen Pixelabweichung und rechnen in nautische Meilen um.
VisualTrack erzeugt Overlay, Masken und JSON-Analyse.
Codex-Regeln sind explizit und komponentenscharf formuliert.
```
