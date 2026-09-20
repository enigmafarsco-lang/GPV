#!/usr/bin/env python3
"""Sub-band tone plan for the GPV RFSoC chain - reference + ROM cross-check.

Mirrors the plan baked by golden/make_golden.m (which is the source of
truth, derived from the GPM MATLAB package):

    f_k      = f_start + k*df,  df = (f_stop-f_start)/(n_tones-1)
    span     = F_CLK/2                      (+-122.88 MHz around each LO)
    n_sb     = ceil((f_stop-f_start)/span)
    sb(k)    = min(n_sb, floor((f_k-f_start)/span) + 1)     [1-based]
    order    = stable sort of tones by sub-band (keeps f order inside)
    lo(s)    = f_start + (s-1)*span + span/2                [RFDC mixer centre]
    beat     = f_k(seq) - lo(sb)                            |beat| <= span/2
    fw       = mod(round(beat/F_CLK * 2^48), 2^48)          [DDS/NCO word]

The fw_seq ROM therefore contains RESIDUAL (beat) words, already relative to
the sub-band LO.  Consequence for the PL RX derotator (gpr_rx_adapter):
SB_CENTER_FW (regs 0x68/0x6C) is a CORRECTION offset, normally 0 - write
non-zero only if the actual RFDC mixer centre deviates from lo(s) by delta
(then write delta/F_CLK*2^48, since the adapter computes fw_rom - correction).

Usage:
    python3 gpr_subband_plan.py --mode a --check-rom ../../golden
    python3 gpr_subband_plan.py --mode b --out plan_b.json

Concept and CLI shape adapted from gpr-hybrid-v3 software/ps/gpr_subband_plan.py
(their uniform tones_per_subband scheme is NOT what the golden ROMs use; the
math above is aligned to make_golden.m instead).
"""
import argparse
import json
import math
import os
import sys

F_CLK = 245_760_000.0     # fabric/RFDC AXIS clock [Hz]
FW_BITS = 48

MODES = {
    "a": dict(f_start=500e6, f_stop=3000e6, n_tones=256),   # UAV shallow
    # NOTE: config_mode_B_ground_deep.m specifies 512 tones, but make_golden.m
    # hardcodes NT=256 for BOTH modes - the shipped golden B ROMs are 256-tone.
    # Keep this preset aligned with the GOLDEN files; if make_golden is ever
    # changed to use cfg.n_tones, set n_tones=512 here.
    "b": dict(f_start=10e6,  f_stop=100e6,  n_tones=256),   # ground deep
}


def matlab_round(x):
    """MATLAB/Octave round(): half away from zero (Python's is banker's)."""
    return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)


def make_plan(f_start, f_stop, n_tones, f_clk=F_CLK):
    span = f_clk / 2.0
    df = (f_stop - f_start) / (n_tones - 1)
    n_sb = math.ceil((f_stop - f_start) / span)

    fk = [f_start + k * df for k in range(n_tones)]
    sb = [min(n_sb, int((f - f_start) // span) + 1) for f in fk]

    order = sorted(range(n_tones), key=lambda k: sb[k])      # stable
    tones = []
    for seq, k in enumerate(order):
        s = sb[k]
        lo = f_start + (s - 1) * span + span / 2.0
        beat = fk[k] - lo
        fw = int(matlab_round(beat / f_clk * (2 ** FW_BITS))) % (2 ** FW_BITS)
        tones.append(dict(seq=seq, tone=k, subband=s - 1, rf_hz=fk[k],
                          lo_hz=lo, beat_hz=beat, fw_word48=fw))

    sb_ends, c = [], 0
    for s in range(1, n_sb + 1):
        c += sum(1 for k in range(n_tones) if sb[k] == s)
        sb_ends.append(c - 1)

    subbands = []
    for s in range(n_sb):
        lo = f_start + s * span + span / 2.0
        subbands.append(dict(
            subband=s, lo_hz=lo,
            rfdc_mixer_hz=lo,             # XRFdc_SetMixerSettings target
            sb_center_fw_word48=0,        # correction offset, normally 0
            last_seq=sb_ends[s]))
    return dict(f_clk_hz=f_clk, df_hz=df, span_hz=span, n_sb=n_sb,
                n_tones=n_tones, sb_ends=sb_ends, subbands=subbands,
                plan=tones)


def read_hex_words(path, per_line=None):
    words = []
    with open(path) as f:
        for line in f:
            line = line.split("//")[0].strip()
            if not line:
                continue
            for tok in line.split():
                words.append(int(tok, 16))
    return words


def check_rom(plan, romdir, tag):
    """Bit-exact cross-check against the golden ROM images."""
    ok = True
    fw = read_hex_words(os.path.join(romdir, f"fw_seq_{tag}.hex"))
    tidx = read_hex_words(os.path.join(romdir, f"tidx_seq_{tag}.hex"))
    sbe = read_hex_words(os.path.join(romdir, f"sb_ends_{tag}.hex"))

    exp_fw = [t["fw_word48"] for t in plan["plan"]]
    exp_tidx = [t["tone"] for t in plan["plan"]]
    for name, got, exp in (("fw_seq", fw, exp_fw), ("tidx_seq", tidx, exp_tidx),
                           ("sb_ends", sbe, plan["sb_ends"])):
        if got == exp:
            print(f"  {name}_{tag}.hex: {len(exp)} words EXACT")
        else:
            ok = False
            bad = [i for i, (g, e) in enumerate(zip(got, exp)) if g != e]
            print(f"  {name}_{tag}.hex: MISMATCH at {len(bad)} entries "
                  f"(first: idx {bad[0] if bad else '?'} "
                  f"got {got[:len(exp)] and (got[bad[0]] if bad else None)} "
                  f"want {exp[bad[0]] if bad else None})" if bad else
                  f"  {name}_{tag}.hex: LENGTH mismatch got {len(got)} want {len(exp)}")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mode", choices=sorted(MODES), default="a")
    ap.add_argument("--f-start", type=float)
    ap.add_argument("--f-stop", type=float)
    ap.add_argument("--tones", type=int)
    ap.add_argument("--out", help="write full plan JSON here")
    ap.add_argument("--check-rom", metavar="GOLDEN_DIR",
                    help="cross-check fw/tidx/sb_ends ROM images (bit-exact)")
    a = ap.parse_args()

    m = MODES[a.mode]
    plan = make_plan(a.f_start or m["f_start"], a.f_stop or m["f_stop"],
                     a.tones or m["n_tones"])
    print(f"mode {a.mode}: {plan['n_tones']} tones, df={plan['df_hz']:.1f} Hz, "
          f"n_sb={plan['n_sb']}, span={plan['span_hz']/1e6:.2f} MHz")
    for s in plan["subbands"]:
        print(f"  sb{s['subband']:02d}: LO={s['lo_hz']/1e6:10.3f} MHz  "
              f"last_seq={s['last_seq']}")
    if a.out:
        with open(a.out, "w") as f:
            json.dump(plan, f, indent=1)
        print(f"written: {a.out}")
    if a.check_rom:
        ok = check_rom(plan, a.check_rom, a.mode)
        print("ROM check:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
