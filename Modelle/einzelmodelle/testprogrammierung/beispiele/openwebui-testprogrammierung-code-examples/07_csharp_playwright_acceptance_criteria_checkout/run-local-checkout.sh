#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   APP_BASE_URL=http://localhost:8080 CHECKOUT_PRODUCT_SKU=SKU-123 EXPIRED_VOUCHER_CODE=EXPIRED ./run-local-checkout.sh
# Test data is environment-driven so the same test can run locally and in CI.

PROJECT="src/CheckoutAcceptance.Playwright.Tests/CheckoutAcceptance.Playwright.Tests.csproj"
CONFIGURATION="Release"

: "${APP_BASE_URL:=https://example.test}"
: "${CHECKOUT_PRODUCT_SKU:=SKU-TEST-001}"
: "${EXPIRED_VOUCHER_CODE:=EXPIRED-TEST-VOUCHER}"
export APP_BASE_URL CHECKOUT_PRODUCT_SKU EXPIRED_VOUCHER_CODE

dotnet restore "${PROJECT}"
dotnet build "${PROJECT}" --configuration "${CONFIGURATION}" --no-restore
pwsh "src/CheckoutAcceptance.Playwright.Tests/bin/${CONFIGURATION}/net8.0/playwright.ps1" install --with-deps
dotnet test "${PROJECT}" --configuration "${CONFIGURATION}" --no-build --logger trx --results-directory TestResults
