param(
    [string]$Hostname = "workbench.top.secret",
    [string]$Address = "127.0.0.1",
    [switch]$NoElevate
)

$ErrorActionPreference = "Stop"

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-IsAdministrator)) {
    if ($NoElevate) {
        throw "Administrator rights are required to update the Windows hosts file."
    }

    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "`"$PSCommandPath`"",
        "-Hostname",
        $Hostname,
        "-Address",
        $Address,
        "-NoElevate"
    )
    Start-Process -FilePath powershell.exe -Verb RunAs -ArgumentList $arguments -Wait
    exit $LASTEXITCODE
}

$hostsPath = Join-Path $env:SystemRoot "System32\drivers\etc\hosts"
$hostsItem = Get-Item -LiteralPath $hostsPath
$wasReadOnly = $hostsItem.IsReadOnly
if ($wasReadOnly) {
    $hostsItem.IsReadOnly = $false
}

$content = Get-Content -LiteralPath $hostsPath -Raw
$escapedHost = [regex]::Escape($Hostname)
$escapedAddress = [regex]::Escape($Address)

if ($content -notmatch "(?im)^\s*$escapedAddress\s+.*\b$escapedHost\b") {
    $lines = [System.Collections.Generic.List[string]]::new()
    $lines.AddRange([string[]]($content -split "\r?\n", -1))
    $inserted = $false

    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match "(?i)^\s*$escapedAddress\s+openwebui\.top\.secret\s*$") {
            $lines.Insert($index + 1, "$Address $Hostname")
            $inserted = $true
            break
        }
    }

    if (-not $inserted) {
        if ($lines.Count -gt 0 -and $lines[$lines.Count - 1] -ne "") {
            $lines.Add("")
        }
        $lines.Add("# Codex local Workbench")
        $lines.Add("$Address $Hostname")
    }

    try {
        [IO.File]::WriteAllText($hostsPath, (($lines -join "`r`n").TrimEnd() + "`r`n"), [Text.Encoding]::ASCII)
    } finally {
        if ($wasReadOnly) {
            (Get-Item -LiteralPath $hostsPath).IsReadOnly = $true
        }
    }
    Write-Host "Added $Address $Hostname to $hostsPath"
} else {
    if ($wasReadOnly) {
        (Get-Item -LiteralPath $hostsPath).IsReadOnly = $true
    }
    Write-Host "$Hostname is already present in $hostsPath"
}

ipconfig /flushdns | Out-Null

$resolved = Resolve-DnsName -Name $Hostname -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -eq $Address } |
    Select-Object -First 1

if (-not $resolved) {
    throw "$Hostname did not resolve to $Address after the hosts update."
}

Write-Host "$Hostname resolves to $Address"
