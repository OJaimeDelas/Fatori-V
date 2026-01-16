# =============================================================================
# FATORI-V • CLI Argument Parser
# File: argument_parser.py
# -----------------------------------------------------------------------------
# Comprehensive argument parsing for command-line interface.
# =============================================================================

import argparse
import sys
from pathlib import Path
import fatori_settings as cfg
from config.constants import LOG_LEVEL_DEFAULT


def create_argument_parser():
    """
    Create argument parser for FATORI-V CLI.
    
    Returns:
        ArgumentParser configured with all CLI options
    """
    parser = argparse.ArgumentParser(
        prog='fatori-v',
        description='FATORI-V Fault Injection Framework for RISC-V Processors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single configuration
  python fatori-v.py runs/config.yaml
  
  # Run multiple configurations
  python fatori-v.py runs/config1.yaml runs/config2.yaml
  
  # Override logging level
  python fatori-v.py runs/config.yaml --log-level DEBUG
  
  # Disable fault injection
  python fatori-v.py runs/config.yaml --no-fi
  
  # Dry run to preview operations
  python fatori-v.py runs/config.yaml --dry-run
  
  # Skip clean step for faster development
  python fatori-v.py runs/config.yaml --no-clean
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'yaml_files',
        nargs='+',
        type=Path,
        help='One or more run configuration YAML files'
    )
    
    # Logging options
    logging_group = parser.add_argument_group('Logging Options')
    logging_group.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=None,
        help=f'Override logging level (default: {LOG_LEVEL_DEFAULT})'
    )
    logging_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (equivalent to --log-level DEBUG)'
    )
    logging_group.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output (equivalent to --log-level ERROR)'
    )
    
    # Build options
    build_group = parser.add_argument_group('Build Options')
    build_group.add_argument(
        '--no-clean',
        action='store_true',
        help='Skip make clean step before build'
    )
    build_group.add_argument(
        '--make-jobs',
        type=int,
        default=None,
        metavar='N',
        help=f'Number of parallel make jobs (default: {cfg.MAKE_JOBS_DEFAULT})'
    )
    
    # Execution options
    exec_group = parser.add_argument_group('Execution Options')
    exec_group.add_argument(
        '--grab-timeout',
        type=int,
        default=None,
        metavar='SECONDS',
        help=f'Board grab timeout in seconds (default: {cfg.BOARD_GRAB_TIMEOUT_DEFAULT})'
    )
    exec_group.add_argument(
        '--no-fi',
        action='store_true',
        help='Disable fault injection even if configured in YAML'
    )
    
    # Run control options
    control_group = parser.add_argument_group('Run Control Options')
    control_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running'
    )
    control_group.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        metavar='PATH',
        help=f'Override results output directory (default: {cfg.RESULTS_DIR})'
    )
    control_group.add_argument(
        '--resume',
        type=Path,
        default=None,
        metavar='STATE_FILE',
        help='Resume from saved state file (future feature)'
    )
    
    # Phase control
    phase_group = parser.add_argument_group('Phase Control Options')
    phase_group.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip configuration validation phase (not recommended)'
    )
    phase_group.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip file generation phase (requires previous generation)'
    )
    phase_group.add_argument(
        '--skip-build',
        action='store_true',
        help='Skip FPGA build phase (requires existing bitstream)'
    )
    phase_group.add_argument(
        '--skip-execution',
        action='store_true',
        help='Skip benchmark execution phase'
    )
    phase_group.add_argument(
        '--skip-results',
        action='store_true',
        help='Skip results collection phase'
    )
    
    return parser


def parse_arguments(args=None):
    """
    Parse command-line arguments.
    
    Args:
        args: List of arguments (None = use sys.argv)
    
    Returns:
        Namespace with parsed arguments
    """
    parser = create_argument_parser()
    
    # If no args provided and sys.argv has no args, show help
    if args is None and len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    parsed_args = parser.parse_args(args)
    
    # Handle verbose/quiet shortcuts
    if parsed_args.verbose:
        parsed_args.log_level = 'DEBUG'
    elif parsed_args.quiet:
        parsed_args.log_level = 'ERROR'
    
    # Validate YAML files exist
    for yaml_file in parsed_args.yaml_files:
        if not yaml_file.exists():
            parser.error(f"Configuration file not found: {yaml_file}")
    
    # Validate mutually exclusive options
    if parsed_args.verbose and parsed_args.quiet:
        parser.error("Cannot use both --verbose and --quiet")
    
    # Warn about future features
    if parsed_args.resume:
        print("WARNING: --resume is not yet implemented")
    
    return parsed_args


def get_cli_summary(args):
    """
    Get summary of CLI arguments for logging.
    
    Args:
        args: Parsed arguments namespace
    
    Returns:
        String with CLI summary
    """
    lines = []
    lines.append("CLI Arguments:")
    lines.append(f"  Configuration files: {len(args.yaml_files)}")
    
    if args.log_level:
        lines.append(f"  Log level: {args.log_level}")
    
    if args.no_clean:
        lines.append("  Skip clean: Yes")
    
    if args.make_jobs:
        lines.append(f"  Make jobs: {args.make_jobs}")
    
    if args.grab_timeout:
        lines.append(f"  Grab timeout: {args.grab_timeout}s")
    
    if args.no_fi:
        lines.append("  Fault injection: Disabled")
    
    if args.dry_run:
        lines.append("  Mode: Dry run")
    
    if args.output_dir:
        lines.append(f"  Output directory: {args.output_dir}")
    
    # Phase skips
    skipped = []
    if args.skip_validation:
        skipped.append("validation")
    if args.skip_generation:
        skipped.append("generation")
    if args.skip_build:
        skipped.append("build")
    if args.skip_execution:
        skipped.append("execution")
    if args.skip_results:
        skipped.append("results")
    
    if skipped:
        lines.append(f"  Skipped phases: {', '.join(skipped)}")
    
    return "\n".join(lines)