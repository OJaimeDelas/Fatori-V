# =============================================================================
# FATORI-V • Execution • FI Launcher
# File: fi_launcher.py
# -----------------------------------------------------------------------------
# Launches fault injection console and monitors execution.
# =============================================================================

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
import fatori_settings as cfg
from scripts.exec.fi_command_builder import build_fi_command
from scripts.exec.fi_collector import collect_fi_output
from scripts.exec.timeout_handler import monitor_with_timeout
from scripts.logging.logger import log_event


@dataclass
class FIResult:
    """
    Container for fault injection execution results.
    """
    success: bool                    # Whether FI completed successfully
    timed_out: bool                  # Whether FI hit timeout
    exit_code: int                   # Process exit code
    error_message: str = None        # Error message if failed
    output_data: dict = None         # Collected output data
    injection_count: int = 0         # Number of injections performed
    
    def __str__(self):
        if self.success:
            return f"FIResult(success, {self.injection_count} injections)"
        elif self.timed_out:
            return f"FIResult(timeout)"
        else:
            return f"FIResult(failed, {self.error_message})"


def launch_fi(config, benchmark_name, session, timeout_s=None):
    """
    Launch fault injection console for a benchmark execution.
    
    This is the main FI launch function that:
    1. Builds FI command from configuration
    2. Starts FI console subprocess
    3. Monitors execution with timeout
    4. Collects FI output
    5. Returns results
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of benchmark being executed
        session: Session object for this execution
        timeout_s: Optional timeout override (uses session timeout by default)
    
    Returns:
        FIResult object
    """
    log_event('FI_LAUNCH_START', benchmark_name=benchmark_name)
    
    # Use session timeout if not specified
    if timeout_s is None:
        timeout_s = session.timeout_s
    
    # Build FI command (no output_log_path param anymore)
    try:
        fi_command = build_fi_command(config, benchmark_name)
    except Exception as e:
        log_event('FI_COMMAND_BUILD_FAILED', error_message=str(e))
        return FIResult(
            success=False,
            timed_out=False,
            exit_code=-1,
            error_message=f"Command build failed: {e}"
        )
    
    # Prepare FI terminal output log file
    # FI terminal output goes to: results/<run_id>/sessions/<bench_id>/fi/fi_terminal_log.txt
    fi_dir = session.session_dir / "fi"
    fi_dir.mkdir(parents=True, exist_ok=True)
    fi_terminal_log_path = fi_dir / "fi_terminal_log.txt"
    
    # Log and print FI command
    log_event('FI_COMMAND_BUILT',
              command=fi_command,
              output_log=str(fi_terminal_log_path),
              timeout_s=timeout_s)
    
    # Start FI console subprocess with output redirected to file
    try:
        fi_terminal_log_file = open(fi_terminal_log_path, 'w')
        
        # Execute from project root
        process = subprocess.Popen(
            fi_command,
            shell=True,
            cwd=str(cfg.ROOT_DIR),
            stdout=fi_terminal_log_file,
            stderr=subprocess.STDOUT  # Merge stderr into stdout
        )
        
        log_event('FI_PROCESS_STARTED', pid=process.pid)
        
        # Monitor process with timeout
        last_report = [0]
        
        def progress_callback(elapsed, remaining):
            # Report progress every 30 seconds
            if elapsed - last_report[0] >= 30:
                log_event('FI_PROGRESS', elapsed_s=elapsed, remaining_s=remaining)
                last_report[0] = elapsed
        
        completed, timed_out, exit_code = monitor_with_timeout(
            process,
            timeout_s,
            callback=progress_callback,
            poll_interval=1.0
        )
        
        # Read any remaining output
        stdout_data = b''
        stderr_data = b''
        
        if process.stdout:
            stdout_data = process.stdout.read()
        
        if process.stderr:
            stderr_data = process.stderr.read()
        
        # Decode output
        stdout_str = stdout_data.decode('utf-8', errors='replace')
        stderr_str = stderr_data.decode('utf-8', errors='replace')
        
        # Log output
        if stdout_str:
            log_event('FI_STDOUT', stdout_preview=stdout_str[:500])
        if stderr_str:
            log_event('FI_STDERR', stderr_preview=stderr_str[:500])
        
        # Determine success
        success = completed and not timed_out and (exit_code == 0)
        
        # Collect FI output
        output_data = None
        injection_count = 0
        
        if success or (completed and not timed_out):
            # Try to collect output even if exit code wasn't 0
            # (FI console might have written partial results)
            log_event('FI_OUTPUT_COLLECTING')
            output_data = collect_fi_output(session.session_dir)
            
            if output_data and output_data.get('parsed'):
                injection_count = output_data['parsed'].get('injection_count', 0)
                log_event('FI_OUTPUT_COLLECTED', injection_count=injection_count)
        
        # Create result
        result = FIResult(
            success=success,
            timed_out=timed_out,
            exit_code=exit_code if exit_code is not None else -1,
            output_data=output_data,
            injection_count=injection_count
        )
        
        # Set error message if failed
        if not success:
            if timed_out:
                result.error_message = f"FI timed out after {timeout_s}s"
            elif exit_code != 0:
                result.error_message = f"FI console exited with code {exit_code}"
                if stderr_str:
                    result.error_message += f": {stderr_str[:200]}"
            else:
                result.error_message = "Unknown FI failure"
        
        log_event('FI_LAUNCH_COMPLETE', result=str(result))
        
        return result
    
    except Exception as e:
        log_event('FI_LAUNCH_EXCEPTION', error_message=str(e))
        return FIResult(
            success=False,
            timed_out=False,
            exit_code=-1,
            error_message=str(e)
        )


