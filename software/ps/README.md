# PS software for the GPV PL chain

Role split (adapted from gpr-hybrid-v3 `software/ps/README.md`, retargeted to
the GPV RTL — see PROVENANCE.md for what changed and why):

The **PL** does all deterministic high-rate work: tone sequencing (DDS), RX
beat scheduling + residual derotation + dwell integration/normalisation
(`gpr_rx_adapter`), averaging, calibration, windowing, IFFT, background
median, migration, 2-D CFAR, clustering, and the report registers. The PL
scheduler is the single timing source — the PS never attaches metadata to
converter data.

The **PS** (R5 or A53 bare-metal / Linux) must:

1. bring up the ZCU208 from a *verified* RFDC/MTS base design and gate
   acquisition on `system_ready` (BRINGUP_GATES.md, gates 0–1);
2. serve the sub-band retune handshake: on `sb_req`, program **both** DAC and
   ADC mixer/NCO from one plan table, issue the deterministic mixer update
   event, then pulse `sb_ack` (gate 2); `gpr_subband_plan.py` generates the
   table and cross-checks the golden ROMs bit-exactly;
3. program the AXI-Lite configuration registers once per mode
   (`golden/regs_a.vh` / `regs_b.vh` carry the mode-A/B presets — same numbers
   the RTL regression uses);
4. cycle frames: `CTRL.run` → wait `irq` (`rep_done`) → read REP1–REP6 →
   W1C `IRQ` (skeleton: `gpr_ps_runtime.c`);
5. monitor STATUS (`bg_overrun`, `frame_count`) and the CNT_* test-point
   counters;
6. handle position/motion (until `pos_req`/`pos_ack` lands in the PL,
   positions free-run — see BRINGUP_GATES.md gate 5).

Files:

| File | Role |
|---|---|
| `gpr_subband_plan.py` | reference plan generator + **bit-exact ROM cross-check** (`--check-rom`, both modes PASS) |
| `gpr_ps_runtime.c` | BSP-independent orchestration skeleton (register map, retune service loop, frame cycle) |
| `BRINGUP_GATES.md` | fail-hard hardware bring-up sequence |
| `PROVENANCE.md` | what was adopted / adapted / rejected from `gpr-hybrid-v3` |
