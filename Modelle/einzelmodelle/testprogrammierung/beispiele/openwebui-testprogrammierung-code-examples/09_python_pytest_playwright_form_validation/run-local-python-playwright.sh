#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   APP_BASE_URL=https://your-test-app.example ./run-local-python-playwright.sh
# The pytest configuration emits JUnit XML and keeps Playwright traces/videos on failure.

: "${APP_BASE_URL:=https://example.test}"
: "${CONTACT_TEST_EMAIL:=qa@example.test}"
export APP_BASE_URL CONTACT_TEST_EMAIL

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium
pytest
