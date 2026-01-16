# =============================================================================
# FATORI-V • Build System • Backup Manager
# File: backup_manager.py
# -----------------------------------------------------------------------------
# Manages backup and restore of files before overwriting.
# =============================================================================

import json
import shutil
from pathlib import Path
from datetime import datetime
import fatori_settings as cfg
from scripts.logging.logger import log_event


def create_backup_manifest(backed_up_files, backup_dir):
    """
    Create a JSON manifest of backed up files.
    
    This manifest tracks which files were backed up, their original
    locations, and timestamps for potential restoration.
    
    Args:
        backed_up_files: List of tuples (original_path, backup_path)
        backup_dir: Directory where backups are stored
    
    Returns:
        Path to the created manifest file
    """
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'backup_dir': str(backup_dir),
        'files': []
    }
    
    for original_path, backup_path in backed_up_files:
        manifest['files'].append({
            'original': str(original_path),
            'backup': str(backup_path),
            'original_size': original_path.stat().st_size if original_path.exists() else 0
        })
    
    # Write manifest to backup directory
    manifest_path = backup_dir / "backup_manifest.json"
    with manifest_path.open('w') as f:
        json.dump(manifest, f, indent=2)
    
    log_event('BACKUP_MANIFEST_CREATED', manifest_path=str(manifest_path))
    return manifest_path


def backup_file(source_path, backup_dir):
    """
    Backup a single file to the backup directory.
    
    Preserves the relative directory structure from source to backup.
    
    Args:
        source_path: Path to the file to backup
        backup_dir: Root backup directory
    
    Returns:
        Path to the backed up file, or None if source doesn't exist
    """
    source_path = Path(source_path)
    backup_dir = Path(backup_dir)
    
    if not source_path.exists():
        log_event('BACKUP_FILE_SKIP_NOT_EXIST', source_path=str(source_path))
        return None
    
    # Create backup path preserving relative structure
    # If source is /path/to/file.txt, backup as backup_dir/path/to/file.txt
    try:
        # Try to make path relative to project root
        relative_path = source_path.relative_to(cfg.ROOT_DIR)
    except ValueError:
        # If not under ROOT_DIR, just use the filename
        relative_path = source_path.name
    
    backup_path = backup_dir / relative_path
    
    # Create parent directories
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    shutil.copy2(source_path, backup_path)
    log_event('BACKUP_FILE_SUCCESS', source_path=str(source_path), backup_path=str(backup_path))
    
    return backup_path


def backup_files(file_list, backup_dir=None):
    """
    Backup a list of files before they are overwritten.
    
    Creates backups in tmp/backup/ preserving the relative directory structure.
    Also creates a JSON manifest for tracking and potential restoration.
    
    Args:
        file_list: List of Path objects to backup
        backup_dir: Directory where backups should be stored.
                   Defaults to tmp/backup/
    
    Returns:
        Tuple of (backup_dir, manifest_path)
        - backup_dir: Path to backup directory
        - manifest_path: Path to backup manifest JSON file
    """
    # Use default backup directory if not specified
    if backup_dir is None:
        backup_dir = cfg.TMP_BACKUP_DIR
    
    backup_dir = Path(backup_dir)
    
    # Create timestamped backup subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_dir / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('BACKUP_FILES_START', backup_dir=str(backup_dir))
    
    backed_up_files = []
    skipped_count = 0
    
    # Backup each file
    for file_path in file_list:
        backup_path = backup_file(file_path, backup_dir)
        
        if backup_path:
            backed_up_files.append((file_path, backup_path))
        else:
            skipped_count += 1
    
    log_event('BACKUP_FILES_COMPLETE',
              backed_up_count=len(backed_up_files),
              skipped_count=skipped_count)
    
    # Create manifest
    manifest_path = None
    if backed_up_files:
        manifest_path = create_backup_manifest(backed_up_files, backup_dir)
    
    return backup_dir, manifest_path


def load_backup_manifest(backup_dir):
    """
    Load a backup manifest from a backup directory.
    
    Args:
        backup_dir: Path to the backup directory
    
    Returns:
        Dictionary with manifest data, or None if not found
    """
    backup_dir = Path(backup_dir)
    manifest_path = backup_dir / "backup_manifest.json"
    
    if not manifest_path.exists():
        log_event('BACKUP_MANIFEST_NOT_FOUND', manifest_path=str(manifest_path))
        return None
    
    try:
        with manifest_path.open('r') as f:
            manifest = json.load(f)
        return manifest
    except Exception as e:
        log_event('BACKUP_MANIFEST_LOAD_ERROR', error_message=str(e))
        return None


def restore_files(backup_dir):
    """
    Restore all files from a backup directory to their original locations.
    
    This reads the backup manifest and copies files back to their original
    locations, overwriting any existing files.
    
    Args:
        backup_dir: Path to the backup directory containing backup_manifest.json
    
    Returns:
        Boolean indicating success
    """
    backup_dir = Path(backup_dir)
    
    log_event('BACKUP_RESTORE_START', backup_dir=str(backup_dir))
    
    # Load manifest
    manifest = load_backup_manifest(backup_dir)
    if not manifest:
        log_event('BACKUP_RESTORE_NO_MANIFEST')
        return False
    
    restored_count = 0
    failed_count = 0
    
    # Restore each file
    for file_entry in manifest['files']:
        original_path = Path(file_entry['original'])
        backup_path = Path(file_entry['backup'])
        
        if not backup_path.exists():
            log_event('BACKUP_FILE_NOT_FOUND', backup_path=str(backup_path))
            failed_count += 1
            continue
        
        try:
            # Create parent directory if needed
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy backup to original location
            shutil.copy2(backup_path, original_path)
            log_event('BACKUP_RESTORE_FILE', original_path=str(original_path))
            restored_count += 1
        except Exception as e:
            log_event('BACKUP_RESTORE_FILE_ERROR',
                      backup_path=str(backup_path),
                      original_path=str(original_path),
                      error_message=str(e))
            failed_count += 1
    
    log_event('BACKUP_RESTORE_COMPLETE',
              restored_count=restored_count,
              failed_count=failed_count)
    
    if failed_count > 0:
        return False
    
    return True