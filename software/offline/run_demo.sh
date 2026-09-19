#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
if [[ ! -x .venv/bin/python ]]; then
  echo "No .venv found; creating it first..."
  ./setup_venv.sh
fi
PY="$HERE/.venv/bin/python"
export PYTHONPATH="$HERE:${PYTHONPATH:-}"
"$PY" examples/generate_demo_capture.py --out demo_capture.npz
"$PY" -m gpr_workstation.cli process demo_capture.npz --config configs/demo_synthetic.yaml --out output/demo
printf '\nDemo complete. Output: %s/output/demo\n' "$HERE"
