# =============================================================================
# FATORI-V • Feature Generation • Override Handler
# File: override_handler.py
# -----------------------------------------------------------------------------
# Handles user-provided override files for generated SVH headers.
# =============================================================================

from pathlib import Path
import shutil
from scripts.common.common_settings import KEY_GENERAL
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.logging.logger import log_event


def get_override_path(config, svh_filename: str):
    """
    Get override file path for a specific SVH file from config.
    
    Args:
        config: The loaded YAML configuration dictionary
        svh_filename: Name of SVH file (e.g., 'fatori_features.svh')
    
    Returns:
        Path object if override specified and not null, None otherwise
    """
    overrides = get_nested(config, KEY_GENERAL, "overrides", default={})
    override_value = overrides.get(svh_filename)
    
    if override_value is None or override_value == 'null':
        return None
    
    return Path(override_value)


def apply_override(config, svh_filename: str, output_dir: Path) -> Path:
    """
    Apply user override for an SVH file by copying from specified path.
    
    If override path is specified and file exists, copies it to output_dir
    with the correct name. Otherwise returns None and generation proceeds normally.
    
    Args:
        config: The loaded YAML configuration dictionary
        svh_filename: Name of SVH file (e.g., 'fatori_features.svh')
        output_dir: Directory where file should be written
    
    Returns:
        Path to copied file if override applied, None if no override or file not found
    """
    override_path = get_override_path(config, svh_filename)
    
    if override_path is None:
        # No override specified
        return None
    
    if not override_path.exists():
        # Override path specified but file not found
        log_event('OVERRIDE_FILE_NOT_FOUND', 
                 svh_file=svh_filename, 
                 override_path=str(override_path))
        return None
    
    # Copy override file to output directory with correct name
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dest_path = output_dir / svh_filename
    
    try:
        shutil.copy2(override_path, dest_path)
        log_event('OVERRIDE_APPLIED', 
                 svh_file=svh_filename, 
                 source=str(override_path),
                 dest=str(dest_path))
        return dest_path
    except Exception as e:
        log_event('OVERRIDE_COPY_FAILED',
                 svh_file=svh_filename,
                 error=str(e))
        return None