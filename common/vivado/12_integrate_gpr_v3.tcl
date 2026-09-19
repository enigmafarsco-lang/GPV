set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir common.tcl]
open_work_project
set ip_repo [file normalize [require_env IP_REPO]]
set_property ip_repo_paths [list $ip_repo] [current_project]
update_ip_catalog
select_base_bd
source [file join $script_dir create_gpr_v3_hier.tcl]
if {[llength [get_bd_cells -quiet /gpr_v3]]} {
    puts "Replacing generated hierarchy /gpr_v3"
    delete_bd_objs [get_bd_cells /gpr_v3]
}
create_gpr_v3_hier / gpr_v3
set map [file normalize [require_env GPR_BD_MAP]]
if {![file exists $map]} { error "GPR_BD_MAP not found: $map" }
source $map
set mode [expr {[info exists ::env(INTEGRATION_MODE)] ? $::env(INTEGRATION_MODE) : "mapped"}]
connect_gpr_v3_to_base gpr_v3 $mode
assign_bd_address
validate_bd_design
save_bd_design
save_project
puts "Integrated Hybrid V3 into [current_bd_design] using mode=$mode"
close_project
