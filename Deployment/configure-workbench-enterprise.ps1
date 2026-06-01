param(
    [ValidateSet("", "bundled", "existing")]
    [string]$OpenWebUIMode = "",
    [string]$OpenWebUIBaseUrl = "",
    [string]$OpenWebUIPublicUrl = "",
    [string]$WorkspaceHostPath = "",
    [string]$RootCaPath = "",
    [string]$WorkbenchImage = "ghcr.io/adrianweidig/openwebui-workbench/workbench-dashboard:latest",
    [string]$OpenWebUIImage = "ghcr.io/open-webui/open-webui:main",
    [string]$WorkbenchPublishedBind = "127.0.0.1:8088",
    [string]$OpenWebUIPublishedBind = "127.0.0.1:3000",
    [string]$DockerNetworkName = "openwebui-workbench_workbench",
    [string]$OutputDir = "Deployment/generated",
    [switch]$UseExternalDockerNetwork,
    [switch]$AllowUnverifiedRootCaPath,
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"

function Read-WorkbenchValue {
    param(
        [string]$Prompt,
        [string]$Default = "",
        [switch]$Required
    )
    if ($NonInteractive) {
        if ($Required -and [string]::IsNullOrWhiteSpace($Default)) {
            throw "Missing required non-interactive value: $Prompt"
        }
        return $Default.Trim()
    }
    $suffix = if ([string]::IsNullOrWhiteSpace($Default)) { "" } else { " [$Default]" }
    do {
        $value = Read-Host "$Prompt$suffix"
        if ([string]::IsNullOrWhiteSpace($value)) {
            $value = $Default
        }
    } while ($Required -and [string]::IsNullOrWhiteSpace($value))
    return $value.Trim()
}

function ConvertFrom-WorkbenchSecureString {
    param([securestring]$SecureValue)
    if ($null -eq $SecureValue -or $SecureValue.Length -eq 0) {
        return ""
    }
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

function Read-WorkbenchSecret {
    param([string]$Prompt)
    if ($NonInteractive) {
        return ""
    }
    return ConvertFrom-WorkbenchSecureString (Read-Host $Prompt -AsSecureString)
}

function Test-RootCaFile {
    param(
        [string]$PathValue,
        [switch]$AllowUnverified
    )
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return ""
    }
    try {
        $resolved = Resolve-Path -LiteralPath $PathValue -ErrorAction Stop
    }
    catch {
        if ($AllowUnverified) {
            return $PathValue.Trim()
        }
        throw "Root-CA-Datei ist lokal nicht lesbar: $PathValue. Wenn dies bewusst ein Docker-/Portainer-Hostpfad ist, prüfe die PEM-Datei administrativ und starte den Assistenten mit -AllowUnverifiedRootCaPath."
    }
    $content = Get-Content -Raw -LiteralPath $resolved.Path
    if ($content -match "BEGIN .*PRIVATE KEY") {
        throw "Root-CA-Datei darf keinen Private Key enthalten: $($resolved.Path)"
    }
    if ($content -notmatch "BEGIN CERTIFICATE") {
        throw "Root-CA-Datei sieht nicht wie ein PEM-Zertifikatsbundle aus: $($resolved.Path)"
    }
    return $resolved.Path
}

function Write-TextFile {
    param(
        [string]$PathValue,
        [string[]]$Lines
    )
    $parent = Split-Path -Parent $PathValue
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Set-Content -LiteralPath $PathValue -Encoding UTF8 -Value ($Lines -join [Environment]::NewLine)
}

if ([string]::IsNullOrWhiteSpace($OpenWebUIMode)) {
    if ($NonInteractive) {
        $OpenWebUIMode = "bundled"
    }
    else {
        $mode = Read-WorkbenchValue -Prompt "OpenWebUI mit starten oder vorhandene Instanz verwenden? (bundled/existing)" -Default "bundled" -Required
        if ($mode -notin @("bundled", "existing")) {
            throw "Erlaubte Werte: bundled oder existing."
        }
        $OpenWebUIMode = $mode
    }
}

if ([string]::IsNullOrWhiteSpace($WorkspaceHostPath)) {
    $WorkspaceHostPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}
$WorkspaceHostPath = Read-WorkbenchValue -Prompt "Host-Pfad zum openwebui-workbench-Repository aus Docker/Portainer-Sicht" -Default $WorkspaceHostPath -Required
$WorkbenchImage = Read-WorkbenchValue -Prompt "Workbench-Dashboard-Image" -Default $WorkbenchImage -Required
$WorkbenchPublishedBind = Read-WorkbenchValue -Prompt "Workbench-Portbindung" -Default $WorkbenchPublishedBind -Required
$DockerNetworkName = Read-WorkbenchValue -Prompt "Docker-Netzwerkname für Workbench und OpenWebUI" -Default $DockerNetworkName -Required
if ($DockerNetworkName -match "\s") {
    throw "Docker-Netzwerkname darf keine Leerzeichen enthalten: $DockerNetworkName"
}
$useExternalDockerNetworkValue = [bool]$UseExternalDockerNetwork
if (-not $NonInteractive -and -not $PSBoundParameters.ContainsKey("UseExternalDockerNetwork")) {
    $networkMode = Read-WorkbenchValue -Prompt "Vorhandenes externes Docker-Netzwerk verwenden? (yes/no)" -Default "no" -Required
    if ($networkMode -notin @("yes", "no", "y", "n", "ja", "nein", "j")) {
        throw "Erlaubte Werte: yes/no oder ja/nein."
    }
    $useExternalDockerNetworkValue = $networkMode -in @("yes", "y", "ja", "j")
}

if ($OpenWebUIMode -eq "bundled") {
    $OpenWebUIImage = Read-WorkbenchValue -Prompt "OpenWebUI-Image" -Default $OpenWebUIImage -Required
    $OpenWebUIPublishedBind = Read-WorkbenchValue -Prompt "OpenWebUI-Portbindung" -Default $OpenWebUIPublishedBind -Required
    $OpenWebUIBaseUrl = if ([string]::IsNullOrWhiteSpace($OpenWebUIBaseUrl)) { "http://openwebui:8080" } else { $OpenWebUIBaseUrl }
    $OpenWebUIPublicUrl = if ([string]::IsNullOrWhiteSpace($OpenWebUIPublicUrl)) {
        if ($OpenWebUIPublishedBind -match "([^:]+)$") { "http://localhost:$($Matches[1])" } else { "http://localhost:3000" }
    }
    else {
        $OpenWebUIPublicUrl
    }
}
else {
    $OpenWebUIBaseUrl = Read-WorkbenchValue -Prompt "Interne OpenWebUI-URL aus dem Workbench-Container" -Default $OpenWebUIBaseUrl -Required
    $OpenWebUIPublicUrl = Read-WorkbenchValue -Prompt "Browser-URL für OpenWebUI" -Default $(if ($OpenWebUIPublicUrl) { $OpenWebUIPublicUrl } else { $OpenWebUIBaseUrl }) -Required
}

$RootCaPath = Read-WorkbenchValue -Prompt "Optionaler Host-Pfad zur Root-CA im PEM-Format" -Default $RootCaPath
$RootCaPath = Test-RootCaFile -PathValue $RootCaPath -AllowUnverified:$AllowUnverifiedRootCaPath

$authUser = Read-WorkbenchValue -Prompt "Workbench-Benutzername" -Default "workbench"
$authPassword = Read-WorkbenchSecret -Prompt "Workbench-Passwort (leer lassen, wenn später in Portainer gesetzt wird; Stack startet erst mit gesetztem Wert)"
$adminToken = Read-WorkbenchSecret -Prompt "OpenWebUI-Admin-Token für Sync-Aktionen (optional)"

$envPath = Join-Path $OutputDir "workbench.env"
$composePath = Join-Path $OutputDir "portainer-compose.yml"
$openwebuiSecret = Read-WorkbenchSecret -Prompt "WEBUI_SECRET_KEY für gebündeltes OpenWebUI (optional)"

$envLines = @(
    "# Generated by Deployment/configure-workbench-enterprise.ps1",
    "# Diese Datei ist lokal und darf keine Git-Versionierung bekommen.",
    "WORKBENCH_IMAGE=$WorkbenchImage",
    "WORKBENCH_WORKSPACE_HOST_PATH=$WorkspaceHostPath",
    "WORKBENCH_PUBLISHED_BIND=$WorkbenchPublishedBind",
    "WORKBENCH_DOCKER_NETWORK=$DockerNetworkName",
    "WORKBENCH_AUTH_USERNAME=$authUser",
    "WORKBENCH_AUTH_PASSWORD=$authPassword",
    "WORKBENCH_ALLOW_WRITE=true",
    "WORKBENCH_COMMAND_TIMEOUT_SECONDS=300",
    "WORKBENCH_AUTOMATION_ENABLED=true",
    "WORKBENCH_AUTOMATION_INTERVAL_MINUTES=30",
    "WORKBENCH_AUTOMATION_ACTIONS=check",
    "WORKBENCH_AUTOMATION_RUN_ON_START=false",
    "WORKBENCH_LOCALE=de",
    "OPENWEBUI_BASE_URL=$OpenWebUIBaseUrl",
    "OPENWEBUI_PUBLIC_URL=$OpenWebUIPublicUrl",
    "OPENWEBUI_TLS_VERIFY=true",
    "OPENWEBUI_ADMIN_TOKEN=$adminToken"
)

if ($OpenWebUIMode -eq "bundled") {
    $envLines += @(
        "OPENWEBUI_IMAGE=$OpenWebUIImage",
        "OPENWEBUI_PUBLISHED_BIND=$OpenWebUIPublishedBind",
        "WEBUI_AUTH=true",
        "WEBUI_SECRET_KEY=$openwebuiSecret",
        "OFFLINE_MODE=true",
        "ENABLE_RAG_WEB_SEARCH=false",
        "ENABLE_WEB_SEARCH=false"
    )
}

if ($RootCaPath) {
    $envLines += @(
        "WORKBENCH_ENTERPRISE_CA_HOST_FILE=$RootCaPath",
        "WORKBENCH_CA_BUNDLE=/certs/company-root-ca.pem",
        "WORKBENCH_SYSTEM_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt",
        "OPENWEBUI_CA_FILE=/certs/company-root-ca.pem",
        "OPENWEBUI_CA_PATH=",
        "SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt",
        "REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt",
        "OPENWEBUI_SSL_CERT_FILE=/certs/company-root-ca.pem",
        "OPENWEBUI_REQUESTS_CA_BUNDLE=/certs/company-root-ca.pem",
        "OPENWEBUI_CURL_CA_BUNDLE=/certs/company-root-ca.pem",
        "OPENWEBUI_NODE_EXTRA_CA_CERTS=/certs/company-root-ca.pem"
    )
}
else {
    $envLines += @(
        "WORKBENCH_ENTERPRISE_CA_HOST_FILE=",
        "WORKBENCH_CA_BUNDLE=",
        "WORKBENCH_SYSTEM_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt",
        "OPENWEBUI_CA_FILE=",
        "OPENWEBUI_CA_PATH="
    )
}

$composeLines = @(
    "name: openwebui-workbench-enterprise",
    "",
    "services:"
)

if ($OpenWebUIMode -eq "bundled") {
    $composeLines += @(
        "  openwebui:",
        "    image: `${OPENWEBUI_IMAGE}",
        "    restart: unless-stopped",
        "    ports:",
        "      - `"`${OPENWEBUI_PUBLISHED_BIND}:8080`"",
        "    environment:",
        "      WEBUI_AUTH: `${WEBUI_AUTH:-true}",
        "      WEBUI_SECRET_KEY: `${WEBUI_SECRET_KEY:-}",
        "      OFFLINE_MODE: `${OFFLINE_MODE:-true}",
        "      ENABLE_RAG_WEB_SEARCH: `${ENABLE_RAG_WEB_SEARCH:-false}",
        "      ENABLE_WEB_SEARCH: `${ENABLE_WEB_SEARCH:-false}",
        "      DO_NOT_TRACK: true",
        "      SCARF_NO_ANALYTICS: true",
        "      ANONYMIZED_TELEMETRY: false"
    )
    if ($RootCaPath) {
        $composeLines += @(
            "      SSL_CERT_FILE: `${OPENWEBUI_SSL_CERT_FILE}",
            "      REQUESTS_CA_BUNDLE: `${OPENWEBUI_REQUESTS_CA_BUNDLE}",
            "      CURL_CA_BUNDLE: `${OPENWEBUI_CURL_CA_BUNDLE}",
            "      NODE_EXTRA_CA_CERTS: `${OPENWEBUI_NODE_EXTRA_CA_CERTS}"
        )
    }
    $composeLines += @(
        "    volumes:",
        "      - openwebui-data:/app/backend/data",
        "      - type: bind",
        "        source: `${WORKBENCH_WORKSPACE_HOST_PATH}/Modelle/dist",
        "        target: /app/backend/data/openwebui-import",
        "        read_only: true",
        "      - type: bind",
        "        source: `${WORKBENCH_WORKSPACE_HOST_PATH}/Tools",
        "        target: /app/backend/data/openwebui-tools",
        "        read_only: true",
        "      - type: bind",
        "        source: `${WORKBENCH_WORKSPACE_HOST_PATH}/Artefakte/output",
        "        target: /app/backend/data/offline_artifacts"
    )
    if ($RootCaPath) {
        $composeLines += @(
            "      - type: bind",
            "        source: `${WORKBENCH_ENTERPRISE_CA_HOST_FILE}",
            "        target: /certs/company-root-ca.pem",
            "        read_only: true"
        )
    }
    $composeLines += @(
        "    networks:",
        "      - workbench",
        ""
    )
}

$composeLines += @(
    "  workbench:",
    "    image: `${WORKBENCH_IMAGE}",
    "    restart: unless-stopped",
    "    ports:",
    "      - `"`${WORKBENCH_PUBLISHED_BIND}:8088`"",
    "    environment:",
    "      WORKBENCH_ROOT: /workspace",
    "      WORKBENCH_HOST: 0.0.0.0",
    "      WORKBENCH_PORT: 8088",
    "      WORKBENCH_ALLOW_WRITE: `${WORKBENCH_ALLOW_WRITE:-true}",
    "      WORKBENCH_COMMAND_TIMEOUT_SECONDS: `${WORKBENCH_COMMAND_TIMEOUT_SECONDS:-300}",
    "      WORKBENCH_AUTOMATION_ENABLED: `${WORKBENCH_AUTOMATION_ENABLED:-true}",
    "      WORKBENCH_AUTOMATION_INTERVAL_MINUTES: `${WORKBENCH_AUTOMATION_INTERVAL_MINUTES:-30}",
    "      WORKBENCH_AUTOMATION_ACTIONS: `${WORKBENCH_AUTOMATION_ACTIONS:-check}",
    "      WORKBENCH_AUTOMATION_RUN_ON_START: `${WORKBENCH_AUTOMATION_RUN_ON_START:-false}",
    "      WORKBENCH_LOCALE: `${WORKBENCH_LOCALE:-de}",
    "      WORKBENCH_AUTH_USERNAME: `${WORKBENCH_AUTH_USERNAME:-}",
    "      WORKBENCH_AUTH_PASSWORD: `${WORKBENCH_AUTH_PASSWORD:?Set WORKBENCH_AUTH_PASSWORD in Portainer stack environment before starting Workbench}",
    "      OPENWEBUI_BASE_URL: `${OPENWEBUI_BASE_URL}",
    "      OPENWEBUI_PUBLIC_URL: `${OPENWEBUI_PUBLIC_URL}",
    "      OPENWEBUI_TLS_VERIFY: `${OPENWEBUI_TLS_VERIFY:-true}",
    "      OPENWEBUI_CA_FILE: `${OPENWEBUI_CA_FILE:-}",
    "      OPENWEBUI_CA_PATH: `${OPENWEBUI_CA_PATH:-}",
    "      OPENWEBUI_ADMIN_TOKEN: `${OPENWEBUI_ADMIN_TOKEN:-}",
    "      WORKBENCH_CA_BUNDLE: `${WORKBENCH_CA_BUNDLE:-}",
    "      WORKBENCH_SYSTEM_CA_BUNDLE: `${WORKBENCH_SYSTEM_CA_BUNDLE:-/etc/ssl/certs/ca-certificates.crt}",
    "      SSL_CERT_FILE: `${SSL_CERT_FILE:-/etc/ssl/certs/ca-certificates.crt}",
    "      REQUESTS_CA_BUNDLE: `${REQUESTS_CA_BUNDLE:-/etc/ssl/certs/ca-certificates.crt}",
    "    volumes:",
    "      - type: bind",
    "        source: `${WORKBENCH_WORKSPACE_HOST_PATH}",
    "        target: /workspace"
)

if ($RootCaPath) {
    $composeLines += @(
        "      - type: bind",
        "        source: `${WORKBENCH_ENTERPRISE_CA_HOST_FILE}",
        "        target: /certs/company-root-ca.pem",
        "        read_only: true"
    )
}

$composeLines += @(
    "    extra_hosts:",
    "      - `"host.docker.internal:host-gateway`"",
    "    networks:",
    "      - workbench",
    ""
)

if ($OpenWebUIMode -eq "bundled") {
    $composeLines += @(
        "volumes:",
        "  openwebui-data:",
        ""
    )
}

$composeLines += @(
    "networks:"
)

if ($useExternalDockerNetworkValue) {
    $composeLines += @(
        "  workbench:",
        "    external: true",
        "    name: `${WORKBENCH_DOCKER_NETWORK}"
    )
}
else {
    $composeLines += @(
        "  workbench:",
        "    name: `${WORKBENCH_DOCKER_NETWORK:-openwebui-workbench_workbench}",
        "    driver: bridge"
    )
}

Write-TextFile -PathValue $envPath -Lines $envLines
Write-TextFile -PathValue $composePath -Lines $composeLines

Write-Host "Erzeugt: $envPath"
Write-Host "Erzeugt: $composePath"
Write-Host "Portainer: Compose-Datei einfügen und die Werte aus workbench.env als Stack-Umgebung übernehmen."
