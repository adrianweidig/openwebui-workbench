#!/usr/bin/env sh
set -eu

BUNDLED_WORKSPACE="${WORKBENCH_BUNDLED_WORKSPACE:-/opt/openwebui-workbench/workspace}"
WORKBENCH_ROOT_DIR="${WORKBENCH_ROOT:-/workspace}"
SYSTEM_CA_BUNDLE="${WORKBENCH_SYSTEM_CA_BUNDLE:-/etc/ssl/certs/ca-certificates.crt}"
CA_SOURCE="${WORKBENCH_CA_BUNDLE:-}"

if [ -d "$BUNDLED_WORKSPACE/Modelle/einzelmodelle/istqb-testfallgenerator" ] \
  && [ -d "$BUNDLED_WORKSPACE/Modelle/einzelmodelle/testprogrammierung" ] \
  && [ ! -d "$WORKBENCH_ROOT_DIR/Modelle/einzelmodelle" ]; then
  mkdir -p "$WORKBENCH_ROOT_DIR"
  cp -a "$BUNDLED_WORKSPACE/." "$WORKBENCH_ROOT_DIR/"
  echo "Initialized Workbench workspace from bundled image content." >&2
fi

if [ -n "$CA_SOURCE" ]; then
  if [ ! -f "$CA_SOURCE" ]; then
    echo "WORKBENCH_CA_BUNDLE points to a missing file: $CA_SOURCE" >&2
    exit 1
  fi
  if grep -q "BEGIN .*PRIVATE KEY" "$CA_SOURCE"; then
    echo "WORKBENCH_CA_BUNDLE must contain certificates only, not private keys." >&2
    exit 1
  fi
  if ! grep -q "BEGIN CERTIFICATE" "$CA_SOURCE"; then
    echo "WORKBENCH_CA_BUNDLE does not look like a PEM certificate bundle." >&2
    exit 1
  fi
  rm -f /usr/local/share/ca-certificates/openwebui-workbench-enterprise-root-ca-*.crt
  awk '
    /-----BEGIN CERTIFICATE-----/ {
      count += 1
      file = sprintf("/usr/local/share/ca-certificates/openwebui-workbench-enterprise-root-ca-%02d.crt", count)
    }
    file {
      print > file
    }
    /-----END CERTIFICATE-----/ {
      close(file)
      file = ""
    }
    END {
      if (count == 0) {
        exit 1
      }
    }
  ' "$CA_SOURCE"
fi

if command -v update-ca-certificates >/dev/null 2>&1; then
  update-ca-certificates >/dev/null
  echo "Refreshed container CA certificates." >&2
fi

if [ -f "$SYSTEM_CA_BUNDLE" ]; then
  export SSL_CERT_FILE="${SSL_CERT_FILE:-$SYSTEM_CA_BUNDLE}"
  export REQUESTS_CA_BUNDLE="${REQUESTS_CA_BUNDLE:-$SYSTEM_CA_BUNDLE}"
fi

exec "$@"
