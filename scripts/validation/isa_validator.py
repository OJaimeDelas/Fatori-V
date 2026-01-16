# =============================================================================
# FATORI-V • ISA Validator
# File: isa_validator.py
# -----------------------------------------------------------------------------
# Validates ISA extension configurations and cross-dependencies.
# =============================================================================

from scripts.common.common_settings import *
from scripts.validation.validation_settings import *


def validate_isa_extensions(config):
    """
    Validate ISA extension configurations and their dependencies.
    
    Critical rules:
    - RV32M enabled requires multiplier != "none" (ERROR)
    - RV32B enabled requires bit_manipulation != "none" (ERROR)
    - Multiplier != "none" without RV32M generates warning
    - Bit manipulation != "none" without RV32B generates warning
    - RV32E incompatible with RV32M (ERROR)
    - RV32E incompatible with RV32B (ERROR)
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    # Extract ISA extension flags
    isa = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, default={})
    rv32e = isa.get(KEY_ISA_RV32E, False)
    rv32m = isa.get(KEY_ISA_RV32M, False)
    rv32b = isa.get(KEY_ISA_RV32B, False)
    rv32c = isa.get(KEY_ISA_RV32C, False)
    
    # Extract hardware configuration
    multiplier = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_MULTIPLIER, default="none")
    bit_manip = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_BIT_MANIP, default="none")
    
    # Validate RV32M requires hardware multiplier
    if rv32m and multiplier == "none":
        add_error(result, "RV32M extension enabled but multiplier is 'none'. Set specifics.ibex.multiplier to 'slow', 'fast', or 'single_cycle'.")
    
    # Validate RV32B requires bit manipulation hardware
    if rv32b and bit_manip == "none":
        add_error(result, "RV32B extension enabled but bit_manipulation is 'none'. Set specifics.ibex.bit_manipulation to 'balanced', 'ot_earlgrey', or 'full'.")
    
    # Warn if hardware enabled without ISA extension
    if not rv32m and multiplier != "none":
        add_warning(result, f"Hardware multiplier is '{multiplier}' but RV32M extension is not enabled. Consider enabling RV32M.")
    
    if not rv32b and bit_manip != "none":
        add_warning(result, f"Bit manipulation is '{bit_manip}' but RV32B extension is not enabled. Consider enabling RV32B.")
    
    # Validate RV32E incompatibilities
    if rv32e and rv32m:
        add_error(result, "RV32E is incompatible with RV32M. RV32E uses 16 registers; disable either RV32E or RV32M.")
    
    if rv32e and rv32b:
        add_error(result, "RV32E is incompatible with RV32B. Disable either RV32E or RV32B.")
    
    return result


def validate_multiplier_config(config):
    """
    Validate multiplier configuration is valid.
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    multiplier = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_MULTIPLIER)
    if multiplier is not None:
        if multiplier not in VALID_MULTIPLIER:
            add_error(result, f"Invalid multiplier value '{multiplier}'. Must be one of: {', '.join(VALID_MULTIPLIER)}")
    
    return result


def validate_bit_manip_config(config):
    """
    Validate bit manipulation configuration is valid.
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    bit_manip = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_BIT_MANIP)
    if bit_manip is not None:
        if bit_manip not in VALID_BIT_MANIP:
            add_error(result, f"Invalid bit_manipulation value '{bit_manip}'. Must be one of: {', '.join(VALID_BIT_MANIP)}")
    
    return result


def validate_regfile_config(config):
    """
    Validate register file configuration is valid.
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    regfile = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_REGFILE)
    if regfile is not None:
        if regfile not in VALID_REGFILE:
            add_error(result, f"Invalid regfile value '{regfile}'. Must be one of: {', '.join(VALID_REGFILE)}")
    
    return result