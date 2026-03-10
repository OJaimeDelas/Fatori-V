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
    
    # Get area_profile from general.fault_injection
    fi_general_config = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    area_profile = fi_general_config.get("area_profile", "device")
    
    # Get detailed FI area configuration from specifics
    fi_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, KEY_FI_AREA, default={})
    
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
        targets_dict = modules_config.get("targets", {})
        
        # targets is a dictionary: {target_name: True/False or "on"/"off"}
        for target_name, target_enabled in targets_dict.items():
            # Check if target is enabled
            if target_enabled is True or (isinstance(target_enabled, str) and target_enabled.lower() == "on"):
                # Verify target exists with current features
                if is_target_enabled_by_features(config, target_name):
                    enabled_targets.add(target_name.lower())
    
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
    
    Always generates exactly 11 macros in fixed order:
    - KEEP_ALU
    - KEEP_BRANCH_PREDICT
    - KEEP_CONTROLLER
    - KEEP_DECODER
    - KEEP_FAULT_MGR
    - KEEP_ID_STAGE
    - KEEP_IF_STAGE
    - KEEP_LSU
    - KEEP_MULTIPLIER
    - KEEP_PREFETCH_BUFFER
    - KEEP_WB_STAGE
    
    Macros are active (keep_hierarchy="true") only if:
    1. FI is enabled (general.fault_injection.enable=on)
    2. Area profile is "modules" (general.fault_injection.area_profile=modules)
    3. Target is enabled in config (specifics.fault_tolerance.fault_injection.area.modules.targets.<target>=on)
    
    Otherwise macros are inactive (empty with trailing spaces).
    
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
    
    # Define the 11 required macros in fixed order
    REQUIRED_MACROS = [
        'KEEP_ALU',
        'KEEP_BRANCH_PREDICT',
        'KEEP_CONTROLLER',
        'KEEP_DECODER',
        'KEEP_FAULT_MGR',
        'KEEP_ID_STAGE',
        'KEEP_IF_STAGE',
        'KEEP_LSU',
        'KEEP_MULTIPLIER',
        'KEEP_PREFETCH_BUFFER',
        'KEEP_WB_STAGE',
    ]
    
    # Map macro names back to config target names
    MACRO_TO_TARGET = {
        'KEEP_ALU': 'alu',
        'KEEP_BRANCH_PREDICT': 'branch_predictor',  # Primary name
        'KEEP_CONTROLLER': 'controller',
        'KEEP_DECODER': 'decoder',
        'KEEP_FAULT_MGR': 'fault_manager',  # Primary name
        'KEEP_ID_STAGE': 'id_stage',
        'KEEP_IF_STAGE': 'if_stage',
        'KEEP_LSU': 'lsu',
        'KEEP_MULTIPLIER': 'multiplier',
        'KEEP_PREFETCH_BUFFER': 'prefetch_buffer',
        'KEEP_WB_STAGE': 'wb_stage',
    }
    
    # Check if FI is enabled
    from scripts.common.yaml_io.yaml_helpers import any_benchmark_has_fi
    fi_enabled = any_benchmark_has_fi(config)
    
    # Check area profile
    fi_general_config = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    area_profile = fi_general_config.get("area_profile", "device")
    
    # Determine if any macros should be active
    macros_can_be_active = fi_enabled and area_profile == "modules"
    
    # Get enabled targets from config
    enabled_targets = set()
    if macros_can_be_active:
        targets_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", default={})
        for target_name, target_value in targets_config.items():
            # Check if target is enabled (handle both boolean and string "on"/"off")
            if target_value is True or (isinstance(target_value, str) and target_value.lower() == "on"):
                enabled_targets.add(target_name.lower())
    
    # Generate all 11 macros in order
    for macro_name in REQUIRED_MACROS:
        # Get the canonical target name for this macro
        target_name = MACRO_TO_TARGET[macro_name]
        
        # Check if this target is enabled
        # Also check aliases (branch_pred, fault_mgr)
        is_enabled = (
            target_name in enabled_targets or
            (target_name == 'branch_predictor' and 'branch_pred' in enabled_targets) or
            (target_name == 'fault_manager' and 'fault_mgr' in enabled_targets)
        ) and macros_can_be_active
        
        if is_enabled:
            # Active: Full keep_hierarchy attribute
            lines.append(f'`define {macro_name} (* keep_hierarchy = "true" *)')
        else:
            # Inactive: Empty define with trailing spaces
            lines.append(f'`define {macro_name}  ')
    
    # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Pblock KEEP hierarchy macros for fault injection",
        content=lines,
        area="Pblocks"
    )