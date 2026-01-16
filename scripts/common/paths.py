# =============================================================================
# FATORI-V • Common • Path Helpers
# File: paths.py
# -----------------------------------------------------------------------------
# Helper functions for getting paths to input files and directories.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg


def get_fatori_registers_yaml() -> Path:
    """
    Get path to fatori_registers.yaml.
    
    Returns:
        Path to fatori_registers.yaml
    """
    return cfg.INPUTS_OTHER_DIR / cfg.FATORI_REGISTERS_YAML_NAME


def get_system_dict_yaml() -> Path:
    """
    Get path to system_dict.yaml.
    
    Returns:
        Path to system_dict.yaml
    """
    return cfg.INPUTS_OTHER_DIR / cfg.SYSTEM_DICT_YAML_NAME


def get_system_hierarchy_yaml() -> Path:
    """
    Get path to system_hierarchy.yaml.
    
    Returns:
        Path to system_hierarchy.yaml
    """
    return cfg.INPUTS_OTHER_DIR / cfg.SYSTEM_HIERARCHY_YAML_NAME


def get_gen_locations_yaml() -> Path:
    """
    Get path to gen_locations.yaml.
    
    Returns:
        Path to gen_locations.yaml
    """
    return cfg.INPUTS_OTHER_DIR / cfg.GEN_LOCATIONS_YAML_NAME


def get_hardware_locations_yaml() -> Path:
    """
    Get path to hardware locations.yaml.
    
    Returns:
        Path to hardware locations.yaml
    """
    return cfg.INPUTS_HARDWARE_DIR / cfg.HARDWARE_LOCATIONS_YAML


def get_software_locations_yaml() -> Path:
    """
    Get path to software locations.yaml.
    
    Returns:
        Path to software locations.yaml
    """
    return cfg.INPUTS_SOFTWARE_DIR / cfg.SOFTWARE_LOCATIONS_YAML


def get_reports_dir(builddir: Path) -> Path:
    """
    Get path to reports directory within builddir.
    
    Args:
        builddir: Path to build directory
    
    Returns:
        Path to reports directory
    """
    return builddir / cfg.REPORTS_DIR_RELATIVE


def get_sync_file_path(builddir: Path) -> Path:
    """
    Get path to sync file within builddir.
    
    Args:
        builddir: Path to build directory
    
    Returns:
        Path to sync file
    """
    return builddir / cfg.SYNC_FILE_RELATIVE_PATH


def get_vivado_parser_script() -> Path:
    """
    Get path to Vivado parser script.
    
    Returns:
        Path to vivado_report_system.py
    """
    return cfg.VIVADO_PARSER_SCRIPT