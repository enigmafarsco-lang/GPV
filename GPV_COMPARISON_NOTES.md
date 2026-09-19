# GPV comparison notes used for Hybrid V3

Compared against `enigmafarsco-lang/GPV` main at commit `d22f442513955d059920798f1cbce6998b4d522b` (19 September 2026).

Ideas adopted:
- sub-band RFDC mixer plan plus PL residual DDS;
- bit-accurate/fixed-point validation philosophy;
- coherent complex migration rather than magnitude-only focusing;
- 2-D image CFAR and connected-component reporting;
- explicit internal loopback/visibility philosophy.

Issues deliberately corrected in Hybrid V3:
- RX does not expect RFDC to generate tone/position TUSER metadata;
- residual RX frequency is derotated before dwell integration;
- dwell normalization is separate from coherent cross-sweep averaging;
- frame acquisition is restartable through HLS control;
- position is externally gated;
- HLS-generated AXI-Lite replaces hand-written same-cycle AW/W behavior;
- production RFDC/MTS mapping remains fail-hard against a verified base;
- converter AXIS width/packing must be explicitly adapted;
- MTS/clock/RFDC readiness gates scheduler start.
