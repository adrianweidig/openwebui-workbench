#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   APP_BASE_URL=https://your-test-app.example HEADLESS=1 ./run-local-java-selenium.sh
# Requires Maven, JDK 21, and Chrome. Selenium Manager resolves the matching browser driver.

: "${APP_BASE_URL:=https://example.test}"
: "${HEADLESS:=1}"
: "${TEST_ARTIFACT_DIR:=target/selenium-artifacts}"
export APP_BASE_URL HEADLESS TEST_ARTIFACT_DIR

mvn -B test
