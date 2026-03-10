# =============================================================================
# FATORI-V • Pblock Algorithm
# File: calculator.py
# 
# Calculate pblock sizes for all target modules based on configuration
# =============================================================================

from constants import (
    BASELINE_SIZES,
    FF_BASELINE_SIZES,
    NAME_ALIASES,
    RV32B_FACTORS,
    ICACHE_FACTOR,
    S_RV32B_DECODER,
    S_MULTDIV_ALU,
    S_MULTDIV_ID,
    S_BP_IF,
    S_BTALU_ID,
    S_WSTAGE_WB,
    S_WSTAGE_CTRL,
    S_WSTAGE_DEC,
    S_MON,
    S_ML_MAX,
    R_MODULE,
    MULTIPLIER_SIZES,
    MULTIPLIER_DSP,
    FATORI_FI_MERGED_MODULES,
    FI_MODE_INVALID_TARGETS,
    CONDITIONAL_MODULES,
    ALWAYS_PRESENT_MODULES,
    get_safety_margin,
)


# =============================================================================
# TARGET SELECTION
# =============================================================================

def select_targets(config):
    """
    Select targets based on explicit user targets list.
    
    Returns tuple: (enabled_targets, disabled_targets, name_mapping)
    - enabled_targets: Normalized names of enabled targets
    - disabled_targets: Normalized names of disabled targets
    - name_mapping: Dict mapping normalized_name -> original_name
    
    Args:
        config (dict): User configuration
    
    Returns:
        tuple: (list of enabled, list of disabled, dict of name mapping)
    """
    if 'targets' in config:
        user_targets = config['targets']
        features = config.get('features', {})
        
        # Normalize and validate, separating enabled from disabled
        enabled, disabled, name_mapping = validate_and_normalize_targets(user_targets, features)
        return enabled, disabled, name_mapping
    else:
        # Auto-select: only enabled targets, no disabled, no name mapping needed
        targets = auto_select_targets(config)
        # For auto-select, normalized name = original name
        name_mapping = {t: t for t in targets}
        return targets, [], name_mapping

def normalize_target_name(target):
    """
    Normalize user config names to internal names.
    
    Args:
        target (str): User-provided target name
    
    Returns:
        str: Normalized internal name
    """
    return NAME_ALIASES.get(target, target)

def validate_and_normalize_targets(user_targets, features):
    """
    Validate and normalize target names, separating enabled from disabled.
    
    Returns tuple of (enabled_targets, disabled_targets, name_mapping):
    - enabled_targets: Normalized names of targets that exist in design
    - disabled_targets: Normalized names of targets that are disabled
    - name_mapping: Dict mapping normalized_name -> original_name
    
    Args:
        user_targets (list): User-provided target names
        features (dict): Feature configuration
    
    Returns:
        tuple: (list of enabled, list of disabled, dict of name mapping)
    """
    enabled_targets = []
    disabled_targets = []
    name_mapping = {}
    errors = []
    
    for target in user_targets:
        # Normalize name
        normalized = normalize_target_name(target)
        
        # Track original name for output
        name_mapping[normalized] = target
        
        # Check if exists in baseline
        if normalized not in BASELINE_SIZES:
            errors.append(f"Unknown target: '{target}' (normalized to '{normalized}')")
            continue
        
        # Check conditional existence - if disabled, add to disabled_targets
        is_disabled = False
        
        if normalized == 'ICACHE' and features.get('FATORI_ICACHE', 0) == 0:
            is_disabled = True
        elif normalized == 'PREFETCH_BUFFER' and features.get('FATORI_ICACHE', 0) == 1:
            is_disabled = True
        elif normalized == 'MULTDIV' and features.get('FATORI_RV32M', 'None') == 'None':
            is_disabled = True
        elif normalized == 'BRANCH_PREDICT' and features.get('FATORI_BRANCH_PRED', 0) == 0:
            is_disabled = True
        elif normalized == 'FAULT_MGR' and features.get('FATORI_FAULT_MGR', 0) == 0:
            is_disabled = True
        elif normalized == 'WB_STAGE' and features.get('FATORI_WSTAGE', 0) == 0:
            is_disabled = True
        
        # Categorize
        if is_disabled:
            disabled_targets.append(normalized)
        else:
            enabled_targets.append(normalized)
    
    if errors:
        raise ValueError("Target validation errors:\n" + "\n".join(errors))
    
    return enabled_targets, disabled_targets, name_mapping

