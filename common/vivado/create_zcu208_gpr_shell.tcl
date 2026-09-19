# Minimal shell only. Production must start from a verified RFDC/MTS ZCU208 base.
set proj "zcu208_gpr_shell"
set part "xczu48dr-2fsvg1517e"
if {[llength $argv] > 0} { set proj [lindex $argv 0] }
if {[llength $argv] > 1} { set part [lindex $argv 1] }
create_project -force $proj [file normalize "build/$proj"] -part $part
create_bd_design design_1
create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e:* zynq_ultra_ps_e_0
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:* rst_pl
puts "Created minimal XCZU48DR shell. RFDC tile, MTS, sample-rate, DAC/ADC mixer and board clock settings MUST come from a verified ZCU208 design."
save_bd_design
