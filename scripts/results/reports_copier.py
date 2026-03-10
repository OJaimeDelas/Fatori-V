# =============================================================================
# FATORI-V • Results • Reports Copier
# File: reports_copier.py
# -----------------------------------------------------------------------------
# Copies Vivado reports directory to results.
# =============================================================================

import shutil
from pathlib import Path
from typing import Optional
import fatori_settings as cfg
from scripts.logging.logger import log_event


def get_reports_source_dir() -> Path:
    """
    Get path to reports directory in architecture.
    
    Returns:
        Path to reports directory
    """
    # Reports are in iob_soc_V1.0/hardware/fpga/reports/ (directly under ROOT_DIR)
    reports_path = cfg.ROOT_DIR / 'iob_soc_V1.0' / 'hardware' / 'fpga' / 'reports'
    
    return reports_path


def copy_reports_to_results(run_dir: Path) -> bool:
    """
    Copy entire reports directory from architecture to results.
    
    This recursively copies all Vivado reports for post-processing.
    Should be called after the last benchmark completes when FULL_MAKE_BUILD is True.
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        Boolean indicating if copy succeeded
    """
    source_dir = get_reports_source_dir()
    dest_dir = run_dir / 'reports'
    
    # Check if source exists
    if not source_dir.exists():
        log_event('REPORTS_COPY_SOURCE_MISSING', source=str(source_dir))
        return False
    
    try:
        # Ensure destination parent exists
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing destination if present
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        
        # Copy entire directory recursively
        shutil.copytree(source_dir, dest_dir)
        
        log_event('REPORTS_COPIED',
                  source=str(source_dir),
                  dest=str(dest_dir))
        
        return True
    
    except Exception as e:
        log_event('REPORTS_COPY_FAILED', error_message=str(e))
        return False


def check_reports_exist() -> bool:
    """
    Check if reports directory exists in architecture.
    
    Returns:
        Boolean indicating if reports exist
    """
    reports_dir = get_reports_source_dir()
    return reports_dir.exists() and reports_dir.is_dir()