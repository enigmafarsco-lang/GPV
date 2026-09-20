#!/usr/bin/env python3
"""Generate the RAP design books (integrated active-passive + passive-only).

Provenance: active-chain facts come from the VALIDATED artifacts only
(GPM v1.8 MATLAB package, GPV RTL + 10/10 testbenches, golden ROMs), plus
UG1410/PG269 hardware facts.  Passive-chain content is classical PCL
engineering (Griffiths & Long, Howland, Colone).  Numbers are labelled
[validated], [derived] or [budget] so nothing fabricated can slip in.
"""
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import datetime

DATE = "2026-09-20"

def new_doc():
    d = docx.Document()
    st = d.styles['Normal']
    st.font.name = 'Calibri'
    st.font.size = Pt(10.5)
    return d

def title_page(d, title, subtitle, docnum, rev):
    p = d.add_paragraph(title, style='Title')
    p = d.add_paragraph(subtitle)
    p.runs[0].italic = True
    d.add_paragraph()
    t = d.add_table(rows=0, cols=2)
    t.style = 'Table Grid'
    for k, v in [("Document number", docnum), ("Revision", rev), ("Date", DATE),
                 ("Platform baseline", "AMD Zynq UltraScale+ RFSoC XCZU48DR (ZCU208 class)"),
                 ("Status", "Engineering design book - issued for review"),
                 ("Companion documents",
                  "GPR_SFCW_Engineering_Design_Book_RFSoC48DR_v1.4 (active RF hardware), "
                  "GPV README + software/ps (validated active chain), GPM v1.8 (golden algorithms)")]:
        r = t.add_row().cells
        r[0].text = k
        r[1].text = v
    d.add_paragraph()
    d.add_paragraph(
        "Number labelling convention used throughout: [validated] = measured or "
        "bit-exact simulated result from the GPM v1.8 / GPV artifact set; [derived] = "
        "closed-form result of an equation stated in this book; [budget] = design target "
        "or resource estimate to be confirmed by implementation. No simulated result is "
        "presented as measured hardware data.", style='Intense Quote')
    d.add_page_break()

def emit(d, items):
    for it in items:
        k = it[0]
        if k == 'h1':
            d.add_heading(it[1], level=1)
        elif k == 'h2':
            d.add_heading(it[1], level=2)
        elif k == 'h3':
            d.add_heading(it[1], level=3)
        elif k == 'p':
            d.add_paragraph(it[1])
        elif k == 'b':
            for line in it[1]:
                d.add_paragraph(line, style='List Bullet')
        elif k == 'n':
            for line in it[1]:
                d.add_paragraph(line, style='List Number')
        elif k == 'eq':
            p = d.add_paragraph()
            r = p.add_run(it[1])
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            p.paragraph_format.left_indent = Pt(18)
        elif k == 'note':
            p = d.add_paragraph()
            r = p.add_run("Design decision: ")
            r.bold = True
            p.add_run(it[1])
        elif k == 't':
            hdr, rows = it[1], it[2]
            t = d.add_table(rows=1, cols=len(hdr))
            t.style = 'Table Grid'
            for c, h in zip(t.rows[0].cells, hdr):
                c.text = h
                for par in c.paragraphs:
                    for run in par.runs:
                        run.bold = True
            for row in rows:
                cells = t.add_row().cells
                for c, v in zip(cells, row):
                    c.text = str(v)
            d.add_paragraph()

# ----------------------------------------------------------------------------
# BOOK 1 - RAP: integrated active-passive counter-surveillance radar
# ----------------------------------------------------------------------------
B1 = []
A = B1.append
A(('h1', 'Document map and engineering scope'))
A(('p', "This book defines the RAP system: an INTEGRATED ACTIVE-PASSIVE "
        "COUNTER-SURVEILLANCE RADAR built from two sensing sub-systems that share one "
        "coherent hardware platform and one fusion engine. The active sub-system is the "
        "already validated stepped-frequency continuous-wave (SFCW) radar chain of the GPM "
        "MATLAB package (v1.8) and its GPV RFSoC implementation (10/10 testbenches "
        "bit-exact). The passive sub-system is a passive coherent location (PCL) receiver "
        "that exploits illuminators of opportunity (FM, DAB, DVB-T, LTE downlinks) with "
        "reference and surveillance channels. The fusion engine correlates passive cues "
        "with active confirms to serve the counter-surveillance mission."))
A(('p', "Scope of this book: mission and threat model, system modes and EMCON policy, "
        "coherent timing architecture, passive chain design (cancellation, cross-ambiguity, "
        "DOA, tracking), fusion and cueing, XCZU48DR implementation partition, PS software "
        "extension, validation plan, failure modes and traceability. The active RF hardware "
        "(boards A-E) is not re-derived here; it is inherited from the v1.4 active design "
        "book and the validated GPV package."))
A(('h2', 'How to read this book'))
A(('b', ["Part I (sections 2-5): mission, modes, architecture, timing - read first.",
         "Part II (sections 6-8): active sub-system as inherited, validated baseline.",
         "Part III (sections 9-14): passive sub-system - the new RF/DSP design.",
         "Part IV (sections 15-17): fusion, cueing, operational timelines.",
         "Part V (sections 18-21): XCZU48DR partition, resources, software, data rates.",
         "Part VI (sections 22-25): validation, failure modes, traceability, references."]))
A(('h2', 'Revision history'))
A(('t', ['Rev', 'Date', 'Change'],
    [['1.0', DATE, 'First issue. Active baseline frozen at GPV ps-runtime / GPM v1.8.']]))

A(('h1', 'System mission and threat model'))
A(('h2', 'Counter-surveillance mission statement'))
A(('p', "The RAP system protects a defended site against surveillance acts. A "
        "surveillance act is any collection of information about the site by a "
        "non-cooperative sensor. The system must (1) detect the sensor platform or its "
        "emissions, (2) locate it, (3) classify the threat type, (4) cue a response "
        "(operator display, counter-measure director, or the active radar for fine "
        "tracking), and (5) hold track continuity while the threat manoeuvres or goes "
        "silent in one of the two sensing domains."))
