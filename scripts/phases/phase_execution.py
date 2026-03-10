# =============================================================================
# FATORI-V • Execution Phase Executor
# File: phase_execution.py
# -----------------------------------------------------------------------------
# Executes benchmark execution phase with fault injection.
# =============================================================================

from typing import List
from scripts.phases.phase_executor import PhaseExecutor
from scripts.orchestration.run_context import RunContext
from scripts.exec.benchmark_manager import BenchmarkManager
from scripts.exec.fi_controller import FIController
from scripts.exec.session_manager import SessionManager
from scripts.exec.session_controller import run_session_loop
from scripts.logging.logger import log_event


def execute_execution_phase(context: RunContext) -> bool:
    """
    Execute execution phase.
    
    This runs all configured benchmarks, optionally with fault injection:
    1. Initialize results directory structure
    2. Copy YAML files to results directory
    3. Create benchmark manager to discover and order benchmarks
    4. Create FI controller if fault injection is enabled
    5. Create session manager to track execution sessions
    6. Run session loop to execute all benchmarks
    7. Collect session results
    
    Args:
        context: Run context with configuration
    
    Returns:
        Boolean indicating if execution succeeded
    """
    log_event('EXECUTION_PHASE_START')
    
    try:
        # Step 1: Initialize results directory structure
        from scripts.results.directory_manager import initialize_run_structure
        from scripts.results.yaml_copier import copy_original_yaml
        
        # Create run directory structure
        structure = initialize_run_structure(context.config, base_dir=context.results_dir.parent)
        context.results_dir = structure['run_dir']
        
        # Copy original YAML to results directory
        # Note: verified_yaml.yaml was already saved during validation phase
        if context.yaml_path:
            copy_original_yaml(context.yaml_path, context.results_dir)
        
        # Step 2: Create benchmark manager
        log_event('BENCHMARKS_DISCOVERING')
        benchmark_manager = BenchmarkManager(context.config)
        
        # Discover all benchmarks
        benchmarks = benchmark_manager.discover_all()
        enabled_benchmarks = benchmark_manager.get_enabled()
        
        if not enabled_benchmarks:
            log_event('BENCHMARKS_NONE_ENABLED')
            return False
        
        log_event('BENCHMARKS_DISCOVERED', count=len(enabled_benchmarks))
        
        # Validate benchmarks
        errors, warnings = benchmark_manager.validate_all()
        if errors:
            log_event('BENCHMARKS_VALIDATION_FAILED', error_count=len(errors), errors=errors)
            return False
        
        if warnings:
            log_event('BENCHMARKS_VALIDATION_WARNINGS', warning_count=len(warnings))
        
        # Step 2: Create FI controller if needed
        fi_controller = None
        if benchmark_manager.has_fi_enabled():
            log_event('FI_ENABLED')
            fi_controller = FIController(context.config)
            
            # Validate FI configuration
            fi_errors, fi_warnings = fi_controller.validate()
            if fi_errors:
                log_event('FI_VALIDATION_FAILED', error_count=len(fi_errors), errors=fi_errors)
                return False
            
            if fi_warnings:
                log_event('FI_VALIDATION_WARNINGS', warning_count=len(fi_warnings))
        else:
            log_event('FI_DISABLED')
        
        # Step 3: Run session loop
        log_event('BENCHMARKS_EXECUTION_START')
        
        # Run all sessions with run-specific results directory
        session_results = run_session_loop(
            context.config,
            benchmark_manager,
            fi_controller,
            results_dir=context.results_dir
        )
        
        # Step 4: Analyze results
        if not session_results:
            log_event('EXECUTION_NO_RESULTS')
            return False
        
        # Count successes and failures
        total_sessions = len(session_results)
        successful_sessions = sum(1 for r in session_results if r.execution_success)
        failed_sessions = total_sessions - successful_sessions
        
        # Count FI sessions
        fi_sessions = sum(1 for r in session_results if r.fi_launched)
        
        log_event('EXECUTION_SUMMARY',
                  total_sessions=total_sessions,
                  successful_sessions=successful_sessions,
                  failed_sessions=failed_sessions,
                  fi_sessions=fi_sessions)
        
        # Consider execution successful if at least one session succeeded
        if successful_sessions == 0:
            log_event('EXECUTION_ALL_FAILED')
            return False
        
        log_event('EXECUTION_PHASE_COMPLETE')
        return True
    
    except Exception as e:
        log_event('EXECUTION_PHASE_EXCEPTION', error_message=str(e))
        import traceback
        log_event('EXECUTION_TRACEBACK', traceback=traceback.format_exc())
        return False


class ExecutionPhaseExecutor(PhaseExecutor):
    """
    Executor for execution phase.
    """
    
    def __init__(self):
        super().__init__("execution")
    
    def execute(self, context: RunContext) -> bool:
        """
        Execute execution phase.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        return execute_execution_phase(context)
    
    def post_execute(self, context: RunContext, success: bool):
        """
        Post-execution hook for execution phase.
        
        Args:
            context: Run context
            success: Whether execution succeeded
        """
        super().post_execute(context, success)
        
        if success:
            log_event('EXECUTION_DATA_READY')