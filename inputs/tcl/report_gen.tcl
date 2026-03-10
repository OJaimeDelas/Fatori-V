# =============================================================================
# FATORI-V • TCL Reports Vivado File
# File: reports_gen.tcl
# =============================================================================

report_utilization -hierarchical -file reports/$NAME\_$PART\_hierarchical_utilization.rpt

# Power Report
report_power -file reports/$NAME\_$PART\_power.rpt

# Methodology/DRC Report  
report_methodology -file reports/$NAME\_$PART\_methodology.rpt

# More detailed DRC if you want comprehensive design rule checks
report_drc -file reports/$NAME\_$PART\_drc.rpt

# Add pblock reports (if pblocks exist)
if {[llength [get_pblocks]] > 0} {
    foreach pb [get_pblocks] {
        set pb_name [get_property NAME $pb]
        report_utilization -pblock $pb_name -file reports/$NAME\_$PART\_${pb_name}_util.rpt
    }
    puts "Generated [llength [get_pblocks]] pblock utilization reports"
}


# # Control Sets Report (shows FF grouping efficiency)
# report_control_sets -file reports/$NAME\_$PART\_control_sets.rpt

# # High Fanout Nets (identifies potential timing bottlenecks)
# report_high_fanout_nets -file reports/$NAME\_$PART\_high_fanout.rpt

# # Route Status (congestion analysis)
# report_route_status -file reports/$NAME\_$PART\_route_status.rpt

# # Design Analysis (comprehensive design metrics)
# report_design_analysis -file reports/$NAME\_$PART\_design_analysis.rpt

# # Datasheet (FPGA characteristics at your operating conditions)
# report_datasheet -file reports/$NAME\_$PART\_datasheet.rpt

# # QoR Assessment (Quality of Results - timing/utilization trade-offs)
# report_qor_assessment -file reports/$NAME\_$PART\_qor_assessment.rpt

# # QoR Suggestions (Vivado's recommendations for improvement)
# report_qor_suggestions -file reports/$NAME\_$PART\_qor_suggestions.rpt

# # Timing per pblock (critical for your SEM IP fault injection work)
# report_timing_summary -pblocks [get_pblocks] -file reports/$NAME\_$PART\_pblock_timing.rpt