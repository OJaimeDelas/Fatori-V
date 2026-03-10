# =============================================================================
# FATORI-V • Execution • FI Log Collector
# File: fi_log_collector.py
# -----------------------------------------------------------------------------
# Collects injection_log.txt from FI system after session execution.
# =============================================================================

import shutil
from pathlib import Path
from typing import Optional
import fatori_settings as cfg
from scripts.logging.logger import log_event


def get_fi_log_path() -> Path:
    """
    Get path to injection_log.txt in FI directory.
    
    Returns:
        Path to injection_log.txt file
    """
    # FI console runs from ROOT_DIR so injection_log.txt is created there
    log_path = cfg.ROOT_DIR / 'injection_log.txt'
    
    return log_path


def collect_fi_log_after_session(session_fi_dir: Path, bench_id: str) -> bool:
    """
    Collect injection_log.txt from FI system after session execution.
    
    This copies the injection_log.txt file from the fi/ directory
    to the session's fi/ subdirectory after a benchmark with FI completes.
    
    Args:
        session_fi_dir: Path to session's fi/ directory
        bench_id: Benchmark identifier for logging
    
    Returns:
        Boolean indicating if collection succeeded
    """
    source_path = get_fi_log_path()
    dest_path = session_fi_dir / 'injection_log.txt'
    
    # Check if source exists
    if not source_path.exists():
        log_event('FI_LOG_SOURCE_MISSING',
                  bench_id=bench_id,
                  source=str(source_path))
        return False
    
    try:
        # Ensure destination directory exists
        session_fi_dir.mkdir(parents=True, exist_ok=True)
        
        # Move (not copy) FI log to session directory
        # If destination already exists, remove it first
        if dest_path.exists():
            dest_path.unlink()
        
        shutil.move(str(source_path), str(dest_path))
        
        # Verify move succeeded and source was removed
        if dest_path.exists() and not source_path.exists():
            log_event('FI_LOG_COLLECTED',
                      bench_id=bench_id,
                      source=str(source_path),
                      dest=str(dest_path))
            return True
        else:
            log_event('FI_LOG_MOVE_VERIFICATION_FAILED',
                      bench_id=bench_id,
                      dest_exists=dest_path.exists(),
                      source_still_exists=source_path.exists())
            return False
    
    except Exception as e:
        log_event('FI_LOG_COLLECTION_FAILED',
                  bench_id=bench_id,
                  error_message=str(e))
        import traceback
        log_event('FI_LOG_COLLECTION_TRACEBACK', traceback=traceback.format_exc())
        return False


def check_fi_log_exists() -> bool:
    """
    Check if injection_log.txt exists in FI directory.
    
    Returns:
        Boolean indicating if FI log exists
    """
    log_path = get_fi_log_path()
    return log_path.exists()