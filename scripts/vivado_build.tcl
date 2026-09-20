# =============================================================================
# vivado_build.tcl - build the GPR PL chain for the AMD RFSoC ZCU208
#                    (XCZU48DR-2FSVG1517E), Vivado 2023.2 through 2025.x
#                    (RFDC IP 2.6 is unchanged across 2025.1/2025.2)
#
# Usage:
#   # quick flat synthesis: utilisation + timing reports, no BD, no bitstream
#   vivado -mode batch -source fpga/scripts/vivado_build.tcl
#
#   # full block-design build: PS + RFDC + interconnect, bitstream + XSA
#   vivado -mode batch -source fpga/scripts/vivado_build.tcl -tclargs full
#
# Prerequisites for the FULL flow:
#   * Xilinx board files for ZCU208 installed (or set board_part manually)
#   * RFSoC RF Data Converter IP licensed (included with Vivado for ZU*DR)
#   * Run from the repository root or anywhere - paths here are script-relative
# =============================================================================

set script_dir [file dirname [file normalize [info script]]]
set fpga_dir   [file normalize "$script_dir/.."]
set rtl_dir    "$fpga_dir/rtl"
set xdc_dir    "$fpga_dir/xdc"
set prj_dir    "$fpga_dir/vivado_prj"

# Part selection.  UG1410 / the AMD kit page describe the ZCU208 silicon as
# XCZU48DR-2FSVG1517E (SCD5184 special silicon), but the standard Vivado part
# catalog offers the ZU48DR in FFVE1156 / FSVE1156 packages (UG1075), and the
# SCD string is only present in installs that include it.  Resolve against
# THIS install's catalog instead of hardcoding: prefer an exact FSVG1517
# match when available, then the standard packages, then any xczu48dr*.
set part_prefs {xczu48dr-2fsvg1517e xczu48dr-2ffve1156e xczu48dr-2fsve1156e}
set part ""
foreach p $part_prefs {
    if {[llength [get_parts -quiet $p]] > 0} { set part $p; break }
}
if {$part eq ""} {
    set c [get_parts -quiet xczu48dr*]
    if {[llength $c] > 0} { set part [lindex $c 0] }
}
if {$part eq ""} {
    error "No xczu48dr part in this Vivado install. Run: get_parts xczu48dr*\n\
If empty, add RFSoC device support (Vivado installer > Add Design Tools or\n\
Devices > SoC > Zynq UltraScale+ RFSoC), or for SCD5184 kits install the\n\
device pack bundled with the node-locked ZCU208 license."
}
puts "=== Using part: $part"
set board_part  ""   ;# resolved below from installed board files
set top_module  gpr_top_zcu208
set full_build  [expr {[llength $argv] > 0 && [lindex $argv 0] eq "full"}]
file mkdir "$fpga_dir/reports"

# ----------------------------------------------------------------------------
# project
# ----------------------------------------------------------------------------
create_project gpr_zcu208 $prj_dir -part $part -force
set bcands [get_board_parts -quiet *zcu208*]
if {[llength $bcands] > 0} {
    set_property board_part [lindex $bcands end] [current_project]
    puts "=== Using board part: [lindex $bcands end]"
} else {
    puts "WARNING: no ZCU208 board part installed - continuing part-only."
    puts "         The FULL BD flow needs the ZCU208 board files."
}

