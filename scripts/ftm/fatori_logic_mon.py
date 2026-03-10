# =============================================================================
# FATORI-V • FTM Generation • Logic M-of-N Header
# File: fatori_logic_mon.py
# -----------------------------------------------------------------------------
# Generates fatori_logic_mon.svh with logic M-of-N redundancy configuration.
# =============================================================================

from pathlib import Path
import yaml
import fatori_settings as cfg
from config.constants import FATORI_LOGIC_MON_SVH
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_ftm_state
from scripts.common.svh_writer.svh_writer import write_svh_file
from scripts.logging.logger import log_event


def load_system_hierarchy():
    """
    Load the system hierarchy YAML file.
    
    Returns:
        Dictionary with hierarchy information, or empty dict if file not found
    """
    # Add import at top of file after other imports
    from scripts.common.paths import get_system_hierarchy_yaml

    # Then in the code, replace:
    hierarchy_file = get_system_hierarchy_yaml()
    
    if not hierarchy_file.exists():
        return {}
    
    with hierarchy_file.open('r') as f:
        return yaml.safe_load(f) or {}


def get_child_modules(hierarchy, parent_module):
    """
    Get list of child modules for a given parent module.
    
    Args:
        hierarchy: System hierarchy dictionary
        parent_module: Name of the parent module
    
    Returns:
        List of child module names
    """
    if not hierarchy:
        return []
    
    parent_entry = hierarchy.get(parent_module, {})
    return parent_entry.get("children", [])


def generate_logic_mon_header(config, output_dir):
    """
    Generate fatori_logic_mon.svh header file with logic M-of-N configuration.
    
    Uses <MODULE>_MON_N, <MODULE>_MON_M, <MODULE>_MON_HOLD format.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where the file should be written
    
    Returns:
        Path to the generated file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = FATORI_LOGIC_MON_SVH
    output_path = output_dir / file_name
    
    lines = []
    
    # Define standard logic modules that should always have macros
    standard_modules = ['alu', 'lsu', 'decoder', 'controller', 'ifstage', 'multdiv']
    
    # Mapping from YAML target names to macro names
    target_to_macro = {
        'load_store_unit': 'LSU',
        'if_stage': 'IFSTAGE',
        'multiplier': 'MULTDIV',
        'controller': 'CONTROLLER',
        'decoder': 'DECODER',
        'alu': 'ALU'
    }
    
    # Reverse mapping: YAML target names to standard module names
    target_to_standard = {
        'load_store_unit': 'lsu',
        'if_stage': 'ifstage',
        'multiplier': 'multdiv',
        'controller': 'controller',
        'decoder': 'decoder',
        'alu': 'alu'
    }
    
    # Check if logic M-of-N is enabled
    logic_mon_enabled = get_ftm_state(config, KEY_FTM_LOGIC_MON)
    
    if not logic_mon_enabled:
        # Output all standard modules with N=1, M=0
        for module_name in standard_modules:
            module_upper = module_name.upper()
            lines.append("")
            lines.append(f"`define {module_upper}_MON_N 1")
            lines.append(f"`define {module_upper}_MON_M 0")
            lines.append(f"`define {module_upper}_MON_HOLD 0")
    else:
        # Get logic M-of-N configuration
        logic_mon_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_LOGIC_MON, default={})
        
        # Get default M and N - use correct keys from YAML
        default_n = logic_mon_config.get("m_of_n_N", cfg.DEFAULT_MON_N)
        default_m = logic_mon_config.get("m_of_n_M", cfg.DEFAULT_MON_M)
        
        # Calculate majority if M not specified
        if default_m is None:
            default_m = (default_n // 2) + 1
        
        hold_on_major = logic_mon_config.get("hold_on_major", False)
        hold_val = 1 if hold_on_major else 0
        block_recursive = logic_mon_config.get("block_recursive", False)
        
        # Get target dictionary
        targets = logic_mon_config.get("target", {})
        
        # Track which standard modules have been configured
        configured_modules = set()
        
        if targets:
            # Load hierarchy if block_recursive is enabled
            hierarchy = {}
            if block_recursive:
                hierarchy = load_system_hierarchy()
            
            # Process each target module
            for target_name, target_config in targets.items():
                # Determine if this target is enabled
                if isinstance(target_config, bool):
                    if not target_config:
                        continue  # Skip disabled
                    target_n = default_n
                    target_m = default_m
                elif isinstance(target_config, dict):
                    if not target_config.get("enable", True):
                        continue
                    target_n = target_config.get("n", default_n)
                    target_m = target_config.get("m", default_m)
                    if target_m is None:
                        target_m = (target_n // 2) + 1
                else:
                    continue
                
                # Map target name to macro name
                macro_name = target_to_macro.get(target_name, target_name.upper().replace("-", "_"))
                
                # Track the standard module name to avoid duplicates
                standard_name = target_to_standard.get(target_name, target_name.lower())
                configured_modules.add(standard_name)
                
                lines.append("")
                lines.append(f"`define {macro_name}_MON_N {target_n}")
                lines.append(f"`define {macro_name}_MON_M {target_m}")
                lines.append(f"`define {macro_name}_MON_HOLD {hold_val}")
                    
                # Handle block_recursive: children get N=1
                if block_recursive and hierarchy:
                    children = get_child_modules(hierarchy, target_name)
                    
                    for child_name in children:
                        child_upper = child_name.upper().replace("-", "_")
                        configured_modules.add(child_name.lower())
                        
                        lines.append("")
                        lines.append(f"`define {child_upper}_MON_N 1")
                        lines.append(f"`define {child_upper}_MON_M 0")
                        lines.append(f"`define {child_upper}_MON_HOLD {hold_val}")
            
            # Add standard modules that weren't configured with N=1, M=0
            for module_name in standard_modules:
                if module_name not in configured_modules:
                    module_upper = module_name.upper()
                    lines.append("")
                    lines.append(f"`define {module_upper}_MON_N 1")
                    lines.append(f"`define {module_upper}_MON_M 0")
                    lines.append(f"`define {module_upper}_MON_HOLD 0")
    
    # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Logic M-of-N redundancy configuration",
        content=lines,
        area="FTM"
    )