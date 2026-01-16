# =============================================================================
# FATORI-V • Execution • Sync File Manager
# File: sync_file_manager.py
# -----------------------------------------------------------------------------
# Manages synchronization file for coordinating benchmark execution with FI.
# =============================================================================

import time
from pathlib import Path
from scripts.logging.logger import log_event


def create_sync_file(sync_path):
    """
    Create an empty synchronization file.
    
    The sync file is used to coordinate between benchmark execution and
    fault injection. The benchmark deletes this file when it's ready for
    FI to begin, signaling that initialization is complete.
    
    Args:
        sync_path: Path where sync file should be created
    
    Returns:
        Boolean indicating success
    """
    sync_path = Path(sync_path)
    
    # Ensure parent directory exists
    sync_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create empty file
        sync_path.touch(exist_ok=True)
        log_event('SYNC_FILE_CREATED', sync_path=str(sync_path))
        return True
    except Exception as e:
        log_event('SYNC_FILE_CREATE_ERROR', 
                  sync_path=str(sync_path),
                  error_message=str(e))
        return False


def wait_for_sync_file_deletion(sync_path, timeout_s, poll_interval=0.5):
    """
    Wait for sync file to be deleted by the benchmark.
    
    This polls the sync file path periodically until either:
    - The file is deleted (benchmark is ready for FI)
    - Timeout is reached (benchmark failed to signal)
    
    Args:
        sync_path: Path to sync file
        timeout_s: Maximum time to wait in seconds
        poll_interval: How often to check file existence (seconds)
    
    Returns:
        Boolean indicating if file was deleted (True) or timeout (False)
    """
    sync_path = Path(sync_path)
    
    if not sync_path.exists():
        log_event('SYNC_FILE_ALREADY_DELETED', sync_path=str(sync_path))
        return True  # Already deleted
    
    log_event('SYNC_FILE_WAITING', timeout_s=timeout_s)
    
    start_time = time.time()
    elapsed = 0
    
    while elapsed < timeout_s:
        # Check if file has been deleted
        if not sync_path.exists():
            log_event('SYNC_FILE_DELETED', elapsed_s=elapsed)
            return True
        
        # Sleep for poll interval
        time.sleep(poll_interval)
        elapsed = time.time() - start_time
    
    # Timeout reached
    log_event('SYNC_FILE_TIMEOUT', timeout_s=timeout_s)
    return False


def cleanup_sync_file(sync_path):
    """
    Remove sync file if it exists.
    
    This cleanup is performed after execution completes to ensure
    a clean state for the next session.
    
    Args:
        sync_path: Path to sync file
    
    Returns:
        Boolean indicating if cleanup was successful
    """
    sync_path = Path(sync_path)
    
    if not sync_path.exists():
        log_event('SYNC_FILE_ALREADY_GONE', sync_path=str(sync_path))
        return True
    
    try:
        sync_path.unlink()
        log_event('SYNC_FILE_CLEANED', sync_path=str(sync_path))
        return True
    except Exception as e:
        log_event('SYNC_FILE_CLEANUP_ERROR',
                  sync_path=str(sync_path),
                  error_message=str(e))
        return False


def check_sync_file_exists(sync_path):
    """
    Check if sync file currently exists.
    
    Args:
        sync_path: Path to sync file
    
    Returns:
        Boolean indicating if file exists
    """
    sync_path = Path(sync_path)
    exists = sync_path.exists()
    
    log_event('SYNC_FILE_CHECK', 
              sync_path=str(sync_path),
              exists=exists)
    return exists