# RTL sources (golden ROM hex files live in fpga/golden and fpga/sim; they are
# simulation-only initialisation - synthesis initialises the ROMs from the
# PS-side or leaves them zero, see fpga/README.md section 'ROM loading')
add_files -norecurse [glob $rtl_dir/*.v]
add_files -fileset constrs_1 -norecurse $xdc_dir/zcu208.xdc
set_property top $top_module [current_fileset]
update_compile_order -fileset sources_1

if {!$full_build} {
    # ------------------------------------------------------------------------
    # SYNTH-ONLY: flat elaboration of gpr_top_zcu208 for resource/timing
    # ------------------------------------------------------------------------
    puts "=== SYNTH_ONLY: synthesising $top_module flat ==="
    synth_design -top $top_module -part $part -mode out_of_context
    opt_design
    report_utilization          -file "$fpga_dir/reports/util_synth.rpt"
    report_timing_summary       -file "$fpga_dir/reports/timing_synth.rpt"
    report_methodology          -file "$fpga_dir/reports/methodology_synth.rpt"
    write_checkpoint -force     "$fpga_dir/reports/synth_only.dcp"
    puts "=== reports in fpga/reports/ ==="
    exit
}

# ============================================================================
# FULL BUILD: block design with Zynq UltraScale+ MPSoC, RF Data Converter,
# clocking, AXI interconnect and the GPR chain as a module reference.
# ============================================================================
create_bd_design gpr_bd

# ---- Zynq MPSoC (PS) --------------------------------------------------------
set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e ps_e]
catch {apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e \
           -config {apply_board_preset "1"} $ps}
# minimal fallback config if the board preset is missing
catch {
    set_property -dict [list \
        CONFIG.PSU__USE__M_AXI_GP0 {1} \
        CONFIG.PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ {100} \
        CONFIG.PSU__GPIO0_MIO__PERIPHERAL__ENABLE {1} \
    ] $ps
}

# ---- PL fabric clock: 245.76 MHz -------------------------------------------
# ZCU208 note: exact 245.76 MHz cannot be derived from pl_clk0 (100 MHz) with
# an integer MMCM ratio.  Production boards feed the PL from the on-board
# SI570 (PS-programmable over I2C, e.g. via the Linux si570 driver) into a PL
# differential clock pin - replace clk_wiz's input accordingly and add the pin
# to zcu208.xdc.  For bring-up the clk_wiz below locks to the closest
# achievable rate (245.833 MHz, 0.03 % off); regenerate golden ROMs
# (make_golden.m, F_CLK) if you keep a non-nominal rate.
set cwin [create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wizard pl_clk_wiz]
set_property -dict [list \
    CONFIG.PRIM_IN_FREQ.VALUE_SRC USER \
    CONFIG.PRIM_SOURCE {Differential_clock_capable_pin} \
    CONFIG.USE_RESET {false} \
    CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {245.76} \
] $cwin
catch {
    # board bring-up alternative: drive clk_wiz from pl_clk0 single-ended
    set_property -dict [list CONFIG.PRIM_SOURCE {Single_ended_clock_capable_pin}] $cwin
}

# ---- RF Data Converter (RFDC) ----------------------------------------------
# GPR mode A: 0.5-3.0 GHz swept in 21 sub-bands (see README 'Sub-band plan').
# ADC tile 224 converter 0, fs = 4.9152 GSPS (LMK04828 refclk 122.88 MHz),
# fine-mixer NCO per sub-band (PS retunes on sb_req/sb_ack), 4x decimation,
# real 2GSPS->IQ.  DAC tile 224 converter 0, fs = 4.9152 GSPS, 4x
# interpolation, fine NCO per sub-band.  Property names vary between IP
# versions - each is applied under catch and reported.
# The unified 'Zynq Ultrascale+ RF Data Converter' IP (usp_rf_data_converter,
# v2.6 in 2024.x/2025.x) covers Gen1-Gen3 RFSoC incl. the ZU48DR on ZCU208.
# Older docs/examples used usmp_rf_data_converter - try both.
set rfdc_ok 0
foreach vlnv {xilinx.com:ip:usp_rf_data_converter xilinx.com:ip:usmp_rf_data_converter} {
    if {![catch {create_bd_cell -type ip -vlnv $vlnv rfdc} cerr]} {
        puts "RFDC IP: $vlnv"
        set rfdc_ok 1
        break
    }
    puts "NOTE: $vlnv not available ($cerr)"
}
if {!$rfdc_ok} { error "No RF Data Converter IP found - check your Vivado install" }

# Converter-level properties first, then per-slice fallbacks (naming varies
# between IP revisions; everything is catch-guarded).  Anything that warns
# must be finished in the GUI against the README section-4 table; run
#   report_property [get_bd_cells rfdc]
# to list the property names your IP version actually supports.
foreach {prop val} {
    CONFIG.ADC0_Enable               {1}
    CONFIG.ADC0_Sampling_Rate        {4.9152}
    CONFIG.ADC0_Refclk_Freq          {0.12288}
    CONFIG.ADC0_Fabric_Freq          {245.76}
    CONFIG.ADC0_Decimation_Mode      {4X}
    CONFIG.ADC0_Mixer_Mode           {Fine}
    CONFIG.ADC0_Data_Width           {4}
    CONFIG.ADC_Slice00_Enable        {true}
    CONFIG.ADC_Decimation_Mode00     {4X}
    CONFIG.ADC_Mixer_Type00          {Fine}
    CONFIG.DAC0_Enable               {1}
    CONFIG.DAC0_Sampling_Rate        {4.9152}
    CONFIG.DAC0_Refclk_Freq          {0.12288}
    CONFIG.DAC0_Fabric_Freq          {245.76}
    CONFIG.DAC0_Interpolation_Mode   {4X}
    CONFIG.DAC0_Mixer_Mode           {Fine}
    CONFIG.DAC_Slice00_Enable        {true}
    CONFIG.DAC_Interpolation_Mode00  {4X}
    CONFIG.DAC_Mixer_Type00          {Fine}
} {
    if {[catch {set_property $prop $val $rfdc} err]} {
        puts "WARNING: RFDC $prop not applied ($err)"
    }
}

# ---- GPR chain (module reference) ------------------------------------------
set gpr [create_bd_cell -type module -reference $top_module gpr]

# ---- AXI-Lite interconnect: PS M_AXI_HPM0_FPD -> gpr ------------------------
set smc [create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect axil_smc]
set_property CONFIG.NUM_SI {1} CONFIG.NUM_MI {1} $smc
connect_bd_net [get_bd_pins ps_e/pl_clk0]    [get_bd_pins smc/aclk]
catch {connect_bd_net [get_bd_pins ps_e/pl_clk0] [get_bd_pins ps_e/maxihpm0_fpd_axi_aclk]}
connect_bd_intf_net [get_bd_intf_pins ps_e/M_AXI_HPM0_FPD] [get_bd_intf_pins smc/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc/M00_AXI]         [get_bd_intf_pins gpr/s_axil]

# ---- clocks / resets ---------------------------------------------------------
set proc_rst [create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_245]
connect_bd_net [get_bd_pins cwin/clk_out1] [get_bd_pins gpr/clk]
connect_bd_net [get_bd_pins cwin/clk_out1] [get_bd_pins rst_245/slowest_sync_clk]
connect_bd_net [get_bd_pins ps_e/pl_resetn0] [get_bd_pins rst_245/ext_reset_in]
connect_bd_net [get_bd_pins rst_245/peripheral_reset] [get_bd_pins gpr/rst]
connect_bd_net [get_bd_pins cwin/clk_out1] [get_bd_pins rfdc/m0_axis_aclk]
catch {connect_bd_net [get_bd_pins cwin/clk_out1] [get_bd_pins rfdc/s_axis_dac_aclk]}

# ---- RFDC <-> GPR data (ADC tile 224 slice 0 -> gpr, gpr -> DAC) -------------
# Interface names depend on the enabled converters; connect the first ADC/DAC
# AXIS pairs.  Adjust slice indices if you enable more converters.
catch {connect_bd_intf_net [get_bd_intf_pins rfdc/m00_axis_adc0] \
                            [get_bd_intf_pins gpr/s_axis_adc]}
catch {connect_bd_intf_net [get_bd_intf_pins gpr/m_axis_dac] \
                            [get_bd_intf_pins rfdc/s00_axis_dac0]}

# ---- sideband retune handshake + irq to PS (EMIO GPIO) ----------------------
# sb_req/sb_ack and irq connect to PS EMIO GPIO (2 out, 1 in).  Enable
# PSU__GPIO1_EMIO in the PS configuration and map the nets; left as external
# ports here so the design validates without EMIO pin budgeting:
create_bd_port -dir O sb_req
create_bd_port -dir I sb_ack
create_bd_port -dir O irq
connect_bd_net [get_bd_pins gpr/sb_req] [get_bd_ports sb_req]
connect_bd_net [get_bd_ports sb_ack]    [get_bd_pins gpr/sb_ack]
connect_bd_net [get_bd_pins gpr/irq]    [get_bd_ports irq]

# loopback = 0: real RFDC data path (loopback=1 is the fabric self-test mode
# used by tb_chain and can be exposed as an external port for lab bring-up)
set tie0 [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant tie_gnd]
set_property CONFIG.CONST_VAL {0} $tie0
connect_bd_net [get_bd_pins tie0/dout] [get_bd_pins gpr/loopback]

# ---- validate, wrap, build ----------------------------------------------------
regenerate_bd_layout
if {[catch {validate_bd_design} err]} {
    puts "WARNING: validate_bd_design reported issues: $err"
    puts "         Fix RFDC/PS configuration in the GUI, then re-run."
}
save_bd_design
make_wrapper -files [get_files gpr_bd.bd] -top
add_files -norecurse [glob -nocomplain $prj_dir/gpr_zcu208.srcs/sources_1/bd/gpr_bd/hdl/*.v]
set_property top gpr_bd_wrapper [current_fileset]
update_compile_order -fileset sources_1

launch_runs synth_1 -jobs 8
wait_on_run synth_1
open_run synth_1 -name synth_1
report_utilization    -file "$fpga_dir/reports/util_bd.rpt"
report_timing_summary -file "$fpga_dir/reports/timing_bd.rpt"

launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {
    error "implementation failed - see $prj_dir runs"
}
write_hw_platform -fixed -include_bit -force "$fpga_dir/gpr_zcu208.xsa"
puts "=== bitstream + XSA written: fpga/gpr_zcu208.xsa ==="
exit
