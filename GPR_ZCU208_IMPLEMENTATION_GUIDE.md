# ZCU208 / XCZU48DR Complete GPR Hybrid V3 Implementation Guide

## 1. RFSoC base requirement

A production build must begin from a ZCU208 project in which converter clocks, DAC/ADC tiles, DUC/DDC, mixer update events and Multi-Tile Synchronization have already been demonstrated on hardware. `BASE_XPR` is cloned into the GPR work project. The package does not create a speculative RFDC design and then hide failures with Tcl `catch`.

The GPR hierarchy receives:

- `aclk`, `aresetn`;
- `system_ready = RFDC_READY & MTS_LOCKED & CLOCKS_LOCKED`;
- RFDC-adapted complex RX stream;
- RFDC-adapted TX stream;
- sub-band handshake to R5/A53;
- position handshake to encoder/GNSS/UAV control.

## 2. SFCW sub-band plan

For uniform frequency spacing:

`f_k = f_start + k*df`

Choose `tones_per_subband = M` and one common residual start `f_res0`. For local tone `m=k mod M`:

`f_res(m) = f_res0 + m*df`

The RFDC LO for sub-band `s=floor(k/M)` is:

`f_LO(s) = f_k - f_res(m)`

This lets every sub-band reuse the same PL residual DDS pattern. `software/ps/gpr_subband_plan.py` generates a reference table.

The scheduler uses a 48-bit residual phase increment:

`phase_step = round(f_res/F_PL * 2^48) mod 2^48`.

## 3. Deterministic RFDC update

When the scheduler asserts `sb_req`:

1. hold TX sequence at the sub-band boundary;
2. program DAC NCO;
3. program ADC NCO to the same sub-band plan;
4. issue the verified RFDC mixer update event;
5. wait for the deterministic update boundary defined by the MTS base;
6. pulse `sb_ack`.

The scheduler never assumes that a register write alone implies phase-coherent retuning.

## 4. Position gating

Before each position the scheduler asserts `pos_req` and `pos_id`. The motion/navigation controller asserts `pos_ack` only when the physical sensor position is valid.

For a static bench test, `pos_ack` may be tied high. For field scanning it must come from the encoder/GNSS/UAV position service.

## 5. RX residual extraction

The converter stream is not assumed to carry tone metadata. The scheduler emits an independent tone-context stream containing:

- residual phase step;
- true tone index;
- position index;
- average/sweep index;
- sub-band index.

The RX extractor:

1. drains RFDC samples when no context is active;
2. consumes exactly `dwell_samples` for the active tone;
3. ignores the first `rx_discard_samples`;
4. multiplies remaining samples by `exp(-j*phase_residual[n])`;
5. averages them to one coherent complex frequency sample.

The phase after the RFDC/analog path can have a deterministic constant offset; calibration removes that system phase. The critical point is removing the rotating residual tone before integration.

## 6. Coherent sweep averaging

`gpr_sweep_average` averages the same true frequency across `n_averages` sweeps. Dwell integration and sweep averaging are separate so accumulator width and normalization are explicit.

## 7. Calibration and range transform

`gpr_cal_window` multiplies by a complex Q1.15 coefficient. Generate:

`C[k] = H_system[k]^-1 * W[k]`

so hardware applies calibration and the frequency-domain Kaiser window in one multiplier.

`gpr_zero_pad_cfg` zero-pads to `N_IFFT`. Production range processing uses AMD/Xilinx XFFT configured as an inverse transform. The runtime config/scaling word must be verified against the exact Vivado XFFT version in HIL.

## 8. Background choices

### Streaming EWMA
Useful for low latency and slowly varying clutter. It can be bypassed.

### DDR median
`gpr_background_median_accel` computes the component-wise median across positions for each complex range bin and subtracts it. Use this path when matching the validated median-background behavior is more important than minimum latency.

A later SVD/PCA stage may still be performed offline/CPU-side when target attenuation has been characterized for the site.

## 9. Coherent migration

`gpr_kirchhoff_coherent_accel` consumes complex B-scan samples. It performs:

- geometric range calculation;
- range-bin interpolation;
- obliquity/spreading weighting;
- absorption compensation;
- aperture taper;
- coherent `exp(+j2π k_beta R)` phase restoration;
- complex accumulation;
- magnitude after coherent summation.

This replaces the earlier magnitude-only migration accelerator.

## 10. Detection and clustering

The real-time streaming 1-D CFAR is retained as a diagnostic range detector.

Primary image-domain detection is:

`coherent migration -> 2-D CFAR -> connected-component clustering`

`gpr_cluster2d_accel` emits six report words:
1. total hits;
2. cluster count;
3. mean cluster depth Q16;
4. mean cross-range Q16;
5. minimum cluster depth Q16;
6. maximum cluster depth Q16.

Target material/type classification remains in the PS/offline workstation unless a trained, validated FPGA model is later supplied.

## 11. DMA and backpressure

The main range IQ and range power branches include FIFOs. Production DMA must still be dimensioned so display/network consumers cannot indefinitely stall acquisition.

Recommended storage:
- raw/extracted frequency IQ for calibration/debug;
- range IQ;
- optional median-cleaned complex B-scan;
- migrated image;
- CFAR mask;
- metadata and cluster reports.

## 12. Hardware bring-up sequence

1. Verify clocks and MTS across cold boots.
2. Tie `pos_ack=1` for bench operation.
3. Coax DAC-to-ADC loopback.
4. Confirm sub-band `sb_req/sb_ack` and identical ADC/DAC LO plan.
5. Inject one residual tone and verify derotated dwell average is phase-stable.
6. Sweep synthetic phase slope and verify IFFT range.
7. Run multiple averages and confirm coherent SNR behavior.
8. Verify background bypass, EWMA and DDR median separately.
9. Compare coherent migration to MATLAB/offline reference.
10. Validate 2-D CFAR and clustering.
11. Only then connect antennas and field targets.
