# =============================================================================
# FATORI-V • Resume Manager
# File: resume_manager.py
# -----------------------------------------------------------------------------
# Manages resuming runs from saved state.
# =============================================================================

from pathlib import Path
from scripts.recovery.state_persistence import load_run_state, is_resumable, get_resume_point
from scripts.orchestration.run_controller import RunController
from scripts.orchestration.run_phases import PHASE_ORDER
from scripts.orchestration.run_cleanup import cleanup_run
from scripts.logging.logger import log_event


def validate_resume_preconditions(context) -> bool:
    """
    Validate preconditions for resuming a run.
    
    Args:
        context: Loaded run context
    
    Returns:
        Boolean indicating if resume is safe
    """
    # Check results directory exists
    if not context.results_dir.exists():
        log_event('RESUME_PRECONDITION_FAILED_DIR', results_dir=str(context.results_dir))
        return False
    
    # Check YAML file exists if specified
    if context.yaml_path and not context.yaml_path.exists():
        log_event('RESUME_YAML_NOT_FOUND', yaml_path=str(context.yaml_path))
        # Not critical, we have config in state
    
    return True


def apply_resume_overrides(context, cli_args):
    """
    Apply CLI overrides to resumed context.
    
    Args:
        context: Run context
        cli_args: CLI arguments namespace
    
    Returns:
        Modified context
    """
    if not cli_args:
        return context
    
    from scripts.cli.override_applicator import apply_cli_overrides
    
    # Apply CLI overrides to config
    context.config = apply_cli_overrides(context.config, cli_args)
    
    log_event('RESUME_OVERRIDES_APPLIED')
    
    return context


def resume_run(state_path: Path, cli_args=None) -> bool:
    """
    Resume a run from saved state.
    
    Args:
        state_path: Path to saved state file
        cli_args: Optional CLI arguments for overrides
    
    Returns:
        Boolean indicating if resume succeeded
    """
    log_event('RESUME_RUN_START', state_file=str(state_path))
    
    # Check if resumable
    if not is_resumable(state_path):
        log_event('RESUME_NOT_RESUMABLE')
        return False
    
    # Load state
    context = load_run_state(state_path)
    
    if not context:
        log_event('RESUME_STATE_LOAD_FAILED')
        return False
    
    # Validate preconditions
    if not validate_resume_preconditions(context):
        log_event('RESUME_PRECONDITIONS_NOT_MET')
        return False
    
    # Apply CLI overrides if provided
    if cli_args:
        context = apply_resume_overrides(context, cli_args)
    
    # Determine resume point
    resume_phase = get_resume_point(state_path)
    
    if not resume_phase:
        log_event('RESUME_POINT_UNDETERMINED')
        return False
    
    log_event('RESUME_PHASE_INFO',
              resume_phase=resume_phase,
              completed_phases=context.run_state.completed_phases)
    
    # Get remaining phases
    resume_index = PHASE_ORDER.index(resume_phase)
    remaining_phases = PHASE_ORDER[resume_index:]
    
    log_event('RESUME_PHASES_REMAINING', phase_count=len(remaining_phases))
    
    # Create controller
    try:
        # Create controller with loaded context
        controller = RunController(context.yaml_path if context.yaml_path else Path("unknown.yaml"))
        controller.context = context
        
        # Execute remaining phases
        for phase_name in remaining_phases:
            success = controller.run_phase(phase_name, context)
            
            if not success:
                log_event('RESUME_PHASE_FAILED', phase_name=phase_name)
                return False
        
        # Mark run as complete
        context.mark_complete()
        
        # Cleanup
        cleanup_run(context, True, preserve_tmp=True)
        
        log_event('RESUME_RUN_COMPLETE')
        
        return True
    
    except Exception as e:
        log_event('RESUME_RUN_ERROR', error_message=str(e))
        return False