A(('h2', 'Threat classes'))
A(('t', ['Class', 'Observable signature', 'Primary sensor', 'Notes'],
   [['T1 covert RF emitter (bug, covert camera uplink, exfiltration radio)',
     'Continuous or bursty transmission, 30 MHz - 6 GHz',
     'Passive (emitter geolocation)', 'Never detectable by active radar alone if static and small.',
     ],
    ['T2 reconnaissance UAV / micro-UAV',
     'Control-link + telemetry emissions; small RCS (0.01-0.1 m2)',
     'Passive cue -> active confirm', 'RF-silent glide phases require active hold.',],
    ['T3 passive observation platform (glider, balloon, periscope-like mast)',
     'No emissions; small RCS', 'Active SFCW chain', 'Passive contributes nothing; active-only mode.',],
    ['T4 hostile radar / mapping sensor observing the site',
     'High-power pulsed or FMCW emissions', 'Passive (TDOA/FDOA geolocation)',
     'Active chain may be commanded silent (EMCON) while T4 is active.',],
    ['T5 ground-level intruder with handheld device',
     'Intermittent emissions + moving RCS', 'Both, fused', 'Urban multipath is the dominant error source.',]]))
A(('h2', 'Why one sensor domain is not enough'))
A(('p', "Active radar alone cannot see a static, RF-silent-free emitter (T1) and radiates "
        "its own presence (bad against T4). Passive PCL alone cannot see RF-silent targets "
        "(T3), has range accuracy limited by the illuminator bandwidth, and loses targets "
        "outside illuminator coverage. The integrated system uses each domain where it is "
        "strong and hands over where it is weak; the EMCON policy below makes the radiation "
        "decision an explicit, schedulable resource."))

A(('h1', 'System modes and EMCON policy'))
A(('t', ['Mode', 'Active TX', 'Passive RX', 'Use case'],
   [['M0 FULL SILENCE', 'off', 'on', 'Default surveillance mode against T4; zero own emission.',],
    ['M1 PASSIVE CUE', 'off until cue, then short confirm dwell', 'on',
     'Passive detects emitter or UAV link; active confirms range/Doppler with minimal dwell.',],
    ['M2 ACTIVE SEARCH', 'on, full schedule', 'on', 'RF-silent target search (T3); passive runs in parallel.',],
    ['M3 ACTIVE TRACK', 'on, track-only waveform', 'on', 'Handover after detection; minimum revisit, minimum power.',],
    ['M4 PASSIVE-ASSISTED CAL', 'on, calibration schedule', 'on',
     'Passive channels observe own TX as a bistatic reference for chain calibration.',]]))
A(('note', "EMCON is implemented as a scheduler resource, not a switch: every active dwell "
           "request carries a cost (radiation time x power) and the arbiter grants it only "
           "against a cue confidence or an operator command. This keeps the integrated "
           "system's probability of intercept (own) bounded by design."))
A(('p', "Mode transitions are driven by the fusion engine (section 15) and reported to the "
        "operator with the evidence that caused them (cue SNR, DOA, emitter class)."))

A(('h1', 'Top-level architecture'))
A(('p', "Five subsystems on one XCZU48DR platform plus an operator workstation:"))
A(('n', ["ACTIVE SFCW RADAR (inherited, validated): DDS tone synthesis -> TX chain (board B) "
         "-> antenna (board E) -> RX front end (board C) -> RF-ADC -> PL chain (IFFT range "
         "processing, background removal, migration, CFAR, clustering) exactly as in GPV.",
         "PASSIVE PCL RECEIVER (new): one directive reference channel per illuminator of "
         "interest plus N surveillance channels (omni or array), all direct-RF sampled; "
         "PL chain: channelisation, interference/clutter cancellation, cross-ambiguity "
         "function (CAF), CFAR on range-Doppler, DOA, emitter geolocation.",
         "COHERENT TIMING UNIT (inherited board A discipline): single 10 MHz site reference "
         "disciplines one SI570-style clock generator; all RFDC tiles receive phase-aligned "
         "clocks and SYSREF so that active and passive chains are phase-coherent (required "
         "for CAF and for M4 calibration).",
         "FUSION AND CUEING ENGINE (PS software): track-to-track association between passive "
         "bistatic tracks / emitter fixes and active tracks; EMCON arbiter; cue messages.",
         "OPERATOR WORKSTATION: displays (range-Doppler maps, B-scans, map overlays), mode "
         "control, evidence log; same data-contract philosophy as GPV software/offline."]))
A(('h2', 'Information flow'))
A(('p', "Passive chain produces (a) emitter fixes (AOA/TDOA/class) at cue rate, and (b) "
        "bistatic tracks of illumination echoes (air targets). Active chain produces "
        "monostatic detections/tracks. Fusion associates by kinematic gating plus "
        "attribute likelihood and maintains a single fused picture; the arbiter converts "
        "association gaps into active dwell requests (M1/M3) or into silence (M0)."))

A(('h1', 'Coherent timing architecture'))
A(('p', "CAF processing gain is only realised if reference and surveillance channels share "
        "phase noise and drift over the integration time; the active chain already requires "
        "tile-to-tile coherence (MTS). One clock plant therefore serves both:"))
A(('b', ["Site 10 MHz reference (GPSDO class) -> clock generator board (board A role).",
         "Clock generator outputs: RFDC ADC/DAC sampling clocks and SYSREF, PL fabric clocks "
         "(245.76 MHz family as in the validated build), PS clocks.",
         "All RFDC tiles programmed for multi-tile sync so that every converted channel has "
         "a deterministic phase relationship [validated practice in GPV full BD flow].",
         "Residual phase drift budget over CAF integration T_int: <= 5 deg rms [budget], "
         "i.e. for DVB-T at 600 MHz and T_int = 1 s the clock plant must hold ~1.4e-14 "
         "Allan deviation over 1 s - trivially met by a common clock, impossible with two "
         "free-running receivers. This is the single strongest argument for the "
         "single-box integrated design."]))
A(('eq', 'phi_drift = 2*pi*f_c*tau_drift ;  require phi_drift <= pi/36 over T_int'))
A(('note', "The passive receiver is NOT a separate box: a separate passive receiver would "
           "need its own disciplined oscillator and a phase-stable distribution path; the "
           "single XCZU48DR box removes that error term entirely."))

