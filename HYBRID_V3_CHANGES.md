# Hybrid V3 changes after comparison with GPV

Hybrid V3 keeps the restartable verified-base BuildKit and offline workstation, but incorporates the strongest architectural ideas observed in GPV while fixing integration hazards.

## Corrections

1. **Shared sweep scheduler** drives TX timing and independently generates RX context; RFDC is never assumed to provide `tone` or `position` TUSER metadata.
2. **Sub-band RFDC NCO + residual PL DDS** retained, with explicit `sb_req/sb_id/sb_ack`; averaging is sub-band-major so RFDC retunes occur once per sub-band per position rather than once per average.
3. **RX residual derotation** added before integration.
4. **Dwell integration and sweep averaging separated**. `dwell_samples_total` and `rx_discard_samples` are explicit.
5. **Position gating** added with `pos_req/pos_id/pos_ack`.
6. **Frame restart** uses the normal HLS `ap_start/ap_done` transaction; no sticky RTL stop bit.
7. **AXI-Lite compliance** is delegated to generated HLS AXI-Lite slaves instead of a hand-coded AW/W-same-cycle slave.
8. **RFDC/MTS readiness gate** is explicit (`system_ready`) and production mapping is fail-hard.
9. **RFDC width/sample adaptation is required in the verified base map**; 32-bit internal IQ format is not blindly wired to converter ports.
10. **Coherent complex Kirchhoff migration** replaces the previous magnitude-only accelerator.
11. **Median background accelerator** is available for frame/DDR processing; streaming EWMA remains for low-latency operation.
12. **2-D CFAR + connected-component clustering** are both available as hardware accelerators.
13. **Xilinx XFFT remains the production IFFT**, while algorithmic HIL/golden comparison remains part of validation.
14. **Independent buffered output branches** reduce accidental acquisition backpressure from DMA/display paths.

## Internal complex sample convention

All custom streaming IQ uses:
- bits `[15:0]`: signed I
- bits `[31:16]`: signed Q

Any RFDC configuration with a different samples-per-clock or TDATA packing must use an explicit adapter in `config/zcu208_gpr_bd_map.tcl`.
