proc require_env {name} {
    if {![info exists ::env($name)] || [string trim $::env($name)] eq ""} {
        error "Required environment variable $name is empty"
    }
    return $::env($name)
}
proc open_work_project {} {
    set project [file normalize [require_env WORK_XPR]]
    if {![file exists $project]} { error "Working project not found: $project. Run step12_vivado_project first." }
    open_project $project
    set expected [require_env PART]
    if {[get_property PART [current_project]] ne $expected} {
        error "Project part [get_property PART [current_project]] does not match $expected"
    }
}
proc select_base_bd {} {
    set requested ""
    if {[info exists ::env(BASE_BD)]} { set requested [string trim $::env(BASE_BD)] }
    if {$requested ne ""} { set candidates [get_files -quiet -all */${requested}.bd] } else { set candidates [get_files -quiet -all *.bd] }
    if {[llength $candidates] != 1} { error "Expected exactly one base BD (or set BASE_BD); found: $candidates" }
    open_bd_design [lindex $candidates 0]
    return [current_bd_design]
}
proc ensure_output_directory {} {
    set build [file normalize [require_env BUILD]]
    set out [file join $build output]; file mkdir $out; return $out
}
proc require_successful_run {name} {
    set r [get_runs -quiet $name]
    if {[llength $r] != 1} { error "Vivado run $name does not exist" }
    set status [get_property STATUS $r]
    if {![string match "*Complete*" $status]} { error "Vivado run $name is not complete: $status" }
}
proc find_unique_ipdef {name} {
    set defs [get_ipdefs -all -filter "NAME == $name"]
    if {[llength $defs] == 0} { error "Packaged IP '$name' is not in the catalog" }
    return [lindex [lsort -dictionary $defs] end]
}
proc require_prop {obj prop value} {
    if {[lsearch -exact [list_property $obj] $prop] < 0} {
        error "Required property $prop is not supported by $obj in this Vivado/IP version"
    }
    if {[catch {set_property $prop $value $obj} err]} {
        error "Failed to set required property $obj $prop=$value: $err"
    }
    puts "INFO required property $prop=[get_property $prop $obj] on $obj"
}
proc must_pin {path} {
    set p [get_bd_pins -quiet $path]
    if {[llength $p] != 1} { error "Required BD pin missing or ambiguous: $path" }
    return $p
}
proc must_intf {path} {
    set p [get_bd_intf_pins -quiet $path]
    if {[llength $p] != 1} { error "Required BD interface missing or ambiguous: $path" }
    return $p
}
proc strict_net {a b} { connect_bd_net [must_pin $a] [must_pin $b] }
proc strict_intf {a b} { connect_bd_intf_net [must_intf $a] [must_intf $b] }
