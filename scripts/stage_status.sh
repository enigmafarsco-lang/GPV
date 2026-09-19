#!/usr/bin/env bash
set -euo pipefail
build="${1:?build path required}"; shift
for s in "$@"; do
  stamp="$build/.stamps/$s.done"
  if [[ -f "$stamp" ]]; then printf 'DONE  %s\n' "$s"; else printf 'TODO  %s\n' "$s"; fi
done
