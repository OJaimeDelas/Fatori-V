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


def collect_tcl_files():
    """
    Collect all TCL files from tmp/tcl/ directory.
    
    Returns:
        List of Path objects for all TCL files
    """
    tcl_dir = cfg.TMP_TCL_DIR
    
    if not tcl_dir.exists():
        logger.log_event('WARNING', warning_message=f"TCL directory doesn't exist: {tcl_dir}")
        return []
    
    # Collect all .tcl files
    files = list(tcl_dir.glob('*.tcl'))
    
    logger.log_event('DEBUG', debug_message=f"Found {len(files)} TCL files in {tcl_dir}")
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


def copy_file_to_destination(source_path, dest_path):
    """
    Copy a file to its destination, creating parent directories as needed.
    
    Args:
        source_path: Source file path
        dest_path: Destination file path
    
    Returns:
        Boolean indicating success
    """
    source_path = Path(source_path)
    dest_path = Path(dest_path)
    
    if not source_path.exists():
        logger.log_event('ERROR_FILE_NOT_FOUND', file_path=str(source_path))
        return False
    
    try:
        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        logger.log_event('FILE_COPY', source=str(source_path.name), destination=str(dest_path))
        return True
    except Exception as e:
        logger.log_event('ERROR', message=f"Error copying {source_path} to {dest_path}: {e}")
        return False


def allocate_generated_files(allocation_map, backup_enabled=True):
    """
    Allocate generated files to architecture tree using allocation map.
    
    Args:
        allocation_map: Dictionary mapping source names to destination paths
        backup_enabled: If True, backup existing files before overwriting
    
    Returns:
        List of successfully copied destination paths
    """
    logger.log_event('DEBUG', debug_message="Allocating generated files to architecture...")
    
    # Collect generated files
    generated_files = collect_generated_files()
    
    if not generated_files:
        logger.log_event('WARNING', warning_message="No generated files to allocate")
        return []
    
    # Determine destinations and files to backup
    file_pairs = []  # List of (source, dest) tuples
    files_to_backup = []
    
    for source_file in generated_files:
        # Get destination from allocation map
        dest_path = get_destination_path(
            source_file, 
            allocation_map, 
            base_dir=cfg.ARCHITECTURE_DIR
        )
        
        if not dest_path:
            logger.log_event('WARNING', warning_message=f"No allocation mapping for: {source_file.name}")
            continue
        
        file_pairs.append((source_file, dest_path))
        
        # If destination exists, mark for backup
        if dest_path.exists():
            files_to_backup.append(dest_path)
    
    # Backup existing files if enabled
    if backup_enabled and files_to_backup:
        logger.log_event('DEBUG', debug_message=f"Backing up {len(files_to_backup)} existing files...")
        backup_files(files_to_backup)
    
    # Copy files to destinations
    copied_files = []
    for source_file, dest_path in file_pairs:
        if copy_file_to_destination(source_file, dest_path):
            copied_files.append(dest_path)
    
    logger.log_event('DEBUG', debug_message=f"Allocated {len(copied_files)} generated files")
    return copied_files


def allocate_tcl_files(backup_enabled=True):
    """
    Allocate TCL files to VIVADO_INPUT directory in architecture.
    
    TCL files go to architecture/hardware/fpga/vivado/tcl/
    
    Args:
        backup_enabled: If True, backup existing files before overwriting
    
    Returns:
        List of successfully copied destination paths
    """
    logger.log_event('DEBUG', debug_message="Allocating TCL files to architecture...")
    
    # Collect TCL files
    tcl_files = collect_tcl_files()
    
    if not tcl_files:
        logger.log_event('WARNING', warning_message="No TCL files to allocate")
        return []
    
    # TCL destination directory (VIVADO_INPUT location)
    tcl_dest_dir = cfg.ARCHITECTURE_DIR / "hardware" / "fpga" / "vivado" / "tcl"
    
    # Determine files to backup
    files_to_backup = []
    for tcl_file in tcl_files:
        dest_path = tcl_dest_dir / tcl_file.name
        if dest_path.exists():
            files_to_backup.append(dest_path)
    
    # Backup existing files if enabled
    if backup_enabled and files_to_backup:
        logger.log_event('DEBUG', debug_message=f"Backing up {len(files_to_backup)} existing TCL files...")
        backup_files(files_to_backup)
    
    # Copy TCL files
    copied_files = []
    for tcl_file in tcl_files:
        dest_path = tcl_dest_dir / tcl_file.name
        if copy_file_to_destination(tcl_file, dest_path):
            copied_files.append(dest_path)
    
    logger.log_event('DEBUG', debug_message=f"Allocated {len(copied_files)} TCL files")
    return copied_files


def allocate_static_files(hardware_map, software_map, backup_enabled=True):
    """
    Allocate static hardware and software files to architecture tree.
    
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
        
        for source_file in hardware_files:
            dest_path = get_destination_path(
                source_file,
                hardware_map,
                base_dir=cfg.ARCHITECTURE_DIR
            )
            
            if not dest_path:
                logger.log_event('WARNING', warning_message=f"No allocation mapping for hardware file: {source_file.name}")
                continue
            
            file_pairs.append((source_file, dest_path))
            if dest_path.exists():
                files_to_backup.append(dest_path)
        
        # Backup if needed
        if backup_enabled and files_to_backup:
            backup_files(files_to_backup)
        
        # Copy files
        for source_file, dest_path in file_pairs:
            if copy_file_to_destination(source_file, dest_path):
                copied_files.append(dest_path)
    
    # Allocate software files
    software_files = collect_static_software_files()
    if software_files:
        files_to_backup = []
        file_pairs = []
        
        for source_file in software_files:
            dest_path = get_destination_path(
                source_file,
                software_map,
                base_dir=cfg.ARCHITECTURE_DIR
            )
            
            if not dest_path:
                logger.log_event('WARNING', warning_message=f"No allocation mapping for software file: {source_file.name}")
                continue
            
            file_pairs.append((source_file, dest_path))
            if dest_path.exists():
                files_to_backup.append(dest_path)
        
        # Backup if needed
        if backup_enabled and files_to_backup:
            backup_files(files_to_backup)
        
        # Copy files
        for source_file, dest_path in file_pairs:
            if copy_file_to_destination(source_file, dest_path):
                copied_files.append(dest_path)
    
    logger.log_event('DEBUG', debug_message=f"Allocated {len(copied_files)} static files")
    return copied_files


def allocate_files(config, backup_enabled=True):
    """
    Main file allocation orchestrator.
    
    Allocates all generated and static files to the architecture tree
    following the location mappings defined in locations.yaml files.
    
    Workflow:
    1. Load allocation maps (gen_locations, hardware, software)
    2. Backup existing files that will be overwritten (if enabled)
    3. Copy generated files to destinations
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
    
    # Load allocation maps
    allocation_maps = load_allocation_maps()
    gen_map = allocation_maps['gen_locations']
    hardware_map = allocation_maps['hardware_locations']
    software_map = allocation_maps['software_locations']
    
    # Allocate files
    allocated_files = {
        'generated': [],
        'tcl': [],
        'static': []
    }
    
    # Allocate generated files
    logger.log_event('DEBUG', debug_message="Allocating generated files...")
    allocated_files['generated'] = allocate_generated_files(gen_map, backup_enabled)
    
    # Allocate TCL files
    logger.log_event('DEBUG', debug_message="Allocating TCL files...")
    allocated_files['tcl'] = allocate_tcl_files(backup_enabled)
    
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