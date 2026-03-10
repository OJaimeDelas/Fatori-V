# =============================================================================
# FATORI-V • Build System • Backup Manager
# File: backup_manager.py
# -----------------------------------------------------------------------------
# Manages backup and restore of allocated files using gen_locations tracking.
# =============================================================================

import json
import shutil
from pathlib import Path
from datetime import datetime
import fatori_settings as cfg
from scripts.logging.logger import log_event


def get_backup_filename(original_path):
    """
    Generate backup filename with benchmark-specific naming for bench_config.h.
    
    For bench_config.h files, extracts benchmark name from path and appends to filename.
    For other files, uses original filename.
    
    Args:
        original_path: Path object for original file
    
    Returns:
        String filename to use in backup
    """
    original_path = Path(original_path)
    filename = original_path.name
    
    # Special handling for bench_config.h files
    if filename == "bench_config.h":
        # Extract benchmark name from path
        # Path format: benchmarks/<bench_name>/bench_config.h
        parts = original_path.parts
        if "benchmarks" in parts:
            bench_idx = parts.index("benchmarks")
            if bench_idx + 1 < len(parts):
                bench_name = parts[bench_idx + 1]
                return f"bench_config_{bench_name}.h"
    
    return filename


def create_backup_manifest(backed_up_files, backup_id):
    """
    Create a JSON manifest of backed up files with gen_locations mapping.
    
    Manifest tracks:
    - Original file locations (from gen_locations.yaml destinations)
    - Backup filenames (with benchmark-specific naming)
    - Timestamps for tracking
    
    Args:
        backed_up_files: List of tuples (original_path, backup_filename)
        backup_id: Unique backup identifier (timestamp)
    
    Returns:
        Path to the created manifest file
    """
    backup_dir = cfg.TMP_BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        'backup_id': backup_id,
        'timestamp': datetime.now().isoformat(),
        'files': []
    }
    
    for original_path, backup_filename in backed_up_files:
        manifest['files'].append({
            'original': str(original_path),
            'backup_filename': backup_filename,
            'original_size': original_path.stat().st_size if original_path.exists() else 0
        })
    
    # Write manifest to backup directory
    manifest_path = backup_dir / f"backup_manifest_{backup_id}.json"
    with manifest_path.open('w') as f:
        json.dump(manifest, f, indent=2)
    
    log_event('BACKUP_MANIFEST_CREATED', manifest_path=str(manifest_path), file_count=len(backed_up_files))
    return manifest_path


def backup_file(source_path, backup_dir, backup_filename):
    """
    Backup a single file to the backup directory with specified filename.
    
    Args:
        source_path: Path to the file to backup
        backup_dir: Root backup directory
        backup_filename: Filename to use in backup
    
    Returns:
        Path to the backed up file, or None if source doesn't exist
    """
    source_path = Path(source_path)
    backup_dir = Path(backup_dir)
    
    if not source_path.exists():
        log_event('DEBUG', debug_message=f"Backup skip (not exists): {source_path}")
        return None
    
    backup_path = backup_dir / backup_filename
    
    # Create backup directory if needed
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    try:
        shutil.copy2(source_path, backup_path)
        log_event('DEBUG', debug_message=f"Backed up: {source_path.name} -> {backup_filename}")
        return backup_path
    except Exception as e:
        log_event('ERROR', error_message=f"Backup failed for {source_path}: {e}")
        return None


def backup_files(file_list):
    """
    Backup a list of files before they are overwritten.
    
    Creates backups in tmp/backup/ with:
    - Unique timestamped backup ID
    - Benchmark-specific naming for bench_config.h files
    - JSON manifest for tracking and restoration
    
    Args:
        file_list: List of Path objects to backup
    
    Returns:
        Tuple of (backup_id, manifest_path)
        - backup_id: Unique identifier for this backup
        - manifest_path: Path to backup manifest JSON file
    """
    if not file_list:
        return None, None
    
    backup_dir = cfg.TMP_BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create unique backup ID
    backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    log_event('BACKUP_FILES_START', backup_id=backup_id, file_count=len(file_list))
    
    backed_up_files = []
    
    # Backup each file
    for file_path in file_list:
        file_path = Path(file_path)
        backup_filename = get_backup_filename(file_path)
        
        backup_path = backup_file(file_path, backup_dir, backup_filename)
        
        if backup_path:
            backed_up_files.append((file_path, backup_filename))
    
    log_event('BACKUP_FILES_COMPLETE', backed_up_count=len(backed_up_files))
    
    # Create manifest
    manifest_path = None
    if backed_up_files:
        manifest_path = create_backup_manifest(backed_up_files, backup_id)
    
    return backup_id, manifest_path


