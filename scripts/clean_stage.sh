#!/usr/bin/env bash
set -euo pipefail
stage="${1:?stage}"; build="${2:?build}"; ip_repo="${3:?ip repo}"; project="${4:?project}"
rm -f "$build/.stamps/$stage.done" "$build/logs/$stage.log"
case "$stage" in
  step02_hls_scheduler) rm -rf ip/custom/gpr_sweep_scheduler/gpr_sweep_scheduler_hls "$ip_repo/gpr_sweep_scheduler" ;;
  step03_hls_rxextract) rm -rf ip/custom/gpr_rx_tone_extractor/gpr_rx_tone_extractor_hls "$ip_repo/gpr_rx_tone_extractor" ;;
  step04_hls_sweepavg) rm -rf ip/custom/gpr_sweep_average/gpr_sweep_average_hls "$ip_repo/gpr_sweep_average" ;;
  step05_hls_cal) rm -rf ip/custom/gpr_cal_window/gpr_cal_window_hls "$ip_repo/gpr_cal_window" ;;
  step06_hls_pad) rm -rf ip/custom/gpr_zero_pad_cfg/gpr_zero_pad_cfg_hls "$ip_repo/gpr_zero_pad_cfg" ;;
  step07_hls_background) rm -rf ip/custom/gpr_background_ewma/gpr_background_ewma_hls "$ip_repo/gpr_background_ewma" ;;
  step08_hls_power) rm -rf ip/custom/gpr_power32/gpr_power32_hls "$ip_repo/gpr_power32" ;;
  step09_hls_cfar1d) rm -rf ip/custom/gpr_cfar1d/gpr_cfar1d_hls "$ip_repo/gpr_cfar1d" ;;
  step10_hls_imaging)
    for x in gpr_background_median_accel gpr_kirchhoff_coherent_accel gpr_cfar2d_accel gpr_cluster2d_accel; do
      rm -rf "ip/custom/$x/${x}_hls" "$ip_repo/$x"
    done ;;
  step12_vivado_project|step13_vivado_integrate|step14_vivado_validate|step15_synth|step16_impl|step17_bitstream|step18_export_xsa)
    rm -rf "$build/vivado/$project" "$build/output" ;;
esac
