#!/usr/bin/env bash
set -euo pipefail

# GNATtest is project-aware. Keep the source project as the single source of truth for compiler switches and harness locations.
gprbuild -P default.gpr

# Skeletons are generated only for visible subprograms in legal Ada units. Existing skeletons are preserved by GNATtest.
gnattest -P default.gpr

# The generated harness project is created under the Harness_Dir configured in default.gpr.
gprbuild -P gnattest/harness/test_driver.gpr
