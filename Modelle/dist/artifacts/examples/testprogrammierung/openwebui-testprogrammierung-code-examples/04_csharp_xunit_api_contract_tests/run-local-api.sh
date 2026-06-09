#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   API_BASE_URL=http://localhost:8080 ./run-local-api.sh
# API_BEARER_TOKEN is optional and must be supplied through the environment when the API requires authentication.

PROJECT="src/ApiContract.Xunit.Tests/ApiContract.Xunit.Tests.csproj"
CONFIGURATION="Release"

: "${API_BASE_URL:=https://example.test}"
export API_BASE_URL

dotnet restore "${PROJECT}"
dotnet build "${PROJECT}" --configuration "${CONFIGURATION}" --no-restore
dotnet test "${PROJECT}" --configuration "${CONFIGURATION}" --no-build --logger trx --results-directory TestResults
