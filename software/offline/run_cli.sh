#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$HERE:${PYTHONPATH:-}"
if [[ -x "$HERE/.venv/bin/python" ]]; then PY="$HERE/.venv/bin/python"; else PY="${PYTHON_BIN:-python3}"; fi
if ! command -v "$PY" >/dev/null 2>&1 && [[ ! -x "$PY" ]]; then
  echo "ERROR: Python not found. Run ./setup_venv.sh first." >&2; exit 2
fi
exec "$PY" -m gpr_workstation.cli "$@"
