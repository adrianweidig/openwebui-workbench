#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   ./run-local-decision-matrix.sh
# These tests lock the model's expected recommendation levels and prevent accidental invented support.

PROJECT="tests/TestStack.Decisions.Tests/TestStack.Decisions.Tests.csproj"
CONFIGURATION="Release"

dotnet restore "${PROJECT}"
dotnet build "${PROJECT}" --configuration "${CONFIGURATION}" --no-restore
dotnet test "${PROJECT}" --configuration "${CONFIGURATION}" --no-build --logger trx --results-directory TestResults
