# =============================================================================
# FATORI-V • Pblock Algorithm
# File: calculator.py
# 
# Calculate pblock sizes for all target modules based on configuration
# =============================================================================

from constants import (
    BASELINE_SIZES,
    RV32B_FACTORS,
    ICACHE_FACTOR,
    BRANCH_PRED_OVERHEAD_LUTS,
    BRANCH_TALU_FACTOR,
    MULTIPLIER_SIZES,
    FATORI_FI_MERGED_MODULES,
    FI_MODE_INVALID_TARGETS,
    CONDITIONAL_MODULES,
    ALWAYS_PRESENT_MODULES,
    get_mon_factor,
    get_safety_margin,
)


# =============================================================================
# TARGET SELECTION
# =============================================================================

def select_targets(config):
    """
    Determine which modules should have pblocks based on configuration.
    
    Args:
        config (dict): User configuration with features and MON settings
    
    Returns:
        list: List of target module names to create pblocks for
    
    Notes:
        - FATORI_FI mode affects target selection (CONTROLLER/DECODER merge)
        - Some modules are conditional (ICACHE, BRANCH_PRED, MULTDIV)
        - WB_STAGE is currently disabled (breaks architecture)
    """
    targets = list(ALWAYS_PRESENT_MODULES)
    
    # Check FATORI_FI mode
    features = config.get('features', {})
    fi_mode = features.get('FATORI_FI', 0)
    
    if not fi_mode:
        # Without FATORI_FI, CONTROLLER and DECODER are valid targets
        targets.extend(['CONTROLLER', 'DECODER'])
    # With FATORI_FI, CONTROLLER and DECODER are merged into ID_STAGE
    # ID_STAGE is already in ALWAYS_PRESENT_MODULES
    
    # Add conditional modules based on configuration
    for module, condition_func in CONDITIONAL_MODULES.items():
        if module == 'WB_STAGE':
            # WB_STAGE currently disabled (architecture issue)
            continue
        
        if condition_func(features):
            targets.append(module)
    
    return targets


# =============================================================================
# SIZE CALCULATION
# =============================================================================

def calculate_pblock_sizes(config):
    """
    Calculate pblock sizes for all target modules.
    
    Args:
        config (dict): User configuration dictionary
    
    Returns:
        dict: {module_name: size_in_luts}
    
    Algorithm:
        For each target:
            size = base × feature_factor × mon_factor × safety_margin
    """
    targets = select_targets(config)
    sizes = {}
    
    for target in targets:
        size = calculate_module_size(target, config)
        sizes[target] = size
    
    return sizes


def calculate_module_size(module, config):
    """
    Calculate pblock size for a single module.
    
    Args:
        module (str): Module name (e.g., 'ALU', 'LSU')
        config (dict): User configuration
    
    Returns:
        int: Pblock size in LUTs
    
    Formula:
        size = baseline × feature_factor × mon_factor × safety_margin
    """
    features = config.get('features', {})
    mon_config = config.get('mon_config', {})
    
    # Get baseline size
    base_size = get_baseline_size(module, features)
    
    # Get feature scaling factor
    feature_factor = get_feature_factor(module, features)
    
    # Get MON_N scaling factor
    mon_n = mon_config.get(module, {}).get('MON_N', 1)
    mon_factor = get_mon_factor(module, mon_n)
    
    # Get safety margin
    margin = get_safety_margin(module)
    
    # Calculate final size
    size = int(base_size * feature_factor * mon_factor * margin)
    
    return size


# =============================================================================
# BASELINE SIZE LOOKUP
# =============================================================================

def get_baseline_size(module, features):
    """
    Get baseline size for a module, accounting for FATORI_FI mode.
    
    Args:
        module (str): Module name
        features (dict): Feature configuration
    
    Returns:
        int: Baseline size in LUTs
    
    Notes:
        - With FATORI_FI=1, CONTROLLER and DECODER use merged sizes
        - Otherwise, use standard baseline from CONFIG 01
    """
    fi_mode = features.get('FATORI_FI', 0)
    
    if fi_mode and module in FATORI_FI_MERGED_MODULES:
        return FATORI_FI_MERGED_MODULES[module]
    
    return BASELINE_SIZES.get(module, 0)


# =============================================================================
# FEATURE FACTOR CALCULATION
# =============================================================================

def get_feature_factor(module, features):
    """
    Calculate feature scaling factor for a module.
    
    Args:
        module (str): Module name
        features (dict): Feature configuration dictionary
    
    Returns:
        float: Feature scaling factor (1.0 = no scaling)
    
    Notes:
        - Different modules affected by different features
        - Some effects are multiplicative, some additive (handled separately)
    """
    if module == 'ALU':
        return get_alu_feature_factor(features)
    
    elif module == 'IF_STAGE':
        return get_if_stage_feature_factor(features)
    
    elif module == 'ID_STAGE':
        return get_id_stage_feature_factor(features)
    
    elif module == 'EX_BLOCK':
        return get_ex_block_feature_factor(features)
    
    else:
        # Other modules not significantly affected by features
        return 1.0


