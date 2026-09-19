/*
 * XCZU48DR/ZCU208 GPR runtime orchestration skeleton.
 *
 * This file is intentionally board-support-package dependent. Wire it into the
 * XRFdc driver generated from the XSA exported by this build kit.
 *
 * Per SFCW tone:
 *   1) program coherent DAC and ADC mixer/NCO frequency using XRFdc;
 *   2) wait for mixer update / deterministic epoch required by your RFDC base;
 *   3) run/stream the TX dwell and collect RX DDC samples;
 *   4) the PL tone accumulator emits one complex sample/tone;
 *   5) after N tones the PL IFFT/background/CFAR chain emits one range frame.
 *
 * Calibration/window coefficients are Q1.15 complex and should be delivered
 * cyclically through the S_AXIS_CAL_COEF source (DMA/FIFO).
 *
 * Do not copy register addresses from another project. Use xparameters.h from
 * the actual XSA and generated HLS driver headers.
 */

#include <stdint.h>

typedef struct {
    uint32_t n_tones;
    uint32_t samples_per_tone;
    double f_start_hz;
    double f_step_hz;
} gpr_sweep_cfg_t;

int gpr_program_rfdc_tone(void *rfdc, double hz)
{
    (void)rfdc; (void)hz;
    /* Call XRFdc_SetMixerSettings for the selected DAC and ADC tiles/blocks,
       then apply the update event defined by the verified MTS base design. */
    return -1; /* replace with BSP-specific implementation */
}

int gpr_run_sweep(void *rfdc, const gpr_sweep_cfg_t *cfg)
{
    for (uint32_t k=0; k<cfg->n_tones; ++k) {
        double f=cfg->f_start_hz + (double)k*cfg->f_step_hz;
        if (gpr_program_rfdc_tone(rfdc,f) != 0) return -1;
        /* Synchronize TX HLS core and RX dwell/capture here. */
    }
    return 0;
}
