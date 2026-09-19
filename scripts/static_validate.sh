#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; cd "$root"

for s in scripts/*.sh; do bash -n "$s"; done
for stage in $(make --no-print-directory list); do make -n "$stage" >/dev/null; done

ips=(
 gpr_sweep_scheduler gpr_rx_tone_extractor gpr_sweep_average gpr_cal_window
 gpr_zero_pad_cfg gpr_background_ewma gpr_power32 gpr_cfar1d
 gpr_background_median_accel gpr_kirchhoff_coherent_accel gpr_cfar2d_accel gpr_cluster2d_accel
)
for ip in "${ips[@]}"; do
  test -s "ip/custom/$ip/src/$ip.cpp"
  test -s "ip/custom/$ip/src/$ip.hpp"
  test -s "ip/custom/$ip/tb/${ip}_tb.cpp"
  test -s "ip/custom/$ip/build_hls.tcl"
done

grep -q 'xczu48dr-2fsvg1517e' config.mk
grep -q 'rx_tone_extractor' common/vivado/create_gpr_v3_hier.tcl
grep -q 'system_ready' common/vivado/create_gpr_v3_hier.tcl
grep -q 'pos_req' common/vivado/create_gpr_v3_hier.tcl
grep -q 'gpr_kirchhoff_coherent_accel' common/vivado/create_gpr_v3_hier.tcl
grep -q 'gpr_background_median_accel' common/vivado/create_gpr_v3_hier.tcl
grep -q 'gpr_cluster2d_accel' common/vivado/create_gpr_v3_hier.tcl
grep -q 'Production map is intentionally fail-hard' config/zcu208_gpr_bd_map.tcl

# Critical integration must not use silent catch.
if grep -n 'catch .*connect_bd' common/vivado/create_gpr_v3_hier.tcl common/vivado/12_integrate_gpr_v3.tcl; then
  echo "FAIL: critical hierarchy/integration contains silent catch" >&2; exit 5
fi

# Regression for the earlier malformed C++ LUT bug: adjacent integer literals without commas
python3 - <<'PY'
import re, pathlib
for f in ["ip/custom/gpr_sweep_scheduler/src/gpr_sweep_scheduler.cpp",
          "ip/custom/gpr_rx_tone_extractor/src/gpr_rx_tone_extractor.cpp"]:
    s=pathlib.Path(f).read_text()
    body=s.split("{",1)[1]
    if re.search(r'(?<![,0-9])[-]?\d+\s+[-]?\d+(?![,0-9])', body[:16000]):
        raise SystemExit("possible missing comma in LUT: "+f)
print("PASS LUT delimiter sanity")
PY

if command -v tclsh >/dev/null 2>&1; then
  while IFS= read -r f; do
    tclsh <<EOF
set h [open {$f} r]; set t [read \$h]; close \$h
if {![info complete \$t]} {error {Incomplete Tcl syntax in $f}}
EOF
  done < <(find common/vivado config ip/custom -name '*.tcl' -type f | sort)
fi

python3 scripts/hybrid_model_test.py
echo "PASS: Hybrid V3 static/build-contract validation"
