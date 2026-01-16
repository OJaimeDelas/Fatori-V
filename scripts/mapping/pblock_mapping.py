# =============================================================================
# FATORI-V • Mappings • Pblock Mapping
# File: pblock_mapping.py
# -----------------------------------------------------------------------------
# Maps pblock target names to KEEP hierarchy macros for fault injection.
# =============================================================================

import fatori_settings as cfg
from config.constants import MACRO_PREFIX

# Pblock target names to KEEP macro names
# These correspond to modules in the Ibex pipeline that can be targeted for FI
PBLOCK_TARGET_MACROS = {
    "alu": "KEEP_ALU",
    "multiplier": "KEEP_MULTIPLIER",
    "mult": "KEEP_MULTIPLIER",  # Alias
    "branch_adder": "KEEP_BRANCH_ADDER",
    "decoder": "KEEP_DECODER",
    "controller": "KEEP_CONTROLLER",
    "lsu": "KEEP_LSU",
}

# Conditional targets - these targets only exist if certain features are enabled
# Maps target name to the condition macro that must be defined
CONDITIONAL_TARGETS = {
    "multiplier": f"{MACRO_PREFIX}FTM_LOGIC_MON",  # Only exists with logic M-of-N
    "mult": f"{MACRO_PREFIX}FTM_LOGIC_MON",
}

# Default targets that should always be available (core pipeline modules)
DEFAULT_TARGETS = [
    "alu",
    "branch_adder",
    "decoder",
    "controller",
]


def get_pblock_macro_name(target):
    """
    Get the KEEP macro name for a pblock target.
    
    The KEEP macros are used in fatori_pblocks.svh to prevent Vivado
    from optimizing away module hierarchies during synthesis.
    
    Args:
        target: Target module name (e.g., "alu", "multiplier")
    
    Returns:
        String containing the KEEP macro name (e.g., "FATORI_KEEP_ALU")
    
    Raises:
        ValueError: If target is not recognized
    """
    target_lower = target.lower()
    
    if target_lower not in PBLOCK_TARGET_MACROS:
        valid_targets = ", ".join(sorted(PBLOCK_TARGET_MACROS.keys()))
        raise ValueError(
            f"Unknown pblock target '{target}'. Valid targets: {valid_targets}"
        )
    
    return PBLOCK_TARGET_MACROS[target_lower]


def is_conditional_target(target):
    """
    Check if a target is conditional on certain features being enabled.
    
    Some modules only exist when specific FTMs are enabled. For example,
    the multiplier with M-of-N redundancy only exists when logic M-of-N is enabled.
    
    Args:
        target: Target module name
    
    Returns:
        Boolean indicating if target is conditional
    """
    target_lower = target.lower()
    return target_lower in CONDITIONAL_TARGETS


def get_target_condition(target):
    """
    Get the condition macro that must be defined for a conditional target.
    
    Args:
        target: Target module name
    
    Returns:
        String containing the condition macro name, or None if not conditional
    """
    target_lower = target.lower()
    return CONDITIONAL_TARGETS.get(target_lower)


def get_all_targets():
    """
    Get list of all valid pblock target names.
    
    Returns:
        List of target name strings (lowercase, unique)
    """
    # Get unique target names (removing aliases)
    unique_targets = set()
    for target in PBLOCK_TARGET_MACROS.keys():
        unique_targets.add(target)
    
    return sorted(unique_targets)


def get_default_targets():
    """
    Get list of default targets that should always be available.
    
    These are core pipeline modules that exist regardless of configuration.
    
    Returns:
        List of default target name strings
    """
    return DEFAULT_TARGETS.copy()


def get_unconditional_targets():
    """
    Get list of targets that don't depend on any features.
    
    Returns:
        List of unconditional target name strings
    """
    all_targets = get_all_targets()
    conditional = set(CONDITIONAL_TARGETS.keys())
    
    unconditional = [t for t in all_targets if t not in conditional]
    return sorted(unconditional)