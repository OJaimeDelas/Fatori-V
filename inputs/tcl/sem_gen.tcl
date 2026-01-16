# =============================================================================
# FATORI-V • TCL SEM IP Generator File
# File: sem_gen.tcl
# =============================================================================

puts "=========================================="
puts ">>> GENERATING SEM ULTRA IP AT BUILD TIME"
puts "=========================================="

set PART "xcku040-fbva676-1-c"
set IP_DIR "./ip"
set SRC_DIR "../src"

if {![file isdirectory $IP_DIR]} {
    file mkdir $IP_DIR
    puts ">>> Created $IP_DIR directory"
}

set marker_file "$SRC_DIR/.sem_generated"

if {[file isdirectory "$IP_DIR/sem_ultra_0"] && [file exists $marker_file]} {
    puts ">>> SEM Ultra IP already exists - skipping generation"
    puts ">>> (Delete $IP_DIR/sem_ultra_0 and $marker_file to force regeneration)"
    
    # Read the main SEM IP
    puts ">>> Reading existing SEM Ultra IP..."
    read_ip $IP_DIR/sem_ultra_0/sem_ultra_0.xci
    
    # Read VIO cores if they exist
    if {[file exists "$IP_DIR/sem_ultra_0_vio_si14/sem_ultra_0_vio_si14.xci"]} {
        puts ">>> Reading VIO cores..."
        read_ip $IP_DIR/sem_ultra_0_vio_si14/sem_ultra_0_vio_si14.xci
        read_ip $IP_DIR/sem_ultra_0_vio_si1_so41/sem_ultra_0_vio_si1_so41.xci
        read_ip $IP_DIR/sem_ultra_0_vio_si1_so5/sem_ultra_0_vio_si1_so5.xci
    }
    
    # Read example design wrapper file
    set wrapper_file "$IP_DIR/sem_ip_gen_temp_ex/sem_ultra_0_ex/imports/sem_ultra_0_example_design.v"
    if {[file exists $wrapper_file]} {
        puts ">>> Reading example design wrapper..."
        puts "    Reading: sem_ultra_0_example_design.v"
        read_verilog $wrapper_file
    }
    
} else {
    puts ">>> SEM IP not found - generating now..."
    
    # Create temporary project for IP generation
    puts ">>> Creating temporary project for IP generation..."
    set temp_proj "sem_ip_gen_temp"
    
    catch {close_project}
    
    create_project $temp_proj $IP_DIR/$temp_proj -part $PART -force
    set_property target_language Verilog [current_project]
    
    # Create SEM Ultra IP
    puts ">>> Creating SEM Ultra IP..."
    create_ip -name sem_ultra -vendor xilinx.com -library ip -version 3.1 \
        -module_name sem_ultra_0 -dir $IP_DIR -force
    
    # Configure for 60MHz clock (16667 ps period)
    set_property -dict [list \
        CONFIG.CLOCK_PERIOD {16667} \
        CONFIG.MODE {mitigation_and_testing} \
        CONFIG.LOCATE_CONFIG_PRIM {example_design} \
        CONFIG.ENABLE_CLASSIFICATION {false} \
    ] [get_ips sem_ultra_0]
    
    puts ">>> Generating SEM Ultra IP with synthesis checkpoint..."
    generate_target all [get_ips sem_ultra_0]
    
    puts ">>> Creating synthesis run for SEM IP..."
    create_ip_run [get_ips sem_ultra_0]
    launch_runs sem_ultra_0_synth_1
    wait_on_run sem_ultra_0_synth_1
    
    puts ">>> Exporting IP user files..."
    export_ip_user_files -of_objects [get_ips sem_ultra_0] -no_script -sync -force -quiet
    
    # Generate example design to get the wrapper files
    puts ">>> Generating SEM Example Design wrapper..."
    set example_dir "$IP_DIR/${temp_proj}_ex"
    open_example_project -force -dir $example_dir [get_ips sem_ultra_0]
    
    close_project
    
    # Now create VIO cores in the main IP directory (not inside example project)
    puts ">>> Creating VIO cores in main IP directory..."
    create_project $temp_proj $IP_DIR/$temp_proj -part $PART -force
    set_property target_language Verilog [current_project]
    
    # VIO core 1: sem_ultra_0_vio_si14
    puts ">>> Creating VIO core: sem_ultra_0_vio_si14..."
    create_ip -name vio -vendor xilinx.com -library ip -version 3.0 \
        -module_name sem_ultra_0_vio_si14 -dir $IP_DIR -force
    set_property -dict [list \
        CONFIG.C_NUM_PROBE_OUT {0} \
        CONFIG.C_NUM_PROBE_IN {14} \
        CONFIG.C_PROBE_IN13_WIDTH {1} \
        CONFIG.C_PROBE_IN12_WIDTH {1} \
        CONFIG.C_PROBE_IN11_WIDTH {1} \
        CONFIG.C_PROBE_IN10_WIDTH {1} \
        CONFIG.C_PROBE_IN9_WIDTH {1} \
        CONFIG.C_PROBE_IN8_WIDTH {1} \
        CONFIG.C_PROBE_IN7_WIDTH {1} \
        CONFIG.C_PROBE_IN6_WIDTH {1} \
        CONFIG.C_PROBE_IN5_WIDTH {1} \
        CONFIG.C_PROBE_IN4_WIDTH {1} \
        CONFIG.C_PROBE_IN3_WIDTH {1} \
        CONFIG.C_PROBE_IN2_WIDTH {1} \
        CONFIG.C_PROBE_IN1_WIDTH {1} \
        CONFIG.C_PROBE_IN0_WIDTH {1} \
    ] [get_ips sem_ultra_0_vio_si14]
    generate_target all [get_ips sem_ultra_0_vio_si14]
    create_ip_run [get_ips sem_ultra_0_vio_si14]
    launch_runs sem_ultra_0_vio_si14_synth_1
    wait_on_run sem_ultra_0_vio_si14_synth_1
    
    # VIO core 2: sem_ultra_0_vio_si1_so41
    puts ">>> Creating VIO core: sem_ultra_0_vio_si1_so41..."
    create_ip -name vio -vendor xilinx.com -library ip -version 3.0 \
        -module_name sem_ultra_0_vio_si1_so41 -dir $IP_DIR -force
    set_property -dict [list \
        CONFIG.C_NUM_PROBE_OUT {41} \
        CONFIG.C_NUM_PROBE_IN {1} \
        CONFIG.C_PROBE_IN0_WIDTH {1} \
    ] [get_ips sem_ultra_0_vio_si1_so41]
    generate_target all [get_ips sem_ultra_0_vio_si1_so41]
    create_ip_run [get_ips sem_ultra_0_vio_si1_so41]
    launch_runs sem_ultra_0_vio_si1_so41_synth_1
    wait_on_run sem_ultra_0_vio_si1_so41_synth_1
    
    # VIO core 3: sem_ultra_0_vio_si1_so5
    puts ">>> Creating VIO core: sem_ultra_0_vio_si1_so5..."
    create_ip -name vio -vendor xilinx.com -library ip -version 3.0 \
        -module_name sem_ultra_0_vio_si1_so5 -dir $IP_DIR -force
    set_property -dict [list \
        CONFIG.C_NUM_PROBE_OUT {5} \
        CONFIG.C_NUM_PROBE_IN {1} \
        CONFIG.C_PROBE_IN0_WIDTH {1} \
    ] [get_ips sem_ultra_0_vio_si1_so5]
    generate_target all [get_ips sem_ultra_0_vio_si1_so5]
    create_ip_run [get_ips sem_ultra_0_vio_si1_so5]
    launch_runs sem_ultra_0_vio_si1_so5_synth_1
    wait_on_run sem_ultra_0_vio_si1_so5_synth_1
    
    close_project
    
    # Cleanup temporary project
    file delete -force $IP_DIR/$temp_proj
    
    # Create marker file
    set marker [open $marker_file w]
    puts $marker "SEM IP generated successfully"
    close $marker
    
    puts ">>> SEM IP generation complete!"
    
    # Read all generated IP
    puts ">>> Reading generated IP..."
    read_ip $IP_DIR/sem_ultra_0/sem_ultra_0.xci
    read_ip $IP_DIR/sem_ultra_0_vio_si14/sem_ultra_0_vio_si14.xci
    read_ip $IP_DIR/sem_ultra_0_vio_si1_so41/sem_ultra_0_vio_si1_so41.xci
    read_ip $IP_DIR/sem_ultra_0_vio_si1_so5/sem_ultra_0_vio_si1_so5.xci
    
    # CRITICAL: Read ALL example design files (not just the wrapper)
    puts ">>> Reading example design files..."
    set example_files_dir "$example_dir/sem_ultra_0_ex/imports"
    if {[file isdirectory $example_files_dir]} {
        foreach vfile [glob -nocomplain $example_files_dir/*.v] {
            puts "    Reading: [file tail $vfile]"
            read_verilog $vfile
        }
    } else {
        puts "    ERROR: Example files directory not found at $example_files_dir"
    }
}

puts "=========================================="
puts ">>> SEM ULTRA IP SETUP COMPLETE"
puts "=========================================="