# =============================================================================
# SIZE CALCULATION
# =============================================================================

def calculate_pblock_sizes(config):
    """
    Calculate pblock sizes for all target modules.
    
    Returns tuple: (enabled_sizes, disabled_targets, name_mapping)
    - enabled_sizes: Dict of {normalized_name: size} for enabled targets
    - disabled_targets: List of normalized names that are disabled
    - name_mapping: Dict mapping normalized_name -> original_name
    
    Args:
        config (dict): User configuration dictionary
    
    Returns:
        tuple: (dict of sizes, list of disabled, dict of name mapping)
    
    Algorithm:
        For each enabled target:
            size = base × feature_factor × mon_factor × safety_margin
        For disabled targets:
            size = 0 (empty pblock)
    """
    enabled_targets, disabled_targets, name_mapping = select_targets(config)
    sizes = {}
    
    # Calculate sizes for enabled targets
    for target in enabled_targets:
        size = calculate_module_size(target, config)
        sizes[target] = size
    
    return sizes, disabled_targets, name_mapping

def auto_select_targets(config):
    """
    Auto-select targets based on enabled features (legacy behavior).
    
    Selects all modules that exist in the design based on configuration.
    This is the old behavior when no explicit targets list is provided.
    
    Args:
        config (dict): User configuration
    
    Returns:
        list: Modules to create pblocks for
    """
    features = config.get('features', {})
    fi_mode = features.get('FATORI_FI', 0)
    
    targets = []
    
    # Always present modules
    targets.extend(ALWAYS_PRESENT_MODULES)
    
    # Conditional modules
    for module, condition_func in CONDITIONAL_MODULES.items():
        if condition_func(features):
            targets.append(module)
    
    # Remove FI-invalid targets
    if fi_mode:
        targets = [t for t in targets if t not in FI_MODE_INVALID_TARGETS]
    
    return targets

def calculate_module_size(module, config):
    """
    Calculate pblock size for a single module using equation 7.1.

    Implements: Pblock = [(B × ΠF + ΣS) × MON_logic(N) + S_MON + S_voter] × M

    S_voter accounts for register M-of-N voter circuits: each replicated FF
    needs approximately 2 LUTs of majority-voter logic (for N=3), giving
    voter_luts = FF_BASELINE[module] × (reg_mon_N - 1).

    Args:
        module (str): Module name (e.g., 'ALU', 'LSU', 'FAULT_MGR')
        config (dict): User configuration

    Returns:
        int: Pblock size in LUTs
    """
    features = config.get('features', {})
    logic_mon_config = config.get('logic_mon_config', {})
    # reg_mon_config maps module name -> N (1 = no replication)
    reg_mon_config = config.get('reg_mon_config', {})

    # Get baseline size
    base_size = get_baseline_size(module, features)

    # Special case: FAULT_MGR — small module, no voter overhead modeled
    if module == 'FAULT_MGR':
        margin = get_safety_margin(module)
        size = int((base_size + S_ML_MAX) * margin)
        return size

    # Step 1: B × ΠF (baseline × multiplicative features)
    feature_factor = get_multiplicative_feature_factor(module, features)
    size_after_mult_features = base_size * feature_factor

    # Step 2: + ΣS (add additive feature components)
    additive_overhead = get_additive_feature_overhead(module, features)
    size_after_features = size_after_mult_features + additive_overhead

    # Step 3: × MON_logic(N) (always 1.0, empirically no scaling)
    # MON_logic(N) = 1.0 for all N, so this is a no-op

    # Step 4: + S_MON (logic M-of-N wrapper overhead if enabled)
    mon_n = logic_mon_config.get(module, {}).get('MON_N', 1)
    mon_overhead = S_MON if mon_n >= 2 else 0
    size_after_mon = size_after_features + mon_overhead

    # Step 5: + S_voter (register M-of-N voter LUT overhead)
    # voter_luts = FF_BASELINE × (N-1): each FF replication adds voter circuits.
    # Vivado does not optimise away replicated FFs, so this overhead is hard.
    reg_mon_n = reg_mon_config.get(module, 1)
    ff_baseline = FF_BASELINE_SIZES.get(module, 0)
    voter_overhead = ff_baseline * max(0, reg_mon_n - 1)
    size_after_voter = size_after_mon + voter_overhead

    # Step 6: × M (apply safety margin)
    margin = get_safety_margin(module)
    final_size = int(size_after_voter * margin)

    return final_size


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

