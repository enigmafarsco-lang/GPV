set part [expr {[info exists ::env(PART)] ? $::env(PART) : "xczu48dr-2fsvg1517e"}]
set period [expr {[info exists ::env(PL_CLOCK_PERIOD_NS)] ? $::env(PL_CLOCK_PERIOD_NS) : "4.000"}]
open_project -reset gpr_cfar1d_hls
add_files src/gpr_cfar1d.cpp -cflags "-Isrc "
add_files -tb tb/gpr_cfar1d_tb.cpp -cflags "-Isrc "
set_top gpr_cfar1d
open_solution -reset solution1
set_part $part
create_clock -period $period -name default
config_export -format ip_catalog -rtl verilog -vendor openai -library gpr -version 1.0 -display_name "GPR 1D CA-CFAR Detector"
csim_design
csynth_design
export_design
exit