A(('h1', 'Active sub-system: inherited validated baseline'))
A(('p', "The active chain is frozen. Its algorithmic truth is GPM v1.8 "
        "(gpr_pipeline_spec.m, validate_package.m, 83 checks) and its hardware truth is GPV "
        "(14 RTL modules, 10/10 testbenches bit-exact against golden ROMs generated by "
        "make_golden.m). This book adds nothing to it; it only states the interface the "
        "integrated system relies on."))
A(('h2', 'Configuration envelopes [validated]'))
A(('t', ['Parameter', 'Mode A (wideband search)', 'Mode B (focused deep)'],
   [['RF span', '0.5 - 3.0 GHz', '10 - 100 MHz',],
    ['Tones per dwell', '256', '256 (golden ROMs; config field says 512 - see GPV PROVENANCE)',],
    ['Dwell / positions', '50 us, 200 positions', 'per config',],
    ['Coherent averages n_avg', '32', 'per config',],
    ['Range IFFT', '2048 pt, Kaiser beta = 8', 'same',],
    ['CFAR', 'mean-CFAR, Pfa 1e-6, guard 8 / train 16', 'log-CFAR, Pfa 1e-5',],
    ['Golden results', 'max_bin 235, band [11,233], n_subband 21, 41 CFAR dets',
     'max_bin 302, band [33,300], n_subband 1',]]))
A(('h2', 'Hardware interface [validated]'))
A(('b', ["RFDC RX: tile 2 block 2 (channel 224), 4.9152 GSPS, 4x decimation in the RFDC DDC.",
         "AXI-Lite control map 0x00-0xB4 (ID/CTRL/STATUS/IRQ, config, SB_CENTER_FW "
         "correction offset, REP1-6, counters); IRQ = rep_done event.",
         "PS runtime skeleton: software/ps/gpr_ps_runtime.c services sb_req/retune and the "
         "frame cycle; the RAP fusion engine extends this service loop (section 20).",
         "Subband plan generator software/ps/gpr_subband_plan.py is bit-exact against the "
         "golden ROMs in both modes; the integrated system reuses it unchanged."]))
A(('h2', 'What the integrated system demands from the active chain'))
A(('b', ["Short-confirm dwell capability: a dwell request with reduced tone count and "
         "reduced positions around a cued range/angle cell (parameter set, not new RTL).",
         "Deterministic TX blanking window output so the passive surveillance channels can "
         "gate out own-TX interference (one GPIO/AXI status bit, see section 18).",
         "Timestamped detection reports in the existing REP registers plus a frame counter "
         "traceable to the common clock (already present via frame cycle)."]))

A(('h1', 'Passive sub-system: illuminators of opportunity'))
A(('p', "A PCL receiver's range/Doppler performance is set by the illuminator waveform, not "
        "by the receiver. The candidate set below covers 87.5 MHz - 2.7 GHz so that the "
        "RFDC can sample every channel directly (section 18). Range resolution is the "
        "monostatic-equivalent c/(2B); in bistatic geometry it degrades by 1/cos(beta/2) "
        "with bistatic angle beta [derived]."))
A(('t', ['Illuminator', 'Band', 'Channel BW B', 'c/(2B) [derived]', 'Integration behaviour', 'Role in RAP'],
   [['FM broadcast', '87.5-108 MHz', '200 kHz', '750 m',
     'Analogue modulation: ambiguity sidelobes follow programme content; long T_int averages them down',
     'Long-range cue, Doppler-only track',],
    ['DAB (COFDM)', '174-240 MHz', '1.536 MHz', '98 m',
     'Continuous OFDM with pilots; clean thumbtack-like CAF after pilot handling', 'Primary VHF track illuminator',],
    ['DVB-T (COFDM)', '470-862 MHz', '7.61 MHz', '19.7 m',
     'Cyclic prefix sets a CAF ambiguity ridge at tau = Tu; guard-band pilots must be filtered',
     'Primary UHF fine-range illuminator',],
    ['LTE FDD downlink', '700-2600 MHz', '5-20 MHz', '30-7.5 m',
     'Traffic-dependent ambiguity; cell-specific references stabilise it',
     'Urban fine resolution, short ranges',],
    ['GSM downlink', '900/1800 MHz', '200 kHz bursts', '750 m',
     'Burst structure => Doppler ambiguities at 1/T_burst; usable for Doppler cues', 'Fallback / cross-check',]]))
A(('h2', 'Illuminator selection policy'))
A(('p', "At start-up and every N minutes the passive chain measures per-channel reference "
        "SNR and CAF peak sharpness and ranks illuminators; the top two per band are "
        "assigned to processing lanes (section 18). Sites with weak DVB-T fall back to "
        "DAB+FM; the policy is data-driven, never hardcoded [budget: re-rank period 300 s]."))

A(('h1', 'Passive RF front end and channelisation'))
A(('h2', 'Channel set'))
A(('t', ['Channel', 'Antenna', 'RFDC input', 'Purpose'],
   [['REF-k (k = 1..2)', 'Directive yagi/patch aimed at illuminator k', 'ADC tile 0, blocks 0-1',
     'Clean copy of illuminator waveform',],
    ['SURV-1..4', 'Omnidirectional or ULA elements', 'ADC tile 0 blocks 2-3 + tile 1 blocks 0-1',
     'Target echoes + direct-path interference + clutter',],
    ['AUX-TX monitor', 'Coupler from active TX (board B coupler)', 'ADC tile 1 block 2',
     'Own-TX blanking reference and M4 calibration',]]))
A(('h2', 'Sampling and Nyquist zones [derived]'))
A(('p', "All passive ADCs run at 2.4576 GSPS (half the validated active rate, same clock "
        "family): Nyquist zone 1 covers DC-1.2288 GHz, which contains FM, DAB and the lower "
        "DVB-T band; upper DVB-T and LTE channels are taken in zone 2 (1.2288-2.4576 GHz) "
        "with the RFDC DDC tuned per channel. RFDC DDC decimation 32x gives a 76.8 MS/s "
        "fabric rate per channel - ample for the widest 20 MHz LTE channel after "
        "channelisation."))
