# =============================================================================
# FATORI-V • Common Utilities • File Allocator
# File: file_allocator.py
# -----------------------------------------------------------------------------
# Loads file allocation maps from location YAML files.
# =============================================================================

from pathlib import Path
import yaml
import fatori_settings as cfg
from scripts.logging.logger import log_event


def load_yaml_allocation_file(file_path, description):
    """
    Load a YAML allocation file and return its contents.
    
    Args:
        file_path: Path to the YAML file
        description: Description of what this file contains (for logging)
    
    Returns:
        Dictionary with allocation mappings, or empty dict if file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        log_event('ALLOCATION_FILE_NOT_FOUND',
                  description=description,
                  file_path=str(file_path))
        return {}
    
    try:
        with file_path.open('r') as f:
            data = yaml.safe_load(f)
            
            if not data or not isinstance(data, dict):
                log_event('ALLOCATION_FILE_INVALID', description=description)
                return {}
            
            log_event('ALLOCATION_FILE_LOADED',
                      description=description,
                      mapping_count=len(data))
            return data
    
    except Exception as e:
        log_event('ALLOCATION_FILE_ERROR',
                  description=description,
                  error_message=str(e))
        return {}


def load_allocation_maps():
    """
    Load all file allocation maps from location YAML files.
    
    These files specify where generated/static files should be copied
    within the architecture directory structure.
    
    The gen_locations.yaml file can contain an 'exclude' section listing
    intermediate files that should be skipped without warnings.
    
    Returns:
        Dictionary with allocation maps and exclude list:
        {
            'gen_locations': {source: destination, ...},
            'hardware_locations': {source: destination, ...},
            'software_locations': {source: destination, ...},
            'exclude_list': [list of filenames to skip]
        }
    """
    log_event('ALLOCATION_MAPS_LOADING')
    
    allocation_maps = {}

    # Add import at top of file after other imports
    from scripts.common.paths import (
        get_gen_locations_yaml,
        get_hardware_locations_yaml,
        get_software_locations_yaml
    )
    
    # Load generated files allocation map
    gen_locations_path = get_gen_locations_yaml()
    gen_locations_data = load_yaml_allocation_file(
        gen_locations_path,
        "gen_locations.yaml (generated files)"
    )
    
    # Extract exclude list if present
    exclude_list = []
    if isinstance(gen_locations_data, dict):
        # Check for 'exclude' section
        if 'exclude' in gen_locations_data:
            exclude_section = gen_locations_data['exclude']
            # Exclude section can be a list or a dict with a list
            if isinstance(exclude_section, list):
                exclude_list = exclude_section
            elif isinstance(exclude_section, dict) and 'files' in exclude_section:
                exclude_list = exclude_section['files']
            
            # Remove exclude section from gen_locations to get clean mapping
            gen_locations_clean = {k: v for k, v in gen_locations_data.items() if k != 'exclude'}
            allocation_maps['gen_locations'] = gen_locations_clean
            
            log_event('ALLOCATION_EXCLUDE_LIST_LOADED', exclude_count=len(exclude_list))
        else:
            allocation_maps['gen_locations'] = gen_locations_data
    else:
        allocation_maps['gen_locations'] = gen_locations_data
    
    allocation_maps['exclude_list'] = exclude_list
    
    # Load hardware files allocation map
    hardware_locations_path = get_hardware_locations_yaml()
    allocation_maps['hardware_locations'] = load_yaml_allocation_file(
        hardware_locations_path,
        "hardware/locations.yaml"
    )
    
    # Load software files allocation map
    software_locations_path = get_software_locations_yaml()
    allocation_maps['software_locations'] = load_yaml_allocation_file(
        software_locations_path,
        "software/locations.yaml"
    )
    
    # Count total mappings
    total_mappings = sum(len(m) for m in allocation_maps.values() if isinstance(m, dict))
    log_event('ALLOCATION_MAPS_LOADED', total_mappings=total_mappings)
    
    return allocation_maps


def get_destination_path(source_file, allocation_map, base_dir=None):
    """
    Get the destination path for a source file using an allocation map.
    
    Args:
        source_file: Source file name or path
        allocation_map: Dictionary mapping source -> destination
        base_dir: Optional base directory to prepend to destination
    
    Returns:
        Path object for destination, or None if not in map
    """
    source_file = Path(source_file)
    source_name = source_file.name
    
    # Look up in allocation map
    destination = allocation_map.get(source_name)
    
    if not destination:
        return None
    
    # Convert to Path
    dest_path = Path(destination)
    
    # Prepend base directory if provided
    if base_dir:
        dest_path = Path(base_dir) / dest_path
    
    return dest_path