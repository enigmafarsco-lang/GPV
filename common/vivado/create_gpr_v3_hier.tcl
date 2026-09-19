proc create_gpr_v3_hier {parent name} {
    set old [current_bd_instance .]
    current_bd_instance $parent
    if {[llength [get_bd_cells -quiet $name]]} { error "BD cell $name already exists" }
    create_bd_cell -type hier $name
    current_bd_instance $name

    # Clock/reset and system readiness
    create_bd_pin -dir I -type clk aclk
    create_bd_pin -dir I -type rst aresetn
    set_property CONFIG.POLARITY ACTIVE_LOW [get_bd_pins aresetn]
    create_bd_pin -dir I system_ready
    create_bd_pin -dir I sb_ack
    create_bd_pin -dir O sb_req
    create_bd_pin -dir O -from 7 -to 0 sb_id
    create_bd_pin -dir I pos_ack
    create_bd_pin -dir O pos_req
    create_bd_pin -dir O -from 15 -to 0 pos_id
    create_bd_pin -dir O frame_done

    # Streaming RF and coefficient interfaces.
    create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M_AXIS_TX_DAC
    create_bd_intf_pin -mode Slave  -vlnv xilinx.com:interface:axis_rtl:1.0 S_AXIS_RX_DDC
    create_bd_intf_pin -mode Slave  -vlnv xilinx.com:interface:axis_rtl:1.0 S_AXIS_CAL_COEF
    create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M_AXIS_RANGE_IQ
    create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M_AXIS_RANGE_POWER
    create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M_AXIS_CFAR1D

    # HLS AXI-Lite control planes.
    foreach p {SCHED RX AVG PAD BG CFAR1D MED MIG CFAR2D CLUSTER} {
        create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S_AXI_${p}_CTRL
    }

    # DDR-facing image-domain accelerators.
    foreach p {MED_IN MED_OUT MIG_IN MIG_OUT CFAR2D_IN CFAR2D_OUT CLUSTER_MASK CLUSTER_MAG CLUSTER_LABEL CLUSTER_REPORT} {
        create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 M_AXI_${p}
    }

    # Custom IP.
    set sched [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_sweep_scheduler] sweep_scheduler]
    set rx    [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_rx_tone_extractor] rx_tone_extractor]
    set avg   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_sweep_average] sweep_average]
    set cal   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_cal_window] cal_window]
    set pad   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_zero_pad_cfg] zero_pad]
    set bg    [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_background_ewma] background_ewma]
    set pwr   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_power32] range_power]
    set cf1   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_cfar1d] cfar1d]
    set med   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_background_median_accel] background_median]
    set mig   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_kirchhoff_coherent_accel] migration]
    set cf2   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_cfar2d_accel] cfar2d]
    set clu   [create_bd_cell -type ip -vlnv [find_unique_ipdef gpr_cluster2d_accel] cluster2d]

    # Context FIFO decouples TX scheduling from RFDC/RX converter latency.
    set ctxfifo [create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:* ctx_fifo]
    require_prop $ctxfifo CONFIG.FIFO_DEPTH {64}

    # Production IFFT primitive.
    set fft [create_bd_cell -type ip -vlnv xilinx.com:ip:xfft:* ifft]
    require_prop $fft CONFIG.transform_length {2048}
    require_prop $fft CONFIG.arch_opt {pipelined_streaming_io}
    require_prop $fft CONFIG.data_format {fixed_point}
    require_prop $fft CONFIG.input_width {16}
    require_prop $fft CONFIG.phase_factor_width {16}
    require_prop $fft CONFIG.scaling_options {scaled}

    # Buffered branch after background/power: normal DMA jitter must not instantly stall acquisition.
    set iqbc [create_bd_cell -type ip -vlnv xilinx.com:ip:axis_broadcaster:* iq_broadcast]
    require_prop $iqbc CONFIG.NUM_MI {2}
    set iqfifo [create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:* iq_dma_fifo]
    require_prop $iqfifo CONFIG.FIFO_DEPTH {2048}

    set pwbc [create_bd_cell -type ip -vlnv xilinx.com:ip:axis_broadcaster:* power_broadcast]
    require_prop $pwbc CONFIG.NUM_MI {2}
    set pwfifo [create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:* power_dma_fifo]
    require_prop $pwfifo CONFIG.FIFO_DEPTH {2048}

    # Clock/reset: no silent catch on coder-critical paths.
    foreach cell {sweep_scheduler rx_tone_extractor sweep_average cal_window zero_pad background_ewma range_power cfar1d background_median migration cfar2d cluster2d} {
        strict_net aclk ${cell}/ap_clk
        strict_net aresetn ${cell}/ap_rst_n
    }
    foreach cell {ctx_fifo ifft iq_broadcast iq_dma_fifo power_broadcast power_dma_fifo} {
        strict_net aclk ${cell}/aclk
        strict_net aresetn ${cell}/aresetn
    }

    # Shared sweep control/status.
    strict_net system_ready sweep_scheduler/system_ready
    strict_net sb_ack sweep_scheduler/sb_ack
    strict_net pos_ack sweep_scheduler/pos_ack
    strict_net sweep_scheduler/sb_req sb_req
    strict_net sweep_scheduler/sb_id sb_id
    strict_net sweep_scheduler/pos_req pos_req
    strict_net sweep_scheduler/pos_id pos_id
    strict_net sweep_scheduler/frame_done frame_done

    # RF/data path.
    strict_intf sweep_scheduler/m_axis_tx M_AXIS_TX_DAC
    strict_intf sweep_scheduler/m_axis_ctx ctx_fifo/S_AXIS
    strict_intf ctx_fifo/M_AXIS rx_tone_extractor/s_axis_ctx
    strict_intf S_AXIS_RX_DDC rx_tone_extractor/s_axis_rx
    strict_intf rx_tone_extractor/m_axis_tone sweep_average/s_axis
    strict_intf sweep_average/m_axis cal_window/s_axis
    strict_intf S_AXIS_CAL_COEF cal_window/s_axis_coef
    strict_intf cal_window/m_axis zero_pad/s_axis
    strict_intf zero_pad/m_axis ifft/S_AXIS_DATA
    strict_intf zero_pad/m_axis_cfg ifft/S_AXIS_CONFIG
    strict_intf ifft/M_AXIS_DATA background_ewma/s_axis
    strict_intf background_ewma/m_axis iq_broadcast/S_AXIS

    # IQ branch 0 -> DMA FIFO, branch 1 -> power/CFAR.
    strict_intf iq_broadcast/M00_AXIS iq_dma_fifo/S_AXIS
    strict_intf iq_dma_fifo/M_AXIS M_AXIS_RANGE_IQ
    strict_intf iq_broadcast/M01_AXIS range_power/s_axis
    strict_intf range_power/m_axis power_broadcast/S_AXIS
    strict_intf power_broadcast/M00_AXIS power_dma_fifo/S_AXIS
    strict_intf power_dma_fifo/M_AXIS M_AXIS_RANGE_POWER
    strict_intf power_broadcast/M01_AXIS cfar1d/s_axis
    strict_intf cfar1d/m_axis M_AXIS_CFAR1D

    # AXI-Lite controls.
    foreach {ext cell} {
        S_AXI_SCHED_CTRL sweep_scheduler
        S_AXI_RX_CTRL rx_tone_extractor
        S_AXI_AVG_CTRL sweep_average
        S_AXI_PAD_CTRL zero_pad
        S_AXI_BG_CTRL background_ewma
        S_AXI_CFAR1D_CTRL cfar1d
        S_AXI_MED_CTRL background_median
        S_AXI_MIG_CTRL migration
        S_AXI_CFAR2D_CTRL cfar2d
        S_AXI_CLUSTER_CTRL cluster2d
    } {
        strict_intf $ext ${cell}/s_axi_control
    }

    # Image-domain memory interfaces.
    strict_intf background_median/m_axi_g0 M_AXI_MED_IN
    strict_intf background_median/m_axi_g1 M_AXI_MED_OUT
    strict_intf migration/m_axi_gmem0 M_AXI_MIG_IN
    strict_intf migration/m_axi_gmem1 M_AXI_MIG_OUT
    strict_intf cfar2d/m_axi_gmem0 M_AXI_CFAR2D_IN
    strict_intf cfar2d/m_axi_gmem1 M_AXI_CFAR2D_OUT
    strict_intf cluster2d/m_axi_g0 M_AXI_CLUSTER_MASK
    strict_intf cluster2d/m_axi_g1 M_AXI_CLUSTER_MAG
    strict_intf cluster2d/m_axi_g2 M_AXI_CLUSTER_LABEL
    strict_intf cluster2d/m_axi_g3 M_AXI_CLUSTER_REPORT

    set buses {
        M_AXIS_TX_DAC S_AXIS_RX_DDC S_AXIS_CAL_COEF M_AXIS_RANGE_IQ M_AXIS_RANGE_POWER M_AXIS_CFAR1D
        S_AXI_SCHED_CTRL S_AXI_RX_CTRL S_AXI_AVG_CTRL S_AXI_PAD_CTRL S_AXI_BG_CTRL S_AXI_CFAR1D_CTRL
        S_AXI_MED_CTRL S_AXI_MIG_CTRL S_AXI_CFAR2D_CTRL S_AXI_CLUSTER_CTRL
        M_AXI_MED_IN M_AXI_MED_OUT M_AXI_MIG_IN M_AXI_MIG_OUT M_AXI_CFAR2D_IN M_AXI_CFAR2D_OUT
        M_AXI_CLUSTER_MASK M_AXI_CLUSTER_MAG M_AXI_CLUSTER_LABEL M_AXI_CLUSTER_REPORT
    }
    set_property CONFIG.ASSOCIATED_BUSIF [join $buses :] [get_bd_pins aclk]
    set_property CONFIG.ASSOCIATED_RESET {aresetn} [get_bd_pins aclk]

    current_bd_instance $old
    return [get_bd_cells $parent/$name]
}
