#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$IP_REPO"
required=(
  gpr_sweep_scheduler
  gpr_rx_tone_extractor
  gpr_sweep_average
  gpr_cal_window
  gpr_zero_pad_cfg
  gpr_background_ewma
  gpr_power32
  gpr_cfar1d
  gpr_background_median_accel
  gpr_kirchhoff_coherent_accel
  gpr_cfar2d_accel
  gpr_cluster2d_accel
)
manifest="$IP_REPO/ip_manifest.tsv"
printf 'name\tcomponent_xml\n' > "$manifest"
for name in "${required[@]}"; do
  directory="$IP_REPO/$name"
  [[ -f "$directory/component.xml" ]] || {
    echo "ERROR: packaged IP missing: $directory/component.xml" >&2
    exit 4
  }
  printf '%s\t%s\n' "$name" "$directory/component.xml" >> "$manifest"
done
echo "Validated Hybrid V3 IP repository: $manifest"
