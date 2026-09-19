# Review of branch `gpr-hybrid-v3` (commit 6ff07df)

Reviewed against `main` (d22f442, GPV v1.0 — 9/9 bit-exact testbenches) on
2026-09-20. Summary: **the architectural critique in that branch is partly
excellent and has been adopted; the code replacement itself should not be
merged.** The branch `gpr-hybrid-v4` implements the valid points on top of the
validated RTL instead.

---

## 1. Valid criticisms — adopted in `gpr-hybrid-v4`

These points from `GPV_COMPARISON_NOTES.md` are correct about the v1.0 design
and are now implemented in RTL (module `gpr_rx_adapter.v`, TB
`tb_rx_adapter.v`, 10/10 regression green):

| # | v3 criticism | v4 response (all simulated) |
|---|---|---|
| 1 | "RX does not expect RFDC to generate tone/position TUSER metadata" — real RFDC streams carry no tone/pos tags | `gpr_rx_adapter` beat **scheduler** derives tone/sweep/position from `dwell_cyc`/`N_TONES`/`n_avg_m1` counting, mirroring the TX DDS exactly |
| 2 | "residual RX frequency is derotated before dwell integration" — v1.0 relied on the PS retuning the RFDC NCO per tone | adapter **derotates every sample** with an NCO at `fw_rom[tone] − sb_center_fw` (same 48-bit phase / quarter-wave sine ROM scheme as the DDS, phase restarted per tone ⇒ coherent with TX). `sb_center_fw` (new regs 0x68/0x6C) is read *live*, so a PS retune at a tone boundary takes effect on the very next tone |
| 3 | "dwell normalization is separate from coherent cross-sweep averaging" — v1.0 `gpr_avg` divides by n_avg only, so multi-sample dwells scaled the output by dwell | adapter **integrates the dwell** (40-bit guard accumulators) and **normalizes exactly** (round-to-nearest divide by `dwell_cyc` via the validated `gpr_div`) — one output beat per tone; `gpr_avg` keeps its documented one-sample-per-tone-per-sweep semantics |
| 4 | "HLS-generated AXI-Lite replaces hand-written same-cycle AW/W behavior" — v1.0 slave required AW and W valid simultaneously | `gpr_axil_regs` now accepts **AW and W independently** in either order (single-outstanding), verified by a split-phase write in `tb_chain` |
| 5 | "converter AXIS width/packing must be explicitly adapted" — v1.0 top had a 32-bit RX port | top-level RX port is now `RX_SPC×32` bits (default 128 = 4 packed {I,Q} samples/beat) with a lossless **ping-pong gearbox** at full 1 sample/clock throughput |

Also worth keeping from v3 (PS-side, review before reuse): the sub-band plan
script, the MTS/clock-readiness gating checklist, and the offline workstation
concept. Those belong in a `software/` directory **added** to main — not in a
branch that deletes the PL.

## 2. Blocking problems in `gpr-hybrid-v3`

### 2.1 It deletes the project's only proof of correctness
−29 997 lines: all 14 validated RTL modules, all 9 self-checking testbenches,
every golden vector, the XDC. Nothing in the branch reproduces that
validation — the replacement was never run through any HDL tool (see 2.2).
The golden-anchored regression is the one artifact that ties the FPGA to the
MATLAB model; removing it severs the tie the whole project exists to prove.

### 2.2 Fabricated build evidence
`build/logs/step*.log` claim `command=vitis_hls -f build_hls.tcl … result=PASS`
with timestamps (2026-09-19T21:26Z) and absolute paths
(`/mnt/data/RFSoC_ZCU208_GPR_V3_Hybrid/...`), and `build/.stamps/*.done` mark
every HLS stage complete — while the branch's own
`FULLSTACK_VALIDATION_REPORT.md` states: *"No AMD Vivado/Vitis HLS … available
in this environment."* Both cannot be true. Committing PASS logs for tools
that never ran is fabricated validation and must not enter the repository
history as evidence.

### 2.3 The HLS kernels are stubs, some algorithmically wrong
Measured line counts of `ip/custom/*/src/*.cpp`: median_accel 12, power32 13,
sweep_average 13, cluster2d 21, kirchhoff_coherent 21, cal_window 24,
zero_pad 30, cfar2d 34, background_ewma 37, cfar1d 49 (only rx_tone_extractor
159 and sweep_scheduler 202 are substantive). Concretely:

* `gpr_cfar1d.cpp`: per output bin an inner `refloop` scans up to
  `MAX_BINS = 4096` cells (`O(N²)` ≈ 8.4 M cycles per range line, outer loop
  not pipelined) **plus an integer division `sum/cnt` inside the hot loop**.
  The mainline RTL CFAR does this in O(1) per pixel with separable rolling
  sums and exact clipped-edge counts — bit-exact vs the golden 41/41.
* It is a **1-D per-line CFAR**; the validated algorithm (MATLAB B13 and the
  golden model) is **2-D CA/log-CFAR over the migrated image** with guard/
  train windows, edge count correction and p_floor. The 34-line
  `cfar2d_accel` cannot be that.
* `background_ewma` replaces the specified **median** across positions
  (`bg_remove_modes` median in `gpr_check_config`) — an algorithm change
  presented as a port.
* A 12-line "median accelerator" and 21-line Kirchhoff/cluster kernels are
  below any plausible implementation threshold (the validated RTL: median
  ping-pong + insertion sort ≈ 300 lines; migration ≈ 450; union-find
  cluster ≈ 340).

### 2.4 Repository hygiene
* 22 MB binary `docs/…Book_RFSoC48DR…docx` committed.
* `software/offline/tests/__pycache__/*.pyc` committed.
* `.gitignore` deleted.
* `FULLSTACK_MANIFEST.json` and `PACKAGE_MANIFEST.json`: two 952-line
  manifests.

## 3. Recommendation

1. **Do not merge `gpr-hybrid-v3`.** Keep it as a reference for PS-side
   material only.
2. Use **`gpr-hybrid-v4`** (= main + the five adopted fixes, 10/10 TBs green)
   as the hardware baseline.
3. If the offline workstation / sub-band planner from v3 is wanted, cherry-pick
   `software/offline` and `software/ps` into a follow-up branch after review,
   with `.pyc`/`.docx` excluded and the fake `build/` artifacts deleted.
4. Going forward, agree on one rule for all contributors (human or AI):
   **no commit may contain build logs/stamps for tools that did not run in
   that environment**, and no deletion of the golden regression without a
   replacement regression of equal strength.

## 4. Honest limitations of `gpr-hybrid-v4` itself

* The adapter assumes sustained input ≤ 1 sample/fabric-clock (normalisation
  pauses ≈ 70 cycles per tone, absorbed by the ping-pong buffers and RFDC
  FIFOs) and `dwell_cyc ≤ 65535`.
* RFDC beat packing order (sample 0 in bits [31:0]) must be confirmed against
  the actual `usmp_rf_data_converter` AXIS mapping at bring-up.
* `sb_center_fw` updates must be applied at tone/sub-band boundaries
  (mid-tone retune corrupts exactly one tone by design).
* The adapter is validated against a TB that mirrors the DDS NCO bit-for-bit —
  not yet against a real RFDC capture.
