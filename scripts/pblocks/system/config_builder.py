# =============================================================================
# FATORI-V • Pblock Generation • Config Builder
# File: config_builder.py
# -----------------------------------------------------------------------------
# Builds pblock_config.yaml for external pblock placement system.
# =============================================================================

from pathlib import Path
import yaml
import fatori_settings as cfg
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import (
    get_isa_extension_state,
    get_ftm_state,
    any_benchmark_has_fi,
)

def extract_targets_list(config):
    """
    Extract explicit targets list from fault injection modules configuration.
    
    When area_profile is 'modules', extracts enabled targets from FI configuration.
    
    Returns:
        list or None: List of uppercase target names with underscores, or None if auto-select
    """
    # Check if FI is enabled
    if not any_benchmark_has_fi(config):
        return None
    
    # Get area_profile from general.fault_injection
    fi_general_config = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    area_profile = fi_general_config.get("area_profile", "device")
    
    # Only extract targets list for 'modules' area profile
    if area_profile != "modules":
        return None  # Auto-select all
    
    # Get modules configuration
    modules_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FI, KEY_FI_AREA, "modules", default={})
    targets_dict = modules_config.get("targets", {})
    
    if not targets_dict:
        return None  # No explicit targets specified
    
    # Extract enabled targets only (targets where value is True or "on")
    targets = []
    for target_name, target_enabled in targets_dict.items():
        # Check if target is enabled
        if target_enabled is True or (isinstance(target_enabled, str) and target_enabled.lower() == "on"):
            # Convert to uppercase with underscores (e.g., "branch_predictor" -> "BRANCH_PREDICTOR")
            targets.append(target_name.upper().replace('-', '_'))
    
    return targets if targets else None

def extract_features_config(config):
    """
    Extract feature configuration in format expected by pblock system.
    
    All values read from config - no hardcoding.
    
    Returns dict with feature flags and their values:
    - FATORI_ICACHE: 0/1
    - FATORI_BRANCH_TARGET_ALU: 0/1
    - FATORI_BRANCH_PREDICTOR: 0/1
    - FATORI_WRITEBACK_STAGE: 0/1
    - FATORI_RV32B: "None"/"Balanced"/"Ot_earlgrey"/"Full"
    - FATORI_RV32M: "None"/"Slow"/"Fast"/"Single_cycle"
    - FATORI_FI: 0/1
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary of feature flags
    """
    features = {}
    
    # Get performance mechanisms from config
    icache_enable = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, KEY_PERF_ICACHE, default=False)
    branch_talu_enable = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, KEY_PERF_BRANCH_TALU, default=False)
    branch_pred_enable = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, KEY_PERF_BRANCH_PRED, default=False)
    wstage_enable = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, KEY_PERF_WSTAGE, default=False)
    
    # Performance mechanisms — use is_on() so string 'off' (truthy) is not
    # misread as enabled; is_on() is imported via common_settings star-import.
    features["FATORI_ICACHE"]      = 1 if is_on(icache_enable)      else 0
    features["FATORI_BRANCH_TALU"] = 1 if is_on(branch_talu_enable) else 0
    features["FATORI_BRANCH_PRED"] = 1 if is_on(branch_pred_enable) else 0
    features["FATORI_WSTAGE"]      = 1 if is_on(wstage_enable)      else 0

    # ISA extensions - only read type if extension is enabled
    # Check if RV32M extension is enabled
    rv32m_enabled = get_isa_extension_state(config, KEY_ISA_RV32M)
    if rv32m_enabled:
        multiplier_type = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_MULTIPLIER, default="none")
        features["FATORI_RV32M"] = multiplier_type.capitalize() if multiplier_type else "None"
    else:
        features["FATORI_RV32M"] = "None"

    # Check if RV32B extension is enabled
    rv32b_enabled = get_isa_extension_state(config, KEY_ISA_RV32B)
    if rv32b_enabled:
        bit_manip_type = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_BIT_MANIP, default="none")
        features["FATORI_RV32B"] = bit_manip_type.capitalize() if bit_manip_type else "None"
    else:
        features["FATORI_RV32B"] = "None"

    # Fault injection flag
    fi_enabled = any_benchmark_has_fi(config)
    features["FATORI_FI"] = 1 if is_on(fi_enabled) else 0

    # Fault manager enable
    fault_mgr_enable = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, "fault_manager", default=False)
    features["FATORI_FAULT_MGR"] = 1 if is_on(fault_mgr_enable) else 0
    
    # METRIC_LAYER decomposition
    metric_layer = get_nested(config, KEY_GENERAL, "metrics_level", default=0)
    
    if metric_layer == 0:
        features["FATORI_MHPMCOUNTER_NUM"] = 0
        features["FATORI_FT_LAYER_1"] = False
        features["FATORI_FT_LAYER_2"] = False
        features["FATORI_FT_LAYER_3"] = False
        features["FATORI_FT_LAYER_4"] = False
    elif metric_layer == 1:
        features["FATORI_MHPMCOUNTER_NUM"] = 10
        features["FATORI_FT_LAYER_1"] = False
        features["FATORI_FT_LAYER_2"] = False
        features["FATORI_FT_LAYER_3"] = False
        features["FATORI_FT_LAYER_4"] = False
    elif metric_layer == 2:
        features["FATORI_MHPMCOUNTER_NUM"] = 10
        features["FATORI_FT_LAYER_1"] = True
        features["FATORI_FT_LAYER_2"] = False
        features["FATORI_FT_LAYER_3"] = False
        features["FATORI_FT_LAYER_4"] = False
    elif metric_layer == 3:
        features["FATORI_MHPMCOUNTER_NUM"] = 10
        features["FATORI_FT_LAYER_1"] = True
        features["FATORI_FT_LAYER_2"] = True
        features["FATORI_FT_LAYER_3"] = False
        features["FATORI_FT_LAYER_4"] = False
    elif metric_layer == 4:
        features["FATORI_MHPMCOUNTER_NUM"] = 10
        features["FATORI_FT_LAYER_1"] = True
        features["FATORI_FT_LAYER_2"] = True
        features["FATORI_FT_LAYER_3"] = True
        features["FATORI_FT_LAYER_4"] = False
    else:  # metric_layer >= 5
        features["FATORI_MHPMCOUNTER_NUM"] = 10
        features["FATORI_FT_LAYER_1"] = True
        features["FATORI_FT_LAYER_2"] = True
        features["FATORI_FT_LAYER_3"] = True
        features["FATORI_FT_LAYER_4"] = True
    
    return features


