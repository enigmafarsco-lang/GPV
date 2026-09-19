# Hybrid V3 validation status

## Performed in the package-construction environment

- shell syntax checks;
- Make dry-run for every restartable stage;
- Tcl completeness checks with `tclsh` when available;
- required HLS source/testbench/build artifact checks;
- check that critical Vivado hierarchy integration contains no silent `catch` connections;
- check for the earlier malformed C++ sine-LUT delimiter defect;
- pure-Python algorithmic regression:
  - residual-tone cancellation without derotation;
  - residual derotation recovery;
  - dwell/discard accounting;
  - frame sample/context counts;
  - correct-sign coherent migration phase focusing;
- offline workstation regression tests (run separately before packaging).

## Not claimed in this environment

AMD Vivado/Vitis HLS and a physical ZCU208 are not available here. Therefore this package does not claim:

- HLS C simulation or HLS synthesis passed on your installed tool version;
- XFFT property/config word compatibility passed;
- IP Integrator validation against your specific RFDC/MTS base passed;
- synthesis, placement/routing or timing closure passed;
- bitstream/XSA generation passed;
- RFDC MTS or mixer update repeatability passed on hardware;
- analog/RF field performance passed.

Those are explicit fail-hard build/bring-up gates in the package.
