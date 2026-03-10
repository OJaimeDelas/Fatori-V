# =============================================================================
# FATORI-V • Pblock Algorithm
# File: writer.py
# 
# Generate output files (YAML, TCL, summary reports)
# =============================================================================

import yaml
import os
from datetime import datetime
from scripts.logging.logger import log_event


# =============================================================================
# SYSTEM_DICT.YAML GENERATION
# =============================================================================

def write_system_dict(placement_plan, output_path, disabled_targets=None, name_mapping=None):
    """
    Write system_dict.yaml for ACME fault injection tool.
    
    Includes both enabled targets (with real pblocks) and disabled targets (empty pblocks).
    Uses original user-provided names in output.
    
    Args:
        placement_plan (dict): Placement plan from placer.py (uses normalized names)
        output_path (str): Output file path
        disabled_targets (list): List of disabled target names (normalized)
        name_mapping (dict): Mapping from normalized_name -> original_name
    
    Output Format:
        fpga: XCKU040-FBVA676-1-C
        targets:
          - name: BRANCH_PREDICTOR  # Original name, not BRANCH_PREDICT
            pblock: CLOCKREGION_X0Y0
            coordinates: SLICE_X0Y0:SLICE_X24Y50
            estimated_luts: 1200
    """
    if disabled_targets is None:
        disabled_targets = []
    if name_mapping is None:
        name_mapping = {}
    
    # Build YAML structure
    yaml_content = {
        'fpga': 'XCKU040-FBVA676-1-C',
        'targets': []
    }
    
    # Add enabled targets (restore original names)
    for target_name in sorted(placement_plan.keys()):
        plan = placement_plan[target_name]
        
        # Use original name from mapping, fall back to normalized if not found
        original_name = name_mapping.get(target_name, target_name)
        
        target_entry = {
            'name': original_name,
            'pblock': plan['region_name'],
            'coordinates': plan['coordinates'],
            'estimated_luts': plan['size']
        }
        
        yaml_content['targets'].append(target_entry)
    
    # Add disabled targets with empty pblocks (restore original names)
    for target_name in sorted(disabled_targets):
        # Use original name from mapping, fall back to normalized if not found
        original_name = name_mapping.get(target_name, target_name)
        
        target_entry = {
            'name': original_name,
            'pblock': None,
            'coordinates': None,
            'estimated_luts': 0
        }
        
        yaml_content['targets'].append(target_entry)
    
    # Write YAML file
    with open(output_path, 'w') as f:
        yaml.dump(yaml_content, f, 
                 default_flow_style=False,
                 sort_keys=False,
                 indent=2)
    
    filename = os.path.basename(output_path)
    log_event('FILE_GENERATED', filename=filename, output_path=output_path)


# =============================================================================
# VIVADO TCL CONSTRAINTS GENERATION
# =============================================================================