A(('eq', 'f_fabric = f_adc / D = 2.4576e9 / 32 = 76.8e6  [derived]'))
A(('h2', 'Front-end requirements'))
A(('b', ["Reference channel: enough directivity that target echoes in REF are <= -20 dB "
         "below the illuminator copy (else signal cancellation, section 12).",
         "Surveillance channels: linearity set by direct-path interference (DPI), which can "
         "be 60-90 dB above target echoes; AGC must hold the ADC below clipping on DPI.",
         "Preselector filters per band to keep out-of-band broadcast energy out of the "
         "cancellation loop; group-delay matched cables so REF/SURV delay offset is a "
         "constant, calibratable tap shift."]))

A(('h1', 'Interference and clutter cancellation'))
A(('p', "Two cancellation problems must be solved before the CAF: direct-path interference "
        "(transmitter seen directly in SURV) and static clutter/multipath (zero-Doppler "
        "ridge). Both are solved by subtracting filtered copies of the REF waveform; the "
        "classical, robust choice is the Extensive Cancellation Algorithm (ECA): batch-wise "
        "least-squares projection, with per-Doppler-shifted replicas for clutter."))
A(('h2', 'DPI cancellation (ECA, batch b)'))
A(('eq', 'x_surv_clean[b] = x_surv[b] - sum_{m=0..M-1} w_m * x_ref[b-m] ,  w = argmin || . ||^2'))
A(('p', "M taps cover the differential delay spread (cable + multipath); a batch length of "
        "0.1-0.5 s keeps the filter quasi-static while allowing kHz-scale Doppler search "
        "afterwards [budget]."))
A(('h2', 'Clutter cancellation (Doppler-shifted ECA)'))
A(('eq', 'residual = x_clean - proj{ x_ref * exp(j 2 pi f_d t) } over f_d in clutter band +-f_c_max'))
A(('p', "The achievable Extensive Cancellation Ratio (ECR) sets the noise floor: with "
        "reference SNR >> 1 the residual floor is k*T0*B*F times (1/ECR). Requirement:"))
A(('eq', 'ECR_req[dB] >= DPI_above_target[dB] + margin ;  typical DPI 70 dB, margin 10 dB => ECR >= 80 dB [budget]'))
A(('note', "ECA (block least-squares) is chosen over NLMS adaptation because its batch "
           "structure maps directly onto the existing GPV matrix/DSP discipline (BRAM "
           "blocks, deterministic latency) and because its numerical behaviour is exactly "
           "predictable in fixed point - the same reason the validated chain avoids "
           "adaptive structures it cannot verify bit-exact."))

A(('h1', 'Cross-ambiguity function and range-Doppler formation'))
A(('h2', 'CAF definition'))
A(('eq', 'chi(tau, f_d) = sum_t x_surv_res[t] * conj(x_ref[t - tau]) * exp(j 2 pi f_d t)'))
A(('p', "Implemented as: range compression per batch by frequency-domain correlation "
        "(FFT/IFFT pair on the RFDC fabric rate), then Doppler FFT across batches per range "
        "gate. Processing gain G = B * T_int [derived]:"))
A(('t', ['Illuminator', 'B', 'T_int', 'G = B*T_int [derived]'],
   [['FM', '200 kHz', '10 s', '63 dB',],
    ['DAB', '1.536 MHz', '2 s', '64.9 dB',],
    ['DVB-T', '7.61 MHz', '1 s', '68.8 dB',],
    ['LTE 20 MHz', '20 MHz', '0.5 s', '70 dB',]]))
A(('h2', 'Bistatic radar equation (passive link budget)'))
A(('eq', 'SNR = (P_t G_t G_r lambda^2 sigma_b ECR_eff) / ((4 pi)^3 R_t^2 R_r^2 k T0 B F L) * (B T_int)'))
A(('p', "with R_t transmitter-to-target and R_r target-to-receiver ranges. Because P_t G_t "
        "of broadcast transmitters is 10^4-10^5 W ERP class, SNR after gain is positive for "
        "air targets at tens of km even with sigma_b = 0.1 m2 [derived, site-dependent]; "
        "the book carries the equation and the budget table, site surveys fill the values."))
A(('h2', 'Ambiguity and sidelobe control'))
A(('b', ["DVB-T cyclic-prefix ridge: suppress by excluding tau = Tu or by CP-aware reference "
         "filtering (reference channel equalisation).",
         "FM programme sidelobes: reciprocal-filtering or long T_int; accept degraded "
         "range-sidelobe level (-25 dB class) and rely on CFAR guard cells.",
         "LTE traffic nulls: reference-channel spectral whitening before CAF.",
         "Range-Doppler map CFAR: 2-D CA-CFAR with guard 2x2 and train 8x8 cells on the "
         "log-magnitude map, Pfa 1e-6 [budget, mirrors validated active CFAR discipline]."]))

A(('h1', 'Direction of arrival and emitter geolocation'))
A(('h2', 'Surveillance array'))
A(('p', "SURV-1..4 form a 4-element uniform linear array (half-wavelength at 550 MHz "
        "compromise spacing, or switchable spacing per band [budget]). DOA per detected "
        "range-Doppler cell by beamscan (robust, low resource) with MUSIC as an option for "
        "co-channel separation:"))
A(('eq', 'sigma_theta ~= lambda / (2 pi d cos(theta) sqrt(2 SNR N_snap))  [derived, CRLB form]'))
A(('h2', 'Emitter geolocation (T1/T4 threats)'))
A(('b', ["AOA from the array on the emitter's own transmission (no illuminator needed): "
         "wideband correlator DOA over the emitter bandwidth.",
         "TDOA between RAP sites (if a second RAP node exists on the site grid): time "
         "difference of the emitter waveform arrival, common 10 MHz site reference makes "
         "this coherent.",
         "Single-site fix = AOA + (TDOA hyperbola if second node) or AOA + power-vs-range "
         "prior; the fusion engine carries the covariance accordingly.",
         "Emitter classification by spectral signature family (constant-envelope analogue, "
         "OFDM, FH burst, pulse radar PRI) feeding the threat table of section 2."]))

