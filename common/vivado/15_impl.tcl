set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir common.tcl]
open_work_project
require_successful_run synth_1
set jobs [expr {[info exists ::env(JOBS)] ? $::env(JOBS) : 8}]
reset_run impl_1
launch_runs impl_1 -to_step route_design -jobs $jobs
wait_on_run impl_1
require_successful_run impl_1
open_run impl_1
set output [ensure_output_directory]
report_utilization -file [file join $output post_route_utilization.rpt]
report_timing_summary -file [file join $output post_route_timing.rpt]
report_route_status -file [file join $output route_status.rpt]
set paths [get_timing_paths -quiet -delay_type max -max_paths 1 -nworst 1]
if {[llength $paths] == 0} { error "No setup timing path was available after routing" }
set wns [get_property SLACK [lindex $paths 0]]
set f [open [file join $output timing_gate.txt] w]; puts $f "WNS=$wns"; close $f
if {$wns < 0.0} { error "Timing gate failed: WNS=$wns ns" }
puts "Implementation passed timing with WNS=$wns ns"
close_project
