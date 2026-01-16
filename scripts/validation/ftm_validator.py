# =============================================================================
# FATORI-V • FTM Validator
# File: ftm_validator.py
# -----------------------------------------------------------------------------
# Validates fault tolerance mechanism configurations.
# =============================================================================

from scripts.common.common_settings import *
from scripts.validation.validation_settings import *


def validate_ftm_consistency(config):
    """
    Validate consistency between FTM flags and fault manager configuration.
    
    Rules:
    - If any FTM is enabled, fault_manager should be enabled (warning)
    - If fault_manager is disabled with FTMs enabled, warn user
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    # Check if fault manager is enabled
    fault_mgr_on = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FAULT_MANAGER, default=False)
    
    # Check if any FTM is enabled
    ftms = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, default={})
    any_ftm_enabled = any([
        ftms.get(KEY_FTM_REG_MON, False),
        ftms.get(KEY_FTM_LOGIC_MON, False),
        ftms.get(KEY_FTM_SELFTEST, False),
        ftms.get(KEY_FTM_RF_ECC, False),
        ftms.get(KEY_FTM_RF_WE_GLITCH, False),
        ftms.get(KEY_FTM_RF_RADDR_GLITCH, False),
        ftms.get(KEY_FTM_HARDENED_PC, False)
    ])
    
    # Warn if FTMs enabled without fault manager
    if any_ftm_enabled and not fault_mgr_on:
        add_warning(result, "One or more FTMs are enabled but fault_manager is disabled. The fault manager coordinates error handling.")
    
    return result


def validate_mon_parameters(config):
    """
    Validate M-of-N redundancy parameters.
    
    Rules:
    - N must be between MON_N_MIN and MON_N_MAX
    - M must be between MON_M_MIN and N
    - M < N (majority voting requires M to be less than N)
    - Percentage must be between 0 and 100
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    # Validate register M-of-N parameters
    reg_mon_enabled = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_REG_MON, default=False)
    if reg_mon_enabled:
        reg_mon_spec = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_REG_MON, default={})
        
        n = reg_mon_spec.get("n")
        m = reg_mon_spec.get("m")
        percentage = reg_mon_spec.get("percentage")
        
        # Validate N
        if n is not None:
            if not isinstance(n, int):
                add_error(result, f"Register M-of-N parameter 'n' must be an integer")
            elif n < MON_N_MIN or n > MON_N_MAX:
                add_error(result, f"Register M-of-N parameter 'n' must be between {MON_N_MIN} and {MON_N_MAX}")
        
        # Validate M
        if m is not None:
            if not isinstance(m, int):
                add_error(result, f"Register M-of-N parameter 'm' must be an integer")
            elif m < MON_M_MIN:
                add_error(result, f"Register M-of-N parameter 'm' must be at least {MON_M_MIN}")
            elif n is not None and m >= n:
                add_error(result, f"Register M-of-N parameter 'm' must be less than 'n' for majority voting")
        
        # Validate percentage
        if percentage is not None:
            if not isinstance(percentage, (int, float)):
                add_error(result, f"Register M-of-N parameter 'percentage' must be a number")
            elif percentage < PERCENTAGE_MIN or percentage > PERCENTAGE_MAX:
                add_error(result, f"Register M-of-N parameter 'percentage' must be between {PERCENTAGE_MIN} and {PERCENTAGE_MAX}")
    
    # Validate logic M-of-N parameters
    logic_mon_enabled = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_LOGIC_MON, default=False)
    if logic_mon_enabled:
        logic_mon_spec = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_LOGIC_MON, default={})
        
        # Logic M-of-N can have per-module configurations
        for module_name, module_config in logic_mon_spec.items():
            if isinstance(module_config, dict):
                n = module_config.get("n")
                m = module_config.get("m")
                
                # Validate N for this module
                if n is not None:
                    if not isinstance(n, int):
                        add_error(result, f"Logic M-of-N module '{module_name}' parameter 'n' must be an integer")
                    elif n < MON_N_MIN or n > MON_N_MAX:
                        add_error(result, f"Logic M-of-N module '{module_name}' parameter 'n' must be between {MON_N_MIN} and {MON_N_MAX}")
                
                # Validate M for this module
                if m is not None:
                    if not isinstance(m, int):
                        add_error(result, f"Logic M-of-N module '{module_name}' parameter 'm' must be an integer")
                    elif m < MON_M_MIN:
                        add_error(result, f"Logic M-of-N module '{module_name}' parameter 'm' must be at least {MON_M_MIN}")
                    elif n is not None and m >= n:
                        add_error(result, f"Logic M-of-N module '{module_name}' parameter 'm' must be less than 'n'")
    
    return result


def validate_ftm_specific_configs(config):
    """
    Validate that enabled FTMs have corresponding configuration in specifics section.
    
    This is informational - missing configs will use defaults, but we warn the user.
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    ftms = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, default={})
    ft_specs = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, default={})
    
    # Check register M-of-N
    if ftms.get(KEY_FTM_REG_MON, False):
        if KEY_FT_REG_MON not in ft_specs:
            add_warning(result, f"Register M-of-N is enabled but no configuration found in specifics.{KEY_SPEC_FT}.{KEY_FT_REG_MON}. Defaults will be used.")
    
    # Check logic M-of-N
    if ftms.get(KEY_FTM_LOGIC_MON, False):
        if KEY_FT_LOGIC_MON not in ft_specs:
            add_warning(result, f"Logic M-of-N is enabled but no configuration found in specifics.{KEY_SPEC_FT}.{KEY_FT_LOGIC_MON}. Defaults will be used.")
    
    return result