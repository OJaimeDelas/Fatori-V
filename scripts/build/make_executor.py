# =============================================================================
# FATORI-V • Build System • Make Executor
# File: make_executor.py
# -----------------------------------------------------------------------------
# Executes make commands with subprocess management and error detection.
# =============================================================================

import subprocess
import time
from pathlib import Path
import fatori_settings as cfg
from scripts.build.build_settings import BUILD_TIMEOUT_DEFAULT
from scripts.logging.logger import log_event


def stream_output(process, log_file_handle):
    """
    Stream process output in real-time to both console and log file.
    
    Args:
        process: subprocess.Popen object
        log_file_handle: Open file handle for logging
    
    Returns:
        Tuple of (stdout_lines, stderr_lines) as lists
    """
    stdout_lines = []
    stderr_lines = []
    
    # Read stdout in real-time
    if process.stdout:
        for line in iter(process.stdout.readline, b''):
            if not line:
                break
            
            decoded_line = line.decode('utf-8', errors='replace').rstrip()
            stdout_lines.append(decoded_line)
            
            # Write to log file
            if log_file_handle:
                log_file_handle.write(decoded_line + '\n')
                log_file_handle.flush()
            
            # Log to console (at DEBUG level to avoid spam)
            log_event('MAKE_OUTPUT_LINE', line=decoded_line)
    
    # Read stderr
    if process.stderr:
        for line in iter(process.stderr.readline, b''):
            if not line:
                break
            
            decoded_line = line.decode('utf-8', errors='replace').rstrip()
            stderr_lines.append(decoded_line)
            
            # Write to log file
            if log_file_handle:
                log_file_handle.write("[STDERR] " + decoded_line + '\n')
                log_file_handle.flush()
            
            # Log stderr at WARNING level
            log_event('MAKE_STDERR_LINE', line=decoded_line)
    
    return stdout_lines, stderr_lines


def detect_errors_in_output(stdout_lines, stderr_lines):
    """
    Detect errors in make command output.
    
    Looks for common error patterns including:
    - Vivado ERROR messages
    - Make errors
    - Compilation failures
    
    Args:
        stdout_lines: List of stdout lines
        stderr_lines: List of stderr lines
    
    Returns:
        List of detected error messages
    """
    errors = []
    
    # Combine all output lines
    all_lines = stdout_lines + stderr_lines
    
    # Error patterns to detect
    error_patterns = [
        'ERROR:',
        'CRITICAL WARNING:',
        'make: *** ',
        'error:',
        'Error:',
        'Synthesis failed',
        'Implementation failed',
        'Bitstream generation failed'
    ]
    
    for line in all_lines:
        for pattern in error_patterns:
            if pattern in line:
                errors.append(line.strip())
                break
    
    return errors


def execute_make_command(command, cwd, log_file=None, timeout=None):
    """
    Execute a make command via subprocess with proper error handling.
    
    In dry-run mode, prints command without executing.
    
    This function:
    - Runs the command in the specified directory
    - Captures stdout/stderr to log file
    - Streams output in real-time
    - Detects errors from output
    - Handles timeouts
    
    Args:
        command: Make command string to execute
        cwd: Working directory for command execution
        log_file: Path to log file for output capture
        timeout: Timeout in seconds (None for no timeout)
    
    Returns:
        Tuple of (success: bool, error_message: str, exit_code: int)
    """
    cwd = Path(cwd)
    
    # Dry-run mode: print command without executing
    if cfg.DRY_RUN_MODE:
        log_event('DRY_RUN_COMMAND', 
                  command=command,
                  cwd=str(cwd))
        return True, None, 0
    
    if not cwd.exists():
        error_msg = f"Working directory does not exist: {cwd}"
        log_event('MAKE_CWD_NOT_FOUND', cwd=str(cwd))
        return False, error_msg, -1
    
    # Use default timeout if not specified
    if timeout is None:
        timeout = BUILD_TIMEOUT_DEFAULT
    
    # Prepare log file
    log_file_handle = None
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file_handle = log_path.open('a', encoding='utf-8')
        log_file_handle.write(f"\n{'='*80}\n")
        log_file_handle.write(f"Command: {command}\n")
        log_file_handle.write(f"Working directory: {cwd}\n")
        log_file_handle.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file_handle.write(f"{'='*80}\n\n")
        log_file_handle.flush()
    
    log_event('MAKE_COMMAND_START',
              command=command,
              cwd=str(cwd))
    
    start_time = time.time()
    
    try:
        # Start process
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1  # Line buffered
        )
        
        # Stream output
        stdout_lines, stderr_lines = stream_output(process, log_file_handle)
        
        # Wait for completion with timeout
        try:
            exit_code = process.wait(timeout=timeout if timeout > 0 else None)
        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = f"Command timed out after {timeout} seconds"
            log_event('MAKE_COMMAND_TIMEOUT', timeout_s=timeout)
            
            if log_file_handle:
                log_file_handle.write(f"\n{error_msg}\n")
                log_file_handle.close()
            
            return False, error_msg, -1
        
        elapsed_time = time.time() - start_time
        
        # Log completion
        if log_file_handle:
            log_file_handle.write(f"\n{'='*80}\n")
            log_file_handle.write(f"Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file_handle.write(f"Elapsed time: {elapsed_time:.1f} seconds\n")
            log_file_handle.write(f"Exit code: {exit_code}\n")
            log_file_handle.write(f"{'='*80}\n")
            log_file_handle.close()
        
        log_event('MAKE_COMMAND_COMPLETE',
                  elapsed_s=elapsed_time,
                  exit_code=exit_code)
        
        # Check for errors
        if exit_code != 0:
            # Detect specific errors from output
            detected_errors = detect_errors_in_output(stdout_lines, stderr_lines)
            
            if detected_errors:
                error_msg = f"Command failed with {len(detected_errors)} error(s): {detected_errors[0]}"
            else:
                error_msg = f"Command failed with exit code {exit_code}"
            
            log_event('MAKE_COMMAND_FAILED',
                      error_message=error_msg,
                      exit_code=exit_code)
            return False, error_msg, exit_code
        
        # Success
        return True, None, exit_code
    
    except Exception as e:
        error_msg = f"Exception during command execution: {e}"
        log_event('MAKE_COMMAND_EXCEPTION', error_message=str(e))
        
        if log_file_handle:
            log_file_handle.write(f"\nException: {error_msg}\n")
            log_file_handle.close()
        
        return False, error_msg, -1


def execute_make_command_simple(command, cwd):
    """
    Simplified version of execute_make_command for quick operations.
    
    This doesn't stream output or create log files, just runs and returns status.
    
    Args:
        command: Make command string
        cwd: Working directory
    
    Returns:
        Tuple of (success: bool, exit_code: int)
    """
    cwd = Path(cwd)
    
    log_event('MAKE_COMMAND_SIMPLE_START', command=command)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=BUILD_TIMEOUT_DEFAULT if BUILD_TIMEOUT_DEFAULT > 0 else None
        )
        
        success = result.returncode == 0
        
        if not success:
            log_event('MAKE_COMMAND_SIMPLE_FAILED',
                      exit_code=result.returncode,
                      stderr_preview=result.stderr[:500] if result.stderr else '')
        
        return success, result.returncode
    
    except subprocess.TimeoutExpired:
        log_event('MAKE_COMMAND_SIMPLE_TIMEOUT')
        return False, -1
    except Exception as e:
        log_event('MAKE_COMMAND_SIMPLE_EXCEPTION', error_message=str(e))
        return False, -1