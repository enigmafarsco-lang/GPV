set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir common.tcl]
open_work_project
require_successful_run impl_1
open_run impl_1
set output [ensure_output_directory]
set bit [file join $output [require_env PROJECT_NAME].bit]
write_bitstream -force $bit
if {![file exists $bit]} { error "write_bitstream did not create $bit" }
puts "Created $bit"
close_project
