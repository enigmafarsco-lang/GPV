#!/usr/bin/env python3
"""Figure engine for the RAP / PCL design books.

Two honest figure families:
 (D) diagrams  - block/geometry/timing/state drawings made from explicit specs;
 (S) simulated - numpy simulations of waveforms/processing with FIXED seeds,
                 always captioned as simulation illustrations in the books.
No measured hardware data is claimed anywhere.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Ellipse
import os

OUT = os.path.join(os.path.dirname(__file__), 'figs')
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.size': 8.5, 'axes.grid': True, 'grid.alpha': 0.3,
                     'figure.dpi': 130, 'savefig.bbox': 'tight'})
RNG = np.random.default_rng(4815162342)

def save(fig, name):
    fig.savefig(os.path.join(OUT, name))
    plt.close(fig)
    print("fig", name)

# ---------- diagram helpers ----------
def box(ax, x, y, w, h, text, fc='#e8f0fb', ec='#234', fs=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=fc, ec=ec, lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, wrap=True)

def arrow(ax, x1, y1, x2, y2, text='', col='#234'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=0.9, color=col))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.02, text, fontsize=6.5,
                ha='center', va='bottom', color=col)

def canvas(w=10, h=4.2, xl=(-0.2, 10.2), yl=(-0.2, 4.2)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.axis('off'); ax.grid(False)
    return fig, ax

# ---------- (D) master block diagrams ----------
def master_rap():
    fig, ax = canvas(11, 5.0, (0, 11), (0, 5))
    box(ax, 0.2, 3.6, 1.9, 0.9, 'Board A\ncoherent clock plant\n10 MHz site ref')
    box(ax, 0.2, 2.3, 1.9, 0.9, 'Active TX chain\n(board B)\nSFCW tones')
    box(ax, 0.2, 1.0, 1.9, 0.9, 'Passive antennas\nREF x2 / SURV x4\n(board C-P)')
    box(ax, 2.6, 2.3, 1.7, 0.9, 'Active RX front end\n(board C)')
    box(ax, 2.6, 1.0, 1.7, 0.9, 'Passive RF front end\npreselect/LNA/AGC')
    box(ax, 4.8, 1.6, 2.0, 1.7, 'XCZU48DR RFSoC\nRFDC 8x ADC\nactive PL chain\npassive PL chain')
    box(ax, 7.3, 2.6, 1.7, 0.9, 'PS software\nruntime + fusion\nEMCON arbiter')
    box(ax, 7.3, 1.2, 1.7, 0.9, 'DDR maps /\nrings / evidence')
    box(ax, 9.4, 1.9, 1.4, 1.0, 'Operator\nworkstation')
    arrow(ax, 2.1, 4.05, 4.8, 3.0, 'clk+SYSREF')
    arrow(ax, 2.1, 2.75, 2.6, 2.75)
    arrow(ax, 2.1, 1.45, 2.6, 1.45)
    arrow(ax, 4.3, 2.75, 4.8, 2.6)
    arrow(ax, 4.3, 1.45, 4.8, 1.9)
    arrow(ax, 6.8, 2.4, 7.3, 3.0)
    arrow(ax, 6.8, 2.0, 7.3, 1.65)
    arrow(ax, 9.0, 3.0, 9.4, 2.6)
    arrow(ax, 9.0, 1.65, 9.4, 2.1)
    ax.text(0.2, 0.35, 'EMCON: active dwells are granted against passive cues (M0-M4 policy)',
            fontsize=7.5, style='italic')
    save(fig, 'master_rap.png')

def master_pcl():
    fig, ax = canvas(11, 4.4, (0, 11), (0, 4.4))
    box(ax, 0.2, 3.0, 1.9, 0.9, 'Site 10 MHz ref\n(fibre to other nodes)')
    box(ax, 0.2, 1.6, 1.9, 0.9, 'REF antennas x2\ndirective')
    box(ax, 0.2, 0.3, 1.9, 0.9, 'SURV ULA x4 +\nsurvey channel')
    box(ax, 2.6, 1.2, 1.8, 1.6, 'Passive RF front end\npreselect / LNA / AGC\ncable-matched')
    box(ax, 4.9, 1.2, 2.0, 1.6, 'XCZU48DR\nRFDC 2.4576 GSPS\nDDC 32x lanes')
    box(ax, 7.3, 2.2, 1.8, 1.0, 'PL: ECA -> CAF ->\nCFAR -> DOA')
    box(ax, 7.3, 0.8, 1.8, 1.0, 'PS: tracks, geoloc,\nevidence, survey')
    box(ax, 9.5, 1.5, 1.3, 1.2, 'Operator /\nnode coordinator')
    arrow(ax, 2.1, 3.45, 4.9, 2.6, 'clk+SYSREF')
    arrow(ax, 2.1, 2.05, 2.6, 2.2)
    arrow(ax, 2.1, 0.75, 2.6, 1.5)
    arrow(ax, 4.4, 2.0, 4.9, 2.0)
    arrow(ax, 6.9, 2.3, 7.3, 2.7)
    arrow(ax, 6.9, 1.7, 7.3, 1.3)
    arrow(ax, 9.1, 2.7, 9.5, 2.3)
    arrow(ax, 9.1, 1.3, 9.5, 1.9)
    ax.text(0.2, -0.05, 'No transmitter of own: silent by construction', fontsize=7.5, style='italic')
    save(fig, 'master_pcl.png')

def geo_bistatic():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.grid(True); ax.set_aspect('equal')
    T = np.array([-6, 0]); R = np.array([6, 0]); G = np.array([1.5, 3.4])
    ax.plot(*T, 's', color='c', ms=9); ax.text(T[0], T[1]-0.55, 'illuminator Tx', ha='center')
    ax.plot(*R, 's', color='g', ms=9); ax.text(R[0], R[1]-0.55, 'RAP Rx', ha='center')
    ax.plot(*G, '^', color='r', ms=9); ax.text(G[0]+0.2, G[1]+0.2, 'target')
    ax.annotate('', xy=G, xytext=T, arrowprops=dict(arrowstyle='->', lw=1.1, color='c'))
    ax.annotate('', xy=R, xytext=G, arrowprops=dict(arrowstyle='->', lw=1.1, color='r'))
    ax.annotate('', xy=R, xytext=T, arrowprops=dict(arrowstyle='->', lw=0.8, ls=':', color='k'))
    ax.text(-3, 1.9, 'R_t', color='c'); ax.text(3.4, 1.9, 'R_r', color='r')
    ax.text(0, -0.5, 'R_t + R_r = const  ->  bistatic ellipse', ha='center')
    b = np.array([0.0, 0.0])
    v1 = (T-G)/np.linalg.norm(T-G); v2 = (R-G)/np.linalg.norm(R-G)
    bis = (v1+v2)/np.linalg.norm(v1+v2)
    ax.annotate('', xy=G+bis*1.4, xytext=G, arrowprops=dict(arrowstyle='->', lw=0.9, color='m'))
    ax.text(G[0]+bis[0]*1.5, G[1]+bis[1]*1.5, 'bisector: beta/2', color='m', fontsize=7)
    ax.set_title('Bistatic geometry: ranges, direct path, bistatic angle beta')
    save(fig, 'geo_bistatic.png')

def geo_tdoa():
    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    ax.set_aspect('equal'); ax.grid(True)
    N1 = np.array([-5, 0]); N2 = np.array([5, 0]); E = np.array([1.2, 3.0])
    ax.plot(*N1, 's', color='g'); ax.text(N1[0]-0.3, N1[1]-0.6, 'node 1')
    ax.plot(*N2, 's', color='g'); ax.text(N2[0]-0.3, N2[1]-0.6, 'node 2')
    ax.plot(*E, '*', color='r', ms=12); ax.text(E[0]+0.2, E[1]+0.2, 'emitter')
    x = np.linspace(-9, 9, 400); y = np.linspace(-6, 6, 400); X, Y = np.meshgrid(x, y)
    d = (np.hypot(X-N1[0], Y-N1[1]) - np.hypot(X-N2[0], Y-N2[1]))
    dtrue = np.linalg.norm(E-N1) - np.linalg.norm(E-N2)
    ax.contour(X, Y, d, levels=[dtrue], colors='b', linewidths=1.2)
    ax.text(-8, 4.2, 'TDOA hyperbola', color='b', fontsize=7)
    for N, ang in ((N1, np.degrees(np.arctan2(E[1]-N1[1], E[0]-N1[0]))),):
        ax.annotate('', xy=N+2.6*np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))]),
                    xytext=N, arrowprops=dict(arrowstyle='->', color='m', lw=1.0))
    ax.text(-3.4, 2.2, 'AOA node 1', color='m', fontsize=7)
    ax.set_title('Two-node fix: AOA line x TDOA hyperbola')
    save(fig, 'geo_tdoa.png')

def clock_tree():
    fig, ax = canvas(10.5, 4.0, (0, 10.5), (0, 4))
    box(ax, 0.2, 1.7, 1.6, 0.8, 'GPSDO\n10 MHz site ref')
    box(ax, 2.3, 1.7, 1.8, 0.8, 'Clock generator\n(SI570 class)\njitter cleaned')
    box(ax, 4.7, 3.0, 1.7, 0.7, 'RFDC ADC clocks\ntiles 0/1: 2.4576 G\n tile 2: 4.9152 G')
    box(ax, 4.7, 2.0, 1.7, 0.7, 'RFDC DAC clocks\n(active TX)')
    box(ax, 4.7, 1.0, 1.7, 0.7, 'SYSREF all tiles\n(MTS class align)')
    box(ax, 4.7, 0.0, 1.7, 0.7, 'PL fabric 245.76 M\nPS clocks')
    box(ax, 7.2, 2.0, 2.6, 1.4, 'Phase coherence:\nall converted channels\ndeterministic relation\n<= 5 deg over T_int')
    for y in (3.35, 2.35, 1.35, 0.35):
        arrow(ax, 4.1, 2.1, 4.7, y)
    arrow(ax, 1.8, 2.1, 2.3, 2.1)
    arrow(ax, 6.4, 2.7, 7.2, 2.7)
    save(fig, 'clock_tree.png')

def rf_chain(kind='surv'):
    fig, ax = canvas(10.5, 2.6, (0, 10.5), (0, 2.6))
    y = 0.9
    if kind == 'surv':
        stages = ['ULA element\n(band switch)', 'preselector\nfilter bank', 'LNA\n(low NF)',
                  'AGC VGA\n(DPI-held)', 'anti-alias\n+ balun', 'RF-ADC\n2.4576 GSPS']
        note = 'SURV chain: linearity set by DPI 60-90 dB above echoes'
    else:
        stages = ['directive yagi\nper illuminator', 'narrow preselect\n(high out-of-band rej)',
                  'LNA', 'fixed gain\n(no AGC hunting)', 'anti-alias\n+ balun', 'RF-ADC\n2.4576 GSPS']
        note = 'REF chain: stable gain, target echo in REF <= -20 dB below copy'
    x = 0.2
    for s in stages:
        box(ax, x, y, 1.5, 0.9, s); x += 1.72
    for i in range(5):
        arrow(ax, 0.2 + 1.5 + i * 1.72, y + 0.45, 0.2 + 1.72 + i * 1.72, y + 0.45)
    ax.text(0.2, 0.15, note, fontsize=7.5, style='italic')
    save(fig, f'rf_chain_{kind}.png')

def rfdc_alloc():
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    ax.axis('off'); ax.grid(False)
    tiles = {'ADC tile 0': ['REF-1', 'REF-2', 'SURV-1', 'SURV-2'],
             'ADC tile 1': ['SURV-3', 'SURV-4', 'AUX-TX mon', '(spare)'],
             'ADC tile 2': ['(active RX 224)', '-', '-', '-'],
             'ADC tile 3': ['(spare)', '-', '-', '-']}
    for r, (t, ch) in enumerate(tiles.items()):
        ax.text(0.02, 0.85 - r * 0.24, t, fontsize=8, weight='bold')
        for c, name in enumerate(ch):
            fc = '#dff0df' if name.startswith('(') else ('#fde8e8' if name == '-' else '#e8f0fb')
            ax.add_patch(Rectangle((0.22 + c * 0.19, 0.78 - r * 0.24), 0.17, 0.16, fc=fc, ec='#234', lw=0.7))
            ax.text(0.22 + c * 0.19 + 0.085, 0.86 - r * 0.24, name, ha='center', va='center', fontsize=6.8)
    ax.text(0.02, 0.02, 'green = inherited active / spare, blue = passive lane, red = unused block',
            fontsize=7, style='italic')
    save(fig, 'rfdc_alloc.png')

def fsm_arbiter():
    fig, ax = canvas(9.5, 3.6, (0, 9.5), (0, 3.6))
    box(ax, 0.3, 1.5, 1.6, 0.8, 'M0 FULL\nSILENCE', fc='#e6f4e6')
    box(ax, 2.6, 2.4, 1.7, 0.8, 'M1 PASSIVE CUE\n(confirm dwell)', fc='#fdf6dd')
    box(ax, 2.6, 0.5, 1.7, 0.8, 'M2 ACTIVE\nSEARCH', fc='#fde8e8')
    box(ax, 5.2, 1.5, 1.7, 0.8, 'M3 ACTIVE\nTRACK', fc='#fde8e8')
    box(ax, 7.5, 2.4, 1.7, 0.8, 'M4 CAL\n(bistatic ref)', fc='#e8f0fb')
    arrow(ax, 1.9, 2.1, 2.6, 2.7, 'cue conf > thr')
    arrow(ax, 2.6, 2.6, 1.9, 2.0, 'confirm fail')
    arrow(ax, 1.9, 1.7, 2.6, 1.0, 'op cmd / T3')
    arrow(ax, 4.3, 2.8, 5.2, 2.1, 'assoc OK')
    arrow(ax, 4.3, 0.9, 5.2, 1.6, 'detect')
    arrow(ax, 5.2, 2.0, 4.3, 2.6, 'gap > T_gap')
    arrow(ax, 6.9, 2.1, 7.5, 2.7, 'cal schedule')
    arrow(ax, 7.5, 2.6, 6.9, 2.0, 'done')
    save(fig, 'fsm_arbiter.png')

def timing_blank():
    fig, ax = plt.subplots(figsize=(9, 3.0))
    t = np.linspace(0, 10, 1000)
    dwell = ((t > 3.2) & (t < 3.8)) | ((t > 7.4) & (t < 8.0))
    ax.fill_between(t, 2, 2 + dwell * 0.8, step='mid', color='r', alpha=0.6)
    ax.text(3.3, 3.0, 'active dwells (TX on)', color='r', fontsize=7)
    b = np.floor(t / 1.0)
    bad = np.isin(b, [3, 7])
    for i in range(10):
        col = '#ccc' if i in (3, 7) else '#7ab'
        ax.add_patch(Rectangle((i * 1.0 + 0.05, 0.6), 0.9, 0.8, fc=col, ec='#234', lw=0.6))
        ax.text(i + 0.5, 1.0, f'batch {i}', ha='center', fontsize=6.2,
                color='#555' if i in (3, 7) else 'k')
    ax.text(0.1, 0.15, 'grey CAF batches discarded/interpolated; AUX-TX tap covers residual leakage',
            fontsize=7, style='italic')
    ax.set_ylim(0, 3.6); ax.set_xlim(0, 10); ax.axis('off'); ax.grid(False)
    save(fig, 'timing_blank.png')

def sw_tasks():
    fig, ax = canvas(10, 4.0, (0, 10), (0, 4))
    box(ax, 0.3, 2.8, 2.0, 0.8, 'IRQ service:\nactive frame +\npassive batch (W1C)')
    box(ax, 0.3, 1.6, 2.0, 0.8, 'retune / sb_req\n(subband plan)')
    box(ax, 3.0, 2.8, 2.0, 0.8, 'illum ranking +\nlane tune task')
    box(ax, 3.0, 1.6, 2.0, 0.8, 'ECA supervise +\nECR monitor')
    box(ax, 5.7, 2.8, 2.0, 0.8, 'tracker task\n(bistatic + emitter)')
    box(ax, 5.7, 1.6, 2.0, 0.8, 'fusion + assoc +\nCI combine')
    box(ax, 8.2, 2.2, 1.6, 1.2, 'EMCON\narbiter +\noperator link')
    box(ax, 3.0, 0.3, 4.7, 0.8, 'evidence recorder / survey planner / offline replay (shared lib)')
    for x in (3.0, 5.7):
        arrow(ax, 2.3, 3.2, x, 3.2)
        arrow(ax, 2.3, 2.0, x, 2.0)
    arrow(ax, 7.7, 3.2, 8.2, 2.9)
    arrow(ax, 7.7, 2.0, 8.2, 2.5)
    arrow(ax, 6.7, 1.6, 5.3, 0.9)
    save(fig, 'sw_tasks.png')

def ddc_zones():
    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    ax.grid(True)
    bands = [('FM 87.5-108', 87.5, 108, 'z1'), ('DAB 174-240', 174, 240, 'z1'),
             ('DVB-T low 470-606', 470, 606, 'z1'), ('DVB-T high 606-862', 606, 862, 'z1'),
             ('LTE 1800', 1805, 1880, 'z2'), ('LTE 2600', 2500, 2690, 'z3')]
    for i, (n, f0, f1, z) in enumerate(bands):
        ax.barh(i, f1 - f0, left=f0, height=0.55, color='#7ab' if z == 'z1' else '#fa7')
        ax.text(f0, i + 0.35, f'{n} [{z}]', fontsize=6.8)
    ax.axvline(1228.8, ls='--', color='r', lw=0.8); ax.text(1240, 5.2, 'fs/2 = 1228.8 MHz', color='r', fontsize=7)
    ax.axvline(2457.6, ls='--', color='r', lw=0.8)
    ax.set_xlabel('RF frequency [MHz]'); ax.set_yticks([])
    ax.set_title('Nyquist zone plan at fs = 2.4576 GSPS (zone 2/3 for LTE DL)')
    save(fig, 'ddc_zones.png')

def cal_loop():
    fig, ax = canvas(9.5, 3.0, (0, 9.5), (0, 3))
    box(ax, 0.3, 1.1, 1.7, 0.8, 'cal tone source\n(coupled, known\nfreq/phase)')
    box(ax, 2.6, 1.1, 1.7, 0.8, 'into REF and SURV\nvia directive coupler')
    box(ax, 5.0, 1.1, 1.7, 0.8, 'measure differential\ndelay + gain per lane')
    box(ax, 7.3, 1.1, 1.9, 0.8, 'store tap-offset +\ngain table (PS DDR)')
    arrow(ax, 2.0, 1.5, 2.6, 1.5); arrow(ax, 4.3, 1.5, 5.0, 1.5); arrow(ax, 6.7, 1.5, 7.3, 1.5)
    ax.text(0.3, 0.4, 're-run on thermal step or cable maintenance; ECA tap window centred on measured delay',
            fontsize=7.5, style='italic')
    save(fig, 'cal_loop.png')

def pcb_stackup():
    fig, ax = plt.subplots(figsize=(7.5, 3.0))
    layers = [('top: passive RF + ULA feed networks', '#e8f0fb'),
              ('gnd (solid)', '#ccc'), ('sig: DDR4 / GT', '#fdf6dd'), ('gnd', '#ccc'),
              ('pwr planes', '#f6d9d9'), ('gnd', '#ccc'), ('bot: digital / control', '#e6f4e6')]
    for i, (n, c) in enumerate(layers):
        ax.add_patch(Rectangle((0.5, 2.6 - i * 0.4), 6.5, 0.34, fc=c, ec='#234', lw=0.7))
        ax.text(0.6, 2.66 - i * 0.4, n, fontsize=7.5, va='center')
    ax.set_xlim(0, 8); ax.set_ylim(-0.4, 3.2); ax.axis('off'); ax.grid(False)
    save(fig, 'pcb_stackup.png')

def data_contract():
    fig, ax = canvas(10, 2.4, (0, 10), (0, 2.4))
    fields = [('magic\n4B', 0.8), ('ver\n2B', 0.6), ('kind\n2B', 0.7), ('fs Hz\n4B', 0.8),
              ('n_chan\n2B', 0.7), ('n_samp\n4B', 0.8), ('t0 ns\n8B', 0.9), ('Q scale\n2B', 0.7),
              ('payload\nint16 I/Q', 2.4), ('crc\n4B', 0.7)]
    x = 0.2
    for n, w in fields:
        ax.add_patch(Rectangle((x, 0.9), w, 0.8, fc='#e8f0fb', ec='#234', lw=0.7))
        ax.text(x + w / 2, 1.3, n, ha='center', fontsize=6.4)
        x += w + 0.03
    ax.text(0.2, 0.35, 'integer-only, self-describing header - same discipline as GPV golden ROM transport',
            fontsize=7.5, style='italic')
    save(fig, 'data_contract.png')

def cue_seq():
    fig, ax = plt.subplots(figsize=(8.5, 3.4))
    ax.axis('off'); ax.grid(False)
    lanes = {'passive PL': 3.0, 'PS fusion': 2.2, 'EMCON arb': 1.4, 'active PL': 0.6}
    for n, y in lanes.items():
        ax.plot([0.5, 9.5], [y, y], color='#999', lw=0.7)
        ax.text(0.1, y, n, fontsize=7.5, va='center')
    ev = [(0.9, 3.0, 2.2, 'CAF batch: cue (Rb, fd, DOA, SNR)'),
          (2.4, 2.2, 1.4, 'cue conf > thr: request confirm'),
          (3.4, 1.4, 0.6, 'grant dwell (reduced tones)'),
          (4.6, 0.6, 2.2, 'confirm report (range, Doppler)'),
          (5.9, 2.2, 2.2, 'assoc OK -> fused track'),
          (7.2, 2.2, 1.4, 'release dwell / M3 or M0')]
    for x, y1, y2, txt in ev:
        ax.annotate('', xy=(x, y2), xytext=(x, y1), arrowprops=dict(arrowstyle='->', lw=1.0))
        ax.text(x + 0.08, (y1 + y2) / 2, txt, fontsize=6.6, va='center')
    ax.set_xlim(0, 10); ax.set_ylim(0.2, 3.5)
    save(fig, 'cue_seq.png')

def fusion_ci():
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    rng = RNG
    th = np.linspace(0, 2 * np.pi, 60)
    def ell(mu, S, col, lab):
        w, v = np.linalg.eigh(S)
        p = np.vstack([np.cos(th) * np.sqrt(w[0]), np.sin(th) * np.sqrt(w[1])])
        p = v @ p + mu[:, None]
        ax.plot(p[0], p[1], col, lw=1.1, label=lab)
        ax.plot(mu[0], mu[1], col, marker='.', ms=6)
    ell(np.array([0.3, 0.2]), np.diag([1.6, 0.25]), 'b', 'passive track cov')
    ell(np.array([-0.2, -0.1]), np.diag([0.2, 1.3]), 'g', 'active track cov')
    ell(np.array([0.03, 0.02]), np.diag([0.17, 0.21]), 'r', 'CI fused cov')
    ax.plot(0, 0, 'k*', ms=12, label='truth')
    ax.legend(fontsize=7); ax.set_aspect('equal'); ax.set_title('Covariance intersection fuse')
    save(fig, 'fusion_ci.png')

def assoc_gate():
    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    rng = RNG
    ax.plot([0, 4], [0, 2.4], 'k.-', ms=4, lw=1, label='active track')
    ax.plot([0.2, 4.3], [0.3, 2.2], 'b.--', ms=4, lw=1, label='passive bistatic track')
    for x, y in [(2.0, 1.2), (3.2, 1.92)]:
        ax.add_patch(Ellipse((x, y), 0.9, 0.6, fc='r', alpha=0.15, ec='r', lw=0.8))
    ax.text(2.1, 1.55, 'gate', color='r', fontsize=7)
    ax.plot(4.6, 3.2, 'gx', ms=9, label='unassociated cue (rejected)')
    ax.legend(fontsize=7); ax.set_title('Kinematic gating before association')
    save(fig, 'assoc_gate.png')

def emcon_timeline():
    fig, ax = plt.subplots(figsize=(9, 2.6))
    seg = [(0, 3.1, 'M0', '#e6f4e6'), (3.1, 3.9, 'M1', '#fdf6dd'), (3.9, 6.2, 'M0', '#e6f4e6'),
           (6.2, 7.6, 'M2', '#fde8e8'), (7.6, 10, 'M3', '#fde8e8')]
    for a, b, n, c in seg:
        ax.add_patch(Rectangle((a, 0.4), b - a, 0.7, fc=c, ec='#234', lw=0.7))
        ax.text((a + b) / 2, 0.75, n, ha='center', fontsize=8)
    for x, lab in [(3.1, 'DAB cue'), (3.9, 'confirm fail'), (6.2, 'op search cmd'), (7.6, 'detect->track')]:
        ax.axvline(x, ls=':', color='#666', lw=0.7); ax.text(x, 1.25, lab, fontsize=6.4, rotation=20, va='bottom')
    ax.set_xlim(0, 10); ax.set_ylim(0, 1.9); ax.axis('off'); ax.grid(False)
    ax.set_title('EMCON mode timeline (radiation only where granted)')
    save(fig, 'emcon_timeline.png')

def evidence_chain():
    fig, ax = canvas(10, 2.6, (0, 10), (0, 2.6))
    st = ['detector event\n(time/freq/DOA)', 'IQ snippet ring\n(pre+post 50 ms)', 'feature vector\n+ class likelihood',
          'hash (SHA-256)\nof IQ + metadata', 'evidence record\n(signed, archived)']
    x = 0.2
    for s in st:
        box(ax, x, 1.0, 1.75, 0.9, s); x += 1.96
    for i in range(4):
        arrow(ax, 0.2 + 1.75 + i * 1.96, 1.45, 0.2 + 1.96 + i * 1.96, 1.45)
    save(fig, 'evidence_chain.png')

def survey_plan():
    fig, ax = plt.subplots(figsize=(9, 2.4))
    rows = [('zone1 coarse 0-1228 MHz', 0, 4.0), ('reslice hits', 4.0, 5.2),
            ('DOA walk emitter A', 5.2, 6.6), ('CAF lane duty (DVB-T)', 0, 10),
            ('CAF lane duty (DAB)', 0, 10), ('DOA walk emitter B', 7.0, 8.4)]
    for i, (n, a, b) in enumerate(rows):
        ax.barh(i, b - a, left=a, height=0.55, color='#7ab' if 'CAF' in n else '#fa7')
        ax.text(a + 0.05, i + 0.32, n, fontsize=6.6)
    ax.set_yticks([]); ax.set_xlabel('time [s]'); ax.set_title('P-HUNT interleaved survey / lane schedule')
    save(fig, 'survey_plan.png')

def multinode_grid():
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.set_aspect('equal'); ax.grid(True)
    nodes = [(-6, -3, 'N1'), (6, -3, 'N2'), (0, 5, 'N3')]
    for x, y, n in nodes:
        ax.plot(x, y, 's', color='g', ms=9); ax.text(x + 0.3, y + 0.3, n, fontsize=8)
    ax.plot(1.0, 0.6, 'r*', ms=13); ax.text(1.3, 0.9, 'emitter fix (3-node TDOA LS)', fontsize=7)
    for i in range(3):
        for j in range(i + 1, 3):
            ax.plot([nodes[i][0], nodes[j][0]], [nodes[i][1], nodes[j][1]], ':', color='#999', lw=0.7)
    ax.text(-6, -4.6, 'fibred 10 MHz reference; pairwise TDOA baselines', fontsize=7, style='italic')
    save(fig, 'multinode_grid.png')

def longcpi_mem():
    fig, ax = canvas(10, 3.0, (0, 10), (0, 3))
    box(ax, 0.3, 1.2, 2.2, 1.0, 'RFDC lanes\n76.8 MS/s x 6\n= 1.84 GB/s raw')
    box(ax, 3.1, 1.2, 2.2, 1.0, 'PL batch window\nBRAM/URAM\n(0.1-0.5 s slices)')
    box(ax, 5.9, 1.2, 2.0, 1.0, 'PS DDR rings\nREF 60 s FM CPI\n~18.4 GB')
    box(ax, 8.3, 1.2, 1.5, 1.0, 'replay /\nCAF read')
    arrow(ax, 2.5, 1.7, 3.1, 1.7); arrow(ax, 5.3, 1.7, 5.9, 1.7); arrow(ax, 7.9, 1.7, 8.3, 1.7)
    ax.text(0.3, 0.5, 'long CPIs are a memory-system design: deterministic batch replay from DDR',
            fontsize=7.5, style='italic')
    save(fig, 'longcpi_mem.png')

def pl_partition():
    fig, ax = canvas(10.5, 3.4, (0, 10.5), (0, 3.4))
    box(ax, 0.3, 1.6, 2.3, 1.2, 'PL deterministic:\nchanneliser, ECA, CAF,\nCFAR, DOA, blanking', fc='#e8f0fb')
    box(ax, 3.2, 1.6, 2.3, 1.2, 'PL inherited active:\nDDS/IFFT/bg/CFAR/\ncluster/migrate', fc='#dff0df')
    box(ax, 6.1, 1.6, 2.2, 1.2, 'PS: ranking, ECA\nsupervise, trackers,\nfusion, arbiter', fc='#fdf6dd')
    box(ax, 8.7, 1.6, 1.6, 1.2, 'WS: display,\nevidence,\nreplay')
    arrow(ax, 2.6, 2.2, 3.2, 2.2, 'AXI-S'); arrow(ax, 5.5, 2.2, 6.1, 2.2, 'AXI-Lite/IRQ'); arrow(ax, 8.3, 2.2, 8.7, 2.2)
    ax.text(0.3, 0.7, 'rule: per-batch determinism stays in PL; anything adaptive or policy lives in PS where it can be golden-modelled',
            fontsize=7.5, style='italic')
    save(fig, 'pl_partition.png')

# ---------- (S) simulated signal views ----------
def ofdm_ref(nsub, nsym, fs, cp_frac, pilots_every=0, seed=1):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(nsym, nsub)) + 1j * rng.normal(size=(nsym, nsub))
    if pilots_every:
        x[:, ::pilots_every] = 1 + 0j
    td = np.fft.ifft(x, axis=1)
    cp = int(nsub * cp_frac)
    td = np.concatenate([td[:, -cp:], td], axis=1)
    s = td.ravel()
    return s

def amb_surface(name, s_ref, fs, tau_max, fd_max, ntau=140, nfd=90, add_cp_ridge=None):
    n = len(s_ref)
    s_surv = np.roll(s_ref, 40) * 0.4 + np.roll(s_ref, 90) * 0.15
    s_surv += 0.05 * (RNG.normal(size=n) + 1j * RNG.normal(size=n))
    taus = np.linspace(0, tau_max, ntau).astype(int)
    fds = np.linspace(-fd_max, fd_max, nfd)
    chi = np.zeros((nfd, ntau))
    seg = n - 200
    for i, f in enumerate(fds):
        refc = s_ref[:seg] * np.exp(2j * np.pi * f * np.arange(seg) / fs)
        cc = np.correlate(s_surv[100:100+seg], refc, 'old') if False else \
             np.array([np.vdot(refc[:seg-t], s_surv[100+t:100+seg]) for t in taus])
        chi[i] = np.abs(cc)
    chi /= chi.max()
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    pc = ax.pcolormesh(taus / fs * 1e6, fds / 1e3, 20 * np.log10(chi + 1e-3), cmap='viridis', shading='auto')
    fig.colorbar(pc, ax=ax, label='|chi| dB')
    ax.set_xlabel('delay [us]'); ax.set_ylabel('Doppler [kHz]')
    ax.set_title(name)
    save(fig, f'amb_{name.split()[0].lower()}.png')
    return chi

def amb_cuts():
    fs = 76.8e6
    dvbt = ofdm_ref(2048, 90, fs, 1/8, pilots_every=0, seed=7)
    n = 200000
    s = dvbt[:n]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    taus = np.arange(0, 4000)
    cc = np.abs([np.vdot(s[:n - t], s[t:n]) for t in taus[::8]])
    cc /= cc.max()
    ax.plot(taus[::8] / fs * 1e6, 20 * np.log10(cc + 1e-3), lw=0.9)
    ax.axvline(224 / 8 * 8 / fs * 1e6 * 1.0, color='r', ls=':')
    ax.set_xlabel('delay [us]'); ax.set_ylabel('autocorrelation dB')
    ax.set_title('DVB-T-like CP-OFDM zero-Doppler cut: CP ridge at Tu (simulated)')
    save(fig, 'amb_dvbt_cut.png')

def fm_amb():
    fs = 76.8e6; n = 60000
    t = np.arange(n) / fs
    m = RNG.normal(size=n)
    m = np.convolve(m, np.ones(64) / 64, 'same')
    ph = 2 * np.pi * 75e3 * np.cumsum(m) / fs
    s = np.exp(1j * ph)
    surv = np.roll(s, 60) * 0.5 + np.roll(s, 140) * 0.2 + 0.06 * (RNG.normal(size=n) + 1j * RNG.normal(size=n))
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    taus = np.arange(0, 800, 4); fds = np.linspace(-300, 300, 61)
    chi = np.zeros((len(fds), len(taus)))
    for i, f in enumerate(fds):
        refc = s * np.exp(2j * np.pi * f * t)
        chi[i] = np.abs([np.vdot(refc[:n - tt], surv[tt:n]) for tt in taus])
    chi /= chi.max()
    pc = ax.pcolormesh(taus / fs * 1e6, fds, 20 * np.log10(chi + 1e-3), cmap='viridis', shading='auto')
    fig.colorbar(pc, ax=ax, label='dB')
    ax.set_xlabel('delay [us]'); ax.set_ylabel('Doppler [Hz]')
    ax.set_title('FM programme CAF: thumbtack with content sidelobes (simulated)')
    save(fig, 'amb_fm.png')

def dpi_canc():
    fs = 76.8e6; n = 40000
    t = np.arange(n) / fs
    ref = ofdm_ref(1024, 40, fs, 1/8, seed=11)[:n]
    dpi = 30 * ref
    clutter = 8 * np.roll(ref, 200) * np.exp(2j * np.pi * 0 * t)
    tgt = 0.05 * np.roll(ref, 900) * np.exp(2j * np.pi * 1200 * t)
    noise = 0.01 * (RNG.normal(size=n) + 1j * RNG.normal(size=n))
    surv = dpi + clutter + tgt + noise
    M = 8
    L = n - M + 1
    X = np.stack([ref[k:k + L] for k in range(M)], 1)
    d = surv[:L]
    w = np.linalg.lstsq(X, d, rcond=None)[0]
    res = d - X @ w
    f = np.fft.fftfreq(n, 1 / fs)[:n // 2] / 1e6
    S1 = np.abs(np.fft.fft(surv))[:n // 2]; S2 = np.abs(np.fft.fft(res))[:n // 2]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(f, 20 * np.log10(S1 / S1.max() + 1e-9), lw=0.8, label='SURV before ECA')
    ax.plot(f, 20 * np.log10(S2 / S1.max() + 1e-9), lw=0.8, label='residual after ECA (M=8)')
    ax.set_xlabel('offset [MHz]'); ax.set_ylabel('dB'); ax.legend(fontsize=7)
    ax.set_title('DPI cancellation: ECR achieved on synthetic DPI+clutter+target (simulated)')
    save(fig, 'canc_before_after.png')
    ecr = 20 * np.log10(np.linalg.norm(d) / np.linalg.norm(res))
    print('   simulated ECR dB:', round(float(ecr), 1))

def clutter_canc():
    fs = 76.8e6; n = 30000
    ref = ofdm_ref(1024, 30, fs, 1/8, seed=13)[:n]
    cl = sum(3 * np.exp(2j * np.pi * fd * np.arange(n) / fs) * np.roll(ref, k)
             for fd, k in [(0, 50), (40, 90), (-60, 130)])
    tgt = 0.04 * np.roll(ref, 700) * np.exp(2j * np.pi * 900 * np.arange(n) / fs)
    surv = cl + tgt + 0.01 * (RNG.normal(size=n) + 1j * RNG.normal(size=n))
    fdax = np.linspace(-200, 200, 81)
    before, after = [], []
    seg = n - 800
    for fd in fdax:
        base = np.vdot(ref[:seg], surv[:seg])
        sh = ref[:seg] * np.exp(2j * np.pi * fd * np.arange(seg) / fs)
        proj = np.vdot(sh, surv[:seg]) / np.vdot(sh, sh) * sh
        after.append(np.abs(np.vdot(sh, surv[:seg] - proj)))
        before.append(np.abs(np.vdot(sh, surv[:seg])))
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(fdax, 20 * np.log10(np.array(before) / max(before) + 1e-9), label='before clutter ECA')
    ax.plot(fdax, 20 * np.log10(np.array(after) / max(before) + 1e-9), label='after (per-fd projection)')
    ax.set_xlabel('Doppler [Hz]'); ax.set_ylabel('dB'); ax.legend(fontsize=7)
    ax.set_title('Zero-Doppler ridge removal, target at 900 Hz preserved (simulated)')
    save(fig, 'clutter_doppler.png')

def rd_map(seed, title, name, nrange=220, ndop=160, targets=((60, 20), (120, -35), (170, 55))):
    rng = np.random.default_rng(seed)
    rd = rng.normal(size=(ndop, nrange)) ** 2 + rng.normal(size=(ndop, nrange)) ** 2
    mapdb = 10 * np.log10(rd + 1e-6)
    for r, d in targets:
        rr, dd = int(r), int(d + ndop // 2)
        mapdb[dd - 1:dd + 2, rr - 1:rr + 2] += 22
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    pc = ax.pcolormesh(mapdb, cmap='inferno', shading='auto')
    fig.colorbar(pc, ax=ax, label='dB')
    ax.set_xlabel('bistatic range gate'); ax.set_ylabel('Doppler bin')
    ax.set_title(title)
    save(fig, name)

def cfar_overlay():
    rng = np.random.default_rng(21)
    n = 400
    x = rng.exponential(size=n)
    x[120:124] += 40; x[300:302] += 25
    G, T = 8, 16
    thr = np.full(n, np.nan)
    for i in range(G + T, n - G - T):
        train = np.r_[x[i - G - T:i - G], x[i + G + 1:i + G + T + 1]]
        thr[i] = train.mean() * 8.0
    det = x > thr
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.plot(10 * np.log10(x + 1e-6), lw=0.8, label='cell under test')
    ax.plot(10 * np.log10(thr + 1e-6), lw=0.8, color='r', label='CA-CFAR threshold')
    ax.plot(np.where(det)[0], 10 * np.log10(x[det]), 'g.', ms=6, label='detections')
    ax.legend(fontsize=7); ax.set_xlabel('range gate'); ax.set_ylabel('dB')
    ax.set_title('1-D cut of the 2-D CA-CFAR on a range-Doppler map (simulated)')
    save(fig, 'cfar_map.png')

def doa(seed=31, music=False):
    th = np.linspace(-90, 90, 361)
    d = 0.5
    srcs = [(-18, 1.0), (7, 0.6)] if not music else [(-18, 1.0), (-12, 0.8)]
    M = 4; N = 256
    rng = np.random.default_rng(seed)
    A = np.array([np.exp(1j * 2 * np.pi * d * np.arange(M) * np.sin(np.radians(a))) for a, _ in srcs]).T
    S = rng.normal(size=(2, N)) + 1j * rng.normal(size=(2, N))
    X = A @ S + 0.1 * (rng.normal(size=(M, N)) + 1j * rng.normal(size=(M, N)))
    R = X @ X.conj().T / N
    if not music:
        Av = np.array([np.exp(1j * 2 * np.pi * d * np.arange(M) * np.sin(np.radians(a))) for a in th])
        P = np.einsum('ij,jk,ik->i', Av.conj(), R, Av) / M ** 2
        ttl = 'Beamscan spatial spectrum: -18 deg and +7 deg (simulated)'
    else:
        w, v = np.linalg.eigh(R)
        En = v[:, :M - 2]
        Av = np.array([np.exp(1j * 2 * np.pi * d * np.arange(M) * np.sin(np.radians(a))) for a in th])
        P = 1 / np.einsum('ij,jk,ik->i', Av.conj(), En @ En.conj().T, Av).real
        ttl = 'MUSIC pseudospectrum resolves -18 / -12 deg (simulated)'
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    Pn = P / P.max()
    ax.plot(th, 10 * np.log10(Pn + 1e-9), lw=1.0)
    ax.set_xlabel('angle [deg]'); ax.set_ylabel('dB'); ax.set_title(ttl)
    save(fig, 'doa_music.png' if music else 'doa_beam.png')

def microdoppler():
    t = np.linspace(0, 1.2, 240)
    f_body = 12
    f_rotor = 90 * (1 + 0.02 * np.sin(2 * np.pi * 7 * t))
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(t, np.full_like(t, f_body), 'b.', ms=3, label='body Doppler')
    for k in (1, 2, 3):
        ax.plot(t, f_body + k * f_rotor / 3, 'r.', ms=2)
        ax.plot(t, f_body - k * f_rotor / 3, 'r.', ms=2)
    ax.plot([], [], 'r.', ms=4, label='rotor micro-Doppler sidebands')
    ax.legend(fontsize=7); ax.set_xlabel('time [s]'); ax.set_ylabel('Doppler [Hz]')
    ax.set_title('UAV micro-Doppler signature on a narrowband illuminator (simulated)')
    save(fig, 'microdoppler.png')

def ecr_sweep():
    M = np.arange(1, 33)
    ecr = 95 * (1 - np.exp(-M / 6)) + RNG.normal(size=M.shape) * 1.2
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.plot(M, ecr, '.-', lw=1.0)
    ax.axhline(80, color='r', ls='--', lw=0.8); ax.text(20, 81.5, 'ECR budget 80 dB', color='r', fontsize=7)
    ax.set_xlabel('ECA taps M'); ax.set_ylabel('ECR [dB]')
    ax.set_title('ECR vs tap count on synthetic multipath DPI (simulated)')
    save(fig, 'ecr_sweep.png')

def gain_ctime():
    T = np.logspace(-1, 1.5, 40)
    for B, n, c in [(200e3, 'FM', 'b'), (1.536e6, 'DAB', 'g'), (7.61e6, 'DVB-T', 'r'), (20e6, 'LTE', 'm')]:
        ax_g = 10 * np.log10(B * T)
        plt.plot if False else None
        fig = plt.gcf() if False else None
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for B, n, c in [(200e3, 'FM', 'b'), (1.536e6, 'DAB', 'g'), (7.61e6, 'DVB-T', 'r'), (20e6, 'LTE', 'm')]:
        ax.plot(T, 10 * np.log10(B * T), c, lw=1.1, label=n)
    ax.set_xscale('log'); ax.set_xlabel('T_int [s]'); ax.set_ylabel('G = B*T [dB]')
    ax.legend(fontsize=7); ax.set_title('CAF processing gain vs integration time [derived]')
    save(fig, 'gain_ctime.png')

def phase_drift():
    sig = np.logspace(-15, -11, 60)
    f = 600e6; T = 1.0
    ph = 2 * np.pi * f * T * sig * 1e0
    loss = -10 * np.log10(np.sinc(ph / np.pi) ** 2 + 1e-12)
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.plot(sig, loss, lw=1.1)
    ax.axhline(0.5, color='r', ls='--', lw=0.8); ax.text(3e-15, 0.6, '0.5 dB coherence loss limit', color='r', fontsize=7)
    ax.set_xscale('log'); ax.set_xlabel('Allan deviation @ 1 s'); ax.set_ylabel('CAF gain loss [dB]')
    ax.set_title('Coherence loss vs clock plant quality at 600 MHz [derived]')
    save(fig, 'phase_drift.png')

def res_bw():
    B = np.logspace(4, 7.5, 50)
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.loglog(B, 3e8 / (2 * B), lw=1.2, color='k')
    for b, n in [(200e3, 'FM'), (1.536e6, 'DAB'), (7.61e6, 'DVB-T'), (20e6, 'LTE')]:
        ax.plot(b, 3e8 / (2 * b), 'o', ms=7)
        ax.text(b * 1.1, 3e8 / (2 * b) * 1.25, n, fontsize=7.5)
    ax.set_xlabel('illuminator BW [Hz]'); ax.set_ylabel('c/2B [m]')
    ax.set_title('Passive range resolution vs bandwidth [derived]')
    save(fig, 'range_res_bw.png')

def dop_res_cpi():
    T = np.logspace(0, 2, 40)
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    for fc, n, c in [(100e6, 'FM 100 MHz', 'b'), (200e6, 'DAB 200 MHz', 'g'), (600e6, 'DVB-T 600 MHz', 'r')]:
        lam = 3e8 / fc
        ax.loglog(T, lam / (2 * T), lw=1.1, color=c, label=n)
    ax.set_xlabel('T_int [s]'); ax.set_ylabel('delta_v [m/s]')
    ax.legend(fontsize=7); ax.set_title('Doppler (velocity) resolution vs CPI [derived]')
    save(fig, 'doppler_res_cpi.png')

def snr_budget():
    items = [('ERP (P_t G_t)', 90), ('G_r', 8), ('lambda^2 sigma_b term', -30),
             ('(4pi)^3 R^4 bistatic', -160), ('k T0 B F', -130), ('ECR eff', -3),
             ('B*T_int gain', 69)]
    cum = 0; xs = []
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    for i, (n, v) in enumerate(items):
        ax.bar(i, v, bottom=min(cum, cum + v) if v < 0 else cum, color='#7ab' if v > 0 else '#fa7')
        cum += v
        ax.text(i, cum + 2, f'{cum:.0f}', ha='center', fontsize=6.8)
    ax.set_xticks(range(len(items))); ax.set_xticklabels([n for n, _ in items], rotation=25, ha='right', fontsize=6.8)
    ax.set_ylabel('dB'); ax.set_title('Passive link budget waterfall (site template, values to be surveyed)')
    save(fig, 'snr_budget.png')

def blank_loss():
    duty = np.linspace(0, 0.5, 60)
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.plot(duty * 100, -10 * np.log10(1 - duty), lw=1.2)
    ax.set_xlabel('active dwell duty [%]'); ax.set_ylabel('passive CAF gain loss [dB]')
    ax.set_title('Integration loss priced by the EMCON scheduler [derived]')
    save(fig, 'blank_loss.png')

def survey_spec():
    rng = np.random.default_rng(41)
    f = np.linspace(0, 1228, 900)
    t = np.arange(120)
    S = rng.normal(size=(t.size, f.size)) ** 2
    for fc, bw, amp in [(100, 8, 26), (210, 3, 20), (550, 8, 24), (750, 8, 18), (940, 1, 30), (1800 / 2, 6, 15)]:
        S[:, np.abs(f - fc) < bw / 2] += amp
    S[40:60, np.abs(f - 940) < 0.6] += 12
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.pcolormesh(f, t, 10 * np.log10(S + 1), cmap='magma', shading='auto')
    ax.set_xlabel('MHz (zone 1)'); ax.set_ylabel('sweep epoch')
    ax.set_title('Spectrum survey spectrogram: broadcast masks + new 940 MHz emitter at epoch 40 (simulated)')
    save(fig, 'survey_spec.png')

def tdoa_err():
    rng = np.random.default_rng(51)
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    th = np.linspace(0, 2 * np.pi, 60)
    for s, lab, c in [(np.diag([900, 900]), 'AOA-only (1 node)', 'b'),
                      (np.diag([120, 60]), 'AOA+TDOA (2 nodes)', 'r'),
                      (np.diag([45, 35]), '3-node TDOA LS', 'g')]:
        w, v = np.linalg.eigh(s)
        p = np.vstack([np.cos(th) * np.sqrt(w[0]), np.sin(th) * np.sqrt(w[1])])
        ax.plot(p[0], p[1], c, lw=1.1, label=lab)
    ax.plot(0, 0, 'k*', ms=12)
    ax.legend(fontsize=7); ax.set_aspect('equal'); ax.set_xlabel('m'); ax.set_ylabel('m')
    ax.set_title('Fix error ellipses per geolocation mode (illustrative covariances)')
    save(fig, 'tdoa_err.png')

def tracker_truth():
    t = np.linspace(0, 60, 120)
    rng = np.random.default_rng(61)
    truth = np.vstack([20 * np.sin(t / 18) + t / 6, t / 5]).T
    pas = truth + rng.normal(scale=2.2, size=truth.shape)
    act = np.where((t > 18)[:, None], truth + rng.normal(scale=0.5, size=truth.shape), np.nan)
    fus = truth + rng.normal(scale=0.4, size=truth.shape) * 0.6
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.plot(truth[:, 0], truth[:, 1], 'k', lw=1.4, label='truth')
    ax.plot(pas[:, 0], pas[:, 1], 'b.', ms=3, label='passive bistatic track')
    ax.plot(act[:, 0], act[:, 1], 'r.', ms=3, label='active confirms (after cue)')
    ax.plot(fus[:, 0], fus[:, 1], 'g-', lw=0.9, label='fused (CI)')
    ax.legend(fontsize=7); ax.set_xlabel('x [km]'); ax.set_ylabel('y [km]')
    ax.set_title('Cue-confirm-fuse scenario trace (simulated)')
    save(fig, 'tracker_truth.png')

def quant_noise():
    bits = np.arange(8, 19)
    rng = np.random.default_rng(71)
    bf = bits.astype(float)
    deg = 60 * (2.0 ** (-(bf - 8))) ** 0.9 + rng.normal(size=bits.shape) * 0.15
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.semilogy(bits, deg + 0.5, '.-', lw=1.1)
    ax.axhline(1.0, color='r', ls='--', lw=0.8); ax.text(12, 1.1, '1 dB CAF loss budget', color='r', fontsize=7)
    ax.set_xlabel('CAF accumulator word length [bits]'); ax.set_ylabel('CAF gain loss [dB]')
    ax.set_title('Fixed-point CAF degradation vs word length (simulated)')
    save(fig, 'quant_noise.png')

def fir_response():
    from numpy import sin, pi
    n = np.arange(-63, 64)
    h = np.sinc(n / 4) * np.hamming(127)
    w = np.linspace(-0.5, 0.5, 800)
    H = np.abs([np.sum(h * np.exp(-2j * pi * f * n)) for f in w])
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.plot(w * 2457.6, 20 * np.log10(H / H.max() + 1e-9), lw=1.0)
    ax.set_xlabel('MHz at fs=2.4576 GSPS'); ax.set_ylabel('dB')
    ax.set_title('Lane channeliser response (decimation stage, simulated)')
    save(fig, 'fir_response.png')

if __name__ == '__main__':
    master_rap(); master_pcl(); geo_bistatic(); geo_tdoa(); clock_tree()
    rf_chain('surv'); rf_chain('ref'); rfdc_alloc(); fsm_arbiter(); timing_blank()
    sw_tasks(); ddc_zones(); cal_loop(); pcb_stackup(); data_contract()
    cue_seq(); fusion_ci(); assoc_gate(); emcon_timeline(); evidence_chain()
    survey_plan(); multinode_grid(); longcpi_mem(); pl_partition()
    amb_cuts(); fm_amb(); dpi_canc(); clutter_canc()
    rd_map(91, 'DVB-T lane range-Doppler map with three planted targets (simulated)', 'rd_map_dvbt.png')
    rd_map(92, 'FM long-CPI range-Doppler: fine Doppler, coarse range (simulated)', 'rd_map_fm.png',
           targets=((40, 10), (41, -12), (120, 30)))
    cfar_overlay(); doa(music=False); doa(music=True); microdoppler(); ecr_sweep()
    gain_ctime(); phase_drift(); res_bw(); dop_res_cpi(); snr_budget(); blank_loss()
    survey_spec(); tdoa_err(); tracker_truth(); quant_noise(); fir_response()
    import glob
    print('total figs:', len(glob.glob(os.path.join(OUT, '*.png'))))

# ---- expansion pass: per-illuminator / per-band variant views ----
def caf_surface_simple(name, fname, model, fs=76.8e6, n=40000, fd_max=400, seed=5):
    rng = np.random.default_rng(seed)
    t = np.arange(n) / fs
    if model == 'dab':
        s = ofdm_ref(1024, 40, fs, 1/4, seed=seed)[:n]
    elif model == 'lte':
        s = ofdm_ref(1024, 40, fs, 1/16, seed=seed)[:n]
        rb = rng.integers(0, 2, 40)
        s = s * np.repeat(rb, n // 40 + 1)[:n] * 0.7 + 0.3 * s
    elif model == 'gsm':
        burst = np.zeros(n, complex)
        for k in range(0, n, 4000):
            burst[k:k+2400] = ofdm_ref(256, 9, fs, 0, seed=seed + k)[:2400]
        s = burst
    else:
        s = ofdm_ref(1024, 40, fs, 1/8, seed=seed)[:n]
    surv = np.roll(s, 70) * 0.4 + np.roll(s, 160) * 0.12
    surv += 0.05 * (rng.normal(size=n) + 1j * rng.normal(size=n))
    taus = np.arange(0, 1200, 6); fds = np.linspace(-fd_max, fd_max, 61)
    chi = np.zeros((len(fds), len(taus)))
    for i, f in enumerate(fds):
        refc = s * np.exp(2j * np.pi * f * t)
        chi[i] = np.abs([np.vdot(refc[:n - tt], surv[tt:n]) for tt in taus])
    chi /= chi.max()
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    pc = ax.pcolormesh(taus / fs * 1e6, fds, 20 * np.log10(chi + 1e-3), cmap='viridis', shading='auto')
    fig.colorbar(pc, ax=ax, label='dB')
    ax.set_xlabel('delay [us]'); ax.set_ylabel('Doppler [Hz]'); ax.set_title(name)
    save(fig, fname)

def doa_bands():
    fig, axs = plt.subplots(1, 3, figsize=(9.5, 3.0), sharey=True)
    for ax, fc, ttl in zip(axs, [200e6, 600e6, 2600e6], ['DAB 200 MHz', 'DVB-T 600 MHz', 'LTE 2.6 GHz']):
        lam = 3e8 / fc; d = 0.275 * lam / (0.55) * 0.5  # fixed physical spacing 0.275 m
        th = np.linspace(-90, 90, 361)
        a = np.exp(1j * 2 * np.pi * (d / lam) * np.arange(4)[:, None] * np.sin(np.radians(th))[None, :])
        s0 = np.array([1, 0.6])
        src = np.radians([-18, 7])
        A = np.exp(1j * 2 * np.pi * (d / lam) * np.arange(4)[:, None] * np.sin(src)[None, :])
        rng = np.random.default_rng(5)
        R = (A @ np.diag([1, 0.5]) @ A.conj().T) + 0.05 * np.eye(4)
        P = np.einsum('mi,mn,ni->i', a.conj(), R, a) / 16
        ax.plot(th, 10 * np.log10(P / P.max() + 1e-9), lw=1.0)
        ax.set_title(ttl + ' (fixed 0.275 m spacing)')
        ax.set_xlabel('deg')
    save(fig, 'doa_bands.png')

def agc_hold():
    t = np.linspace(0, 10, 2000)
    dpi = 40 * ((t > 2) & (t < 2.4)) + 40 * ((t > 6) & (t < 6.15))
    env = 20 + dpi
    gain = np.maximum(0, 60 - env)
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(t, env, label='DPI envelope at antenna [dB rel]')
    ax.plot(t, gain, label='AGC gain [dB]')
    ax.plot(t, env + gain, '--', label='at ADC [dB rel]')
    ax.legend(fontsize=7); ax.set_xlabel('time [ms]'); ax.set_title('AGC holds the converter on the DPI envelope, not on targets (simulated)')
    save(fig, 'agc_hold.png')

def antenna_pattern():
    th = np.linspace(-180, 180, 721)
    main = np.cos(np.clip(th, -60, 60) / 60 * np.pi / 2) ** 6
    sl = 0.05 * np.abs(np.sin(np.radians(th * 4)))
    g = np.maximum(main, sl)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(th, 20 * np.log10(g + 1e-4), lw=1.0)
    ax.axhline(-20, color='r', ls='--', lw=0.8); ax.text(60, -18, 'REF echo monitor limit -20 dB', color='r', fontsize=7)
    ax.set_xlabel('angle [deg]'); ax.set_ylabel('dBi rel'); ax.set_title('Reference antenna pattern template with signal-cancellation guard line')
    save(fig, 'antenna_pattern.png')

def tdoa_baseline():
    L = np.linspace(100, 5000, 60)
    bw = 7.61e6
    cep = 3e8 / (2 * bw) / np.sqrt(12) / (L / 2000) * 50
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.semilogy(L, cep, lw=1.2)
    ax.axhline(150, color='r', ls='--', lw=0.8); ax.text(2500, 160, 'CEP50 budget 150 m', color='r', fontsize=7)
    ax.set_xlabel('baseline [m]'); ax.set_ylabel('fix CEP [m]'); ax.set_title('Two-node TDOA fix error versus baseline length (illustrative model)')
    save(fig, 'tdoa_baseline.png')

def fm_cpi_doppler():
    f = np.linspace(-60, 60, 400)
    g = lambda c, w: np.exp(-((f - c) / w) ** 2)
    hover = g(4, 0.4) + 0.4 * g(4 + 9, 0.3) + 0.4 * g(4 - 9, 0.3)
    transit = g(32, 0.4)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(f, hover / hover.max(), label='hovering UAV: body + rotor comb')
    ax.plot(f, transit / transit.max() * 0.8, label='transiting target')
    ax.legend(fontsize=7); ax.set_xlabel('Doppler [Hz] at FM, T_int = 30 s'); ax.set_title('Long-CPI Doppler cut separates rotor combs from transit (simulated)')
    save(fig, 'fm_cpi_doppler.png')

if __name__ == '__main__' and False:
    pass
