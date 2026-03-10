# =============================================================================
# FATORI-V • Pblock Algorithm
# File: generate_pblocks.py
# 
# CLI entry point for pblock generation system
# =============================================================================

import argparse
import sys
import yaml
from pathlib import Path

# Add both project root and local directory to sys.path
# This allows imports of both local modules (calculator, placer, writer)
# and project modules (scripts.logging.logger)
project_root = Path(__file__).parent.parent.parent.parent
local_dir = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(local_dir))

from calculator import calculate_pblock_sizes, validate_configuration, get_size_breakdown
from placer import create_placement_plan, analyze_utilization, validate_placement
from writer import write_all_outputs


# =============================================================================
# CLI INTERFACE
# =============================================================================

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='FATORI-V Pblock Generation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate pblocks from config file
  python generate_pblocks.py --input my_config.yaml --output system_dict.yaml
  
  # Verbose mode with detailed output
  python generate_pblocks.py --input my_config.yaml --output system_dict.yaml --verbose
  
  # Specify different output directory
  python generate_pblocks.py --input my_config.yaml --output ./output/system_dict.yaml

For more information, see README.md
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input configuration YAML file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output system_dict.yaml file path'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed progress and debug information'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Auto-approve warnings without user prompt (for automated execution)'
    )
    
    return parser.parse_args()


# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

def load_configuration(input_path):
    """
    Load and parse user configuration YAML file.
    
    Args:
        input_path (str): Path to input YAML file
    
    Returns:
        dict: Configuration dictionary
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    try:
        with open(input_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f" Error: Input file not found: {input_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f" Error: Failed to parse YAML file: {e}")
        sys.exit(1)


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline(config, output_path, verbose=False, auto_approve=False):
    """
    Execute complete pblock generation pipeline.
    
    Args:
        config (dict): User configuration
        output_path (str): Output YAML file path
        verbose (bool): Print detailed progress
        auto_approve (bool): Auto-approve warnings without user prompt
    
    Pipeline:
        1. Validate configuration
        2. Calculate pblock sizes
        3. Generate placement plan
        4. Validate placement
        5. Write output files
    """
    
    # # Step 1: Validate configuration
    # if verbose:
    #     print("\n" + "=" * 80)
    #     print("STEP 1: VALIDATING CONFIGURATION")
    #     print("=" * 80)
    
    # warnings = validate_configuration(config)
    
    # if warnings:
    #     print("\nConfiguration warnings:")
    #     for warning in warnings:
    #         print(f"  • {warning}")
        
    #     # Ask user to continue (unless auto-approved)
    #     if not auto_approve:
    #         response = input("\nContinue anyway? (y/n): ")
    #         if response.lower() != 'y':
    #             print("Aborted by user.")
    #             sys.exit(0)
    #     else:
    #         print("\nAuto-approving (--yes flag set)")
    # else:
    #     if verbose:
    #         print(" Configuration valid")
    
    
    # Step 2: Calculate pblock sizes
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 2: CALCULATING PBLOCK SIZES")
        print("=" * 80)
    
    sizes, disabled_targets, name_mapping = calculate_pblock_sizes(config)
    
    if verbose:
        print(f"\nEnabled targets: {len(sizes)}")
        for target, size in sorted(sizes.items()):
            print(f"  {target:<20} {size:>6,} LUTs")
        if disabled_targets:
            print(f"\nDisabled targets: {len(disabled_targets)}")
            for target in sorted(disabled_targets):
                print(f"  {target:<20} (feature disabled)")
    else:
        print(f" Calculated sizes for {len(sizes)} targets")
        if disabled_targets:
            print(f" {len(disabled_targets)} targets disabled (features not enabled)")
    
    # Get detailed breakdowns for reporting
    size_breakdowns = {}
    for target in sizes.keys():
        size_breakdowns[target] = get_size_breakdown(target, config)
    
    
    # Step 3: Generate placement plan
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 3: GENERATING PLACEMENT PLAN")
        print("=" * 80)
    
    placement_plan = create_placement_plan(sizes, config)
    
    if verbose:
        print("\nPlacement assignments:")
        for target, plan in sorted(placement_plan.items()):
            print(f"  {target:<20} → {plan['region_name']:<20} ({plan['coordinates']})")
    else:
        print(" Generated placement plan")
    
    
    # Step 4: Analyze utilization
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 4: ANALYZING UTILIZATION")
        print("=" * 80)
    
    utilization = analyze_utilization(placement_plan)
    
    if verbose:
        print(f"\nFPGA Utilization: {utilization['fpga_utilization_percent']:.1f}%")
        print(f"Regions Used: {utilization['regions_used']}/{utilization['total_regions']}")
        print(f"\nPer-region utilization:")
        for region in utilization['region_utilization']:
            if region['luts_used'] > 0:
                print(f"  {region['region_name']:<20} {region['utilization_percent']:>6.1f}%  "
                      f"({region['luts_used']:,}/{region['capacity']:,} LUTs)")
    else:
        print(f" FPGA utilization: {utilization['fpga_utilization_percent']:.1f}%")
    
    
    # Step 5: Validate placement
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 5: VALIDATING PLACEMENT")
        print("=" * 80)
    
    placement_warnings = validate_placement(placement_plan)
    
    if placement_warnings:
        print("\n⚠ Placement warnings:")
        for warning in placement_warnings:
            print(f"  • {warning}")
    else:
        if verbose:
            print(" Placement valid")
    
    
    # Step 6: Write outputs
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 6: WRITING OUTPUT FILES")
        print("=" * 80)
    
    write_all_outputs(placement_plan, size_breakdowns, utilization, output_path, disabled_targets, name_mapping)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    
    # Print banner
    print("=" * 80)
    print("FATORI-V PBLOCK GENERATION SYSTEM")
    print("=" * 80)
    
    # Parse arguments
    args = parse_arguments()
    
    # Load configuration
    print(f"\nLoading configuration: {args.input}")
    config = load_configuration(args.input)
    print(" Configuration loaded")
    
    # Run pipeline
    try:
        run_pipeline(config, args.output, verbose=args.verbose, auto_approve=args.yes)
        
        print("\n" + "=" * 80)
        print(" PBLOCK GENERATION COMPLETE")
        print("=" * 80)
        print(f"\nOutput written to: {args.output}")
        print("\nNext steps:")
        print("  1. Review pblock_summary.txt for detailed breakdown")
        print("  2. Add pblocks.xdc to your Vivado project")
        print("  3. Use system_dict.yaml with ACME fault injection tool")
        
    except Exception as e:
        print(f"\n Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()