#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   ./run-local-mstest.sh
# Unit tests do not require external URLs, browsers, or secrets.

PROJECT="tests/DiscountEngine.Tests/DiscountEngine.Tests.csproj"
CONFIGURATION="Release"

dotnet restore "${PROJECT}"
dotnet build "${PROJECT}" --configuration "${CONFIGURATION}" --no-restore
dotnet test "${PROJECT}" --configuration "${CONFIGURATION}" --no-build --logger trx --results-directory TestResults --collect "XPlat Code Coverage"
