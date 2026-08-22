#!/usr/bin/env bash
# Run OPA unit tests for SkandaShield policies
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if ! command -v opa >/dev/null 2>&1; then
  echo "OPA CLI not found. Install from https://www.openpolicyagent.org/docs/latest/#running-opa"
  exit 1
fi
opa test policies/ tests/rego/ -v
echo "Rego tests passed."
