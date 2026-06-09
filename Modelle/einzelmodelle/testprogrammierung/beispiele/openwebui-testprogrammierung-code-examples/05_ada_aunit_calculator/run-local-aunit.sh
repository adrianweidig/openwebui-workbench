#!/usr/bin/env bash
set -euo pipefail

# Local execution example:
#   ./run-local-aunit.sh
# Requires GNAT, gprbuild, and AUnit with aunit.gpr available on the project path.

gprbuild -P default.gpr
gprbuild -P tests.gpr
mkdir -p test-results
./obj/tests/test_runner | tee test-results/aunit-output.txt