A(('h1', 'Passive detection and tracking'))
A(('b', ["Detection: 2-D CA-CFAR on each illuminator's range-Doppler map; detections carry "
         "(bistatic range, Doppler, DOA, SNR, illuminator id, frame timestamp).",
         "Per-illuminator bistatic tracking: UKF in bistatic coordinates (R_b = R_t + R_r, "
         "Doppler, DOA) with conversion to site Cartesian at fusion.",
         "Emitter tracks: AOA(/TDOA) filters with class-dependent motion models "
         "(static bug vs moving UAV vs airborne radar platform).",
         "Track lifecycle mirrors the validated chain's philosophy: deterministic gates, "
         "no adaptive structures that cannot be golden-modelled."]))

A(('h1', 'Fusion, cueing and the EMCON arbiter'))
A(('h2', 'Association'))
A(('p', "Passive bistatic tracks and emitter fixes are associated to active tracks by "
        "kinematic gating (Mahalanobis distance in site Cartesian) plus attribute "
        "likelihood (Doppler agreement between passive f_d and active radial, class "
        "agreement). Track-to-track fusion with covariance intersection keeps both chains' "
        "filters independent - deliberately avoiding a centralised filter that would couple "
        "their noise models."))
A(('h2', 'Cueing rules'))
A(('t', ['Cue source', 'Condition', 'Arbiter action'],
   [['Passive emitter fix (T1/T4)', 'class in {bug, uplink, hostile radar}, SNR > thr',
     'M0 hold; report to operator; T4 => active stays silent',],
    ['Passive bistatic track (T2)', 'track age >= 3 updates, no active correlate',
     'M1: grant short confirm dwell at cued range/DOA cell',],
    ['Active detection without passive correlate (T3)', 'CFAR + cluster valid',
     'M3 track; passive asked to sweep for emissions at the track position',],
    ['Association gap > T_gap', 'fused track coasting', 're-grant dwell or declare lost per policy',]]))
A(('h2', 'Latency budget [budget]'))
A(('t', ['Step', 'Budget'],
   [['Passive CAF update (DVB-T lane)', '1.0 s integration + 0.1 s process',],
    ['Cue to active confirm dwell grant', '<= 0.2 s',],
    ['Active confirm dwell + report', '<= 0.3 s (reduced tone set)',],
    ['End-to-end cue-to-fused-track', '<= 2.5 s',]]))

A(('h1', 'XCZU48DR implementation partition'))
A(('h2', 'RFDC allocation'))
A(('t', ['Function', 'RFDC channel', 'Rate', 'DDC'],
   [['Active RX (validated)', 'ADC tile 2 blk 2 (224)', '4.9152 GSPS', '4x',],
    ['Active TX (DDS-driven)', 'DAC per validated BD', 'per validated BD', '4x',],
    ['REF-1 / REF-2', 'ADC tile 0 blk 0/1', '2.4576 GSPS', '32x',],
    ['SURV-1..4', 'ADC t0 b2, t0 b3, t1 b0, t1 b1', '2.4576 GSPS', '32x',],
    ['AUX-TX monitor', 'ADC tile 1 blk 2', '2.4576 GSPS', '32x',]]))
A(('p', "ZU48DR provides 8 RF-ADCs; the allocation above uses 8 of 8 (active + 2 ref + 4 "
        "surv + 1 aux). No spare ADC remains - a fifth surveillance element would require "
        "element multiplexing per band [budget note]."))
A(('h2', 'PL fabric budget [budget]'))
A(('t', ['Function', 'DSP slices (est)', 'BRAM (est, Kb)', 'Notes'],
   [['Active chain (validated)', 'as synthesised in GPV', 'as synthesised', 'frozen',],
    ['Channelisation + resample (6 lanes)', '240', '128', 'FIR/CIC per lane',],
    ['ECA cancellers (2 illuminators)', '180', '512', 'batch LS via QR or normal equations',],
    ['CAF range compression', '420', '1024', 'FFT/IFFT 8k-16k per batch',],
    ['Doppler FFT + map memory', '240', '2048', 'map pages in URAM/DDR',],
    ['CFAR + DOA beamscan', '200', '256', 'mirrors validated CFAR structure',],
    ['Total passive add-on', '~1280', '~3968', 'ZU48DR has 4272 DSP / 60.5 Mb - feasible headroom',]]))
A(('note', "These are budgets, not measurements. Gate G-RES (section 22) requires an "
           "out-of-context synthesis of the passive lane before system integration; the "
           "validated active chain's numbers are inherited from GPV reports."))
A(('h2', 'PS/PL split'))
A(('b', ["PL: everything with per-batch determinism (channelisation, cancellation, CAF, CFAR, "
         "beamscan) - same AXI-Stream beat discipline as GPV (tdata {I,Q} Q15, tready "
         "backpressure honoured).",
         "PS: illuminator ranking, ECA weight solve supervision, trackers, fusion, EMCON "
         "arbiter, operator link - extensions of software/ps runtime skeleton.",
         "DDR: range-Doppler map pages and REF ring buffers streamed through the validated "
         "smartconnect/DDR path; bandwidth budget 76.8 MS/s x 4 B x 6 lanes = 1.84 GB/s "
         "raw, reduced to < 0.3 GB/s after PL-side cancellation+CAF [derived]."]))

A(('h1', 'Own-TX interference control (integrated-specific)'))
A(('b', ["The active TX is, to the passive SURV channels, the strongest interferer on site. "
         "Three layered defences:",
         "(1) Blanking gate: passive lanes hold CAF batch boundaries around active dwells "
         "using the TX-blanking status bit; batches containing a dwell are discarded or "
         "interpolated.",
         "(2) AUX-TX monitor cancellation: the coupled TX copy enters the ECA tap set as an "
         "extra reference, so residual TX leakage inside kept batches is projected out.",
         "(3) Frequency planning: active subband plan (gpr_subband_plan.py) and passive "
         "lane tuning are jointly scheduled so active tones never sit inside a passive "
         "lane's channelised band when M1/M3 is active."]))
A(('note', "Blanking loses integration time; the scheduler prices it: dwell grants reduce "
           "passive gain by B*T_lost, which the fusion engine accounts for in cue "
           "confidence."))