def get_multiplicative_feature_factor(module, features):
    """
    Calculate MULTIPLICATIVE feature scaling factor for a module.
    
    Additive terms handled separately via get_additive_feature_overhead().
    
    Args:
        module (str): Module name
        features (dict): Feature configuration dictionary
    
    Returns:
        float: Multiplicative scaling factor (1.0 = no scaling)
    """
    if module == 'ALU':
        return get_alu_mult_factor(features)
    
    elif module == 'IF_STAGE':
        return get_if_stage_mult_factor(features)
    
    elif module == 'ID_STAGE':
        return get_id_stage_mult_factor(features)
    
    elif module == 'EX_BLOCK':
        return get_ex_block_mult_factor(features)
    
    else:
        return 1.0


def get_additive_feature_overhead(module, features):
    """
    Calculate total ADDITIVE feature overhead for a module (ΣS).
    
    Args:
        module (str): Module name
        features (dict): Feature configuration
    
    Returns:
        int: Total additive overhead in LUTs
    """
    overhead = 0
    
    # Per-module additive terms
    if module == 'ALU':
        overhead += get_alu_additive(features)
    elif module == 'DECODER':
        overhead += get_decoder_additive(features)
    elif module == 'IF_STAGE':
        overhead += get_if_stage_additive(features)
    elif module == 'ID_STAGE':
        overhead += get_id_stage_additive(features)
    elif module == 'WB_STAGE':
        overhead += get_wb_stage_additive(features)
    elif module == 'CONTROLLER':
        overhead += get_controller_additive(features)
    
    return overhead


# =============================================================================
# MULTIPLICATIVE FEATURE FACTORS (ΠF terms)
# =============================================================================

def get_alu_mult_factor(features):
    """ALU multiplicative factor: RV32B only."""
    rv32b = features.get('FATORI_RV32B', 'None')
    return RV32B_FACTORS.get(rv32b, 1.0)


def get_if_stage_mult_factor(features):
    """IF_STAGE multiplicative factor: ICACHE only."""
    if features.get('FATORI_ICACHE', 0) == 1:
        return ICACHE_FACTOR
    return 1.0


def get_id_stage_mult_factor(features):
    """ID_STAGE has no multiplicative factors."""
    return 1.0


def get_ex_block_mult_factor(features):
    """
    EX_BLOCK multiplicative factor: ALU RV32B scaling.
    
    Note: MULTDIV is additive (absolute size), not multiplicative.
    """
    rv32b = features.get('FATORI_RV32B', 'None')
    return RV32B_FACTORS.get(rv32b, 1.0)


# =============================================================================
# ADDITIVE FEATURE OVERHEADS (ΣS terms)
# =============================================================================

def get_alu_additive(features):
    """ALU additive overhead: MULTDIV integration."""
    overhead = 0
    rv32m = features.get('FATORI_RV32M', 'None')
    if rv32m != 'None':
        overhead += S_MULTDIV_ALU
    return overhead


def get_decoder_additive(features):
    """DECODER additive overhead: RV32B decode logic + WSTAGE."""
    overhead = 0
    
    # RV32B decode logic
    rv32b = features.get('FATORI_RV32B', 'None')
    overhead += S_RV32B_DECODER.get(rv32b, 0)
    
    # WSTAGE overhead
    if features.get('FATORI_WSTAGE', 0) == 1:
        overhead += S_WSTAGE_DEC
    
    return overhead