def write_vivado_constraints(placement_plan, output_path):
    """
    Write Vivado TCL constraints file for pblock implementation.
    
    Generates HARD pblocks (CONTAIN_ROUTING=1) with proper resource allocation.
    For MULTIPLIER pblocks, includes DSP48 blocks based on variant.
    
    Args:
        placement_plan (dict): Placement plan from placer.py with structure:
            {
                'target': {
                    'size': LUT_count,
                    'coordinates': 'SLICE_X0Y0:SLICE_X10Y20',
                    'dsp_count': N,  # Optional, for MULTIPLIER only
                    'dsp_coordinates': 'DSP48_X0Y0:DSP48_X0Y3',  # Optional
                }
            }
        output_path (str): Output TCL file path (.tcl)
    
    Output:
        TCL commands to create and populate HARD pblocks in Vivado
    """
    lines = []
    
    # Header
    lines.append("# " + "=" * 77)
    lines.append("# FATORI-V Pblock Constraints")
    lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("# Device: XCKU040-FBVA676-1-C")
    lines.append("# NOTE: All pblocks are HARD and EXCLUSIVE")
    lines.append("#   IS_SOFT=0: Hard constraint (no overflow)")
    lines.append("#   EXCLUDE_PLACEMENT=1: No other cells allowed in region")
    lines.append("#   CONTAIN_ROUTING=1: No routing outside pblock")
    lines.append("# " + "=" * 77)
    lines.append("")
    
    # Generate pblock for each target
    for target_name in sorted(placement_plan.keys()):
        plan = placement_plan[target_name]
        pblock_name = f"pblock_{target_name.lower()}"
        
        # Comment with resource summary
        comment = f"# {target_name} - {plan['size']} LUTs"
        if 'dsp_count' in plan and plan['dsp_count'] > 0:
            comment += f", {plan['dsp_count']} DSPs"
        lines.append(comment)
        
        # Create pblock
        lines.append(f"create_pblock {pblock_name}")
        
        # Resize with SLICE coordinates
        lines.append(f"resize_pblock {pblock_name} -add {{{plan['coordinates']}}}")
        
        # Add DSP coordinates if present (MULTIPLIER only)
        if 'dsp_coordinates' in plan and plan['dsp_coordinates']:
            lines.append(f"resize_pblock {pblock_name} -add {{{plan['dsp_coordinates']}}}")
        
        # Set pblock properties for hard, exclusive placement
        # IS_SOFT=0: Force all assigned cells inside pblock (hard constraint)
        # EXCLUDE_PLACEMENT=1: Prevent ANY other cells from using this region
        # CONTAIN_ROUTING=1: Prevent routing from leaving pblock
        lines.append(f"set_property IS_SOFT 0 [get_pblocks {pblock_name}]")
        lines.append(f"set_property EXCLUDE_PLACEMENT 1 [get_pblocks {pblock_name}]")
        lines.append(f"set_property CONTAIN_ROUTING 1 [get_pblocks {pblock_name}]")
        
        # Add cells to pblock with exclusion patterns for parent modules
        cell_pattern = get_cell_pattern(target_name)
        exclusion_pattern = get_cell_exclusion_pattern(target_name)
        
        if exclusion_pattern:
            # Parent module - exclude children that have separate pblocks
            lines.append(f"add_cells_to_pblock {pblock_name} [get_cells -hierarchical -filter {{NAME =~ {cell_pattern} && {exclusion_pattern}}}]")
        else:
            # Leaf module - no exclusions needed
            lines.append(f"add_cells_to_pblock {pblock_name} [get_cells -hierarchical -filter {{NAME =~ {cell_pattern}}}]")
        
        lines.append("")
    
    # Write file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    filename = os.path.basename(output_path)
    log_event('FILE_GENERATED', filename=filename, output_path=output_path)


def get_cell_pattern(target_name):
    """
    Get hierarchical cell pattern for Vivado cell matching.

    Patterns are anchored under u_ibex_core to prevent accidental capture of
    SEM IP internals (e.g. sem_ultra_v3_1_16_controller) or other IPs that
    share keywords with ibex module names.

    Hierarchy confirmed from placed-design utilization reports:
      u_ibex_core
      ├─ ex_block_i / g_alu_single.alu_i
      ├─ g_if_single.if_stage_i / gen_prefetch_buffer.prefetch_buffer_i
      ├─ g_lsu_single.load_store_unit_i
      ├─ id_stage_i / g_ctrl_single.controller_i
      │              g_dec_single.decoder_i
      └─ wb_stage_i

    Args:
        target_name (str): Module name (e.g. 'ALU', 'CONTROLLER')

    Returns:
        str: Vivado NAME filter pattern
    """
    patterns = {
        # ALU is a child of ex_block_i — anchor both levels.
        'ALU':             '*u_ibex_core/ex_block_i/g_alu_single.alu_i*',
        # CONTROLLER is a child of id_stage_i, not a top-level sibling.
        'CONTROLLER':      '*u_ibex_core/id_stage_i/g_ctrl_single.controller_i*',
        # DECODER is a sibling of CONTROLLER inside id_stage_i.
        'DECODER':         '*u_ibex_core/id_stage_i/g_dec_single.decoder_i*',
        # LSU is a direct child of u_ibex_core.
        'LSU':             '*u_ibex_core/g_lsu_single.load_store_unit_i*',
        # IF_STAGE includes prefetch, icache and branch-predict as sub-instances.
        'IF_STAGE':        '*u_ibex_core/g_if_single.if_stage_i*',
        # ID_STAGE includes controller and decoder; used when the whole stage is one pblock.
        'ID_STAGE':        '*u_ibex_core/id_stage_i*',
        # EX_BLOCK includes ALU and MULTDIV; used when the whole block is one pblock.
        'EX_BLOCK':        '*u_ibex_core/ex_block_i*',
        'WB_STAGE':        '*u_ibex_core/wb_stage_i*',
        # Sub-instances within if_stage_i.
        'PREFETCH_BUFFER': '*u_ibex_core/g_if_single.if_stage_i/gen_prefetch_buffer.prefetch_buffer_i*',
        'BRANCH_PREDICT':  '*u_ibex_core/g_if_single.if_stage_i*ibex_branch_predict*',
        'MULTDIV':         '*u_ibex_core/ex_block_i*multdiv*',
        'ICACHE':          '*u_ibex_core/g_if_single.if_stage_i*icache*',
    }

    return patterns.get(target_name, f"*u_ibex_core*{target_name.lower()}*")


