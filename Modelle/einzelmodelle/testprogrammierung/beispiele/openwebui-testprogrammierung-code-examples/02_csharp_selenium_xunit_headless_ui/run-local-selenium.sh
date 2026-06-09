#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   APP_BASE_URL=http://localhost:8080 HEADLESS=1 ./run-local-selenium.sh
# Selenium Manager resolves the browser driver; Chrome must be installed locally or on the build agent.

PROJECT="src/SeleniumAutomation.Xunit.Tests/SeleniumAutomation.Xunit.Tests.csproj"
CONFIGURATION="Release"

: "${APP_BASE_URL:=https://example.test}"
: "${HEADLESS:=1}"
: "${TEST_ARTIFACT_DIR:=artifacts}"
export APP_BASE_URL HEADLESS TEST_ARTIFACT_DIR

dotnet restore "${PROJECT}"
dotnet build "${PROJECT}" --configuration "${CONFIGURATION}" --no-restore
dotnet test "${PROJECT}" --configuration "${CONFIGURATION}" --no-build --logger trx --results-directory TestResults
