#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$RELEASE_DIR"
archive="$RELEASE_DIR/${PROJECT_NAME}_source_and_artifacts.tar.gz"
items=(
  README.md HYBRID_V3_CHANGES.md GPR_ZCU208_IMPLEMENTATION_GUIDE.md
  BUILD_STAGES.md FILE_AND_CODE_GUIDE.md VALIDATION_REPORT.md
  Makefile config.mk
  common config docs hil ip scripts software
)
[[ -d build/output ]] && items+=(build/output)
[[ -d build/logs ]] && items+=(build/logs)
[[ -d "$HIL_OUTPUT_DIR" ]] && items+=("${HIL_OUTPUT_DIR#"$PWD/"}")
tar -czf "$archive" "${items[@]}"
sha256sum "$archive" > "$archive.sha256"
echo "Packaged $archive"
