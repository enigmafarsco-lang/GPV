# Hybrid V3 hardware addendum

This addendum supersedes the FPGA acquisition/integration details in the bundled v1.4 engineering book.

The physical/RF system description in the book remains useful, but the production FPGA flow is now:

1. verified XCZU48DR RFDC/MTS base;
2. shared sweep scheduler;
3. sub-band DAC/ADC NCO handshake;
4. PL residual TX DDS;
5. internally generated tone/position context;
6. RX residual derotation;
7. dwell integration;
8. coherent sweep averaging;
9. calibration × Kaiser;
10. zero-pad + Xilinx IFFT;
11. streaming EWMA or DDR median background removal;
12. coherent complex Kirchhoff migration;
13. 2-D CFAR;
14. connected-component clustering/report;
15. DMA/offline A/B/C-scan and 3-D workstation.

The scheduler also includes `pos_req/pos_id/pos_ack`; field acquisition must not advance to a new spatial sample until the motion/navigation system confirms the position.
