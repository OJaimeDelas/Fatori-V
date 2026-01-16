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
from scripts.build.path_resolver import resolve_builddir, resolve_sync_file
from scripts.exec.sync_file_manager import create_sync_file, cleanup_sync_file
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
    
    This creates necessary files and ensures the execution environment
    is ready for the benchmark to run.
    
    Args:
        session: Session object
    
    Returns:
        Dictionary with environment paths
    """
    # Get sync file path
    sync_path = resolve_sync_file()
    
    # Clean up any existing sync file
    cleanup_sync_file(sync_path)
    
    # Create new sync file for this session
    if session.injection_enabled:
        create_sync_file(sync_path)
        log_event('EXECUTION_SYNC_FILE_CREATED', sync_path=str(sync_path))
    
    return {
        'sync_path': sync_path,
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
    
    # Prepare execution environment
    env = prepare_execution_environment(session)
    builddir = env['builddir']
    
    # Check build directory exists
    if not builddir.exists():
        error_msg = f"Build directory not found: {builddir}"
        log_event('EXECUTION_BUILDDIR_NOT_FOUND', builddir=str(builddir))
        return ExecutionResult(
            success=False,
            timed_out=False,
            exit_code=-1,
            error_message=error_msg
        )
    
    # Build make command for this benchmark
    # Use benchmark's timeout for GRAB_TIMEOUT
    make_command = build_fpga_run_command(
        config,
        benchmark_info.name,
        grab_timeout=session.timeout_s
    )
    
    log_event('EXECUTION_COMMAND_BUILT',
              command=make_command,
              builddir=str(builddir))
    
    # Dry-run mode: print command without executing
    if cfg.DRY_RUN_MODE:
        log_event('DRY_RUN_COMMAND',
                  command=make_command,
                  cwd=str(builddir))
        return ExecutionResult(
            success=True,
            timed_out=False,
            exit_code=0,
            error_message=None
        )
    
    # Start subprocess
    try:
        process = subprocess.Popen(
            make_command,
            shell=True,
            cwd=str(builddir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1  # Line buffered
        )
        
        log_event('EXECUTION_PROCESS_STARTED', pid=process.pid)
        
        # Monitor process with timeout and stream output simultaneously
        # We'll use a simple approach: monitor with timeout in a way that
        # allows us to stream output
        
        # Create callback for progress reporting
        last_report = [0]  # Use list to allow modification in nested function
        
        def progress_callback(elapsed, remaining):
            # Report progress every 30 seconds
            if elapsed - last_report[0] >= 30:
                log_event('EXECUTION_PROGRESS',
                          elapsed_s=elapsed,
                          remaining_s=remaining)
                last_report[0] = elapsed
        
        # Monitor with timeout
        completed, timed_out, exit_code = monitor_with_timeout(
            process,
            session.timeout_s,
            callback=progress_callback,
            poll_interval=1.0
        )
        
        # After process completes (or times out), capture any remaining output
        # Read stdout
        stdout_output = []
        if process.stdout:
            remaining = process.stdout.read()
            if remaining:
                lines = remaining.decode('utf-8', errors='replace').split('\n')
                stdout_output.extend(lines)
        
        # Read stderr
        stderr_output = []
        if process.stderr:
            remaining = process.stderr.read()
            if remaining:
                lines = remaining.decode('utf-8', errors='replace').split('\n')
                stderr_output.extend(lines)
        
        # Combine output
        all_output = stdout_output + stderr_output
        
        # Write output to console log file
        if session.console_output_path:
            with session.console_output_path.open('w', encoding='utf-8') as f:
                for line in all_output:
                    f.write(line + '\n')
        
        # Extract metrics from output
        metrics = extract_console_summary(session.console_output_path) if session.console_output_path else {}
        
        # Determine success
        success = completed and not timed_out and (exit_code == 0)
        
        # Create result
        result = ExecutionResult(
            success=success,
            timed_out=timed_out,
            exit_code=exit_code if exit_code is not None else -1,
            console_output=all_output,
            metrics=metrics
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
        
        return result
    
    except Exception as e:
        log_event('BENCHMARK_EXECUTION_EXCEPTION', error_message=str(e))
        return ExecutionResult(
            success=False,
            timed_out=False,
            exit_code=-1,
            error_message=str(e)
        )
    
    finally:
        # Cleanup sync file
        cleanup_sync_file(env['sync_path'])