@dataclass
class FIAsyncHandle:
    """
    Handle for asynchronously launched FI process.
    
    This allows the caller to wait for completion and collect results later.
    """
    process: subprocess.Popen  # The running subprocess
    benchmark_name: str        # Associated benchmark
    session: object            # Associated session
    timeout_s: int             # Timeout for this FI execution
    output_log_path: Path      # Where FI output is being logged
    start_time: float          # When FI was started (time.time())


def launch_fi_async(config, benchmark_name, session, timeout_s=None):
    """
    Launch fault injection console asynchronously as background process.
    
    This starts the FI console subprocess but does not wait for it to complete.
    The subprocess will wait for the sync file before beginning injections.
    
    Caller should:
    1. Call this to start FI subprocess
    2. Start the benchmark (which creates/deletes sync file)
    3. Call wait_for_fi_completion() to collect results
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of benchmark being executed
        session: Session object for this execution
        timeout_s: Optional timeout override (uses session timeout by default)
    
    Returns:
        FIAsyncHandle object, or None if launch fails
    """
    log_event('FI_LAUNCH_ASYNC_START', benchmark_name=benchmark_name)
    
    # Use session timeout if not specified
    if timeout_s is None:
        timeout_s = session.timeout_s
    
    # Build FI command (no output_log_path param anymore)
    try:
        fi_command = build_fi_command(config, benchmark_name)
    except Exception as e:
        log_event('FI_COMMAND_BUILD_FAILED', error_message=str(e))
        return None
    
    # Prepare FI terminal output log file
    # FI terminal output goes to: results/<run_id>/sessions/<bench_id>/fi/fi_terminal_log.txt
    fi_dir = session.session_dir / "fi"
    fi_dir.mkdir(parents=True, exist_ok=True)
    fi_terminal_log_path = fi_dir / "fi_terminal_log.txt"
    
    # Log and print FI command
    log_event('FI_COMMAND_BUILT',
              command=fi_command,
              output_log=str(fi_terminal_log_path),
              timeout_s=timeout_s)
    
    # Start FI console subprocess with output redirected to file
    try:
        fi_terminal_log_file = open(fi_terminal_log_path, 'w')
        
        # Execute from project root
        process = subprocess.Popen(
            fi_command,
            shell=True,
            cwd=str(cfg.ROOT_DIR),
            stdout=fi_terminal_log_file,
            stderr=subprocess.STDOUT  # Merge stderr into stdout
        )
        
        log_event('FI_PROCESS_STARTED_ASYNC', pid=process.pid)
        
        # Create handle
        handle = FIAsyncHandle(
            process=process,
            benchmark_name=benchmark_name,
            session=session,
            timeout_s=timeout_s,
            output_log_path=fi_terminal_log_path,
            start_time=time.time()
        )
        
        return handle
    
    except Exception as e:
        log_event('FI_LAUNCH_ASYNC_EXCEPTION', error_message=str(e))
        return None


def wait_for_fi_completion(fi_handle):
    """
    Wait for asynchronously launched FI to complete and collect results.
    
    This blocks indefinitely until the FI subprocess finishes.
    No timeout - FI must complete naturally.
    
    Args:
        fi_handle: FIAsyncHandle from launch_fi_async()
    
    Returns:
        FIResult object
    """
    if fi_handle is None:
        return FIResult(
            success=False,
            timed_out=False,
            exit_code=-1,
            error_message="No FI handle provided"
        )
    
    log_event('FI_WAIT_FOR_COMPLETION_START', pid=fi_handle.process.pid)
    log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] Blocking on process.wait() for PID {fi_handle.process.pid}")
    
    try:
        process = fi_handle.process
        
        # Wait indefinitely for FI subprocess to complete
        # No timeout - just block until process exits
        log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] Calling process.wait() with no timeout...")
        exit_code = process.wait()
        log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] process.wait() returned with exit_code={exit_code}")
        
        # Determine success based on exit code
        success = (exit_code == 0)
        
        # Collect FI output
        output_data = None
        injection_count = 0
        
        log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] Collecting FI output...")
        try:
            output_data = collect_fi_output(fi_handle.session.session_dir)
            
            if output_data and output_data.get('parsed'):
                injection_count = output_data['parsed'].get('injection_count', 0)
                log_event('FI_OUTPUT_COLLECTED', injection_count=injection_count)
        except Exception as e:
            log_event('WARNING', warning_message=f"Failed to collect FI output: {e}")
        
        # Create result
        result = FIResult(
            success=success,
            timed_out=False,
            exit_code=exit_code,
            injection_count=injection_count,
            error_message=None if success else f"FI exited with code {exit_code}"
        )
        
        log_event('FI_WAIT_FOR_COMPLETION_COMPLETE', 
                  success=success,
                  exit_code=exit_code,
                  injection_count=injection_count)
        
        return result
    
    except Exception as e:
        log_event('FI_WAIT_FOR_COMPLETION_EXCEPTION', error_message=str(e))
        import traceback
        log_event('FI_WAIT_TRACEBACK', traceback=traceback.format_exc())
        
        return FIResult(
            success=False,
            timed_out=False,
            exit_code=-1,
            injection_count=0,
            error_message=f"Exception while waiting: {e}"
        )