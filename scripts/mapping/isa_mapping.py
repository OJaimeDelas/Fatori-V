# =============================================================================
# FATORI-V • Mappings • ISA Mapping
# File: isa_mapping.py
# -----------------------------------------------------------------------------
# Maps YAML ISA configuration values to Ibex package enums and make flags.
# =============================================================================

import fatori_settings as cfg
from scripts.common.common_settings import (
    VALID_MULTIPLIER,
    VALID_BIT_MANIP,
    VALID_REGFILE,
)

# Multiplier configuration mapping: YAML value → ibex_pkg enum
MULTIPLIER_MAPPING = {
    "none": "ibex_pkg::RV32MNone",
    "slow": "ibex_pkg::RV32MSlow",
    "fast": "ibex_pkg::RV32MFast",
    "single_cycle": "ibex_pkg::RV32MSingleCycle",
}

# Bit manipulation configuration mapping: YAML value → ibex_pkg enum
BIT_MANIP_MAPPING = {
    "none": "ibex_pkg::RV32BNone",
    "balanced": "ibex_pkg::RV32BBalanced",
    "ot_earlgrey": "ibex_pkg::RV32BOTEarlGrey",
    "full": "ibex_pkg::RV32BFull",
}

# Register file configuration mapping: YAML value → ibex_pkg enum
REGFILE_MAPPING = {
    "ff": "ibex_pkg::RegFileFF",
    "fpga": "ibex_pkg::RegFileFPGA",
    "file_latch": "ibex_pkg::RegFileLatch",
}


def get_multiplier_enum(yaml_value):
    """
    Convert YAML multiplier value to Ibex package enum.
    
    Args:
        yaml_value: Multiplier type from YAML (e.g., "fast", "slow")
    
    Returns:
        String containing the ibex_pkg:: enum value
    
    Raises:
        ValueError: If multiplier value is not recognized
    """
    if yaml_value is None:
        yaml_value = "none"
    
    yaml_value_lower = yaml_value.lower()
    
    if yaml_value_lower not in MULTIPLIER_MAPPING:
        valid_values = ", ".join(VALID_MULTIPLIER)
        raise ValueError(
            f"Unknown multiplier value '{yaml_value}'. Valid values: {valid_values}"
        )
    
    return MULTIPLIER_MAPPING[yaml_value_lower]


def get_bit_manip_enum(yaml_value):
    """
    Convert YAML bit manipulation value to Ibex package enum.
    
    Args:
        yaml_value: Bit manipulation type from YAML (e.g., "balanced", "full")
    
    Returns:
        String containing the ibex_pkg:: enum value
    
    Raises:
        ValueError: If bit manipulation value is not recognized
    """
    if yaml_value is None:
        yaml_value = "none"
    
    yaml_value_lower = yaml_value.lower()
    
    if yaml_value_lower not in BIT_MANIP_MAPPING:
        valid_values = ", ".join(VALID_BIT_MANIP)
        raise ValueError(
            f"Unknown bit_manipulation value '{yaml_value}'. Valid values: {valid_values}"
        )
    
    return BIT_MANIP_MAPPING[yaml_value_lower]


def get_regfile_enum(yaml_value):
    """
    Convert YAML register file value to Ibex package enum.
    
    Args:
        yaml_value: Register file type from YAML (e.g., "ff", "fpga")
    
    Returns:
        String containing the ibex_pkg:: enum value
    
    Raises:
        ValueError: If register file value is not recognized
    """
    if yaml_value is None:
        yaml_value = "ff"  # Default to flip-flop implementation
    
    yaml_value_lower = yaml_value.lower()
    
    if yaml_value_lower not in REGFILE_MAPPING:
        valid_values = ", ".join(VALID_REGFILE)
        raise ValueError(
            f"Unknown regfile value '{yaml_value}'. Valid values: {valid_values}"
        )
    
    return REGFILE_MAPPING[yaml_value_lower]


def requires_use_mul_div(rv32m_enabled):
    """
    Determine if USE_MUL_DIV make flag should be set.
    
    When RV32M is enabled, the firmware compilation needs the
    USE_MUL_DIV flag to enable multiplication/division instructions.
    
    Args:
        rv32m_enabled: Boolean indicating if RV32M ISA extension is enabled
    
    Returns:
        Boolean indicating if USE_MUL_DIV should be set
    """
    return rv32m_enabled


def requires_use_compressed(rv32c_enabled):
    """
    Determine if USE_COMPRESSED make flag should be set.
    
    When RV32C is enabled, the firmware compilation needs the
    USE_COMPRESSED flag to enable compressed instructions.
    
    Args:
        rv32c_enabled: Boolean indicating if RV32C ISA extension is enabled
    
    Returns:
        Boolean indicating if USE_COMPRESSED should be set
    """
    return rv32c_enabled


def get_isa_make_flags(rv32m_enabled, rv32c_enabled):
    """
    Get list of ISA-related make flags based on enabled extensions.
    
    Args:
        rv32m_enabled: Boolean indicating if RV32M is enabled
        rv32c_enabled: Boolean indicating if RV32C is enabled
    
    Returns:
        List of make flag strings (e.g., ["USE_MUL_DIV=1"])
    """
    flags = []
    
    if requires_use_mul_div(rv32m_enabled):
        flags.append("USE_MUL_DIV=1")
    
    if requires_use_compressed(rv32c_enabled):
        flags.append("USE_COMPRESSED=1")
    
    return flags