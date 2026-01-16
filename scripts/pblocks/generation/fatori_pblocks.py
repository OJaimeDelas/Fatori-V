# =============================================================================
# FATORI-V • Pblock Generation • Pblocks SVH
# File: fatori_pblocks.py
# -----------------------------------------------------------------------------
# Generates fatori_pblocks.svh with KEEP hierarchy macros for FI targeting.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import FATORI_PBLOCKS_SVH
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import (
    get_isa_extension_state,
    any_benchmark_has_fi,
)
from scripts.mapping.pblock_mapping import (
    get_all_targets,
    get_pblock_macro_name,
)
from scripts.common.svh_writer.svh_writer import write_svh_file


def is_target_enabled_by_features(config, target):
    """
    Check if a target module exists based on feature configuration.
    
    Some modules are conditional on features like RV32M or icache.
    
    Args:
        config: The loaded YAML configuration dictionary
        target: Target module name (e.g., "multiplier")
    
    Returns:
        Boolean indicating if target can exist with current features
    """
    target_lower = target.lower()
    
    # Multiplier only exists if RV32M is enabled
    if target_lower in ["multiplier", "mult"]:
        return get_isa_extension_state(config, KEY_ISA_RV32M)
    
    # Most targets always exist
    return True


def get_fi_enabled_targets(config):
    """
    Get list of pblock targets enabled for fault injection.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Set of target names that should have KEEP macros enabled
    """
    # Check if FI is enabled at all
    fi_enabled = any_benchmark_has_fi(config)
    if not fi_enabled:
        return set()
    
    # Get FI area configuration
    fi_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FI, KEY_FI_AREA, default={})
    area_profile = fi_config.get("area_profile", "device")
    
    enabled_targets = set()
    
    if area_profile == "device":
        # Device profile: Enable all available targets
        all_targets = get_all_targets()
        for target in all_targets:
            # Check if target exists based on features
            if is_target_enabled_by_features(config, target):
                enabled_targets.add(target.lower())
    
    elif area_profile == "modules":
        # Modules profile: Only enable specified targets
        modules_config = fi_config.get("modules", {})
        target_list = modules_config.get("targets", [])
        
        for target in target_list:
            # Verify target exists with current features
            if is_target_enabled_by_features(config, target):
                enabled_targets.add(target.lower())
    
    # For other profiles (address_list, target_list), we still enable all targets
    # as the targeting is done at runtime, not synthesis time
    elif area_profile in ["address_list", "target_list"]:
        all_targets = get_all_targets()
        for target in all_targets:
            if is_target_enabled_by_features(config, target):
                enabled_targets.add(target.lower())
    
    return enabled_targets


def generate_pblocks_svh(config, output_dir):
    """
    Generate fatori_pblocks.svh header file with KEEP hierarchy macros.
    
    Uses simple format with direct `define statements.
    Macro names come from pblock_mapping (e.g., KEEP_ALU, not FATORI_KEEP_ALU).
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where the file should be written
    
    Returns:
        Path to the generated file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = FATORI_PBLOCKS_SVH
    output_path = output_dir / file_name
    
    lines = []
    
    # Get enabled targets
    enabled_targets = get_fi_enabled_targets(config)
    
    # Get all possible targets
    all_targets = get_all_targets()
    
    # Generate KEEP macros for each target
    # Track which macros we've already generated (to handle aliases)
    generated_macros = set()
    
    for target in sorted(all_targets):
        target_lower = target.lower()
        
        # Skip if target doesn't exist with current features
        if not is_target_enabled_by_features(config, target):
            continue
        
        # Get macro name from centralized mapping
        macro_name = get_pblock_macro_name(target)
        
        # Skip if we've already generated this macro (handles aliases like mult/multiplier)
        if macro_name in generated_macros:
            continue
        generated_macros.add(macro_name)
        
        # Check if enabled
        is_enabled = target_lower in enabled_targets
        
        if is_enabled:
            # Enabled: Full keep_hierarchy attribute
            lines.append(f'`define {macro_name} (* keep_hierarchy = "true" *)')
        else:
            # Disabled: Empty define
            lines.append(f'`define {macro_name}')
    
    # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Pblock KEEP hierarchy macros for fault injection",
        content=lines,
        area="Pblocks"
    )