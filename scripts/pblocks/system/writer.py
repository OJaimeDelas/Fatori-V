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

def write_system_dict(placement_plan, output_path):
    """
    Write system_dict.yaml for ACME fault injection tool.
    
    Args:
        placement_plan (dict): Placement plan from placer.py
        output_path (str): Output file path
    
    Output Format:
        fpga: XCKU040-FBVA676-1-C
        targets:
          - name: ALU
            pblock: CLOCKREGION_X0Y0
            coordinates: SLICE_X0Y0:SLICE_X24Y50
            estimated_luts: 1200
    """
    # Build YAML structure
    yaml_content = {
        'fpga': 'XCKU040-FBVA676-1-C',
        'targets': []
    }
    
    # Add each target
    for target_name in sorted(placement_plan.keys()):
        plan = placement_plan[target_name]
        
        target_entry = {
            'name': target_name,
            'pblock': plan['region_name'],
            'coordinates': plan['coordinates'],
            'estimated_luts': plan['size']
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
    
    Args:
        placement_plan (dict): Placement plan from placer.py
        output_path (str): Output TCL file path (.tcl)
    
    Output:
        TCL commands to create and populate pblocks in Vivado
    """
    lines = []
    
    # Header
    lines.append("# " + "=" * 77)
    lines.append("# FATORI-V Pblock Constraints")
    lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("# Device: XCKU040-FBVA676-1-C")
    lines.append("# " + "=" * 77)
    lines.append("")
    
    # Generate pblock for each target
    for target_name in sorted(placement_plan.keys()):
        plan = placement_plan[target_name]
        pblock_name = f"pblock_{target_name.lower()}"
        
        lines.append(f"# {target_name} - {plan['size']} LUTs")
        lines.append(f"create_pblock {pblock_name}")
        lines.append(f"resize_pblock {pblock_name} -add {{{plan['coordinates']}}}")
        
        # Add cells to pblock (hierarchical pattern matching)
        cell_pattern = get_cell_pattern(target_name)
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
    
    Args:
        target_name (str): Module name
    
    Returns:
        str: Vivado cell pattern (e.g., "*alu*", "*controller*")
    
    Notes:
        - Patterns are case-insensitive in Vivado
        - Use wildcards for hierarchical matching
    """
    patterns = {
        'ALU': '*alu*',
        'CONTROLLER': '*controller*',
        'DECODER': '*decoder*',
        'LSU': '*load_store*',
        'IF_STAGE': '*if_stage*',
        'ID_STAGE': '*id_stage*',
        'EX_BLOCK': '*ex_block*',
        'WB_STAGE': '*wb_stage*',
        'PREFETCH_BUFFER': '*prefetch*',
        'BRANCH_PREDICT': '*branch_predict*',
        'MULTDIV': '*multdiv*',
        'ICACHE': '*icache*',
    }
    
    return patterns.get(target_name, f"*{target_name.lower()}*")


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

def write_all_outputs(placement_plan, size_breakdowns, utilization, output_yaml_path):
    """
    Write all output files (YAML, TCL, summary).
    
    Args:
        placement_plan (dict): Placement plan
        size_breakdowns (dict): Size breakdowns
        utilization (dict): Utilization statistics
        output_yaml_path (str): Path to system_dict.yaml (others derived from this)
    
    Outputs:
        - system_dict.yaml (main output)
        - pblocks.tcl (Vivado constraints)
        - pblock_summary.txt (human-readable report)
    """
    # Ensure output directory exists
    ensure_output_directory(output_yaml_path)
    
    # Derive other output paths
    base_dir = os.path.dirname(output_yaml_path)
    base_name = os.path.splitext(os.path.basename(output_yaml_path))[0]
    
    tcl_path = os.path.join(base_dir, 'fatori_pblocks.tcl')
    summary_path = os.path.join(base_dir, 'pblock_summary.txt')
    
    # Write all outputs
    log_event('INFO', info_message="Generating output files")
    write_system_dict(placement_plan, output_yaml_path)
    write_vivado_constraints(placement_plan, tcl_path)
    write_summary_report(placement_plan, size_breakdowns, utilization, summary_path)
    log_event('INFO', info_message="All outputs generated successfully")