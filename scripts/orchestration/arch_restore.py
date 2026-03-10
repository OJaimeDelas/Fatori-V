# =============================================================================
# FATORI-V • Orchestration • Architecture Restore
# File: arch_restore.py
# -----------------------------------------------------------------------------
# Restore specific generated files from backup using manifest tracking.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from scripts.build.backup_manager import restore_files_from_manifest, cleanup_backup_dir
from scripts.logging.logger import log_event


def restore_architecture_from_backup():
    """
    Restore generated files to architecture using backup manifest.
    
    This restores only the specific files that were backed up (those that
    were overwritten during file allocation), not the entire architecture directory.
    
    Uses the manifest from tmp/backup/ to:
    1. Identify which files were backed up
    2. Restore them to their original locations
    3. Handle benchmark-specific files correctly
    
    Returns:
        Boolean indicating if restoration succeeded
    """
    log_event('ARCH_RESTORE_START')
    
    # Check if backup directory exists
    backup_dir = cfg.TMP_BACKUP_DIR
    if not backup_dir.exists():
        log_event('ARCH_RESTORE_NO_BACKUP', backup_path=str(backup_dir))
        return False
    
    # Check if architecture directory exists
    arch_dir = cfg.ARCHITECTURE_DIR
    if not arch_dir.exists():
        log_event('WARNING', warning_message=f"Architecture directory doesn't exist: {arch_dir}")
        # Create it if needed (shouldn't happen in normal operation)
        arch_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Restore files using manifest
        success = restore_files_from_manifest()
        
        if success:
            log_event('ARCH_RESTORE_SUCCESS')
        else:
            log_event('ARCH_RESTORE_FAILED')
        
        return success
    
    except Exception as e:
        log_event('ARCH_RESTORE_FAILED', error_message=str(e))
        return False


def cleanup_tmp_after_restore():
    """
    Clean tmp directory after architecture restoration.
    
    Removes:
    - tmp/backup/ contents (manifests and backed up files)
    - tmp/generated/ contents
    - tmp/tcl/ contents
    
    Returns:
        Boolean indicating if cleanup succeeded
    """
    tmp_dir = cfg.TMP_DIR
    
    if not tmp_dir.exists():
        return True
    
    try:
        log_event('ARCH_RESTORE_CLEANUP_START', tmp_path=str(tmp_dir))
        
        # Clean specific subdirectories
        subdirs_to_clean = ['backup', 'generated', 'tcl']
        
        for subdir_name in subdirs_to_clean:
            subdir = tmp_dir / subdir_name
            if subdir.exists():
                import shutil
                shutil.rmtree(subdir)
                log_event('DEBUG', debug_message=f"Cleaned: {subdir}")
        
        log_event('ARCH_RESTORE_CLEANUP_SUCCESS')
        return True
    
    except Exception as e:
        log_event('ARCH_RESTORE_CLEANUP_FAILED', error_message=str(e))
        return False


def execute_arch_restore():
    """
    Execute full architecture restoration workflow.
    
    This:
    1. Restores backed up files to original locations using manifest
    2. Cleans tmp/ directory
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    log_event('ARCH_RESTORE_WORKFLOW_START')
    
    # Restore architecture files
    success = restore_architecture_from_backup()
    
    if not success:
        log_event('ARCH_RESTORE_WORKFLOW_FAILED')
        return 1
    
    # Cleanup tmp
    cleanup_success = cleanup_tmp_after_restore()
    
    if not cleanup_success:
        log_event('WARNING', warning_message="Restore succeeded but tmp cleanup had issues")
        # Don't fail on cleanup issues
    
    log_event('ARCH_RESTORE_WORKFLOW_COMPLETE')
    return 0