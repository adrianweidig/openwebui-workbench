#!/usr/bin/env bash
set -euo pipefail

# GNATtest harness executable names may differ by toolchain options and separate-driver mode.
# This script fails explicitly if the generated executable cannot be located.
mapfile -t candidates < <(find gnattest/harness -maxdepth 4 -type f -perm -111 | sort)

if [[ ${#candidates[@]} -eq 0 ]]; then
  echo "No executable GNATtest driver found under gnattest/harness." >&2
  exit 2
fi

for candidate in "${candidates[@]}"; do
  echo "Running GNATtest driver: ${candidate}"
  "${candidate}"
done
