# SPDX-FileCopyrightText: 2025 IObundle
#
# SPDX-License-Identifier: MIT

#extract cli args
set NAME [lindex $argv 0]
set CSR_IF [lindex $argv 1]
set BOARD [lindex $argv 2]
set VSRC [lindex $argv 3]
set INCLUDE_DIRS [lindex $argv 4]
set IS_FPGA [lindex $argv 5]
set USE_EXTMEM [lindex $argv 6]
set USE_ETHERNET [lindex $argv 7]
set SDC_PREFIX [lindex $argv 8]

set VIVADO_INPUT [lindex $argv 9]

# Helper procedure to source probes with proper context
proc source_probe {probe_dir probe_name} {
    if {$probe_dir == ""} {
        return
    }
    
    set probe_file "${probe_dir}/${probe_name}"
    if {[file exists $probe_file]} {
        puts "=========================================="
        puts ">>> Sourcing: ${probe_name}"
        puts ">>> From: ${probe_dir}"
        puts "=========================================="
        
        # Make build.tcl variables available to probes
        global NAME CSR_IF BOARD VSRC INCLUDE_DIRS IS_FPGA USE_EXTMEM USE_ETHERNET SDC_PREFIX VIVADO_INPUT PART
        global PROBE_DIR
        set PROBE_DIR $probe_dir
        
        # Source the probe directly
        # This keeps the working directory at build_dir/hardware/fpga/
        source $probe_file
        
        puts ">>> ${probe_name} complete!"
        puts "==========================================\n"
    } else {
        puts ">>> Probe not found: ${probe_file} (skipping)"
    }
}

# ============================================================================
# HOOK PROBE 1: Pre-Synthesis
# ============================================================================
source_probe $VIVADO_INPUT "pre_synthesis.tcl"

#verilog sources, vivado IPs, use file extension
foreach file [split $VSRC \ ] {
    puts $file
    if { [ file extension $file ] == ".edif" } {
        read_edif $file
    } elseif {$file != "" && $file != " " && $file != "\n"} {
        read_verilog -sv $file
    }
}

#verilog sources, vivado IPs, use file extension
foreach file [split $VSRC \ ] {
    puts $file
    if { [ file extension $file ] == ".edif" } {
        read_edif $file
    } elseif {$file != "" && $file != " " && $file != "\n"} {
        read_verilog -sv $file
    }
}

#read board properties
source vivado/$BOARD/board.tcl


#set pre-map custom assignments
if {[file exists "vivado/premap.tcl"]} {
    source "vivado/premap.tcl"
}

set SYNTH_FLAGS {}
foreach dir $INCLUDE_DIRS {
    lappend SYNTH_FLAGS "-include_dirs" "${dir}"
}


#read design constraints and synthesize design
if { $IS_FPGA == "1" } {
    puts "Synthesizing for FPGA"
    read_xdc vivado/$BOARD/$SDC_PREFIX\_dev.sdc
    if {[file exists "../src/$SDC_PREFIX.sdc"]} {
        read_xdc ../src/$SDC_PREFIX.sdc
    }
    if {[file exists "../../src/$SDC_PREFIX\_$CSR_IF.sdc"]} {
        read_xdc ../src/$SDC_PREFIX\_$CSR_IF.sdc
    }
    if {[file exists "vivado/$SDC_PREFIX\_tool.sdc"]} {
        read_xdc vivado/$SDC_PREFIX\_tool.sdc
    }
    eval synth_design -include_dirs ../src -include_dirs ../common_src -include_dirs ./src -include_dirs ./vivado/$BOARD $SYNTH_FLAGS -part $PART -top $NAME -verbose
} else {
    #read design constraints
    puts "Out of context synthesis"
    read_xdc -mode out_of_context vivado/$BOARD/$SDC_PREFIX\_dev.sdc
    read_xdc -mode out_of_context ../src/$SDC_PREFIX.sdc
    if {[file exists "../src/$SDC_PREFIX\_$CSR_IF.sdc"]} {
        read_xdc ../src/$SDC_PREFIX\_$CSR_IF.sdc
    }
    if {[file exists "./src/$SDC_PREFIX.sdc"]} {
        read_xdc ./src/$SDC_PREFIX.sdc
    }
    if {[file exists "vivado/$SDC_PREFIX\_tool.sdc"]} {
        read_xdc -mode out_of_context vivado/$SDC_PREFIX\_tool.sdc
    }
    eval synth_design -include_dirs ../src -include_dirs ../common_src -include_dirs ./src -include_dirs ./vivado/$BOARD $SYNTH_FLAGS -part $PART -top $NAME -mode out_of_context -flatten_hierarchy full -verbose
}

#set post-map custom assignments
if {[file exists "vivado/postmap.tcl"]} {
    source "vivado/postmap.tcl"
}

opt_design

# ============================================================================
# HOOK PROBE 2: Post-Optimization 
# ============================================================================
source_probe $VIVADO_INPUT "post_opt.tcl"

place_design

route_design -timing

# ============================================================================
# HOOK PROBE 3: Post-Route
# ============================================================================
source_probe $VIVADO_INPUT "post_route.tcl"

report_clocks
report_clock_interaction
report_cdc -details
report_bus_skew

report_clocks -file reports/$NAME\_$PART\_clocks.rpt
report_clock_interaction -file reports/$NAME\_$PART\_clock_interaction.rpt
report_cdc -details -file reports/$NAME\_$PART\_cdc.rpt
report_synchronizer_mtbf -file reports/$NAME\_$PART\_synchronizer_mtbf.rpt
report_utilization -file reports/$NAME\_$PART\_utilization.rpt
report_timing -file reports/$NAME\_$PART\_timing.rpt
report_timing_summary -file reports/$NAME\_$PART\_timing_summary.rpt
report_timing -file reports/$NAME\_$PART\_timing_paths.rpt -max_paths 30
report_bus_skew -file reports/$NAME\_$PART\_bus_skew.rpt


# ========================================================================
# HOOK PROBE 4: Pre-Bitstream
# ========================================================================
source_probe $VIVADO_INPUT "pre_bitstream.tcl"

if { $IS_FPGA == "1" } {
    write_bitstream -force $NAME.bit

    # ========================================================================
    # HOOK PROBE 5: Post-Bitstream
    # ========================================================================
    source_probe $VIVADO_INPUT "post_bitstream.tcl"

} else {
    write_verilog -force $NAME\_netlist.v
    write_verilog -force -mode synth_stub ${NAME}_stub.v
}
