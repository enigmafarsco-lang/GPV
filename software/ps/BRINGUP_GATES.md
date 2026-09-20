# ZCU208 bring-up gates (adopted from gpr-hybrid-v3, retargeted to GPV RTL)

Fail-hard ordering for hardware bring-up. Each gate must be demonstrated
before the next is attempted; none of them may be bypassed with silent
error handling.

## Gate 0 — Verified RFDC/MTS base design

Start from a ZCU208 project in which converter clocks, DAC/ADC tiles,
DUC/DDC, mixer update events and Multi-Tile Synchronization have **already
been demonstrated on the physical board** (vendor base design or your own
verified project). Clone that `.xpr`, then integrate the GPV hierarchy
(`scripts/vivado_build.tcl` FULL flow instantiates into exactly this shape).
Do not let any integration script hide connection failures behind Tcl
`catch` — validate the BD and fix every reported issue.

## Gate 1 — system_ready

```
system_ready = RFDC_READY  &  MTS_LOCKED  &  CLOCKS_LOCKED
```

* `RFDC_READY`: `XRFdc_CheckIpReady` / driver init succeeded for the tiles
  in use (ADC tile 224, DAC tile 224 in the reference build).
* `MTS_LOCKED`: multi-tile sync done and reported locked (ADC and DAC MTS
  groups as applicable).
* `CLOCKS_LOCKED`: LMK04828/SI5328 locked (refclk 122.88 MHz), PL fabric
  clock locked at 245.76 MHz (SI570 or clk_wiz per xdc/zcu208.xdc notes).

The acquisition loop (`gpr_ps_runtime.c: gpr_run_frame`) refuses to write
`CTRL.run` until this gate passes.

## Gate 2 — deterministic sub-band retune (per `sb_req`)

Sequence for every sub-band transition (21 per mode-A sweep):

1. PL scheduler asserts `sb_req` with the sub-band id at a tone boundary and
   holds the TX sequence there.
2. PS programs the **DAC** mixer/NCO for the sub-band LO
   (`XRFdc_SetMixerSettings`).
3. PS programs the **ADC** mixer/NCO to the **same** LO plan
   (`gpr_subband_plan.py` prints `lo_hz` per sub-band; both directions must
   use one table).
4. PS issues the mixer **update event** required by the verified base
   (`XRFdc_Update_Event` / MTS-style deterministic boundary) — a register
   write alone does **not** imply phase-coherent retuning.
5. Only after the update boundary commits: pulse `sb_ack`.
6. If the PS additionally knows the real mixer centre deviates from the plan
   LO by Δf, write Δf/F_CLK·2^48 to `SB_CENTER_FW` (0x68/0x6C) — the golden
   `fw_seq` ROMs already contain residual (beat) words, so the nominal value
   is 0 and the adapter computes `fw_rom[tone] − SB_CENTER_FW`.

## Gate 3 — loopback smoke test (no RF)

With `loopback = 1` (BD bring-up port or `CTRL.loop_mode`): the chain must
reproduce the `tb_chain` result on hardware — constant loopback ⇒ median
background removal cancels everything ⇒ REP1 = REP2 = 0, all CNT_* counters
exact (256 / 8 / 512 / 512 / 512 / 512 at the TB parameter set, scaled by
the programmed config), IRQ fires per frame. Any counter mismatch is a
fabric/clock-domain defect, not an RF issue — fix before enabling RF.

## Gate 4 — single sub-band RF loop

Program one sub-band, run one frame with the RX port connected (cable from
DAC to ADC through an attenuator). Check: CNT_ADC advances at the expected
rate, `gpr_rx_adapter` output amplitude is consistent across tones of the
sub-band (residual derotation working: flat response, no fan-shaped loss at
sub-band edges), and the tone at the sub-band centre has maximum SNR.

## Gate 5 — full sweep + position gating

Full 21-sub-band mode-A sweep. Recommended (not yet in RTL): a `pos_req` /
`pos_ack` handshake so the motion controller gates each position (encoder /
GNSS / UAV confirmation). Until that lands, positions advance open-loop from
the scheduler — tie the bench setup to a fixed position trigger, and treat
`pos_ack` gating as the first field-deployment RTL extension. Static bench:
positions may free-run.

## Known PS-side duties (from the v3 review, still true)

* Keep ADC DDC and DAC DUC NCOs on the **same** frequency plan table
  (generated once by `gpr_subband_plan.py`, not recomputed ad hoc).
* Service `sb_req` within one sub-band boundary budget: at 50 µs dwell and
  ~12 tones per sub-band the PS has ≈ 600 µs per retune — measure
  `XRFdc_SetMixerSettings` + update-event latency on the actual base design
  before field scans.
* Read `STATUS.bg_overrun` (bit 24) after every frame; a set bit means the
  background RAM could not keep up — reduce frame rate, not `nbg`.
* Adapter assumptions to respect: sustained RX ≤ 1 sample/fabric clock,
  `DWELL_CYC ≤ 65535`, retunes only at tone boundaries.
