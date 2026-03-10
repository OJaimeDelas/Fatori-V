# =============================================================================
# FATORI-V • Build System • File Allocator
# File: file_allocator.py
# -----------------------------------------------------------------------------
# Allocates generated and static files to architecture tree.
# =============================================================================

import shutil
from pathlib import Path
import fatori_settings as cfg
from scripts.common.file_allocator import load_allocation_maps, get_destination_path
from scripts.build.backup_manager import backup_files
from scripts.logging import logger


def collect_generated_files():
    """
    Collect all generated files from tmp/generated/ directory.
    
    Returns:
        List of Path objects for all generated files
    """
    generated_dir = cfg.TMP_GENERATED_DIR
    
    if not generated_dir.exists():
        logger.log_event('WARNING', warning_message=f"Generated directory doesn't exist: {generated_dir}")
        return []
    
    # Collect all files (not directories) recursively
    files = [f for f in generated_dir.rglob('*') if f.is_file()]
    
    logger.log_event('DEBUG', debug_message=f"Found {len(files)} generated files in {generated_dir}")
    return files


def collect_static_hardware_files():
    """
    Collect static hardware files from inputs/hardware/ directory.
    
    Returns:
        List of Path objects for static hardware files
    """
    hardware_dir = cfg.INPUTS_HARDWARE_DIR
    
    if not hardware_dir.exists():
        logger.log_event('WARNING', warning_message=f"Hardware directory doesn't exist: {hardware_dir}")
        return []
    
    # Collect all files recursively, excluding locations.yaml
    files = [
        f for f in hardware_dir.rglob('*') 
        if f.is_file() and f.name != 'locations.yaml'
    ]
    
    logger.log_event('DEBUG', debug_message=f"Found {len(files)} static hardware files")
    return files


def collect_static_software_files():
    """
    Collect static software files from inputs/software/ directory.
    
    Returns:
        List of Path objects for static software files
    """
    software_dir = cfg.INPUTS_SOFTWARE_DIR
    
    if not software_dir.exists():
        logger.log_event('WARNING', warning_message=f"Software directory doesn't exist: {software_dir}")
        return []
    
    # Collect all files recursively, excluding locations.yaml
    files = [
        f for f in software_dir.rglob('*') 
        if f.is_file() and f.name != 'locations.yaml'
    ]
    
    logger.log_event('DEBUG', debug_message=f"Found {len(files)} static software files")
    return files