def extract_mon_config(config):
    """
    Extract M-of-N redundancy configuration for logic FTM.
    
    Always returns config for ALL possible targets:
    - If logic_mon disabled: all targets get N=1, M=0
    - If logic_mon enabled: 
      - Active targets get N and M from config
      - Inactive targets get N=1, M=0
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary mapping module names to {MON_N: X, MON_M: Y}
    """
    mon_config = {}
    
    # Get all possible target names from pblock mapping
    from scripts.mapping.pblock_mapping import PBLOCK_TARGET_MACROS
    all_possible_targets = sorted(set(PBLOCK_TARGET_MACROS.keys()))
    
    # Check if logic M-of-N is enabled
    logic_mon_enabled = get_ftm_state(config, KEY_FTM_LOGIC_MON)
    
    if not logic_mon_enabled:
        # Logic M-of-N disabled: all targets get N=1, M=0
        for target in all_possible_targets:
            target_upper = target.upper().replace("-", "_")
            mon_config[target_upper] = {
                "MON_N": 1,
                "MON_M": 0
            }
        return mon_config
    
    # Logic M-of-N enabled: get configuration
    logic_mon_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_LOGIC_MON, default={})
    
    # Get default M and N
    default_n = logic_mon_config.get("n", cfg.DEFAULT_MON_N)
    default_m = logic_mon_config.get("m", cfg.DEFAULT_MON_M)
    
    # Calculate majority if M not specified or is None
    if default_m is None:
        default_m = (default_n // 2) + 1
    
    # Get target dictionary
    targets_config = logic_mon_config.get("target", {})
    
    # Process all possible targets
    for target in all_possible_targets:
        target_upper = target.upper().replace("-", "_")
        
        # Check if this target has config
        target_config = targets_config.get(target)
        
        if target_config is None:
            # Target not mentioned in config: use N=1, M=0 (inactive)
            mon_config[target_upper] = {"MON_N": 1, "MON_M": 0}
        elif isinstance(target_config, bool):
            if target_config:
                # Enabled with bool: use defaults
                mon_config[target_upper] = {"MON_N": default_n, "MON_M": default_m}
            else:
                # Disabled: use N=1, M=0
                mon_config[target_upper] = {"MON_N": 1, "MON_M": 0}
        elif isinstance(target_config, dict):
            if target_config.get("enable", True):
                # Enabled: read N and M from config
                target_n = target_config.get("n", default_n)
                target_m = target_config.get("m", default_m)
                if target_m is None:
                    target_m = (target_n // 2) + 1
                mon_config[target_upper] = {"MON_N": target_n, "MON_M": target_m}
            else:
                # Disabled: use N=1, M=0
                mon_config[target_upper] = {"MON_N": 1, "MON_M": 0}
        else:
            # Unknown config type: default to inactive
            mon_config[target_upper] = {"MON_N": 1, "MON_M": 0}
    
    return mon_config


def extract_reg_mon_config(config):
    """
    Extract register M-of-N N value per pblock target module.

    Returns {MODULE_NAME: N} where N >= 2 means register replication is active.
    For disabled modules, returns N=1 (no replication, no voter overhead).

    Args:
        config: The loaded YAML configuration dictionary

    Returns:
        Dictionary mapping pblock module names to their reg_mon N value
    """
    # RTL reg_mon target name -> pblock module name
    REG_MON_TARGET_MAP = {
        'load_store_unit':  'LSU',
        'controller':       'CONTROLLER',
        'decoder':          'DECODER',
        'if_stage':         'IF_STAGE',
        'id_stage':         'ID_STAGE',
        'prefetch_buffer':  'PREFETCH_BUFFER',
        'wb_stage':         'WB_STAGE',
    }

    # Start with N=1 for all modules (no voter overhead)
    reg_mon_n = {m: 1 for m in REG_MON_TARGET_MAP.values()}

    reg_mon_enabled = get_ftm_state(config, KEY_FTM_REG_MON)
    if not reg_mon_enabled:
        return reg_mon_n

    reg_mon_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_REG_MON, default={})
    global_n = reg_mon_config.get('m_of_n_N', 1)
    targets = reg_mon_config.get('target', {})

    for rtl_name, pblock_name in REG_MON_TARGET_MAP.items():
        target_val = targets.get(rtl_name)
        is_on = (target_val is True or
                 (isinstance(target_val, str) and target_val.lower() == 'on'))
        if is_on:
            reg_mon_n[pblock_name] = global_n

    return reg_mon_n


def build_pblock_config(config, output_path):
    """
    Build pblock_config.yaml for external pblock placement system.
    
    This config file contains:
    - features: Feature flags that affect module sizing
    - targets: List of targets (enabled uncommented, disabled commented)
    - mon_config: M-of-N redundancy configuration per module
    
    The external system uses this to calculate pblock sizes and generate
    placement constraints.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where pblock_config.yaml should be written
    
    Returns:
        Path to the generated config file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
   # Get configuration components
    features_config = extract_features_config(config)
    mon_config = extract_mon_config(config)
    reg_mon_n_config = extract_reg_mon_config(config)

    # Get area profile to determine target handling
    fi_general_config = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    area_profile = fi_general_config.get("area_profile", "device")
    
    # Get targets dict from specifics if area_profile is modules
    targets_dict = {}
    if area_profile == "modules" and any_benchmark_has_fi(config):
        modules_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", default={})
        targets_dict = modules_config.get("targets", {})
    
    # Write YAML file manually to support comments for disabled targets
    with output_path.open('w') as f:
        # Write features section
        f.write("features:\n")
        for key, value in features_config.items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")
        
       # Write targets section
        # Only write if there are enabled targets, otherwise omit to allow auto-select
        enabled_targets = []
        disabled_targets = []
        
        if targets_dict:
            # area_profile is modules - collect enabled/disabled targets
            for target_name, target_enabled in targets_dict.items():
                target_upper = target_name.upper().replace('-', '_')
                is_enabled = (target_enabled is True or 
                            (isinstance(target_enabled, str) and target_enabled.lower() == "on"))
                
                if is_enabled:
                    enabled_targets.append(target_upper)
                else:
                    disabled_targets.append(target_upper)
        
        if enabled_targets:
            # Write targets section with enabled targets
            f.write("targets:\n")
            for target in enabled_targets:
                f.write(f"  - {target}\n")
            # Write disabled as comments
            for target in disabled_targets:
                f.write(f"  # {target}\n")
            f.write("\n")
        else:
            # No enabled targets - omit targets section entirely
            # This allows pblock system's auto_select_targets to work
            # Write comment explaining why targets section is omitted
            f.write("# targets: (omitted - auto-select will determine targets based on features)\n\n")
        
        # Write logic_mon_config section (logic M-of-N wrapper per module)
        f.write("logic_mon_config:\n")
        if mon_config:
            for module, params in mon_config.items():
                f.write(f"  {module}:\n")
                for param, value in params.items():
                    f.write(f"    {param}: {value}\n")
        else:
            f.write("  {}\n")
        f.write("\n")

        # Write reg_mon_config section (register M-of-N, N per module for voter sizing)
        f.write("reg_mon_config:\n")
        for module, n_val in sorted(reg_mon_n_config.items()):
            f.write(f"  {module}: {n_val}\n")

    return output_path