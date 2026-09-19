#!/usr/bin/env bash
set -euo pipefail
failures=0; warnings=0
check_tool() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    printf 'PASS tool %-12s %s\n' "$name" "$(command -v "$name")"
  else
    printf 'FAIL tool %-12s not found on PATH\n' "$name"
    failures=$((failures+1))
  fi
}
check_tool make
check_tool git
check_tool "${VITIS_HLS:-vitis_hls}"
check_tool "${VIVADO:-vivado}"
check_tool "${MATLAB:-matlab}"
check_tool "${PYTHON3:-python3}"

[[ "${PART:-}" == "xczu48dr-2fsvg1517e" ]] || { echo "FAIL PART=${PART:-unset}"; failures=$((failures+1)); }

if [[ -n "${BASE_XPR:-}" ]]; then
  [[ -f "$BASE_XPR" ]] || { echo "FAIL BASE_XPR not found: $BASE_XPR"; failures=$((failures+1)); }
else
  echo "WARN BASE_XPR unset. HLS/model stages can run, but Vivado production stages require a verified ZCU208 RFDC/MTS base."
  warnings=$((warnings+1))
fi

if command -v "${VIVADO:-vivado}" >/dev/null 2>&1; then
  actual="$(${VIVADO:-vivado} -version 2>/dev/null | sed -n '1s/.*v\([0-9][0-9.]*\).*/\1/p')"
  echo "INFO Vivado version=${actual:-unknown}"
  if [[ -n "${EXPECTED_VIVADO_VERSION:-}" && "$actual" != "$EXPECTED_VIVADO_VERSION" ]]; then
    echo "FAIL expected Vivado $EXPECTED_VIVADO_VERSION, detected $actual"; failures=$((failures+1))
  fi
fi
echo "INFO part=$PART clock_period_ns=${PL_CLOCK_PERIOD_NS:-unset}"
echo "INFO hybrid-v3 limits tones=${MAX_TONES:-} ifft=${MAX_IFFT:-} positions=${MAX_POSITIONS:-}"
echo "INFO required readiness gate: RFDC_READY && MTS_LOCKED && CLOCKS_LOCKED"
echo "SUMMARY failures=$failures warnings=$warnings"
((failures == 0))
