# =============================================================================
# FATORI-V • Main Entry Point
# File: fatori-v.py
# -----------------------------------------------------------------------------
# Main entry point for FATORI-V fault injection framework with CLI support.
# =============================================================================

import sys
from pathlib import Path
from scripts.cli.argument_parser import parse_arguments
from scripts.logging.logger import initialize_logger, log_event
from scripts.orchestration.run_executors import execute_single_run, execute_multiple_runs

# ANSI color codes
COLOR_HEADER = '\033[1;36m'  # Cyan bold
COLOR_INFO = '\033[1;37m'    # White bold  
COLOR_DRY_RUN = '\033[1;35m' # Magenta bold
COLOR_RESET = '\033[0m'


def print_fatori_header(yaml_files: list, dry_run: bool):
    """
    Print FATORI-V header with run list and dry-run notice.
    
    Args:
        yaml_files: List of YAML configuration files
        dry_run: Whether dry-run mode is enabled
    """
    print(f"\n{COLOR_HEADER}{'='*80}")
    print("FATORI-V - Fault Injection Framework for RISC-V")
    print(f"{'='*80}{COLOR_RESET}\n")
    
    # Show run list
    if len(yaml_files) == 1:
        print(f"{COLOR_INFO}Configuration: {yaml_files[0]}{COLOR_RESET}\n")
    else:
        print(f"{COLOR_INFO}Scheduled runs: {len(yaml_files)}{COLOR_RESET}")
        for yaml_file in yaml_files:
            print(f"  - {yaml_file.name}")
        print()
    
    # Show dry-run notice if enabled
    if dry_run:
        print(f"{COLOR_DRY_RUN}{'='*80}")
        print("DRY-RUN MODE ENABLED")
        print(f"{'='*80}{COLOR_RESET}")
        print("Commands will be displayed but not executed.")
        print("Files will be generated and validation will run.")
        print(f"{COLOR_DRY_RUN}{'='*80}{COLOR_RESET}\n")


def discover_yaml_files():
    """
    Auto-discover all .yaml files in runs/ directory.
    
    Returns:
        Sorted list of Path objects for .yaml files
    """
    runs_dir = Path('runs')
    
    if not runs_dir.exists():
        log_event('ERROR', message="runs/ directory not found")
        return []
    
    yaml_files = sorted(runs_dir.glob('*.yaml'))
    
    if not yaml_files:
        log_event('WARNING', warning_message="No .yaml files found in runs/ directory")
    
    return yaml_files


def main():
    """
    Main entry point for FATORI-V.
    
    Steps:
    1. Parse CLI arguments
    2. Initialize logger
    3. Handle special modes (arch-restore, display-checks)
    4. Discover/validate YAML files
    5. Print header
    6. Execute runs
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Parse CLI arguments
    try:
        args = parse_arguments()
    except SystemExit as e:
        return e.code
    
    # Initialize logger
    general_log_file = Path('results') / 'fatori_general_log.txt'
    log_level = args.log_level if hasattr(args, 'log_level') and args.log_level else 'normal'
    initialize_logger(log_level=log_level, general_log_file=general_log_file)
    
    # Special mode: --arch-restore
    if args.arch_restore:
        from scripts.orchestration.arch_restore import execute_arch_restore
        return execute_arch_restore()
    
    # Special mode: --display-checks
    if args.display_checks:
        from config.validation_checks import display_all_checks
        print("=" * 80)
        print("FATORI-V Validation Checks")
        print("=" * 80)
        display_all_checks()
        return 0
    
    # Determine which YAML files to run
    if args.single_run:
        # Single run mode: run specific file from runs/
        single_yaml = Path('runs') / args.single_run
        if not single_yaml.exists():
            log_event('ERROR_FILE_NOT_FOUND', filepath=str(single_yaml))
            print(f"ERROR: Configuration file not found: {single_yaml}")
            return 1
        args.yaml_files = [single_yaml]
    elif not args.yaml_files:
        # Auto-discovery mode: find all .yaml in runs/
        args.yaml_files = discover_yaml_files()
        if not args.yaml_files:
            print("ERROR: No configuration files found. Specify YAML files or add them to runs/ directory.")
            return 1
    
    # Validate all YAML files exist
    for yaml_path in args.yaml_files:
        if not yaml_path.exists():
            log_event('ERROR_FILE_NOT_FOUND', filepath=str(yaml_path))
            print(f"ERROR: Configuration file not found: {yaml_path}")
            return 1
    
    # Add continue_on_error attribute if not present
    if not hasattr(args, 'continue_on_error'):
        args.continue_on_error = False
    
    # Print FATORI-V header with run list and dry-run notice
    dry_run = hasattr(args, 'dry_run') and args.dry_run
    print_fatori_header(args.yaml_files, dry_run)
    
    # Execute runs
    if len(args.yaml_files) == 1:
        return execute_single_run(args.yaml_files[0], args)
    else:
        return execute_multiple_runs(args.yaml_files, args)


if __name__ == "__main__":
    sys.exit(main())