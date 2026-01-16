# =============================================================================
# FATORI-V • Generation Phase Executor
# File: phase_generation.py
# -----------------------------------------------------------------------------
# Executes hardware file generation phase.
# =============================================================================

from scripts.phases.phase_executor import PhaseExecutor
from scripts.orchestration.run_context import RunContext
from scripts.orchestration.generate_all import generate_all_files
from scripts.logging.logger import log_event


def execute_generation_phase(context: RunContext) -> bool:
    """
    Execute generation phase.
    
    This generates all hardware files including:
    - SystemVerilog headers (.svh)
    - Pblock configuration files
    - TCL scripts for Vivado
    - System integration files
    
    Args:
        context: Run context with configuration
    
    Returns:
        Boolean indicating if generation succeeded
    """
    log_event('GENERATION_PHASE_EXECUTING')
    
    try:
        # Generate all files
        generation_result = generate_all_files(context.config)
        
        # Check if generation was valid
        if not generation_result.get('valid', False):
            log_event('GENERATION_PHASE_VALIDATION_FAILED')
            return False
        
        # Log summary of generated files
        svh_headers = generation_result.get('svh_headers', {})
        pblock_files = generation_result.get('pblock_files', {})
        tcl_scripts = generation_result.get('tcl_scripts', {})
        system_files = generation_result.get('system_files', {})
        
        total_files = (
            len([v for v in svh_headers.values() if v]) +
            len([v for v in pblock_files.values() if v]) +
            len([v for v in tcl_scripts.values() if v]) +
            len([v for v in system_files.values() if v])
        )
        
        log_event('GENERATION_PHASE_COMPLETE',
                  total_files=total_files,
                  svh_count=len(svh_headers),
                  pblock_count=len([v for v in pblock_files.values() if v]),
                  tcl_count=len(tcl_scripts),
                  system_count=len(system_files))
        
        return True
    
    except Exception as e:
        log_event('GENERATION_PHASE_ERROR', error_message=str(e))
        return False


class GenerationPhaseExecutor(PhaseExecutor):
    """
    Executor for generation phase.
    """
    
    def __init__(self):
        super().__init__("generation")
    
    def execute(self, context: RunContext) -> bool:
        """
        Execute generation phase.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        return execute_generation_phase(context)