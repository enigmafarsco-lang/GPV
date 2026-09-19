# DOA BuildKit -> GPR Hybrid V3 mapping

The supplied DOA build kit remains the structural reference for restartable packaging, independent HLS stages, Vivado integration, synthesis/implementation gates, XSA export and HIL.

| DOA concept | Hybrid V3 GPR counterpart |
|---|---|
| deterministic RFSoC capture timing | shared SFCW sweep scheduler |
| channel/reference coherence | shared TX residual DDS + RX conjugate residual derotation |
| frame accumulation | dwell integration then coherent sweep averaging |
| calibration preprocessing | complex inverse system response × Kaiser coefficient |
| frequency-domain frame | SFCW tone vector |
| transform/search path | zero-pad + Xilinx IFFT + range IQ |
| candidate path | 1-D diagnostic CFAR and 2-D image CFAR |
| spatial estimator | coherent complex Kirchhoff migration |
| candidate grouping/report | 2-D connected components + report buffer |
| R5/A53 orchestration | RFDC/MTS retune, position gating, DMA, metadata, B/C-scan, storage/network |
| verified RFDC base project | mandatory `BASE_XPR` |
| HIL | MATLAB sweep plan + synthetic target vectors + offline replay |
| build restartability | stamped Make stages with per-stage logs |

Board-specific RFDC tile, clock and MTS settings remain outside the reusable algorithm hierarchy and are mapped only in `config/zcu208_gpr_bd_map.tcl`.
