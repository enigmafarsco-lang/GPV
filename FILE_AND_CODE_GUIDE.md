# Hybrid V3 file and code guide

## Real-time acquisition IP

### `gpr_sweep_scheduler`
One hardware timing source for TX, RX context, sub-band retune and spatial position gating. It is restartable through the standard HLS control register.

### `gpr_rx_tone_extractor`
Consumes RFDC DDC samples and the scheduler context. It discards a configurable settling interval, mixes with the conjugate residual DDS phase and averages the valid dwell samples.

### `gpr_sweep_average`
Averages the extracted complex value for each frequency across `n_averages` sweeps.

### `gpr_cal_window`
Multiplies each complex tone by a Q1.15 complex coefficient. Precompute coefficient = inverse system response × frequency window.

### `gpr_zero_pad_cfg` + Xilinx XFFT
Zero-padding and runtime FFT config are custom; the transform itself uses the production Xilinx FFT IP.

### `gpr_background_ewma`
Low-latency range-bin background estimate. Set bypass when using the frame/DDR median accelerator.

## Image/DDR IP

### `gpr_background_median_accel`
Component-wise median across positions for each complex range bin.

### `gpr_kirchhoff_coherent_accel`
Coherent complex Kirchhoff focusing with interpolation, phase restoration, spreading/obliquity, absorption and aperture taper.

### `gpr_cfar2d_accel`
2-D image CFAR.

### `gpr_cluster2d_accel`
8-neighbour connected-component clustering and compact report output.

## Integration

`config/zcu208_gpr_bd_map.tcl` is the only production file that should know exact RFDC, MTS, PS, DMA and clock interface names.
