#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OFF="$ROOT/software/offline"
if [[ ! -x "$OFF/.venv/bin/python" ]]; then
  echo "No offline virtual environment found. Run ./setup_offline.sh first." >&2
  exit 2
fi
export PYTHONPATH="$OFF:${PYTHONPATH:-}"
exec "$OFF/.venv/bin/python" -m gpr_workstation.gui "$@"
