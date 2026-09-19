# PS/R5/A53 runtime role

The PL hierarchy does deterministic high-rate work. The PS must:

1. configure ZCU208 RFDC/MTS using the **actual XSA/BSP**;
2. keep ADC DDC and DAC DUC/NCO on the same SFCW frequency plan;
3. program HLS AXI-Lite controls (tone count, dwell samples, FFT length, EWMA, CFAR);
4. circulate calibration/window coefficients to `S_AXIS_CAL_COEF`;
5. DMA range IQ/power/CFAR streams to DDR;
6. assemble B-scans with position/GNSS metadata;
7. launch the DDR-based migration and 2-D CFAR accelerators, or execute the equivalent CPU/GPU algorithms;
8. build C-scans/3-D products, network/record results, and feed the monitoring GUI.

`gpr_rfsoc_runtime.c` is a BSP-dependent orchestration skeleton, not a hard-coded register map.
