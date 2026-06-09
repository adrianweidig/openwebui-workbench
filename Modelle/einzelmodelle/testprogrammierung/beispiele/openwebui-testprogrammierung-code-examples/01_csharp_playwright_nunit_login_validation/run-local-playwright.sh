#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   APP_BASE_URL=http://localhost:8080 ./run-local-playwright.sh
# The test project writes TRX results to TestResults and captures screenshots on failure.

PROJECT="src/LoginAutomation.Playwright.Tests/LoginAutomation.Playwright.Tests.csproj"
CONFIGURATION="Release"

: "${APP_BASE_URL:=https://example.test}"
export APP_BASE_URL

dotnet restore "${PROJECT}"
dotnet build "${PROJECT}" --configuration "${CONFIGURATION}" --no-restore
pwsh "src/LoginAutomation.Playwright.Tests/bin/${CONFIGURATION}/net8.0/playwright.ps1" install --with-deps
dotnet test "${PROJECT}" --configuration "${CONFIGURATION}" --no-build --logger trx --results-directory TestResults