A(('h1', 'PS software extension'))
A(('b', ["Register map extension at 0x100+: PASS_CTRL, PASS_STATUS, ILLUM_RANK table, "
         "LANE_tune (DDC NCO per lane), CAF_CFG (T_int, batches, Doppler span), ECR_MON "
         "(residual power taps), CUE_FIFO (read-out cues), EMCON_POLICY.",
         "Runtime loop extension: the existing retune/frame service loop gains a passive "
         "service slice executed per CAF batch interrupt (new IRQ bit, W1C like 0x0C).",
         "Fusion engine as a PS task consuming CUE_FIFO + active REP registers; outputs "
         "fused track table and dwell grants through the existing CTRL/retune path.",
         "Data contract to workstation: extend the GPV offline protocol with passive map "
         "pages and cue records; keep integer-only, self-describing headers (the discipline "
         "that made golden ROM comparison bit-exact)."]))

A(('h1', 'Validation plan'))
A(('h2', 'Golden model extension (MATLAB, GPM discipline)'))
A(('b', ["passive_channel_sim.m: illuminator waveforms (FM stereo composite, DAB/DVB-T "
         "CP-OFDM with pilots, LTE DL grid), bistatic target echoes, DPI geometry, clutter "
         "patch set - integer-exportable for ROM comparison.",
         "pcl_chain_ref.m: channelisation, ECA, CAF, CFAR, DOA reference implementation with "
         "the same fixed-point rounding rules as make_golden.m.",
         "fusion_ref.m: association + CI fusion + arbiter state machine, scenario-driven.",
         "Acceptance: PL testbenches bit-exact vs exported ROMs (GPV convention), PS "
         "fusion traces equal to fusion_ref within stated quantisation."]))
A(('h2', 'Testbench list (additions to GPV tb set)'))
A(('t', ['TB', 'Checks'],
   [['tb_chan', 'DDC/decimation lanes: tone placement, group delay',],
    ['tb_eca', 'DPI suppression >= modelled ECR on synthetic DPI+target',],
    ['tb_caf', 'CAF peak position/gain vs pcl_chain_ref on golden ROM',],
    ['tb_cfar2d', 'Pfa on noise-only maps; detection on planted targets',],
    ['tb_doa', 'beamscan/MUSIC angle error vs CRLB trend',],
    ['tb_blank', 'blanking gate: no CAF batch corruption across a dwell',],
    ['tb_fusion_ps', 'PS trace vs fusion_ref scenarios (cue, confirm, gap)',]]))
A(('h2', 'Gates'))
A(('n', ["G0 golden ROMs exported and plan/rounding cross-check PASS (mirrors --check-rom).",
         "G1 lane + ECA TBs bit-exact.",
         "G2 CAF/CFAR/DOA TBs bit-exact or within stated LSB bounds.",
         "G-RES passive lane out-of-context synthesis within budget table.",
         "G3 integrated regression: active 10/10 unchanged + passive TBs PASS.",
         "G4 hardware loopback (cable bistatic): CAF peak at cable delay/Doppler offset.",
         "G5 field trial: illuminator survey, ECR measurement, cue-to-confirm timeline."]))

A(('h1', 'Failure modes and diagnostics'))
A(('t', ['Failure', 'Observable', 'Mitigation'],
   [['Reference channel contaminated by target echo', 'CAF peak suppression / split peak',
     'REF SNR monitor + directive antenna; flag lane degraded',],
    ['Co-channel second illuminator', 'second ridge in CAF', 'whitening; lane rank drop',],
    ['Clock plant unlock', 'CAF gain collapse across all lanes at once', 'holdover alarm; M0 until relock',],
    ['Own-TX leakage residual', 'ridge at zero bistatic range during dwells', 'AUX cancellation tap health; blanking audit',],
    ['Multipath ghost tracks', 'tracks mirrored across reflector geometry', 'DOA-vs-bistatic consistency gate',],
    ['Illuminator outage (transmitter off)', 'REF power drop', 're-rank; fall back per band policy',],
    ['EMCON conflict (operator vs arbiter)', 'grant log mismatch', 'operator override always wins, logged',]]))

A(('h1', 'Requirements traceability (top level)'))
A(('t', ['Req', 'Statement', 'Subsystem', 'Validation'],
   [['REQ-CS-001', 'Detect T1 emitters 30 MHz-6 GHz, silent mode', 'Passive geolocation', 'G5 + fusion_ref',],
    ['REQ-CS-002', 'Detect T2 UAV via cue-confirm <= 2.5 s', 'Fusion + active confirm', 'tb_fusion_ps, G5',],
    ['REQ-CS-003', 'Hold T3 RF-silent targets', 'Active chain', 'GPV 10/10 + G3',],
    ['REQ-CS-004', 'Own emission bounded by EMCON policy', 'Arbiter', 'grant log audit',],
    ['REQ-CS-005', 'Passive lane coherence over T_int', 'Timing unit', 'G4 CAF gain vs theory',],
    ['REQ-CS-006', 'No regression of validated active chain', 'All', 'G3 active 10/10',]]))

A(('h1', 'References and provenance'))
A(('n', ["GPM repository v1.8 (MATLAB/Simulink validated package) - active algorithm truth.",
         "GPV repository, branch ps-runtime - validated RTL, PS runtime, subband plan.",
         "GPR_SFCW_Engineering_Design_Book_RFSoC48DR_v1.4 - active RF hardware boards A-E.",
         "AMD UG1410 (ZCU208 board), PG269 (RF Data Converter), ZCU208 kit page (XCZU48DR "
         "SCD5184 / FSVG1517 part note).",
         "Griffiths & Long, 'Television-based bistatic radar', 1986 - PCL foundation.",
         "Howland, 'Target tracking using television-based bistatic radar', 1999.",
         "Colone et al., 'Multistage processing for wireless LAN-based passive radar', and "
         "ECA family: Bournaka et al., 'A two stage algorithm for phase cancellation in "
         "DVB-T based passive radar', 2008.",
         "Skolnik, Radar Handbook - bistatic equations and CFAR discipline."]))

