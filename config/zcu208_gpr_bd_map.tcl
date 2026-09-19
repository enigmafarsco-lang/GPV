# ZCU208 / XCZU48DR Hybrid V3 board map.
#
# This file is deliberately the ONLY place where verified-base interface names belong.
# Production mode is fail-hard. Do not wrap RFDC/MTS/clock connections in catch.
#
# Required signal semantics:
#   system_ready = rfdc_ready && mts_locked && clocks_locked
#   sb_req/sb_id -> PS/R5 retune service; sb_ack only after BOTH DAC and ADC NCO updates commit
#   M_AXIS_TX_DAC -> RFDC DAC/DUC through an explicit width adapter if RFDC TDATA != 32 bits
#   S_AXIS_RX_DDC <- RFDC ADC/DDC through an explicit sample/width adapter to complex int16 I[15:0],Q[31:16]
#   S_AXIS_CAL_COEF <- cyclic MM2S coefficient source, Q1.15 complex
#   range IQ/power/CFAR outputs -> independent FIFO/DMA paths
#   all image accelerators -> DDR HP/HPC via SmartConnect
#
# IMPORTANT: RFDC does not provide tone/position TUSER metadata. Hybrid V3 generates metadata internally
# from the same sweep scheduler that drives TX, then carries it through the context FIFO to the RX extractor.
#
# A production map must also prove that GUI/logging cannot indefinitely backpressure acquisition.

proc connect_gpr_v3_to_base {hier integration_mode} {
    if {$integration_mode eq "external_ports"} {
        foreach pin {
            M_AXIS_TX_DAC S_AXIS_RX_DDC S_AXIS_CAL_COEF
            M_AXIS_RANGE_IQ M_AXIS_RANGE_POWER M_AXIS_CFAR1D
            S_AXI_SCHED_CTRL S_AXI_RX_CTRL S_AXI_AVG_CTRL S_AXI_PAD_CTRL
            S_AXI_BG_CTRL S_AXI_CFAR1D_CTRL S_AXI_MED_CTRL S_AXI_MIG_CTRL
            S_AXI_CFAR2D_CTRL S_AXI_CLUSTER_CTRL
            M_AXI_MED_IN M_AXI_MED_OUT M_AXI_MIG_IN M_AXI_MIG_OUT
            M_AXI_CFAR2D_IN M_AXI_CFAR2D_OUT
            M_AXI_CLUSTER_MASK M_AXI_CLUSTER_MAG M_AXI_CLUSTER_LABEL M_AXI_CLUSTER_REPORT
        } {
            make_bd_intf_pins_external [must_intf ${hier}/${pin}]
        }
        foreach pin {aclk aresetn system_ready sb_ack sb_req sb_id pos_ack pos_req pos_id frame_done} {
            make_bd_pins_external [must_pin ${hier}/${pin}]
        }
        puts "WARNING: structural external-port mode only; not a deployable RFDC integration."
        return
    }

    error {Production map is intentionally fail-hard and project-specific.
Edit config/zcu208_gpr_bd_map.tcl against your VERIFIED ZCU208/XCZU48DR RFDC+MTS base.

You must explicitly connect:
  gpr_v3/aclk, aresetn
  gpr_v3/system_ready = RFDC_READY & MTS_LOCKED & CLOCKS_LOCKED
  gpr_v3/sb_req, sb_id, sb_ack to the PS/R5 retune service
  gpr_v3/pos_req, pos_id, pos_ack to encoder/GNSS/UAV position gating
  gpr_v3/M_AXIS_TX_DAC through the correct RFDC TX width/sample adapter
  gpr_v3/S_AXIS_RX_DDC through the correct RFDC RX width/sample adapter
  gpr_v3/S_AXIS_CAL_COEF to cyclic MM2S/FIFO calibration-window coefficients
  all S_AXI_* controls to PS HPM SmartConnect
  range IQ / power / CFAR outputs to independent S2MM/FIFO paths
  all M_AXI_* imaging ports to DDR HP/HPC SmartConnect

Before asserting sb_ack, firmware must:
  1. program the RFDC DAC NCO for sb_id,
  2. program the RFDC ADC NCO for the same sub-band,
  3. issue the configured mixer update event,
  4. wait for the deterministic update boundary required by the verified MTS base.

No production build should proceed with unverified RFDC interface names, converter widths, clocks, or MTS state.}
}