def find_latest_backup_manifest():
    """
    Find the most recent backup manifest in tmp/backup/.
    
    Returns:
        Path to latest manifest, or None if no backups exist
    """
    backup_dir = cfg.TMP_BACKUP_DIR
    
    if not backup_dir.exists():
        return None
    
    # Find all manifest files
    manifests = list(backup_dir.glob("backup_manifest_*.json"))
    
    if not manifests:
        return None
    
    # Sort by modification time, return latest
    manifests.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return manifests[0]


def load_backup_manifest(manifest_path=None):
    """
    Load a backup manifest from tmp/backup/.
    
    Args:
        manifest_path: Path to specific manifest, or None to load latest
    
    Returns:
        Dictionary with manifest data, or None if not found
    """
    if manifest_path is None:
        manifest_path = find_latest_backup_manifest()
    
    if not manifest_path or not Path(manifest_path).exists():
        log_event('BACKUP_MANIFEST_NOT_FOUND')
        return None
    
    try:
        with Path(manifest_path).open('r') as f:
            manifest = json.load(f)
        log_event('BACKUP_MANIFEST_LOADED', 
                  manifest_path=str(manifest_path),
                  backup_id=manifest.get('backup_id', 'unknown'),
                  file_count=len(manifest.get('files', [])))
        return manifest
    except Exception as e:
        log_event('BACKUP_MANIFEST_LOAD_ERROR', error_message=str(e))
        return None


def restore_files_from_manifest(manifest=None):
    """
    Restore all files from a backup manifest to their original locations.
    
    This:
    1. Loads manifest (latest if not provided)
    2. Copies backed up files to their original locations
    3. Overwrites existing files
    
    Args:
        manifest: Manifest dictionary, or None to load latest
    
    Returns:
        Boolean indicating success
    """
    backup_dir = cfg.TMP_BACKUP_DIR
    
    # Load manifest if not provided
    if manifest is None:
        manifest = load_backup_manifest()
    
    if not manifest:
        log_event('ERROR', error_message="No backup manifest found")
        return False
    
    backup_id = manifest.get('backup_id', 'unknown')
    log_event('BACKUP_RESTORE_START', backup_id=backup_id)
    
    restored_count = 0
    failed_count = 0
    
    # Restore each file
    for file_entry in manifest['files']:
        original_path = Path(file_entry['original'])
        backup_filename = file_entry['backup_filename']
        backup_path = backup_dir / backup_filename
        
        if not backup_path.exists():
            log_event('WARNING', warning_message=f"Backup file not found: {backup_filename}")
            failed_count += 1
            continue
        
        try:
            # Create parent directory if needed
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy backup to original location
            shutil.copy2(backup_path, original_path)
            log_event('DEBUG', debug_message=f"Restored: {backup_filename} -> {original_path}")
            restored_count += 1
        except Exception as e:
            log_event('ERROR', error_message=f"Restore failed for {backup_filename}: {e}")
            failed_count += 1
    
    log_event('BACKUP_RESTORE_COMPLETE',
              restored_count=restored_count,
              failed_count=failed_count)
    
    return failed_count == 0


def cleanup_backup_dir():
    """
    Clean all files from tmp/backup/ directory.
    
    Returns:
        Boolean indicating success
    """
    backup_dir = cfg.TMP_BACKUP_DIR
    
    if not backup_dir.exists():
        return True
    
    try:
        log_event('BACKUP_CLEANUP_START', backup_dir=str(backup_dir))
        
        # Remove all files and subdirectories
        for item in backup_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        
        log_event('BACKUP_CLEANUP_SUCCESS')
        return True
    except Exception as e:
        log_event('BACKUP_CLEANUP_ERROR', error_message=str(e))
        return False