def validate_destination_path(dest_path, base_dir):
    """
    Validate that destination path is safe and within expected boundaries.
    
    This prevents accidental deletion or corruption of files outside
    the architecture directory or in critical system locations.
    
    Args:
        dest_path: Destination path to validate
        base_dir: Expected base directory (e.g., architecture/)
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    dest_path = Path(dest_path).resolve()
    base_dir = Path(base_dir).resolve()
    
    # Check 1: Path must be absolute
    if not dest_path.is_absolute():
        return False, f"Destination path must be absolute: {dest_path}"
    
    # Check 2: Path must be under base directory
    try:
        dest_path.relative_to(base_dir)
    except ValueError:
        return False, f"Destination path {dest_path} is not under base directory {base_dir}"
    
    # Check 3: Path must not go to critical system directories
    critical_dirs = ['/bin', '/boot', '/dev', '/etc', '/lib', '/proc', '/sys', '/usr']
    for critical_dir in critical_dirs:
        try:
            dest_path.relative_to(critical_dir)
            return False, f"Destination path {dest_path} targets critical system directory {critical_dir}"
        except ValueError:
            continue  # Not under this critical dir, check next
    
    # Check 4: Parent directory must be creatable/accessible
    parent = dest_path.parent
    if parent.exists() and not parent.is_dir():
        return False, f"Parent path exists but is not a directory: {parent}"
    
    return True, None


def copy_file_to_destination(source_path, dest_path, validate_base_dir=None):
    """
    Copy a file to its destination with validation and error handling.
    
    This is the surgical copy operation that ensures only the specified
    file is touched and nothing else in the architecture is affected.
    
    Args:
        source_path: Source file path
        dest_path: Destination file path
        validate_base_dir: Optional base directory for validation
    
    Returns:
        Boolean indicating success
    """
    source_path = Path(source_path)
    dest_path = Path(dest_path)
    
    # Validate source exists
    if not source_path.exists():
        logger.log_event('ERROR_FILE_NOT_FOUND', file_path=str(source_path))
        return False
    
    # Validate source is a file
    if not source_path.is_file():
        logger.log_event('ERROR', message=f"Source is not a file: {source_path}")
        return False
    
    # Validate destination path if base directory provided
    if validate_base_dir:
        is_valid, error_msg = validate_destination_path(dest_path, validate_base_dir)
        if not is_valid:
            logger.log_event('ERROR', message=f"Invalid destination path: {error_msg}")
            return False
    
    try:
        # Create parent directories only (never delete anything)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file (this only writes the single file, never deletes)
        shutil.copy2(source_path, dest_path)
        logger.log_event('FILE_COPY', source=str(source_path.name), destination=str(dest_path))
        return True
    except PermissionError as e:
        logger.log_event('ERROR', message=f"Permission denied copying {source_path} to {dest_path}: {e}")
        return False
    except Exception as e:
        logger.log_event('ERROR', message=f"Error copying {source_path} to {dest_path}: {e}")
        return False


def allocate_generated_files(allocation_map, exclude_list=None, backup_enabled=True):
    """
    Allocate generated files to architecture tree using allocation map.
    
    This performs surgical file allocation with validation:
    - Skips files in exclude list (silently, no warnings)
    - Skips files without mappings (with warning)
    - Validates all destination paths before any copying
    - Backs up existing files before overwriting
    - Only copies successfully validated files
    
    Args:
        allocation_map: Dictionary mapping source names to destination paths
        exclude_list: List of filenames to skip (no warnings)
        backup_enabled: If True, backup existing files before overwriting
    
    Returns:
        List of successfully copied destination paths
    """
    logger.log_event('DEBUG', debug_message="Allocating generated files to architecture...")
    
    if exclude_list is None:
        exclude_list = []
    
    # Collect generated files
    generated_files = collect_generated_files()
    
    if not generated_files:
        logger.log_event('WARNING', warning_message="No generated files to allocate")
        return []
    
    # Determine destinations and validate paths
    file_pairs = []  # List of (source, dest) tuples
    files_to_backup = []
    validation_failed = []
    excluded_count = 0
    
    for source_file in generated_files:
        # Check if file is in exclude list
        if source_file.name in exclude_list:
            excluded_count += 1
            logger.log_event('DEBUG', debug_message=f"Skipping excluded file: {source_file.name}")
            continue
        
        # Get destination from allocation map
        dest_path = get_destination_path(
            source_file, 
            allocation_map, 
            base_dir=cfg.ROOT_DIR  # Use ROOT_DIR as base for path resolution
        )
        
        if not dest_path:
            logger.log_event('WARNING', warning_message=f"No allocation mapping for: {source_file.name}")
            continue
        
        # Validate destination path
        is_valid, error_msg = validate_destination_path(dest_path, cfg.ROOT_DIR)
        if not is_valid:
            logger.log_event('ERROR', message=f"Invalid destination for {source_file.name}: {error_msg}")
            validation_failed.append(source_file.name)
            continue
        
        file_pairs.append((source_file, dest_path))
        
        # If destination exists, mark for backup
        if dest_path.exists():
            files_to_backup.append(dest_path)
    
    # Log excluded files summary
    if excluded_count > 0:
        logger.log_event('DEBUG', debug_message=f"Excluded {excluded_count} intermediate file(s) from allocation")
    
    # Report validation failures
    if validation_failed:
        logger.log_event('ERROR', message=f"Allocation validation failed for {len(validation_failed)} file(s): {', '.join(validation_failed)}")
        logger.log_event('ERROR', message="File allocation aborted to prevent corruption. Fix allocation mappings in gen_locations.yaml")
        return []
    
    # Backup existing files if enabled
    if backup_enabled and files_to_backup:
        logger.log_event('DEBUG', debug_message=f"Backing up {len(files_to_backup)} existing files...")
        backup_files(files_to_backup)
    
    # Copy files to destinations with validation
    copied_files = []
    failed_copies = []
    
    for source_file, dest_path in file_pairs:
        if copy_file_to_destination(source_file, dest_path, validate_base_dir=cfg.ROOT_DIR):
            copied_files.append(dest_path)
        else:
            failed_copies.append(source_file.name)
    
    # Report copy failures
    if failed_copies:
        logger.log_event('WARNING', warning_message=f"Failed to copy {len(failed_copies)} file(s): {', '.join(failed_copies)}")
    
    logger.log_event('DEBUG', debug_message=f"Allocated {len(copied_files)} generated files")
    return copied_files

def allocate_static_files(hardware_map, software_map, backup_enabled=True):
    """
    Allocate static hardware and software files to architecture tree.
    
    This performs surgical file allocation with validation for both
    hardware and software static files.
    
    Args:
        hardware_map: Hardware allocation mapping
        software_map: Software allocation mapping
        backup_enabled: If True, backup existing files before overwriting
    
    Returns:
        List of successfully copied destination paths
    """
    logger.log_event('DEBUG', debug_message="Allocating static files to architecture...")
    
    copied_files = []
    
    # Allocate hardware files
    hardware_files = collect_static_hardware_files()
    if hardware_files:
        files_to_backup = []
        file_pairs = []
        validation_failed = []
        
        for source_file in hardware_files:
            dest_path = get_destination_path(
                source_file,
                hardware_map,
                base_dir=cfg.ROOT_DIR
            )
            
            if not dest_path:
                logger.log_event('WARNING', warning_message=f"No allocation mapping for hardware file: {source_file.name}")
                continue
            
            # Validate destination path
            is_valid, error_msg = validate_destination_path(dest_path, cfg.ROOT_DIR)
            if not is_valid:
                logger.log_event('ERROR', message=f"Invalid destination for {source_file.name}: {error_msg}")
                validation_failed.append(source_file.name)
                continue
            
            file_pairs.append((source_file, dest_path))
            if dest_path.exists():
                files_to_backup.append(dest_path)
        
        # Report validation failures
        if validation_failed:
            logger.log_event('ERROR', message=f"Hardware file validation failed for {len(validation_failed)} file(s)")
            logger.log_event('ERROR', message="Allocation aborted for hardware files to prevent corruption")
        else:
            # Backup if needed
            if backup_enabled and files_to_backup:
                backup_files(files_to_backup)
            
            # Copy files with validation
            for source_file, dest_path in file_pairs:
                if copy_file_to_destination(source_file, dest_path, validate_base_dir=cfg.ROOT_DIR):
                    copied_files.append(dest_path)
    
    # Allocate software files
    software_files = collect_static_software_files()
    if software_files:
        files_to_backup = []
        file_pairs = []
        validation_failed = []
        
        for source_file in software_files:
            dest_path = get_destination_path(
                source_file,
                software_map,
                base_dir=cfg.ROOT_DIR
            )
            
            if not dest_path:
                logger.log_event('WARNING', warning_message=f"No allocation mapping for software file: {source_file.name}")
                continue
            
            # Validate destination path
            is_valid, error_msg = validate_destination_path(dest_path, cfg.ROOT_DIR)
            if not is_valid:
                logger.log_event('ERROR', message=f"Invalid destination for {source_file.name}: {error_msg}")
                validation_failed.append(source_file.name)
                continue
            
            file_pairs.append((source_file, dest_path))
            if dest_path.exists():
                files_to_backup.append(dest_path)
        
        # Report validation failures
        if validation_failed:
            logger.log_event('ERROR', message=f"Software file validation failed for {len(validation_failed)} file(s)")
            logger.log_event('ERROR', message="Allocation aborted for software files to prevent corruption")
        else:
            # Backup if needed
            if backup_enabled and files_to_backup:
                backup_files(files_to_backup)
            
            # Copy files with validation
            for source_file, dest_path in file_pairs:
                if copy_file_to_destination(source_file, dest_path, validate_base_dir=cfg.ROOT_DIR):
                    copied_files.append(dest_path)
    
    logger.log_event('DEBUG', debug_message=f"Allocated {len(copied_files)} static files")
    return copied_files


def allocate_files(config, backup_enabled=True):
    """
    Main file allocation orchestrator.
    
    Allocates all generated and static files to the architecture tree
    following the location mappings defined in locations.yaml files.
    
    Workflow:
    1. Load allocation maps (gen_locations, hardware, software) and exclude list
    2. Backup existing files that will be overwritten (if enabled)
    3. Copy generated files to destinations (skip excluded files)
    4. Copy TCL files to VIVADO_INPUT location
    5. Copy static hardware and software files
    
    Args:
        config: The loaded YAML configuration dictionary (for context)
        backup_enabled: If True, backup files before overwriting
    
    Returns:
        Dictionary with lists of copied files:
        {
            'generated': [list of paths],
            'tcl': [list of paths],
            'static': [list of paths]
        }
    """
    logger.log_event('FILE_MOVEMENT_START')
    
    # Load allocation maps and exclude list
    allocation_maps = load_allocation_maps()
    gen_map = allocation_maps['gen_locations']
    hardware_map = allocation_maps['hardware_locations']
    software_map = allocation_maps['software_locations']
    exclude_list = allocation_maps.get('exclude_list', [])
    
    # Allocate files
    allocated_files = {
        'generated': [],
        'tcl': [],
        'static': []
    }
    
    # Allocate generated files (with exclude list)
    logger.log_event('DEBUG', debug_message="Allocating generated files...")
    allocated_files['generated'] = allocate_generated_files(gen_map, exclude_list, backup_enabled)
    
    # Allocate TCL files
    logger.log_event('DEBUG', debug_message="Allocating TCL files...")
    # TCL files stay in tmp/tcl and are sourced from there by hook scripts
    allocated_files['tcl'] = []
    
    # Allocate static files
    logger.log_event('DEBUG', debug_message="Allocating static files...")
    allocated_files['static'] = allocate_static_files(
        hardware_map,
        software_map,
        backup_enabled
    )
    
    # Summary
    total_files = sum(len(files) for files in allocated_files.values())
    logger.log_event('FILE_MOVEMENT_END', file_count=total_files)
    
    return allocated_files