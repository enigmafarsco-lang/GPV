#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: python3 is not installed or not on PATH." >&2
  exit 2
fi
if ! "$PYTHON_BIN" -m venv --help >/dev/null 2>&1; then
  echo "ERROR: Python venv support is missing." >&2
  echo "On Debian/Ubuntu install it with: sudo apt update && sudo apt install -y python3-venv" >&2
  exit 3
fi
if [[ ! -x .venv/bin/python ]]; then
  echo "Creating isolated virtual environment: $HERE/.venv"
  if ! "$PYTHON_BIN" -m venv .venv; then
    echo "ERROR: could not create .venv. On Debian/Ubuntu install python3-venv (or python3-full)." >&2
    exit 4
  fi
fi
VENV_PY="$HERE/.venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip setuptools wheel
"$VENV_PY" -m pip install -r requirements.txt
export PYTHONPATH="$HERE:${PYTHONPATH:-}"
"$VENV_PY" -m gpr_workstation.doctor
printf '\nReady. Use:\n  ./run_demo.sh\n  ./run_cli.sh process demo_capture.npz --config configs/demo_synthetic.yaml --out output/demo\n'
