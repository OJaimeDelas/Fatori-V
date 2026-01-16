# =============================================================================
# FATORI-V • Mappings • Feature Mapping
# File: feature_mapping.py
# -----------------------------------------------------------------------------
# Maps YAML feature and FTM keys to SystemVerilog macro names.
# =============================================================================

import fatori_settings as cfg
from config.constants import MACRO_PREFIX
from scripts.common.common_settings import (
    KEY_FEAT_FAULT_MANAGER,
    KEY_FTM_REG_MON,
    KEY_FTM_LOGIC_MON,
    KEY_FTM_SELFTEST,
    KEY_FTM_RF_ECC,
    KEY_FTM_RF_WE_GLITCH,
    KEY_FTM_RF_RADDR_GLITCH,
    KEY_FTM_HARDENED_PC,
)

# Feature macro names (features that are not FTMs)
FEATURE_MACROS = {
    KEY_FEAT_FAULT_MANAGER: f"{MACRO_PREFIX}FAULT_MANAGER",
}

# FTM macro names - these get defined when FTMs are enabled
FTM_MACROS = {
    KEY_FTM_REG_MON: f"{MACRO_PREFIX}FTM_REG_MON",
    KEY_FTM_LOGIC_MON: f"{MACRO_PREFIX}FTM_LOGIC_MON",
    KEY_FTM_SELFTEST: f"{MACRO_PREFIX}FTM_SELFTEST",
    KEY_FTM_RF_ECC: f"{MACRO_PREFIX}FTM_RF_ECC",
    KEY_FTM_RF_WE_GLITCH: f"{MACRO_PREFIX}FTM_RF_WE_GLITCH",
    KEY_FTM_RF_RADDR_GLITCH: f"{MACRO_PREFIX}FTM_RF_RADDR_GLITCH",
    KEY_FTM_HARDENED_PC: f"{MACRO_PREFIX}FTM_HARDENED_PC",
}

# Fault tolerance layer macros for metrics
# Layer 0: Basic cycle/instruction counters
# Layer 1-5: Progressively more detailed FT metrics
FT_LAYER_MACROS = {
    0: f"{MACRO_PREFIX}METRICS_LAYER_0",
    1: f"{MACRO_PREFIX}METRICS_LAYER_1",
    2: f"{MACRO_PREFIX}METRICS_LAYER_2",
    3: f"{MACRO_PREFIX}METRICS_LAYER_3",
    4: f"{MACRO_PREFIX}METRICS_LAYER_4",
    5: f"{MACRO_PREFIX}METRICS_LAYER_5",
}


def get_feature_macro_name(feature_key):
    """
    Get the macro name for a feature.
    
    Args:
        feature_key: Feature key from common_settings (e.g., KEY_FEAT_FAULT_MANAGER)
    
    Returns:
        String containing the macro name (e.g., "FATORI_FAULT_MANAGER")
    
    Raises:
        ValueError: If feature key is not recognized
    """
    if feature_key not in FEATURE_MACROS:
        raise ValueError(f"Unknown feature key: {feature_key}")
    
    return FEATURE_MACROS[feature_key]


def get_ftm_macro_name(ftm_key):
    """
    Get the macro name for a fault tolerance mechanism.
    
    Args:
        ftm_key: FTM key from common_settings (e.g., KEY_FTM_REG_MON)
    
    Returns:
        String containing the macro name (e.g., "FATORI_FTM_REG_MON")
    
    Raises:
        ValueError: If FTM key is not recognized
    """
    if ftm_key not in FTM_MACROS:
        raise ValueError(f"Unknown FTM key: {ftm_key}")
    
    return FTM_MACROS[ftm_key]


def get_ft_layer_macro(layer):
    """
    Get the macro name for a fault tolerance metrics layer.
    
    Layers range from 0 (basic) to 5 (comprehensive):
    - Layer 0: Just cycle and instruction counters
    - Layer 1+: Progressively more detailed FT monitoring
    
    Args:
        layer: Integer layer number (0-5)
    
    Returns:
        String containing the macro name for that layer
    
    Raises:
        ValueError: If layer is out of range
    """
    if layer not in FT_LAYER_MACROS:
        raise ValueError(f"Invalid metrics layer: {layer}. Must be 0-5.")
    
    return FT_LAYER_MACROS[layer]


def get_all_ftm_keys():
    """
    Get list of all FTM keys.
    
    Returns:
        List of FTM key strings
    """
    return list(FTM_MACROS.keys())


def get_all_ftm_macros():
    """
    Get list of all FTM macro names.
    
    Returns:
        List of FTM macro name strings
    """
    return list(FTM_MACROS.values())