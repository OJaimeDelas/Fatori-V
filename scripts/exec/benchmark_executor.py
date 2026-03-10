# =============================================================================
# FATORI-V • Execution • Benchmark Executor
# File: benchmark_executor.py
# -----------------------------------------------------------------------------
# Executes individual benchmarks with subprocess management and output capture.
# =============================================================================

import subprocess
from dataclasses import dataclass
from pathlib import Path
import fatori_settings as cfg
from scripts.build.make_commands import build_fpga_run_command
from scripts.build.path_resolver import resolve_builddir
from scripts.exec.timeout_handler import monitor_with_timeout
from scripts.exec.console_manager import stream_output, extract_console_summary
from scripts.logging.logger import log_event


@dataclass
class ExecutionResult:
    """
    Container for benchmark execution results.
    
    This holds all information about a benchmark execution attempt.
    """
    success: bool                    # Whether execution completed successfully
    timed_out: bool                  # Whether execution hit timeout
    exit_code: int                   # Process exit code
    error_message: str = None        # Error message if failed
    console_output: list = None      # Captured console output lines
    metrics: dict = None             # Extracted metrics from output
    
    def __str__(self):
        if self.success:
            return f"ExecutionResult(success, exit={self.exit_code})"
        elif self.timed_out:
            return f"ExecutionResult(timeout)"
        else:
            return f"ExecutionResult(failed, exit={self.exit_code}, error={self.error_message})"


def prepare_execution_environment(session):
    """
    Prepare environment for benchmark execution.
    
    Note: Sync file is NOT created by FATORI-V - it's created by the
    firmware inside the architecture. FATORI-V only tells FI where to look.
    
    Args:
        session: Session object
    
    Returns:
        Dictionary with environment paths
    """
    return {
        'builddir': resolve_builddir(),
    }


def execute_benchmark(config, benchmark_info, session):
    """
    Execute a benchmark with full process management.
    
    This is the main execution function that:
    1. Prepares the execution environment
    2. Builds the make command
    3. Launches the benchmark subprocess
    4. Monitors execution with timeout
    5. Captures console output
    6. Returns execution results
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_info: BenchmarkInfo object for the benchmark
        session: Session object tracking this execution
    
    Returns:
        ExecutionResult object
    """
    log_event('BENCHMARK_EXECUTION_START',
              benchmark_name=benchmark_info.name,
              session_id=session.session_id,
              timeout_s=session.timeout_s,
              fi_enabled=session.injection_enabled)
    
    # Build make command for this benchmark
    # Use benchmark's timeout for GRAB_TIMEOUT
    make_command = build_fpga_run_command(
        config,
        benchmark_info.name,
        grab_timeout=session.timeout_s
    )
    
    log_event('EXECUTION_COMMAND_BUILT',
              command=make_command,
              cwd=str(cfg.ARCHITECTURE_DIR))
    
    # Always display command (dry-run uses same event)
    log_event('DRY_RUN_COMMAND',
              command=make_command,
              cwd=str(cfg.ARCHITECTURE_DIR))
    # In dry-run mode: skip execution, simulate success
    if cfg.DRY_RUN_MODE:
        result = ExecutionResult(
            success=True,
            timed_out=False,
            exit_code=0,
            error_message=None
        )
    else:
        # Normal mode: execute the command
        benchmark_log_path = session.session_dir / f"fatori_{benchmark_info.name}_log.txt"
        
        try:
            # Open log file for writing
            with open(benchmark_log_path, 'w') as benchmark_log_file:
                # Start subprocess with output redirected to file
                process = subprocess.Popen(
                    make_command,
                    shell=True,
                    cwd=str(cfg.ARCHITECTURE_DIR),
                    stdout=benchmark_log_file,
                    stderr=subprocess.STDOUT
                )
                
                log_event('EXECUTION_PROCESS_STARTED', pid=process.pid)
                
                # Monitor with timeout
                completed, timed_out, exit_code = monitor_with_timeout(
                    process,
                    session.timeout_s,
                    callback=None,
                    poll_interval=1.0
                )
            
            # Determine success based on exit code
            exit_success = completed and not timed_out and (exit_code == 0)
            
            # Check if metrics.txt was produced (alternative success indicator)
            metrics_file = session.session_dir / 'metrics.txt'
            metrics_exist = metrics_file.exists() and metrics_file.stat().st_size > 0
            
            # Consider successful if either: clean exit OR metrics produced
            success = exit_success or metrics_exist
            
            # Create result
            result = ExecutionResult(
                success=success,
                timed_out=timed_out,
                exit_code=exit_code if exit_code is not None else -1,
                error_message=None
            )
            
            # Set error message if failed
            if not success:
                if timed_out:
                    result.error_message = f"Execution timed out after {session.timeout_s}s"
                elif exit_code != 0:
                    result.error_message = f"Process exited with code {exit_code}"
                else:
                    result.error_message = "Unknown execution failure"
            
            log_event('BENCHMARK_EXECUTION_COMPLETE', result=str(result))
        
        except Exception as e:
            log_event('BENCHMARK_EXECUTION_EXCEPTION', error_message=str(e))
            result = ExecutionResult(
                success=False,
                timed_out=False,
                exit_code=-1,
                error_message=str(e)
            )
    # Always retrieve metrics.txt after execution (both dry-run and normal modes)
    # Even if execution failed, try to retrieve metrics in case partial execution occurred
    from scripts.exec.metrics_retriever import retrieve_metrics_after_execution
    metrics_retrieved = retrieve_metrics_after_execution(session.session_dir, benchmark_info.name)
    
    # Re-evaluate success after metrics retrieval
    # If metrics exist, consider execution successful even if exit code was non-zero
    if not result.success and metrics_retrieved:
        metrics_file = session.session_dir / 'metrics.txt'
        if metrics_file.exists() and metrics_file.stat().st_size > 0:
            log_event('DEBUG', debug_message=f"Benchmark had non-zero exit but produced metrics - considering successful")
            result.success = True
            result.error_message = None
    
    # Collect FI injection_log.txt if FI was enabled (both modes)
    if session.injection_enabled:
        from scripts.exec.fi_log_collector import collect_fi_log_after_session
        fi_dir = session.session_dir / 'fi'
        collect_fi_log_after_session(fi_dir, benchmark_info.name)
    
    return result