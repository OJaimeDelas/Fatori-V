# =============================================================================
# FATORI-V • Execution • Timeout Handler
# File: timeout_handler.py
# -----------------------------------------------------------------------------
# Monitors processes with timeout and handles process tree termination.
# =============================================================================

import time
import signal
import os
from typing import Callable, Optional
from scripts.logging.logger import log_event


def kill_process_tree(pid, sig=signal.SIGTERM):
    """
    Terminate a process and all its children.
    
    This ensures that child processes are also killed when terminating
    a process tree (like a make command that spawns subprocesses).
    
    Args:
        pid: Process ID to terminate
        sig: Signal to send (default: SIGTERM)
    
    Returns:
        Boolean indicating success
    """
    try:
        # Try to get child processes using ps
        import subprocess
        result = subprocess.run(
            ['ps', '--ppid', str(pid), '-o', 'pid', '--no-headers'],
            capture_output=True,
            text=True
        )
        
        # Kill children first
        if result.returncode == 0:
            child_pids = result.stdout.strip().split('\n')
            for child_pid_str in child_pids:
                child_pid_str = child_pid_str.strip()
                if child_pid_str and child_pid_str.isdigit():
                    child_pid = int(child_pid_str)
                    try:
                        os.kill(child_pid, sig)
                        log_event('PROCESS_CHILD_KILLED', child_pid=child_pid)
                    except ProcessLookupError:
                        pass  # Process already gone
                    except Exception as e:
                        log_event('PROCESS_CHILD_KILL_FAILED',
                                  child_pid=child_pid,
                                  error_message=str(e))
        
        # Kill parent process
        try:
            os.kill(pid, sig)
            log_event('PROCESS_KILLED', pid=pid)
            return True
        except ProcessLookupError:
            log_event('PROCESS_ALREADY_GONE', pid=pid)
            return True
        except Exception as e:
            log_event('PROCESS_KILL_FAILED', pid=pid, error_message=str(e))
            return False
    
    except Exception as e:
        log_event('PROCESS_TREE_KILL_ERROR', error_message=str(e))
        return False


def monitor_with_timeout(process, timeout_s, callback=None, poll_interval=1.0):
    """
    Monitor a subprocess with timeout and optional periodic callback.
    
    This function:
    - Waits for process completion
    - Calls callback periodically (if provided)
    - Terminates process if timeout is reached
    
    Args:
        process: subprocess.Popen object
        timeout_s: Timeout in seconds (-1 for no timeout)
        callback: Optional function called each poll interval with (elapsed_s, remaining_s)
        poll_interval: How often to poll in seconds
    
    Returns:
        Tuple of (completed: bool, timed_out: bool, exit_code: int or None)
        - completed: True if process finished normally
        - timed_out: True if timeout was reached
        - exit_code: Process exit code (None if killed)
    """
    if timeout_s <= 0:
        # No timeout - just wait for completion
        exit_code = process.wait()
        return True, False, exit_code
    
    start_time = time.time()
    elapsed = 0
    
    while elapsed < timeout_s:
        # Check if process is still running
        exit_code = process.poll()
        if exit_code is not None:
            # Process completed
            log_event('PROCESS_COMPLETED', exit_code=exit_code)
            return True, False, exit_code
        
        # Calculate remaining time
        remaining = timeout_s - elapsed
        
        # Call callback if provided
        if callback:
            try:
                callback(elapsed, remaining)
            except Exception as e:
                log_event('TIMEOUT_CALLBACK_ERROR', error_message=str(e))
        
        # Sleep for poll interval
        time.sleep(poll_interval)
        elapsed = time.time() - start_time
    
    # Timeout reached - kill process
    log_event('PROCESS_TIMEOUT', timeout_s=timeout_s, pid=process.pid)
    
    pid = process.pid
    kill_process_tree(pid, signal.SIGTERM)
    
    # Give it a moment to die gracefully
    time.sleep(1.0)
    
    # Check if it's really dead
    exit_code = process.poll()
    if exit_code is None:
        # Still alive, use SIGKILL
        log_event('PROCESS_SIGKILL', pid=pid)
        kill_process_tree(pid, signal.SIGKILL)
        time.sleep(0.5)
        exit_code = process.poll()
    
    return False, True, exit_code


def monitor_with_simple_timeout(process, timeout_s):
    """
    Simplified version of monitor_with_timeout without callback.
    
    Args:
        process: subprocess.Popen object
        timeout_s: Timeout in seconds
    
    Returns:
        Boolean indicating if process completed (False = timeout)
    """
    completed, timed_out, exit_code = monitor_with_timeout(
        process,
        timeout_s,
        callback=None
    )
    
    return completed and not timed_out