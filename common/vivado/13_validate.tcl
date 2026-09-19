set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir common.tcl]
open_work_project
select_base_bd
validate_bd_design
save_bd_design
set output [ensure_output_directory]
report_ip_status -file [file join $output ip_status.txt]
write_bd_tcl -force [file join $output integrated_gpr_block_design.tcl]
set f [open [file join $output gpr_interfaces.txt] w]
foreach i [lsort [get_bd_intf_pins -quiet /gpr_v1/*]] { puts $f "$i [get_property MODE $i]" }
close $f
set messages [get_messages -severity {CRITICAL WARNING ERROR}]
set m [open [file join $output validation_messages.txt] w]
foreach message $messages { puts $m $message }
close $m
save_project
puts "GPR BD validation passed; reports are in $output"
close_project
