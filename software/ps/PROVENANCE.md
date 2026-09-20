# Provenance — cherry-pick from `gpr-hybrid-v3` (option 2 of the review)

Source: branch `gpr-hybrid-v3` (commit 6ff07df), reviewed 2026-09-20
(see `REVIEW_HYBRID_V3.md` at the repository root). Only PS-side material was
considered; the branch's PL replacement (HLS stubs, deleted RTL/TB/goldens,
fabricated `build/` PASS logs) was **not** cherry-picked.

## Adopted (concept), rewritten for the GPV architecture

| v3 source | What was kept | What changed and why |
|---|---|---|
| `GPR_ZCU208_IMPLEMENTATION_GUIDE.md` §1, §3, §4, §5 | verified-base-design rule; `system_ready = RFDC & MTS & clocks`; 6-step deterministic retune sequence; position-gating concept; RX drain/discard/derotate/average discipline | → `BRINGUP_GATES.md`, retargeted to GPV signals (`sb_req/sb_ack` exist in `gpr_top_zcu208`; `pos_req/pos_ack` documented as the next RTL extension; added the GPV-specific loopback and single-sub-band gates 3–4) |
| `HYBRID_V3_RUNTIME.md` | sub-band-major scheduling rationale; "PS never attaches metadata"; mixer update event before `sb_ack` | merged into `BRINGUP_GATES.md` + `README.md`; their scheduler/pos_id stream terminology replaced by the actual `gpr_rx_adapter` interface |
| `gpr_rfsoc_runtime_v3.c` | service-loop contract: readiness gate, sb_req→program→ack with explicit ack-low/ack-high pulse, hooks-not-addresses discipline | → `gpr_ps_runtime.c`, retargeted to the GPV register map (0x00–0x94 incl. SB_CENTER_FW 0x68/0x6C), IRQ/REP frame cycle, `bg_overrun` monitoring |
| `gpr_subband_plan.py` | CLI shape; "one table for DAC and ADC"; 48-bit phase-word output; JSON plan | math **re-aligned from their uniform `tones_per_subband` scheme to `make_golden.m`** (span = F_CLK/2, LO = band centre, residual beat words, stable sub-band sort, `sb_ends`), MATLAB-compatible rounding, plus the new `--check-rom` mode: bit-exact vs `fw_seq/tidx_seq/sb_ends` for **both** golden modes (PASS) |

## Rejected

| v3 material | Reason |
|---|---|
| `gpr_rfsoc_runtime.c` (per-tone version) | per-tone mixer retune (256/sweep at 50 µs dwell) contradicts the sub-band plan their own docs advocate; superseded by the sub-band service loop |
| `software/ps/README.md` items 3–7 (HLS AXI-Lite controls, `S_AXIS_CAL_COEF` DMA, DDR-based migration/CFAR launch, EWMA) | describe the v3 HLS architecture that does not exist in GPV; the GPV chain is fully in-PL with the register map in the root README |
| `build/.stamps/*`, `build/logs/*` | fabricated PASS evidence for `vitis_hls` runs that the branch's own validation report says could not have happened — must never be committed |
| `docs/…Book_RFSoC48DR…docx` (22 MB), `software/offline/tests/__pycache__/*.pyc` | binary/bloat artifacts; excluded by policy |
| `software/offline/` workstation | not reviewed in depth; potentially useful later, but it depends on the v3 pipeline semantics (EWMA, 1-D CFAR) — keep on the v3 branch until someone ports it against the validated GPV algorithms |

## Findings surfaced by this cherry-pick

1. **`SB_CENTER_FW` semantics corrected.** `make_golden.m` bakes `fw_seq`
   ROMs with **residual (beat) words** (`fw = f_tone − LO`), so the v4
   adapter's `fw_rom[tone] − sb_center_fw` means `SB_CENTER_FW` is a
   *correction offset, nominally 0* — not the LO itself. Docs in
   `rtl/gpr_rx_adapter.v` and the root README are fixed on this branch; the
   runtime skeleton writes 0 at every retune unless the PS knows a real Δf.
2. **`make_golden.m` hardcodes `NT = 256` for both modes**, while
   `config_mode_B_ground_deep.m` specifies 512 tones. The golden B ROMs are
   therefore 256-tone. `gpr_subband_plan.py` documents this and matches the
   shipped goldens; if make_golden is ever changed to honour `cfg.n_tones`,
   the mode-B preset (and an `N_TONES=512` RTL build) must follow.
