# =============================================================================
# FATORI-V • Run Cleanup
# File: run_cleanup.py
# -----------------------------------------------------------------------------
# Cleanup operations after run completion or failure.
# =============================================================================

import shutil
from pathlib import Path
import fatori_settings as cfg
from scripts.orchestration.run_context import RunContext
from scripts.logging.logger import log_event


def cleanup_tmp_directory(preserve_on_failure: bool = True, run_succeeded: bool = True):
    """
    Clean up temporary directory.
    
    Args:
        preserve_on_failure: If True, preserve tmp/ on failure for debugging
        run_succeeded: Whether the run succeeded
    
    Returns:
        Boolean indicating if cleanup succeeded
    """
    tmp_dir = cfg.TMP_DIR
    
    if not tmp_dir.exists():
        log_event('DEBUG_TMP_DIR_NOT_EXISTS')
        return True
    
    # In dry-run mode, never cleanup tmp/ (preserve for inspection)
    if cfg.DRY_RUN_MODE:
        log_event('CLEANUP_SKIP_DRY_RUN', tmp_dir=str(tmp_dir))
        return True
    
    # Preserve on failure if requested
    if preserve_on_failure and not run_succeeded:
        log_event('CLEANUP_PRESERVING_TMP', tmp_dir=str(tmp_dir))
        return True
    
    try:
        # Remove tmp directory contents but keep the directory
        for item in tmp_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        
        log_event('CLEANUP_TMP_CLEANED')
        return True
    
    except Exception as e:
        log_event('CLEANUP_TMP_FAILED', error_message=str(e))
        return False


def log_final_statistics(context: RunContext):
    """
    Log final run statistics.
    
    Args:
        context: Run context
    """
    summary = context.get_summary()
    
    log_event('CLEANUP_STATS_START')
    log_event('CLEANUP_STATS_DURATION', duration=summary['elapsed_seconds'])
    log_event('CLEANUP_STATS_PHASES', 
              completed=len(summary['completed_phases']), 
              failed=len(summary['failed_phases']))
    
    if summary['failed_phases']:
        for phase, error in summary['failed_phases'].items():
            log_event('CLEANUP_STATS_FAILED_PHASE', phase_name=phase, error_message=error)
    
    log_event('CLEANUP_STATS_RESULTS_DIR', results_dir=summary['results_dir'])


def display_completion_message(context: RunContext, success: bool):
    """
    Display completion message to user.
    
    Args:
        context: Run context
        success: Whether run succeeded
    """
    if success:
        log_event('RUN_COMPLETED_SUCCESS', 
                  results_dir=str(context.results_dir), 
                  duration=context.elapsed_seconds())
    else:
        failed_phases = context.run_state.failed_phases
        failed_phase_names = ', '.join(failed_phases.keys()) if failed_phases else 'unknown'
        log_event('RUN_COMPLETED_FAILURE', 
                  results_dir=str(context.results_dir), 
                  duration=context.elapsed_seconds(),
                  failed_phases=failed_phase_names)


def cleanup_run(context: RunContext, success: bool, preserve_tmp: bool = True) -> bool:
    """
    Perform cleanup operations after run completion.
    
    This handles:
    1. Cleaning tmp/ directory (optional, based on success)
    2. Logging final statistics
    3. Displaying completion message
    
    Args:
        context: Run context
        success: Whether run succeeded
        preserve_tmp: Whether to preserve tmp/ on failure
    
    Returns:
        Boolean indicating if cleanup succeeded
    """
    log_event('CLEANUP_START')
    
    try:
        # Clean tmp directory
        cleanup_tmp_directory(
            preserve_on_failure=preserve_tmp,
            run_succeeded=success
        )
        
        # Log final statistics
        log_final_statistics(context)
        
        # Display completion message
        display_completion_message(context, success)
        
        return True
    
    except Exception as e:
        log_event('CLEANUP_FAILED', error_message=str(e))
        return False