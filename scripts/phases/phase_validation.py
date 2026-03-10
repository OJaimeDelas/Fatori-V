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
    
    This validates the configuration, applies corrections, and saves
    the verified config immediately after validation passes.
    
    Args:
        context: Run context with configuration
    
    Returns:
        Boolean indicating if validation passed
    """
    log_event('VALIDATION_PHASE_EXECUTING')
    
    # Delete builddir to ensure clean state for this run
    # Each run starts with no iob_soc_V1.0/, final run leaves its builddir
    import shutil
    import fatori_settings as cfg
    if cfg.BUILDDIR.exists():
        log_event('DEBUG', debug_message=f"Deleting builddir: {cfg.BUILDDIR}")
        shutil.rmtree(cfg.BUILDDIR)
    
    # Run validation (corrections are applied in-place to context.config)
    is_valid, validation_result = validate_run(
        context.config,
        context.results_dir
    )
    
    # Log validation results
    errors = validation_result.get('errors', [])
    warnings = validation_result.get('warnings', [])
    corrections = validation_result.get('corrections', [])
    
    if is_valid:
        log_event('VALIDATION_PHASE_PASSED')
        
        # Save verified YAML immediately after validation
        # This ensures all subsequent phases use the corrected configuration
        if corrections:
            log_event('VALIDATION_SAVING_VERIFIED_CONFIG', correction_count=len(corrections))
        
        from scripts.results.yaml_copier import save_verified_yaml
        save_verified_yaml(context.config, context.results_dir)
        
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