# =============================================================================
# FATORI-V • Run Reporter
# File: run_reporter.py
# -----------------------------------------------------------------------------
# Reporting and progress display for run execution.
# =============================================================================

from scripts.orchestration.run_context import RunContext
from scripts.orchestration.run_phases import get_phase_description
from scripts.logging.logger import log_event


def print_run_summary(context: RunContext):
    """
    Print summary of run execution.
    
    Args:
        context: Run context containing run information
    """
    log_event('REPORT_RUN_SUMMARY_START')
    log_event('REPORT_RUN_NAME', run_name=context.run_name if hasattr(context, 'run_name') else 'unknown')
    log_event('REPORT_CONFIG_PATH', yaml_path=str(context.yaml_path))
    log_event('REPORT_RESULTS_DIR', results_dir=str(context.results_dir))
    
    # Duration if available
    if context.end_time:
        duration = context.elapsed_seconds()
        log_event('REPORT_DURATION', duration=duration)
    
    # Phase summary
    log_event('REPORT_PHASES_START')
    for phase_name, phase_info in context.run_state.phase_status.items():
        if phase_info.get('completed'):
            phase_duration = phase_info.get('duration', 0.0)
            log_event('REPORT_PHASE_SUCCESS', phase_name=phase_name, duration=phase_duration)
        elif phase_info.get('failed'):
            log_event('REPORT_PHASE_FAILED', phase_name=phase_name)
        else:
            log_event('REPORT_PHASE_SKIPPED', phase_name=phase_name)


def print_phase_progress(phase_name: str, completed: int = None, total: int = None):
    """
    Print progress for a running phase.
    
    Args:
        phase_name: Name of current phase
        completed: Number of completed steps (optional)
        total: Total number of steps (optional)
    """
    description = get_phase_description(phase_name)
    log_event('PHASE_START', phase_name=phase_name)
    
    if description:
        log_event('REPORT_PHASE_DESCRIPTION', phase_name=phase_name, description=description)
    
    if completed is not None and total is not None:
        log_event('REPORT_PHASE_PROGRESS', completed=completed, total=total)


def print_error_details(error: Exception, context: str = None):
    """
    Print detailed error information.
    
    Args:
        error: Exception that occurred
        context: Optional context string describing where error occurred
    """
    error_msg = str(error)
    if context:
        log_event('ERROR_DETAILED', context=context, error_message=error_msg)
    else:
        log_event('ERROR', error_message=error_msg)


def print_validation_summary(results: dict):
    """
    Print validation results summary.
    
    Args:
        results: Validation results dictionary
    """
    error_count = len(results.get('errors', []))
    warning_count = len(results.get('warnings', []))
    
    log_event('VALIDATION_END', error_count=error_count, warning_count=warning_count)
    
    if results.get('errors'):
        for error in results['errors']:
            log_event('VALIDATION_ERROR', error_message=error)
    
    if results.get('warnings'):
        for warning in results['warnings']:
            log_event('VALIDATION_WARNING', warning_message=warning)
    
    if results.get('corrections'):
        for correction in results['corrections']:
            log_event('VALIDATION_AUTO_CORRECTION', correction_message=correction)


def print_build_progress(step: str, progress: float = None):
    """
    Print build progress information.
    
    Args:
        step: Current build step description
        progress: Optional progress percentage (0-100)
    """
    if progress is not None:
        log_event('BUILD_PROGRESS', step=step, progress=progress)
    else:
        log_event('BUILD_STEP', step=step)


def print_benchmark_output(benchmark_name: str, output_line: str):
    """
    Print benchmark execution output.
    
    Args:
        benchmark_name: Name of benchmark
        output_line: Output line from benchmark
    """
    log_event('BENCHMARK_OUTPUT', benchmark_name=benchmark_name, line=output_line)