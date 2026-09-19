# FullStack Hybrid V3 Validation Report

## Completed here

- `make lint`: PASS.
- Hybrid acquisition/model regression: **5/5 PASS**.
- Offline workstation test suite: **5/5 PASS**.
- Synthetic offline end-to-end replay: PASS:
  - 256 tones;
  - 200 positions;
  - 2 detections;
  - raw magnitude/phase;
  - calibration;
  - range B-scan;
  - median clutter suppression;
  - Kirchhoff migration;
  - 2-D CFAR;
  - 3-D visualization;
  - STFT diagnostic;
  - CSV/NPZ/HDF5/HTML output.
- Production IP list audited: old V1 tone accumulator / magnitude migration are not collected.
- ZCU208 part spelling corrected to `xczu48dr-2fsvg1517e` across build and software profiles.
- Critical Vivado hierarchy connections use fail-hard helpers rather than silent `catch`.

## Not completed here

No AMD Vivado/Vitis HLS or physical ZCU208 is available in this environment. The following remain target-system gates:

- Vitis HLS C simulation and synthesis;
- packaged-IP port-name confirmation against the installed Vitis version;
- Xilinx XFFT property and inverse/scaling-word confirmation;
- integration with the user's verified ZCU208 RFDC/MTS base;
- Vivado synthesis / route / WNS;
- bitstream and XSA;
- RFDC MTS repeatability;
- sub-band NCO retune timing;
- physical position handshake;
- converter loopback;
- antenna/soil field testing.