def get_if_stage_additive(features):
    """IF_STAGE additive overhead: BRANCH_PRED integration."""
    overhead = 0
    if features.get('FATORI_BRANCH_PRED', 0) == 1:
        overhead += S_BP_IF
    return overhead


def get_id_stage_additive(features):
    """ID_STAGE additive overhead: BTALU + MULTDIV integration."""
    overhead = 0
    
    if features.get('FATORI_BRANCH_TALU', 0) == 1:
        overhead += S_BTALU_ID
    
    rv32m = features.get('FATORI_RV32M', 'None')
    if rv32m != 'None':
        overhead += S_MULTDIV_ID
    
    return overhead


def get_wb_stage_additive(features):
    """WB_STAGE additive overhead: WSTAGE pipeline logic."""
    overhead = 0
    if features.get('FATORI_WSTAGE', 0) == 1:
        overhead += S_WSTAGE_WB
    return overhead


def get_controller_additive(features):
    """CONTROLLER additive overhead: WSTAGE control logic."""
    overhead = 0
    if features.get('FATORI_WSTAGE', 0) == 1:
        overhead += S_WSTAGE_CTRL
    return overhead


# =============================================================================
# SIZE BREAKDOWN (for reporting)
# =============================================================================

def get_size_breakdown(module, config):
    """
    Get detailed breakdown of size calculation per equation 7.1.
    
    Args:
        module (str): Module name
        config (dict): User configuration
    
    Returns:
        dict: Breakdown showing each term in the calculation
    """
    features = config.get('features', {})
    logic_mon_config = config.get('logic_mon_config', {})
    reg_mon_config = config.get('reg_mon_config', {})

    base_size = get_baseline_size(module, features)
    mult_factor = get_multiplicative_feature_factor(module, features)
    additive_overhead = get_additive_feature_overhead(module, features)

    size_after_mult = base_size * mult_factor
    size_after_add = size_after_mult + additive_overhead

    mon_n = logic_mon_config.get(module, {}).get('MON_N', 1)
    mon_overhead = S_MON if mon_n >= 2 else 0
    size_after_mon = size_after_add + mon_overhead

    # Step 5: voter overhead from register M-of-N replication
    reg_mon_n = reg_mon_config.get(module, 1)
    ff_baseline = FF_BASELINE_SIZES.get(module, 0)
    voter_overhead = ff_baseline * max(0, reg_mon_n - 1)
    size_after_voter = size_after_mon + voter_overhead

    margin = get_safety_margin(module)
    final_size = int(size_after_voter * margin)

    return {
        'module': module,
        'base_size': base_size,
        'mult_factor': mult_factor,
        'size_after_mult': int(size_after_mult),
        'additive_overhead': additive_overhead,
        'size_after_additive': int(size_after_add),
        'mon_n': mon_n,
        'mon_overhead': mon_overhead,
        'size_after_mon': int(size_after_mon),
        'reg_mon_n': reg_mon_n,
        'voter_overhead': voter_overhead,
        'size_after_voter': int(size_after_voter),
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
    """
    warnings = []
    
    features = config.get('features', {})
    logic_mon_config = config.get('logic_mon_config', {})

    # Check RV32B value (updated to include OTEarlGrey)
    rv32b = features.get('FATORI_RV32B', 'None')
    if rv32b not in ['None', 'Balanced', 'OTEarlGrey', 'Full']:
        warnings.append(f"Invalid FATORI_RV32B value: {rv32b}. Use None/Balanced/OTEarlGrey/Full.")

    # Check RV32M value (updated to include Single_cycle)
    rv32m = features.get('FATORI_RV32M', 'None')
    if rv32m not in ['None', 'Slow', 'Fast', 'Single_cycle']:
        warnings.append(f"Invalid FATORI_RV32M value: {rv32m}. Use None/Slow/Fast/Single_cycle.")

    # Check MON_N values (empirically N≥2 gives same overhead)
    for module, mon_cfg in logic_mon_config.items():
        mon_n = mon_cfg.get('MON_N', 1)
        if not (1 <= mon_n <= 5):
            warnings.append(f"{module}: MON_N={mon_n} out of valid range [1-5].")
    
    return warnings