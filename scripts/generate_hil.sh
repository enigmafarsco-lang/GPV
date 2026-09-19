#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$HIL_OUTPUT_DIR"
"${MATLAB:-matlab}" -batch "addpath('hil/matlab'); generate_gpr_hil_vectors('${HIL_OUTPUT_DIR}'); generate_gpr_hybrid_v3_plan('${HIL_OUTPUT_DIR}');"
