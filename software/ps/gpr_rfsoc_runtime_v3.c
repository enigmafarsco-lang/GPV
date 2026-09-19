/*
 * Hybrid V3 PS/R5 orchestration contract.
 * Use xparameters.h + XRFdc from the XSA generated from the VERIFIED RFDC/MTS base.
 * No absolute register addresses are hard-coded here.
 */
#include <stdint.h>

typedef struct {
    uint16_t n_tones;
    uint16_t n_positions;
    uint8_t  n_averages;
    uint32_t dwell_samples_total;
    uint32_t rx_discard_samples;
    uint16_t tones_per_subband;
    double   f_start_hz;
    double   df_hz;
    double   subband_span_hz;
} gpr_v3_cfg_t;

/* BSP-specific hooks that the application must implement. */
int gpr_rfdc_is_ready_and_mts_locked(void *rfdc);
int gpr_rfdc_program_subband(void *rfdc, unsigned sb_id,
                             const gpr_v3_cfg_t *cfg);
int gpr_position_is_ready(unsigned pos_id);
void gpr_scheduler_set_system_ready(int ready);
void gpr_scheduler_set_sb_ack(int ack);
int  gpr_scheduler_get_sb_req(unsigned *sb_id);
void gpr_scheduler_set_pos_ack(int ack);
int  gpr_scheduler_get_pos_req(unsigned *pos_id);

/*
 * Service loop:
 * - scheduler cannot start acquisition until RFDC/MTS/clock readiness is true;
 * - sb_ack is only asserted after BOTH ADC and DAC mixer/NCO updates commit;
 * - pos_ack is only asserted when encoder/GNSS/UAV controller confirms position.
 */
int gpr_v3_service(void *rfdc, const gpr_v3_cfg_t *cfg)
{
    int ready = gpr_rfdc_is_ready_and_mts_locked(rfdc);
    gpr_scheduler_set_system_ready(ready);
    if (!ready) return -1;

    unsigned sb=0, pos=0;
    if (gpr_scheduler_get_sb_req(&sb)) {
        gpr_scheduler_set_sb_ack(0);
        if (gpr_rfdc_program_subband(rfdc, sb, cfg) != 0) return -2;
        gpr_scheduler_set_sb_ack(1);
        gpr_scheduler_set_sb_ack(0);
    }
    if (gpr_scheduler_get_pos_req(&pos)) {
        gpr_scheduler_set_pos_ack(0);
        if (gpr_position_is_ready(pos)) {
            gpr_scheduler_set_pos_ack(1);
            gpr_scheduler_set_pos_ack(0);
        }
    }
    return 0;
}
