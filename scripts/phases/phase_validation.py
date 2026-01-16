# =============================================================================
# FATORI-V • Validation Phase Executor
# File: phase_validation.py
# -----------------------------------------------------------------------------
# Executes configuration validation phase.
# =============================================================================

from scripts.phases.phase_executor import PhaseExecutor
from scripts.orchestration.run_context import RunContext
from scripts.orchestration.run_validation import validate_run
from scripts.logging.logger import log_event


def execute_validation_phase(context: RunContext) -> bool:
    """
    Execute validation phase.
    
    This validates the configuration and saves the verified config
    if validation passes.
    
    Args:
        context: Run context with configuration
    
    Returns:
        Boolean indicating if validation passed
    """
    log_event('VALIDATION_PHASE_EXECUTING')
    
    # Run validation
    is_valid, validation_result = validate_run(
        context.config,
        context.results_dir
    )
    
    # Log validation results
    errors = validation_result.get('errors', [])
    warnings = validation_result.get('warnings', [])
    
    if is_valid:
        log_event('VALIDATION_PHASE_PASSED')
    else:
        log_event('VALIDATION_PHASE_FAILED', error_count=len(errors))
    
    if warnings:
        log_event('VALIDATION_PHASE_WARNINGS', warning_count=len(warnings))
    
    return is_valid


class ValidationPhaseExecutor(PhaseExecutor):
    """
    Executor for validation phase.
    """
    
    def __init__(self):
        super().__init__("validation")
    
    def execute(self, context: RunContext) -> bool:
        """
        Execute validation phase.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        return execute_validation_phase(context)