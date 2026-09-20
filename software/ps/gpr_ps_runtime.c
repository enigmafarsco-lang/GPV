/* ---------------------------------------------------------------------------
 * gpr_ps_runtime.c - PS/R5 orchestration skeleton for the GPV PL chain
 *                    (AMD RFSoC ZCU208, gpr_top_zcu208 + gpr_rx_adapter).
 *
 * Adapted from gpr-hybrid-v3 software/ps/gpr_rfsoc_runtime_v3.c (service-loop
 * contract, readiness gating).  Retargeted to THIS project's register map and
 * handshakes - see fpga README.md section 3 and golden/regs_a.vh / regs_b.vh
 * for the mode presets.  BSP-dependent parts stay behind hooks; wire them to
 * XRFdc (from the actual XSA) and to the EMIO/GPIO lines carrying sb_req /
 * sb_ack (and irq, if not using the GIC).
 *
 * Design rules adopted from the v3 review (BRINGUP_GATES.md):
 *   - acquisition starts only when RFDC ready AND MTS locked AND clocks locked;
 *   - sb_ack pulses only AFTER both DAC and ADC mixer updates have committed
 *     at the deterministic MTS update boundary;
 *   - the PL RX scheduler (gpr_rx_adapter) is the single timing source; the PS
 *     never attaches metadata to converter data.
 * ------------------------------------------------------------------------- */
#include <stdint.h>

/* ---- GPV AXI-Lite register map (byte offsets) ---------------------------- */
#define GPR_ID            0x00u   /* 0x47505218                                   */
#define GPR_CTRL          0x04u   /* bit0 run (one-shot frame), bit1 loop_mode    */
#define GPR_STATUS        0x08u   /* bit1 irq_ev, [23:8] frame_count, bit24 ovr   */
#define GPR_IRQ           0x0Cu   /* bit0 irq_ev (W1C), bit1 irq_en               */
#define GPR_DWELL_CYC     0x10u
#define GPR_NAVG_M1       0x14u
#define GPR_AGC_Q14       0x18u
#define GPR_FFTGAIN_Q10   0x1Cu
#define GPR_NBG           0x20u
#define GPR_INV_DR_Q20    0x24u
#define GPR_ROFF_Q20      0x28u
#define GPR_DX_Q20        0x2Cu
#define GPR_DR_Q20        0x30u
#define GPR_KBETA_Q16     0x34u
#define GPR_ALPHA2_Q8     0x38u
#define GPR_MAXBIN_SCALE  0x3Cu   /* [31:16] out_scale_q8, [15:0] max_bin         */
#define GPR_BMIN0         0x44u
#define GPR_BMAX0         0x48u
#define GPR_CFAR_MODE     0x4Cu
#define GPR_ALPHA_Q12     0x50u
#define GPR_LOG2ALPHA     0x54u
#define GPR_GAMMA2        0x58u
#define GPR_PFLOOR        0x5Cu   /* [31:16] k, [4:0] sh                          */
#define GPR_DR_Q16        0x60u
#define GPR_DX_Q16        0x64u
#define GPR_SB_CENTER_LO  0x68u   /* RX derotation correction, normally 0         */
#define GPR_SB_CENTER_HI  0x6Cu   /* see gpr_subband_plan.py docstring            */

typedef struct {
    uint16_t n_tones;            /* 256                                          */
    uint16_t n_positions;        /* 200 (mode A)                                 */
    uint8_t  n_avg_log2;         /* LOG2NAV: n_avg = 2^n (32 -> 5)               */
    uint32_t dwell_cyc;          /* fabric clocks per tone (50 us -> 12288)      */
    uint8_t  n_subbands;         /* 21 (mode A), 1 (mode B)                      */
    const uint64_t *sb_lo_word;  /* per-sub-band LO phase words (plan script)    */
} gpr_cfg_t;

typedef struct {
    uint32_t hits, nclust;
    uint32_t mean_depth_q16, mean_xrange_q16;
    uint32_t min_depth_q16, max_depth_q16;
} gpr_report_t;

/* ---- BSP hooks (implement against XRFdc / xparameters from the real XSA) -- */
uint32_t gpr_reg_read (uint32_t off);
void     gpr_reg_write(uint32_t off, uint32_t val);
int      gpr_rfdc_ready_and_mts_locked(void);           /* RFDC & MTS & clocks  */
int      gpr_rfdc_program_subband(double lo_hz);        /* DAC+ADC mixers +
                                                           deterministic update
                                                           event; 0 = committed */
int      gpr_pl_sb_req(unsigned *sb_id);                /* 1 = request pending  */
void     gpr_pl_sb_ack(int level);
int      gpr_pl_irq_pending(void);                      /* EMIO/GIC poll        */

/* ---- one sub-band retune, per the deterministic sequence ------------------ */
int gpr_service_subband(const gpr_cfg_t *cfg)
{
    unsigned sb = 0;
    if (!gpr_pl_sb_req(&sb))
        return 0;
    gpr_pl_sb_ack(0);
    if (sb >= cfg->n_subbands)
        return -1;

    double lo_hz = (double)cfg->sb_lo_word[sb];         /* word -> Hz if needed */
    if (gpr_rfdc_program_subband(lo_hz) != 0)
        return -2;                                      /* do NOT ack - retry   */

    /* SB_CENTER_FW is the RX derotation CORRECTION (fw_rom holds residual
     * words already relative to lo; see gpr_subband_plan.py).  Nominal 0. */
    gpr_reg_write(GPR_SB_CENTER_LO, 0u);
    gpr_reg_write(GPR_SB_CENTER_HI, 0u);

    gpr_pl_sb_ack(1);                                   /* pulse                */
    gpr_pl_sb_ack(0);
    return 1;
}

/* ---- one frame: run, service retunes until the report IRQ, read REP1..6 --- */
int gpr_run_frame(const gpr_cfg_t *cfg, gpr_report_t *rep)
{
    if (!gpr_rfdc_ready_and_mts_locked())
        return -1;                                      /* system_ready gate    */

    gpr_reg_write(GPR_IRQ,  0x2u);                      /* irq_en               */
    gpr_reg_write(GPR_CTRL, 0x1u);                      /* run (one-shot)       */

    for (;;) {
        int rc = gpr_service_subband(cfg);
        if (rc < 0) {
            gpr_reg_write(GPR_CTRL, 0x0u);
            return rc;
        }
        if (gpr_pl_irq_pending() ||
            (gpr_reg_read(GPR_STATUS) & (1u << 1)))      /* irq_ev fallback poll */
            break;
    }

    rep->hits            = gpr_reg_read(0x80u);
    rep->nclust          = gpr_reg_read(0x84u);
    rep->mean_depth_q16  = gpr_reg_read(0x88u);
    rep->mean_xrange_q16 = gpr_reg_read(0x8Cu);
    rep->min_depth_q16   = gpr_reg_read(0x90u);
    rep->max_depth_q16   = gpr_reg_read(0x94u);

    gpr_reg_write(GPR_IRQ, 0x1u);                       /* W1C irq_ev           */
    gpr_reg_write(GPR_CTRL, 0x0u);                      /* re-arm for next frame*/
    return 0;
}
