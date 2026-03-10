# =============================================================================
# FATORI-V • Build Phase Executor
# File: phase_build.py
# -----------------------------------------------------------------------------
# Executes FPGA build phase.
# =============================================================================

from scripts.phases.phase_executor import PhaseExecutor
from scripts.orchestration.run_context import RunContext
from scripts.build.build_orchestrator import build_hardware
from scripts.build.build_settings import CLEAN_BEFORE_BUILD, RUN_IBEX_SETUP
from scripts.logging.logger import log_event


def execute_build_phase(context: RunContext) -> bool:
    """
    Execute build phase.
    
    This builds the FPGA bitstream using Vivado:
    1. Runs make clean setup (if configured)
    2. Runs make ibex-setup (if configured)
    3. Runs make fpga-only-bit to generate bitstream
    
    Args:
        context: Run context with configuration
    
    Returns:
        Boolean indicating if build succeeded
    """
    log_event('BUILD_PHASE_EXECUTING')
    
    try:
        # Determine skip flags based on settings
        skip_clean = not CLEAN_BEFORE_BUILD
        skip_ibex_setup = not RUN_IBEX_SETUP
        
        # log_event('BUILD_PHASE_CONFIG',
        #           clean_before_build=CLEAN_BEFORE_BUILD,
        #           run_ibex_setup=RUN_IBEX_SETUP)
        
        # Get enabled benchmarks from config
        from scripts.common.yaml_io.yaml_helpers import get_benchmarks, is_benchmark_enabled
        all_benchmarks = get_benchmarks(context.config)
        enabled_benchmarks = [name for name in all_benchmarks if is_benchmark_enabled(context.config, name)]
        
        # Run hardware build
        build_result = build_hardware(
            context.config,
            enabled_benchmarks
        )
        
        # Check build result
        if not build_result.success:
            log_event('BUILD_PHASE_FAILED',
                      step_completed=build_result.step_completed,
                      error_message=build_result.error_message or "Unknown error")
            
            # Log first few errors if analysis available
            if hasattr(build_result, 'error_analysis') and build_result.error_analysis:
                errors = build_result.error_analysis.get('errors', [])
                if errors:
                    log_event('BUILD_ERRORS_SUMMARY',
                              error_count=len(errors),
                              first_errors=errors[:3])
            
            return False
        
        log_event('BUILD_PHASE_SUCCESS')
        
        # Log build log location
        if build_result.log_file:
            log_event('BUILD_LOG_LOCATION', log_file=str(build_result.log_file))
        
        return True
    
    except Exception as e:
        log_event('BUILD_PHASE_EXCEPTION', error_message=str(e))
        return False


class BuildPhaseExecutor(PhaseExecutor):
    """
    Executor for build phase.
    """
    
    def __init__(self):
        super().__init__("build")
    
    def execute(self, context: RunContext) -> bool:
        """
        Execute build phase.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        return execute_build_phase(context)
    
    def post_execute(self, context: RunContext, success: bool):
        """
        Post-execution hook for build phase.
        
        Args:
            context: Run context
            success: Whether build succeeded
        """
        super().post_execute(context, success)
        
        if success:
            log_event('BUILD_BITSTREAM_READY')