# ----------------------------------------------------------------------------
# BOOK 2 - passive-only counter-surveillance radar
# ----------------------------------------------------------------------------
B2 = []
A = B2.append
A(('h1', 'Document map and engineering scope'))
A(('p', "This book defines the PASSIVE-ONLY configuration of the counter-surveillance "
        "radar family: a standalone passive coherent location (PCL) and emitter-geolocation "
        "system with no transmitter of its own. It shares the passive sub-system design "
        "with the RAP integrated book (RAP-EDB-001) but is complete on its own: mission, "
        "illuminators, front end, cancellation, CAF, DOA, tracking, geolocation, spectrum-"
        "surveillance mode, XCZU48DR standalone partition, software, validation and failure "
        "modes. Where the integrated book adds fusion with an active radar, this book "
        "instead adds multi-site passive coherence and long-duration silent operation."))
A(('t', ['Rev', 'Date', 'Change'], [['1.0', DATE, 'First issue.']]))

A(('h1', 'Mission: silent counter-surveillance'))
A(('p', "The passive-only system never radiates. Its mission value is threefold: (1) it "
        "cannot be detected by a hostile RF-seeking sensor (T4), so it survives the "
        "contested electromagnetic environment; (2) it sees covert emitters (T1) that no "
        "radar can see; (3) it provides cue-quality air pictures from broadcast "
        "illuminators at ranges beyond small-radar horizon. Its limitations are equally "
        "explicit: no coverage against RF-silent targets, range accuracy bounded by "
        "illuminator bandwidth, and dependence on third-party transmitters."))
A(('h2', 'Operational profiles'))
A(('t', ['Profile', 'Description'],
   [['P-SENTRY', 'Permanent silent site guard: 2 illuminator lanes + emitter scan, hours-long CPIs where bandwidth allows.',],
    ['P-DEPLOY', 'Rapid-deploy node on the site grid: battery/vehicle power, TDOA partner to other nodes.',],
    ['P-HUNT', 'Operator-directed emitter hunt: wideband spectrum survey + DOA walk, recording evidence chain.',]]))

A(('h1', 'Illuminators and waveforms'))
A(('p', "Identical candidate set and selection policy as RAP-EDB-001 section 9; repeated "
        "here for standalone completeness with the passive-only emphasis on long CPIs:"))
A(('t', ['Illuminator', 'B', 'c/(2B) [derived]', 'Best CPI', 'Silent-mode value'],
   [['FM', '200 kHz', '750 m', '10-60 s', 'Doppler-only air cue at very long range',],
    ['DAB', '1.536 MHz', '98 m', '2-10 s', 'Stable VHF track lane',],
    ['DVB-T', '7.61 MHz', '19.7 m', '0.5-2 s', 'Fine bistatic range, urban',],
    ['LTE DL', '5-20 MHz', '30-7.5 m', '0.2-1 s', 'Fine short-range, dense urban',],
    ['GSM DL', '200 kHz', '750 m', 'burst-limited', 'Cross-check lane',]]))
A(('p', "Long CPIs on narrowband illuminators trade range resolution for enormous "
        "Doppler resolution: delta_v = lambda / (2 T_int cos(beta/2)) [derived]; FM at "
        "100 MHz with T_int = 60 s resolves ~0.15 m/s radial - enough to separate "
        "hovering vs transiting UAVs by micro-Doppler sidebands."))
A(('eq', 'delta_f_d = 1 / T_int ;  delta_v = lambda / (2 T_int cos(beta/2))'))

A(('h1', 'Receiver architecture (standalone box)'))
A(('p', "One XCZU48DR box with: 2 reference channels (directive), 4 surveillance channels "
        "(ULA), 1 wideband spectrum-survey channel (switchable or 5th element via RF "
        "switch matrix [budget]), common clock plant as in RAP-EDB-001 section 5 (no active "
        "chain to share, but multi-node TDOA still demands site-disciplined 10 MHz)."))
A(('t', ['Channel', 'RFDC', 'Rate', 'Use'],
   [['REF-1/2', 'ADC t0 b0/b1', '2.4576 GSPS, DDC 32x', 'Illuminator copies',],
    ['SURV-1..4 (ULA)', 't0 b2, t0 b3, t1 b0, t1 b1', '2.4576 GSPS, DDC 32x', 'Echoes + DOA',],
    ['SURVEY', 't1 b2', '2.4576 GSPS, DDC bypass-ish 4x', 'Wideband emitter scan 0-1.2 GHz zone 1',]]))
A(('h2', 'Multi-node coherence'))
A(('b', ["Two or more passive nodes on the site grid share the 10 MHz site reference "
         "(fiber/white-rabbit class distribution [budget]) enabling TDOA geolocation and "
         "coherent map fusion.",
         "Per-node timestamps derive from the common reference so cue records from "
         "different nodes associate without resynchronisation."]))

A(('h1', 'Cancellation, CAF, detection (standalone restatement)'))
A(('p', "The processing chain is identical to RAP-EDB-001 sections 10-12: ECA DPI "
        "cancellation, Doppler-shifted clutter cancellation with ECR >= 80 dB budget, "
        "batch CAF with G = B*T_int, 2-D CA-CFAR (Pfa 1e-6 budget), beamscan/MUSIC DOA. "
        "Differences for standalone operation:"))
A(('b', ["No own-TX blanking needed (no transmitter): CPI scheduling is free, which is why "
         "the passive-only box can run the long FM CPIs the integrated system must "
         "interrupt.",
         "Survey channel duty-cycles against CAF lanes only by fabric time-slice, not by RF "
         "conflict.",
         "Evidence-chain recording: every emitter fix stores raw IQ snippet hashes for "
         "later forensic replay (counter-surveillance reporting requirement)."]))

A(('h1', 'Emitter geolocation and classification'))
A(('h2', 'Fix construction'))
A(('n', ["Single node: AOA from ULA on emitter waveform (wideband correlator DOA).",
         "Two nodes: AOA + TDOA hyperbola => 2-D fix with covariance from CRLB of both "
         "observables.",
         "Three+ nodes: TDOA least-squares fix; AOA used for gating only.",
         "Altitude: unresolved without a third vertical baseline; reported as 2-D fix with "
         "altitude-unbounded covariance (honest error model)."]))
A(('h2', 'Classification feature set'))
A(('t', ['Feature', 'Discriminates'],
   [['Occupied bandwidth / mask shape', 'analogue video vs WiFi vs narrowband radio',],
    ['Modulation family (OFDM cyclic prefix length, FSK deviation)', 'WiFi 20/40/80 MHz, LTE, DMR',],
    ['Burst/PRI structure', 'FH radios, pulse radars, TDMA uplinks',],
    ['Doppler sideband pattern', 'rotor micro-Doppler on UAV video links',],
    ['Persistence / duty cycle', 'covert implant (scheduled beacon) vs operator-held radio',]]))
