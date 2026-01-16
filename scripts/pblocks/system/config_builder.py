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


def extract_features_config(config):
    """
    Extract feature configuration in format expected by pblock system.
    
    Returns dict with feature flags and their values:
    - FATORI_ICACHE: 0/1
    - FATORI_BRANCH_TALU: 0/1
    - FATORI_BRANCH_PRED: 0/1
    - FATORI_WSTAGE: 0/1
    - FATORI_RV32B: "none"/"balanced"/"ot_earlgrey"/"full"
    - FATORI_RV32M: "none"/"slow"/"fast"/"single_cycle"
    - FATORI_FI: 0/1
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary of feature flags
    """
    features = {}
    
    # Get Ibex configuration
    icache_enable = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_ICACHE, default=False)
    multiplier_type = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_MULTIPLIER, default="none")
    bit_manip_type = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_BIT_MANIP, default="none")
    
    # Ibex features (most are hardcoded to 1 for our configuration)
    features["FATORI_ICACHE"] = 1 if icache_enable else 0
    features["FATORI_BRANCH_TARGET_ALU"] = 1  # Always enabled
    features["FATORI_BRANCH_PREDICTOR"] = 1  # Always enabled
    features["FATORI_WRITEBACK_STAGE"] = 1  # Always enabled
    
    # ISA configuration with actual values - capitalize for external pblock system
    # External system expects: None, Fast, Slow, Balanced, etc.
    features["FATORI_RV32B"] = bit_manip_type.capitalize() if bit_manip_type else "None"
    features["FATORI_RV32M"] = multiplier_type.capitalize() if multiplier_type else "None"
    
    # Fault injection flag
    fi_enabled = any_benchmark_has_fi(config)
    features["FATORI_FI"] = 1 if fi_enabled else 0
    
    return features


def extract_mon_config(config):
    """
    Extract M-of-N redundancy configuration for logic FTM.
    
    Returns dict mapping module names to their MON_N and MON_M values.
    This is used by the pblock system to calculate sizing.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary mapping module names to {MON_N: X, MON_M: Y}
    """
    mon_config = {}
    
    # Check if logic M-of-N is enabled
    logic_mon_enabled = get_ftm_state(config, KEY_FTM_LOGIC_MON)
    
    if not logic_mon_enabled:
        return mon_config
    
    # Get logic M-of-N configuration
    logic_mon_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_LOGIC_MON, default={})
    
    # Get default M and N
    default_n = logic_mon_config.get("n", cfg.DEFAULT_MON_N)
    default_m = logic_mon_config.get("m", cfg.DEFAULT_MON_M)
    
    # Calculate majority if M not specified
    if default_m is None:
        default_m = (default_n // 2) + 1
    
    # Get target dictionary
    targets = logic_mon_config.get("target", {})
    
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
        
        # Add to mon_config with uppercase name
        target_upper = target_name.upper().replace("-", "_")
        mon_config[target_upper] = {
            "MON_N": target_n,
            "MON_M": target_m
        }
    
    return mon_config


def build_pblock_config(config, output_path):
    """
    Build pblock_config.yaml for external pblock placement system.
    
    This config file contains:
    - features: Feature flags that affect module sizing
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
    
    # Build the configuration dictionary
    pblock_config = {
        "features": extract_features_config(config),
        "mon_config": extract_mon_config(config)
    }
    
    # Write to YAML file
    with output_path.open('w') as f:
        yaml.dump(pblock_config, f, default_flow_style=False, sort_keys=False)
    
    return output_path