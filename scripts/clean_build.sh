#!/usr/bin/env bash
set -euo pipefail
build="${1:?build}"; ip_repo="${2:?ip repo}"
rm -rf "$build" "$ip_repo"
find ip/custom -maxdepth 2 -type d -name '*_hls' -prune -exec rm -rf {} +
