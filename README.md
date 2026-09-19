# RFSoC ZCU208 / XCZU48DR Complete GPR Hybrid V3

Hybrid V3 is the revised FPGA/PS/offline package after comparing the earlier BuildKit with the GPV RTL implementation. It keeps the restartable, fail-hard ZCU208 integration model and adds the missing coherent SFCW acquisition details.

## Main hardware flow

```text
                     verified RFDC/MTS base
                 ┌────────────────────────────┐
                 │  DAC DUC/NCO   ADC DDC/NCO│
                 └──────▲──────────────┬──────┘
                        │              │
        TX residual DDS│              │RX residual IQ
                        │              ▼
                 shared sweep     RX derotator
                   scheduler       + dwell average
                        │              │
                        └─context──────┘
                                       ▼
                               coherent sweep average
                                       ▼
                           calibration × Kaiser window
                                       ▼
                              zero pad + Xilinx IFFT
                                       ▼
                          streaming EWMA (bypassable)
                                  ┌────┴────┐
                                  │         │
                              DMA range   1D CFAR diagnostic
                                  │
                                  ▼
                                 DDR
                       ┌──────────┼─────────────┐
                       ▼          ▼             ▼
                    median     coherent      offline/GUI
                  background   Kirchhoff
                       │          ▼
                       └──────► 2D CFAR ─► clustering/report
```

## Corrections relative to V2

- RFDC is **not** expected to produce tone/position metadata.
- TX and RX use one shared scheduler/context stream.
- Residual sub-band frequency is explicitly derotated before integration.
- Dwell integration and cross-sweep coherent averaging are separate.
- `dwell_samples` and `rx_discard_samples` are explicit.
- Acquisition waits for `system_ready = RFDC_READY && MTS_LOCKED && CLOCKS_LOCKED`.
- Sub-band retune uses `sb_req/sb_id/sb_ack`; `sb_ack` is only legal after both ADC and DAC NCO updates commit.
- Position capture uses `pos_req/pos_id/pos_ack`.
- HLS transaction control provides clean frame restart.
- AXI-Lite protocol handling comes from HLS-generated compliant slaves.
- Production RFDC width/sample adapters are explicit responsibilities of the verified base map.
- Migration is coherent complex Kirchhoff, not magnitude-only.
- DDR median background and hardware connected-component clustering are included.
- Xilinx XFFT remains the production IFFT.
- Vivado integration contains no silent `catch` on critical hierarchy wiring.

See `HYBRID_V3_CHANGES.md` and `GPR_ZCU208_IMPLEMENTATION_GUIDE.md`.

## Build

Static/model checks:

```bash
make lint
```

HLS + structural integration:

```bash
make step02_hls_scheduler
make step03_hls_rxextract
make step04_hls_sweepavg
make step05_hls_cal
make step06_hls_pad
make step07_hls_background
make step08_hls_power
make step09_hls_cfar1d
make step10_hls_imaging
make step11_collect_ip

make step12_vivado_project \
  BASE_XPR=/absolute/path/verified_zcu208_rfdc_mts.xpr

make step13_vivado_integrate \
  BASE_XPR=/absolute/path/verified_zcu208_rfdc_mts.xpr \
  INTEGRATION_MODE=external_ports
```

For production, edit `config/zcu208_gpr_bd_map.tcl` against the verified base and run mapped integration. The package intentionally refuses to guess RFDC/MTS/clock interface names.

## Internal IQ convention

Custom 32-bit complex streams use:

- `[15:0]` = signed I
- `[31:16]` = signed Q

The RFDC base must adapt its actual samples-per-clock and AXIS packing to this contract.

## Software / offline

The `software/offline` workstation from V2.1 remains included for NPZ/MAT/HDF5/UDP replay, calibration, background removal, migration, CFAR, classification scaffolding, A/B/C-scan and 3D visualization.
