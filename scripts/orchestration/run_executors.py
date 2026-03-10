# =============================================================================
# FATORI-V • Run Executors
# File: run_executors.py
# -----------------------------------------------------------------------------
# Functions for executing single and multiple runs.
# =============================================================================

from pathlib import Path
from scripts.cli.override_applicator import apply_cli_overrides
from scripts.orchestration.run_controller import RunController
from scripts.common.yaml_io.load_run_yaml import load_run_yaml
from scripts.logging.logger import log_event


# ANSI color codes
COLOR_HEADER = '\033[1;36m'  # Cyan bold
COLOR_RUN = '\033[1;33m'     # Yellow bold
COLOR_SUCCESS = '\033[1;32m' # Green bold
COLOR_ERROR = '\033[1;31m'   # Red bold
COLOR_RESET = '\033[0m'


def execute_single_run(yaml_path: Path, cli_args, run_number: int = None, total_runs: int = None) -> int:
    """
    Execute a single run configuration.
    
    Args:
        yaml_path: Path to configuration YAML file
        cli_args: Parsed CLI arguments
        run_number: Optional run number for multi-run display
        total_runs: Optional total number of runs for multi-run display
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Print run header if in multi-run mode
    if run_number and total_runs:
        print(f"\n{COLOR_RUN}{'='*80}")
        print(f"RUN {run_number}/{total_runs}: {yaml_path.name}")
        print(f"{'='*80}{COLOR_RESET}\n")
    
    log_event('FATORI_START')
    log_event('CONFIG_LOADED', yaml_path=yaml_path)
    
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
    is_dry_run = cli_args and cli_args.dry_run
    if is_dry_run:
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
        
        # Return appropriate exit code
        if success:
            log_event('RUN_SUCCESS')
            
            # Dry-run reminder for single runs (after RUN_SUCCESS)
            if is_dry_run and not run_number:
                log_event('DRY_RUN_REMINDER')
            
            return 0
        else:
            # Get run name from yaml_path if available
            run_name = yaml_path.stem if yaml_path else "unknown"
            log_event('RUN_FAILED', run_name=run_name, error_message="Phase execution failed")
            return 1
    
    except KeyboardInterrupt:
        log_event('RUN_INTERRUPTED')
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        log_event('ERROR_UNEXPECTED', error_message=str(e))
        return 1


def execute_multiple_runs(yaml_paths: list, cli_args) -> int:
    """
    Execute multiple run configurations sequentially.
    
    Each run is executed using the same execute_single_run() path to ensure
    consistency and easier debugging.
    
    In dry-run mode, architecture is restored between runs to ensure each run
    starts with a clean state.
    
    Args:
        yaml_paths: List of paths to configuration YAML files
        cli_args: Parsed CLI arguments
    
    Returns:
        Exit code (0 if all succeeded, non-zero otherwise)
    """
    log_event('MULTI_RUN_START', run_count=len(yaml_paths))
    
    is_dry_run = cli_args and hasattr(cli_args, 'dry_run') and cli_args.dry_run
    successful_runs = 0
    failed_runs = 0
    
    # Execute each run sequentially
    # Always continue to next run even if current run fails
    for idx, yaml_path in enumerate(yaml_paths, 1):
        # Execute single run with run number display
        exit_code = execute_single_run(yaml_path, cli_args, run_number=idx, total_runs=len(yaml_paths))
        
        if exit_code == 0:
            successful_runs += 1
            log_event('MULTI_RUN_ITEM_SUCCESS', run_number=idx, yaml_path=str(yaml_path))
        else:
            failed_runs += 1
            log_event('MULTI_RUN_ITEM_FAILED', run_number=idx, yaml_path=str(yaml_path))
            # Continue to next run - never abort multi-run on failure
        
        # In dry-run mode, restore architecture between runs (except after last run)
        if is_dry_run and idx < len(yaml_paths):
            log_event('MULTI_RUN_DRY_RESTORE', run_number=idx)
            from scripts.orchestration.arch_restore import restore_architecture_from_backup
            from scripts.build.backup_manager import cleanup_backup_dir
            
            # Restore files from backup
            if not restore_architecture_from_backup():
                log_event('WARNING', warning_message=f"Failed to restore architecture after run {idx}")
            
            # Clean backup directory for next run
            cleanup_backup_dir()
    
    # Report final results
    print(f"\n{COLOR_HEADER}{'='*80}")
    if failed_runs == 0:
        print(f"{COLOR_SUCCESS}MULTI-RUN COMPLETE: All {successful_runs} runs succeeded{COLOR_RESET}")
    else:
        print(f"{COLOR_ERROR}MULTI-RUN COMPLETE: {successful_runs} succeeded, {failed_runs} failed{COLOR_RESET}")
    print(f"{COLOR_HEADER}{'='*80}{COLOR_RESET}\n")
    
    if failed_runs == 0:
        log_event('ALL_RUNS_SUCCESS', total_count=len(yaml_paths))
        
        # Dry-run reminder for multi-run mode (after ALL_RUNS_SUCCESS)
        if is_dry_run:
            log_event('DRY_RUN_REMINDER')
        
        return 0
    else:
        log_event('MULTIPLE_RUNS_FAILED', failed_count=failed_runs, total_count=len(yaml_paths))
        return 1