def get_cell_exclusion_pattern(target_name):
    """
    Get exclusion pattern for parent modules that have children with separate pblocks.
    
    When a parent module like ID_STAGE has children (CONTROLLER, DECODER) with their
    own pblocks, we need to exclude those children from the parent's pblock assignment.
    
    Args:
        target_name (str): Module name
    
    Returns:
        str: Vivado NAME filter exclusion pattern, or empty string if no exclusions
    """
    exclusions = {
        # ID_STAGE contains CONTROLLER and DECODER as children
        # Exclude them from ID_STAGE pblock if they have separate pblocks
        'ID_STAGE': "NAME !~ *controller_i* && NAME !~ *decoder_i*",
        
        # EX_BLOCK contains ALU and MULTDIV as children
        # Exclude them if they have separate pblocks
        'EX_BLOCK': "NAME !~ *alu_i* && NAME !~ *multdiv*",
    }
    
    return exclusions.get(target_name, "")


# =============================================================================
# SUMMARY REPORT GENERATION
# =============================================================================

def write_summary_report(placement_plan, size_breakdowns, utilization, output_path):
    """
    Write human-readable summary report.
    
    Args:
        placement_plan (dict): Placement plan
        size_breakdowns (dict): Size calculation breakdowns
        utilization (dict): Utilization statistics
        output_path (str): Output text file path
    
    Output:
        Detailed report with sizes, factors, placement, and utilization
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("FATORI-V PBLOCK GENERATION SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"FPGA: XCKU040-FBVA676-1-C (Kintex UltraScale)")
    lines.append("")
    
    # Overall utilization
    lines.append("-" * 80)
    lines.append("FPGA UTILIZATION")
    lines.append("-" * 80)
    lines.append(f"Total LUTs Allocated: {utilization['total_luts_allocated']:,}")
    lines.append(f"Total FPGA LUTs:      {utilization['total_fpga_luts']:,}")
    lines.append(f"FPGA Utilization:     {utilization['fpga_utilization_percent']:.1f}%")
    lines.append(f"Clock Regions Used:   {utilization['regions_used']}/{utilization['total_regions']}")
    lines.append("")
    
    # Per-region utilization
    lines.append("-" * 80)
    lines.append("CLOCK REGION UTILIZATION")
    lines.append("-" * 80)
    lines.append(f"{'Region':<20} {'LUTs Used':<15} {'Capacity':<15} {'Utilization':<15}")
    lines.append("-" * 80)
    
    for region in utilization['region_utilization']:
        if region['luts_used'] > 0:
            lines.append(
                f"{region['region_name']:<20} "
                f"{region['luts_used']:<15,} "
                f"{region['capacity']:<15,} "
                f"{region['utilization_percent']:<14.1f}%"
            )
    lines.append("")
    
    # Size breakdown per target
    lines.append("-" * 80)
    lines.append("TARGET MODULE SIZE BREAKDOWN")
    lines.append("-" * 80)
    
    for target_name in sorted(placement_plan.keys()):
        plan = placement_plan[target_name]
        breakdown = size_breakdowns.get(target_name, {})
        
        lines.append(f"\n{target_name}:")
        lines.append(f"  Baseline Size:        {breakdown.get('base_size', 0):>6} LUTs")
        lines.append(f"  Feature Factor:       {breakdown.get('feature_factor', 1.0):>6.2f}x")
        lines.append(f"  After Features:       {breakdown.get('size_after_features', 0):>6} LUTs")
        lines.append(f"  MON_N:                {breakdown.get('mon_n', 1):>6}")
        lines.append(f"  MON Factor:           {breakdown.get('mon_factor', 1.0):>6.2f}x")
        lines.append(f"  After MON:            {breakdown.get('size_after_mon', 0):>6} LUTs")
        lines.append(f"  Safety Margin:        {breakdown.get('safety_margin', 1.0):>6.2f}x")
        lines.append(f"  Final Size:           {breakdown.get('final_size', 0):>6} LUTs")
        lines.append(f"  Region:               {plan['region_name']}")
        lines.append(f"  Coordinates:          {plan['coordinates']}")
    
    lines.append("")
    lines.append("=" * 80)
    
    # Write file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    filename = os.path.basename(output_path)
    log_event('FILE_GENERATED', filename=filename, output_path=output_path)


# =============================================================================
# OUTPUT DIRECTORY MANAGEMENT
# =============================================================================

def ensure_output_directory(output_path):
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_path (str): File path (directory will be created)
    """
    directory = os.path.dirname(output_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        log_event('DIRECTORY_CREATED', dir_path=directory)


# =============================================================================
# BATCH OUTPUT GENERATION
# =============================================================================

def write_all_outputs(placement_plan, size_breakdowns, utilization, output_yaml_path, disabled_targets=None, name_mapping=None):
    """
    Write all output files (YAML, TCL, summary).
    
    Disabled targets get empty pblocks in YAML output but are excluded from TCL.
    Original user-provided names are preserved in YAML output.
    
    Args:
        placement_plan (dict): Placement plan for enabled targets (normalized names)
        size_breakdowns (dict): Size breakdowns for enabled targets
        utilization (dict): Utilization statistics
        output_yaml_path (str): Path to system_dict.yaml (others derived from this)
        disabled_targets (list): List of disabled target names (normalized)
        name_mapping (dict): Mapping from normalized_name -> original_name
    
    Outputs:
        - system_dict.yaml (main output with all targets, using original names)
        - pblocks.tcl (Vivado constraints - enabled targets only, normalized names)
        - pblock_summary.txt (human-readable report)
    """
    if disabled_targets is None:
        disabled_targets = []
    if name_mapping is None:
        name_mapping = {}
    
    # Ensure output directory exists
    ensure_output_directory(output_yaml_path)
    
    # Derive other output paths
    base_dir = os.path.dirname(output_yaml_path)
    base_name = os.path.splitext(os.path.basename(output_yaml_path))[0]
    
    tcl_path = os.path.join(base_dir, 'fatori_pblocks.tcl')
    summary_path = os.path.join(base_dir, 'pblock_summary.txt')
    
    # Write all outputs
    log_event('INFO', info_message="Generating output files")
    write_system_dict(placement_plan, output_yaml_path, disabled_targets, name_mapping)
    write_vivado_constraints(placement_plan, tcl_path)
    write_summary_report(placement_plan, size_breakdowns, utilization, summary_path)
    
    ## Copy TCL file to tmp/tcl/ where Vivado looks for it (VIVADO_INPUT path)
    # This ensures Vivado always uses the freshly generated pblock constraints
    import shutil
    from pathlib import Path
    
    # Find project root (go up from scripts/pblocks/system/ to project root)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    
    tcl_vivado_path = project_root / 'tmp' / 'tcl' / 'fatori_pblocks.tcl'
    try:
        tcl_vivado_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tcl_path, str(tcl_vivado_path))
        log_event('INFO', info_message=f"Copied pblock constraints to {tcl_vivado_path}")
    except Exception as e:
        log_event('WARNING', warning_message=f"Failed to copy TCL to tmp/tcl/: {e}")
    
    log_event('INFO', info_message="All outputs generated successfully")