def get_alu_feature_factor(features):
    """
    Calculate ALU feature factor based on RV32B extension.
    
    Returns:
        float: Scaling factor (1.0, 4.2, or 8.9)
    """
    rv32b = features.get('FATORI_RV32B', 'None')
    return RV32B_FACTORS.get(rv32b, 1.0)


def get_if_stage_feature_factor(features):
    """
    Calculate IF_STAGE feature factor based on ICACHE and BRANCH_PRED.
    
    Returns:
        float: Scaling factor
    
    Notes:
        - ICACHE increases base by 3.2x (replaces prefetch)
        - BRANCH_PRED adds 120 LUTs (additive, handled as percentage)
    """
    factor = 1.0
    
    # I-Cache impact (multiplicative)
    if features.get('FATORI_ICACHE', 0) == 1:
        factor *= ICACHE_FACTOR
    
    # Branch predictor impact (additive - approximate as percentage)
    if features.get('FATORI_BRANCH_PRED', 0) == 1:
        # 120 LUTs on baseline 431L = 28% increase
        # On cached IF_STAGE (1382L), it's 9% increase
        # Use average: ~15% increase
        factor *= 1.15
    
    return factor


def get_id_stage_feature_factor(features):
    """
    Calculate ID_STAGE feature factor based on BRANCH_TALU.
    
    Returns:
        float: Scaling factor
    """
    if features.get('FATORI_BRANCH_TALU', 0) == 1:
        return BRANCH_TALU_FACTOR
    return 1.0


def get_ex_block_feature_factor(features):
    """
    Calculate EX_BLOCK feature factor.
    
    Returns:
        float: Effective size considering ALU + MULTDIV
    
    Notes:
        - EX_BLOCK = ALU + MULTDIV
        - Both can scale independently
        - This function returns a composite effective factor
    """
    # EX_BLOCK contains ALU (which scales with RV32B)
    alu_base = BASELINE_SIZES['ALU']
    rv32b = features.get('FATORI_RV32B', 'None')
    alu_size = alu_base * RV32B_FACTORS.get(rv32b, 1.0)
    
    # Add multiplier if enabled
    rv32m = features.get('FATORI_RV32M', 'None')
    mul_size = MULTIPLIER_SIZES.get(rv32m, 0)
    
    # Total EX_BLOCK size before MON and margin
    total_size = alu_size + mul_size
    
    # Return as factor relative to baseline EX_BLOCK
    ex_base = BASELINE_SIZES['EX_BLOCK']
    return total_size / ex_base


# =============================================================================
# SIZE BREAKDOWN (for reporting)
# =============================================================================

def get_size_breakdown(module, config):
    """
    Get detailed breakdown of size calculation for a module.
    
    Args:
        module (str): Module name
        config (dict): User configuration
    
    Returns:
        dict: Breakdown with base, factors, and final size
    
    Useful for debugging and reporting.
    """
    features = config.get('features', {})
    mon_config = config.get('mon_config', {})
    
    base_size = get_baseline_size(module, features)
    feature_factor = get_feature_factor(module, features)
    mon_n = mon_config.get(module, {}).get('MON_N', 1)
    mon_factor = get_mon_factor(module, mon_n)
    margin = get_safety_margin(module)
    
    size_after_features = base_size * feature_factor
    size_after_mon = size_after_features * mon_factor
    final_size = int(size_after_mon * margin)
    
    return {
        'module': module,
        'base_size': base_size,
        'feature_factor': feature_factor,
        'size_after_features': int(size_after_features),
        'mon_n': mon_n,
        'mon_factor': mon_factor,
        'size_after_mon': int(size_after_mon),
        'safety_margin': margin,
        'final_size': final_size,
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_configuration(config):
    """
    Validate user configuration for common errors.
    
    Args:
        config (dict): User configuration
    
    Returns:
        list: List of warning/error messages (empty if valid)
    
    Checks:
        - Required fields present
        - Valid feature values
        - MON_N in valid range
        - WB_STAGE not enabled (currently broken)
    """
    warnings = []
    
    features = config.get('features', {})
    mon_config = config.get('mon_config', {})
    
    # Check RV32B value
    rv32b = features.get('FATORI_RV32B', 'None')
    if rv32b not in ['None', 'Balanced', 'Full']:
        warnings.append(f"Invalid FATORI_RV32B value: {rv32b}. Use None/Balanced/Full.")
    
    # Check RV32M value
    rv32m = features.get('FATORI_RV32M', 'None')
    if rv32m not in ['None', 'Slow', 'Fast']:
        warnings.append(f"Invalid FATORI_RV32M value: {rv32m}. Use None/Slow/Fast.")
    
    # Check WB_STAGE
    if features.get('FATORI_WSTAGE', 0) == 1:
        warnings.append("WARNING: FATORI_WSTAGE is enabled but currently breaks architecture. Set to 0.")
    
    # Check MON_N values
    for module, mon_cfg in mon_config.items():
        mon_n = mon_cfg.get('MON_N', 1)
        if not (1 <= mon_n <= 5):
            warnings.append(f"{module}: MON_N={mon_n} out of valid range [1-5].")
        
        if mon_n > 3 and module not in ['ALU']:
            warnings.append(f"{module}: MON_N={mon_n} > 3 is untested and may cause issues.")
    
    return warnings