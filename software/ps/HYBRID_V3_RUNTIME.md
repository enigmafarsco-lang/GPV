# Hybrid V3 RFSoC runtime

The PS/R5 is no longer expected to attach tone/position metadata to RFDC data. The PL scheduler is the single timing source.

The scheduler is sub-band-major: all coherent averages for one sub-band are acquired before the next RFDC retune.

For every sub-band transition:
1. `sb_req` rises with `sb_id`.
2. R5 programs **both** DAC and ADC RFDC mixer/NCO settings.
3. R5 performs the mixer update event required by the verified MTS base.
4. Only after the deterministic update boundary does it pulse `sb_ack`.

For every scan position:
1. `pos_req` rises with `pos_id`.
2. Encoder/GNSS/UAV control confirms the requested spatial sample.
3. R5 pulses `pos_ack`.
4. The scheduler executes all averages and tones for that position.

`system_ready` must be the logical AND of RFDC readiness, MTS lock and required clock locks.

## RX extraction

The RX extractor consumes exactly `dwell_samples_total` converter samples per tone:
- first `rx_discard_samples` are ignored for RFDC/filter/analog settling;
- the remainder are multiplied by the conjugate residual DDS reference;
- the derotated complex values are averaged to one `H(f_k,x,sweep)` sample;
- the sweep averager then coherently averages `n_averages`.

This fixes the cancellation that occurs if residual sub-band frequency is integrated without derotation.

The RX extractor drains and drops RFDC samples when no tone context is active. This prevents stale/free-running converter data from accumulating ahead of the next scheduled tone.