A(('p', "Classification outputs a likelihood vector over the threat table (RAP-EDB-001 "
        "section 2); no hard decision is made below a stated confidence [budget 0.8]."))

A(('h1', 'Spectrum-surveillance mode (P-HUNT)'))
A(('b', ["Sweep plan: zone-1 coarse sweep (0-1.2288 GHz) at 76.8 MS/s fabric slices, "
         "spectrogram pages to PS; detector: log-mean CFAR across frequency with occupancy "
         "mask of known-friendly emitters (site radio plan).",
         "On new emitter: auto-slice a narrowband record (IQ + metadata), estimate "
         "features, hand to classification, then schedule DOA walks interleaved with CAF "
         "lane duty.",
         "Output: evidence package (time, frequency mask, features, AOA(/fix), IQ hash)."]))

A(('h1', 'XCZU48DR standalone partition and resources'))
A(('p', "Without the active chain the fabric budget of RAP-EDB-001 section 18 loses the "
        "frozen active block and gains the survey slicer: passive add-on ~1280 DSP + "
        "survey ~150 DSP [budget]; BRAM/URAM dominated by long-CPI REF ring buffers "
        "(60 s FM CPI at 76.8 MS/s x 2 B x 2 ref = 18.4 GB => REF rings live in PS DDR, "
        "PL holds batch windows only [derived])."))
A(('note', "Long CPIs are a memory-system design, not a DSP design: batch streaming from "
           "DDR with deterministic replay is the same discipline the validated chain uses "
           "for frame buffers."))
A(('h2', 'Power and thermal'))
A(('p', "Silent operation removes TX power; box power is RFSoC + clock plant class, "
        "battery-profiled for P-DEPLOY [budget 60 W typical]."))

A(('h1', 'Software'))
A(('b', ["PS runtime: same skeleton discipline as GPV software/ps (service loop, IRQ W1C, "
         "integer data contract), register map 0x00-0xFF passive-only variant: PASS_CTRL, "
         "LANE_tune, CAF_CFG, ECR_MON, SURVEY_PLAN, EVID_FIFO, NODE_ID/TDOA_CLK.",
         "Node coordination: cue/fix exchange over site LAN with common-reference "
         "timestamps; a coordinator node runs the multi-node fix least-squares.",
         "Operator workstation: range-Doppler lanes, DOA roses, emitter table, evidence "
         "browser; offline replay from recorded IQ (same offline philosophy as GPM/GPV "
         "packages)."]))

A(('h1', 'Validation plan (passive-only)'))
A(('b', ["Golden: passive_channel_sim.m + pcl_chain_ref.m shared with RAP book; added "
         "geolocation_ref.m (AOA/TDOA CRLB-consistent) and survey_ref.m.",
         "TBs: tb_chan, tb_eca, tb_caf, tb_cfar2d, tb_doa (shared) + tb_tdoa (two-node "
         "timestamp association), tb_survey (mask/CFAR on synthetic spectrum).",
         "Gates G0-G2 as RAP book; G4' = cable TDOA/DOA loopback; G5' = field: ECR survey, "
         "emitter fix accuracy vs surveyed truth points, evidence-package audit."]))
A(('h2', 'Acceptance metrics [budget]'))
A(('t', ['Metric', 'Target'],
   [['ECR on strongest DPI', '>= 80 dB',],
    ['CAF gain vs theory', 'within 1 dB',],
    ['AOA rms (SNR >= 20 dB, in-band)', '<= 3 deg',],
    ['Two-node fix CEP50 (urban, DVB-T lane)', '<= 150 m',],
    ['Emitter detection sensitivity', '-100 dBm in-band, Pd 0.9 @ 1e-6 FA/h',]]))

A(('h1', 'Failure modes and diagnostics (passive-only)'))
A(('t', ['Failure', 'Observable', 'Mitigation'],
   [['Illuminator maintenance outage', 'REF power drop, lane dead', 're-rank; profile degrades gracefully',],
    ['Site reference distribution fault (multi-node)', 'TDOA residuals jump', 'fall back to single-node AOA fixes',],
    ['ULA element fault', 'DOA bias/sidelobe rise', 'element health tone injection; array recal',],
    ['Dense co-channel emitters', 'classification confidence collapse', 'report as unresolved cluster, never force class',],
    ['Survey self-blindness during long CPI', 'missed new emitters', 'interleaved survey slices priced into CPI schedule',]]))

A(('h1', 'References and provenance'))
A(('n', ["RAP-EDB-001 (integrated book) - shared passive sub-system sections.",
         "GPV ps-runtime / GPM v1.8 - software and validation discipline, RFDC practice.",
         "UG1410, PG269 - board and converter facts.",
         "Griffiths & Long 1986; Howland 1999; Colone et al. (ECA/multistage); Bournaka et "
         "al. 2008; Malanowski et al. on DAB/DVB-T PCL; Skolnik Radar Handbook.",
         "IEEE standards on emitter classification are not assumed; feature set is "
         "engineering practice, flagged [budget] where thresholds are site-tuned."]))

def build(path, title, subtitle, docnum, items):
    d = new_doc()
    title_page(d, title, subtitle, docnum, "1.0")
    emit(d, items)
    d.core_properties.title = title
    d.core_properties.author = "GPV engineering documentation"
    d.core_properties.comments = docnum
    d.save(path)
    return path

if __name__ == '__main__':
    import sys
    out1, out2 = sys.argv[1], sys.argv[2]
    build(out1, "RAP - Integrated Active-Passive Counter-Surveillance Radar System",
          "Engineering Design Book: coherent fusion of the validated SFCW active radar "
          "with a passive coherent location receiver on one XCZU48DR platform",
          "RAP-EDB-001", B1)
    build(out2, "Passive-Only Counter-Surveillance Radar System",
          "Engineering Design Book: silent PCL and emitter geolocation on XCZU48DR, "
          "no transmitter of own",
          "PCL-EDB-002", B2)
    print("books written:", out1, out2)
