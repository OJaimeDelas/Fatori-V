# =============================================================================
# FATORI-V • Main Entry Point
# File: fatori-v.py
# -----------------------------------------------------------------------------
# Main entry point for FATORI-V fault injection framework with CLI support.
# =============================================================================

import sys
from pathlib import Path
from scripts.cli.argument_parser import parse_arguments, get_cli_summary
from scripts.cli.override_applicator import apply_cli_overrides
from scripts.cli.progress_display import ProgressDisplay
from scripts.orchestration.run_controller import RunController
from scripts.orchestration.run_cleanup import cleanup_run
from scripts.orchestration.multi_run_controller import run_multiple
from scripts.common.yaml_io.load_run_yaml import load_run_yaml
from scripts.logging.logger import initialize_logger, log_event


def execute_single_run(yaml_path: Path, cli_args) -> int:
    """
    Execute a single run configuration.
    
    Args:
        yaml_path: Path to configuration YAML file
        cli_args: Parsed CLI arguments
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    log_event('FATORI_START')
    log_event('CONFIG_LOADED', yaml_path=yaml_path)
    
    # Display CLI arguments if any overrides
    if cli_args:
        log_event('CLI_SUMMARY', summary=get_cli_summary(cli_args))
    
    # Load configuration
    try:
        config = load_run_yaml(yaml_path)
    except Exception as e:
        log_event('ERROR_CONFIG_LOAD_FAILED', error_message=str(e))
        return 1
    
    # Apply CLI overrides if provided
    if cli_args:
        config = apply_cli_overrides(config, cli_args)
    
    # Set dry-run mode flag if requested
    if cli_args and cli_args.dry_run:
        import fatori_settings as cfg
        cfg.DRY_RUN_MODE = True
        log_event('DRY_RUN_MODE_ENABLED')
    
    # Create and execute run controller
    try:
        # Determine log level
        log_level = cli_args.log_level if cli_args else None
        
        # Create controller (pass config if CLI overrides applied)
        if cli_args:
            controller = RunController(yaml_path, log_level=log_level, config=config)
        else:
            controller = RunController(yaml_path, log_level=log_level)
        
        # Execute workflow
        success = controller.execute()
        
        # Cleanup
        if controller.context:
            cleanup_run(controller.context, success, preserve_tmp=True)
        
        # Return appropriate exit code
        if success:
            log_event('RUN_SUCCESS')
            return 0
        else:
            log_event('RUN_FAILED_GENERAL')
            return 1
    
    except KeyboardInterrupt:
        log_event('RUN_INTERRUPTED')
        if controller.context:
            cleanup_run(controller.context, False, preserve_tmp=True)
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        log_event('ERROR_UNEXPECTED', error_message=str(e))
        
        # Try to cleanup
        if controller and controller.context:
            try:
                cleanup_run(controller.context, False, preserve_tmp=True)
            except:
                pass
        
        return 1


def execute_multiple_runs(yaml_paths: list, cli_args) -> int:
    """
    Execute multiple run configurations.
    
    Args:
        yaml_paths: List of paths to configuration YAML files
        cli_args: Parsed CLI arguments
    
    Returns:
        Exit code (0 if all succeeded, non-zero otherwise)
    """
    # Display CLI arguments if any overrides
    if cli_args:
        log_event('CLI_SUMMARY', summary=get_cli_summary(cli_args))
    
    # Run all configurations
    results = run_multiple(yaml_paths, cli_args)
    
    # Determine overall success
    if all_successful:
        log_event('ALL_RUNS_SUCCESS', total_count=len(results))
        return 0
    else:
        failed_count = sum(1 for r in results if not r.success)
        log_event('MULTIPLE_RUNS_FAILED', failed_count=failed_count, total_count=len(results))
        return 1


def main():
    """
    Main entry point for FATORI-V.
    
    Parses CLI arguments and executes single or multiple runs.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Initialize general log file
    general_log_file = Path('results') / 'fatori_general_log.txt'
    
    # Parse CLI arguments
    try:
        args = parse_arguments()
        
        # Initialize logger with general log and user's log level
        log_level = args.log_level if hasattr(args, 'log_level') and args.log_level else 'normal'
        initialize_logger(
            log_level=log_level,
            general_log_file=general_log_file
        )
        
    except SystemExit as e:
        return e.code
    
    # Check if YAML files exist
    for yaml_path in args.yaml_files:
        if not yaml_path.exists():
            log_event('ERROR_FILE_NOT_FOUND', filepath=str(yaml_path))
            return 1
    
    # Add continue_on_error attribute if not present
    if not hasattr(args, 'continue_on_error'):
        args.continue_on_error = False
    
    # Single run or multiple runs
    if len(args.yaml_files) == 1:
        return execute_single_run(args.yaml_files[0], args)
    else:
        return execute_multiple_runs(args.yaml_files, args)


if __name__ == "__main__":
    sys.exit(main())