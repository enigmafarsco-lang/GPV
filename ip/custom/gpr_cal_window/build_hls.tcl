set part [expr {[info exists ::env(PART)] ? $::env(PART) : "xczu48dr-2fsvg1517e"}]
set period [expr {[info exists ::env(PL_CLOCK_PERIOD_NS)] ? $::env(PL_CLOCK_PERIOD_NS) : "4.000"}]
open_project -reset gpr_cal_window_hls
add_files src/gpr_cal_window.cpp -cflags "-Isrc "
add_files -tb tb/gpr_cal_window_tb.cpp -cflags "-Isrc "
set_top gpr_cal_window
open_solution -reset solution1
set_part $part
create_clock -period $period -name default
config_export -format ip_catalog -rtl verilog -vendor openai -library gpr -version 1.0 -display_name "GPR Calibration + Window Complex Multiplier"
csim_design
csynth_design
export_design
exit
