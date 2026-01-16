# =============================================================================
# FATORI-V • Multi-Run Controller
# File: multi_run_controller.py
# -----------------------------------------------------------------------------
# Orchestrates execution of multiple runs with progress tracking.
# =============================================================================

from pathlib import Path
from typing import List
from dataclasses import dataclass
from scripts.orchestration.run_controller import RunController
from scripts.orchestration.run_cleanup import cleanup_run
from scripts.logging.logger import log_event
from scripts.cli.override_applicator import apply_cli_overrides
from scripts.cli.progress_display import ProgressDisplay
from scripts.common.yaml_io.load_run_yaml import load_run_yaml
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.common.common_settings import KEY_RUN, KEY_RUN_IDENTIFICATION, KEY_IDENT_NAME


@dataclass
class RunResult:
    """
    Result of a single run execution.
    """
    yaml_path: Path
    success: bool
    error: str = None
    duration: float = 0.0


def execute_single_run(yaml_path: Path, cli_args, display: ProgressDisplay = None) -> RunResult:
    """
    Execute a single run configuration.
    
    Args:
        yaml_path: Path to configuration YAML
        cli_args: CLI arguments
        display: Optional progress display
    
    Returns:
        RunResult object
    """
    try:
        # Load configuration
        config = load_run_yaml(yaml_path)
        
        # Apply CLI overrides
        if cli_args:
            config = apply_cli_overrides(config, cli_args)
        
        # Get run name for display
        run_ident = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, default={})
        run_name = run_ident.get(KEY_IDENT_NAME, yaml_path.stem)
        
        # Update progress display
        if display:
            display.set_current_run(run_name)
        
        # Create and execute controller
        log_level = cli_args.log_level if cli_args and hasattr(cli_args, 'log_level') else None
        controller = RunController(yaml_path, log_level=log_level)
        
        # Override config
        if cli_args:
            controller.context.config = config
        
        # Execute
        success = controller.execute()
        
        # Cleanup
        if controller.context:
            cleanup_run(controller.context, success, preserve_tmp=True)
        
        return RunResult(
            yaml_path=yaml_path,
            success=success,
            duration=controller.context.elapsed_seconds() if controller.context else 0.0
        )
    
    except Exception as e:
        return RunResult(
            yaml_path=yaml_path,
            success=False,
            error=str(e)
        )


def run_multiple(yaml_paths: List[Path], cli_args) -> List[RunResult]:
    """
    Execute multiple run configurations.
    
    Args:
        yaml_paths: List of YAML configuration paths
        cli_args: CLI arguments
    
    Returns:
        List of RunResult objects
    """
    log_event('MULTI_RUN_START', run_count=len(yaml_paths))
    
    results = []
    
    # Create progress display if not in quiet mode
    display = None
    if not (cli_args and hasattr(cli_args, 'quiet') and cli_args.quiet):
        display = ProgressDisplay(total_runs=len(yaml_paths))
    
    # Execute each run
    for i, yaml_path in enumerate(yaml_paths):
        log_event('MULTI_RUN_SINGLE_START', 
                  run_index=i+1, 
                  total_runs=len(yaml_paths), 
                  yaml_path=str(yaml_path))
        
        try:
            result = execute_single_run(yaml_path, cli_args, display)
            results.append(result)
            
            if display:
                if result.success:
                    display.increment_successful()
                else:
                    display.increment_failed()
        
        except KeyboardInterrupt:
            log_event('MULTI_RUN_INTERRUPTED')
            
            # Mark remaining as skipped
            for remaining_path in yaml_paths[i+1:]:
                results.append(RunResult(
                    yaml_path=remaining_path,
                    success=False,
                    error="Interrupted by user"
                ))
            
            break
        
        except Exception as e:
            log_event('MULTI_RUN_SINGLE_FAILED', run_index=i+1, error_message=str(e))
            
            results.append(RunResult(
                yaml_path=yaml_path,
                success=False,
                error=str(e)
            ))
            
            # Check if should continue on error
            if cli_args and hasattr(cli_args, 'continue_on_error') and cli_args.continue_on_error:
                log_event('MULTI_RUN_CONTINUING_AFTER_ERROR')
            else:
                log_event('MULTI_RUN_STOPPING_ON_ERROR')
                
                # Mark remaining as skipped
                for remaining_path in yaml_paths[i+1:]:
                    results.append(RunResult(
                        yaml_path=remaining_path,
                        success=False,
                        error="Skipped due to previous failure"
                    ))
                
                break
    
    # Final summary
    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count
    log_event('MULTI_RUN_SUMMARY', total_runs=len(results), successful=success_count, failed=fail_count)
    
    return results