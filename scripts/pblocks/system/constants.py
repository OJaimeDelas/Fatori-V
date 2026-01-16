# =============================================================================
# FATORI-V • Pblock Algorithm
# File: constants.py
# 
# Baseline module sizes, scaling factors, and FPGA specifications
# =============================================================================

# =============================================================================
# BASELINE MODULE SIZES (from CONFIG 01 - Absolute Baseline)
# =============================================================================
# These are the minimum sizes measured with all features disabled:
# - ICACHE=0, RV32B=None, RV32M=None, BRANCH_PRED=0, BRANCH_TALU=0
# - All MON_N=1, All FTMs=0, METRIC_LAYER=0

BASELINE_SIZES = {
    'ALU': 238,                # Arithmetic Logic Unit (LUTs, FFs)
    'CONTROLLER': 129,         # Control FSM
    'DECODER': 93,             # Instruction decoder
    'LSU': 154,                # Load/Store Unit
    'IF_STAGE': 431,           # Instruction Fetch stage (with prefetch)
    'ID_STAGE': 365,           # Instruction Decode stage
    'EX_BLOCK': 238,           # Execution block (ALU only, no multiplier)
    'WB_STAGE': 33,            # Writeback stage (minimal glue logic)
    'PREFETCH_BUFFER': 168,    # Prefetch buffer (mutually exclusive with cache)
    'BRANCH_PREDICT': 38,      # Branch predictor
    'MULTDIV': 466,            # Multiplier/Divider (fast variant baseline)
    'ICACHE': 4,               # I-cache wrapper (actual cache in BRAM)
}

# Baseline FFs for reference (not used in pblock sizing, but documented)
BASELINE_FFS = {
    'ALU': 0,
    'CONTROLLER': 14,
    'DECODER': 0,
    'LSU': 68,
    'IF_STAGE': 280,
    'ID_STAGE': 17,
    'EX_BLOCK': 0,
    'WB_STAGE': 0,
    'PREFETCH_BUFFER': 196,
    'BRANCH_PREDICT': 0,
    'MULTDIV': 75,
    'ICACHE': 1,
}

# =============================================================================
# FATORI_FI MODE EFFECTS
# =============================================================================
# When FATORI_FI is enabled, some modules are heavily optimized/merged

FATORI_FI_MERGED_MODULES = {
    'CONTROLLER': 18,  # 129L → 18L (86% reduction, merged into parent)
    'DECODER': 27,     # 93L → 27L (71% reduction, merged into parent)
}

# When FI mode is active, these modules should NOT be targeted independently
# Instead, target their parent module (ID_STAGE)
FI_MODE_INVALID_TARGETS = ['CONTROLLER', 'DECODER']

# =============================================================================
# ARCHITECTURAL FEATURE SCALING FACTORS
# =============================================================================

# RV32B (Bitmanip Extension) impact on ALU size
RV32B_FACTORS = {
    'None': 1.0,      # No bitmanip (baseline 238L)
    'Balanced': 4.2,  # Balanced bitmanip (measured 1006L in CONFIG 02)
    'Full': 8.9,      # Full bitmanip (measured 2118L in CONFIG 03)
}

# I-Cache impact on IF_STAGE size
ICACHE_FACTOR = 3.2  # IF_STAGE grows from 431L to 1382L (CONFIG 04)

# Branch predictor overhead (additive to IF_STAGE)
BRANCH_PRED_OVERHEAD_LUTS = 120  # Adds ~28% to IF_STAGE (CONFIG 06)

# Branch Target ALU overhead (percentage increase to ID_STAGE)
BRANCH_TALU_FACTOR = 1.10  # ID_STAGE: 365L → 402L (CONFIG 05)

# Multiplier sizes (absolute LUT counts to add to EX_BLOCK)
MULTIPLIER_SIZES = {
    'None': 0,
    'Slow': 621,   # Multi-cycle multiplier (CONFIG 07)
    'Fast': 466,   # Single-cycle multiplier (CONFIG 08)
}

# =============================================================================
# MON_N SCALING FACTORS
# =============================================================================
# M-of-N replication scales sub-linearly due to Vivado optimization
# (No keep_hierarchy on individual replicas for timing closure)

def get_mon_factor(module, mon_n):
    """
    Calculate MON_N scaling factor for a given module.
    
    Args:
        module (str): Module name (e.g., 'ALU', 'LSU')
        mon_n (int): Number of replicas (1-5)
    
    Returns:
        float: Scaling factor to apply to base size
    
    Notes:
        - MON_N=1 returns 1.0 (no replication)
        - ALU has validated empirical formula: 1.5 + 1.4*N
        - Other modules use conservative estimates until tested
    """
    if mon_n == 1:
        return 1.0
    
    # Validated formula from ALU experiments (CONFIG 09, 10)
    # MON_N=3: 238L × 4.7 = 1129L (measured)
    # MON_N=5: 238L × 8.6 = 2054L (measured)
    if module == 'ALU':
        return 1.5 + 1.4 * mon_n
    
    # DECODER showed anomalous scaling (11.1x for MON_N=3 in CONFIG 13)
    # Use conservative linear scaling with high base overhead
    elif module == 'DECODER':
        return 3.7 * mon_n
    
    # Other modules: No validated data yet
    # Use ALU formula with 30% pessimism factor
    else:
        return (1.5 + 1.4 * mon_n) * 1.30


# =============================================================================
# SAFETY MARGINS
# =============================================================================
# Optional margins to account for routing overhead and placement constraints

SAFETY_MARGINS = {
    'ALU': 1.10,              # 10%
    'DECODER': 1.15,          # 15% (anomaly protection)
    'LSU': 1.10,              # 10%
    'CONTROLLER': 1.10,       # 10%
    'IF_STAGE': 1.10,         # 10%
    'ID_STAGE': 1.10,         # 10%
    'EX_BLOCK': 1.10,         # 10%
    'WB_STAGE': 1.08,         # 8%
    'PREFETCH_BUFFER': 1.08,  # 8%
    'BRANCH_PREDICT': 1.08,   # 8%
    'MULTDIV': 1.08,          # 8%
    'ICACHE': 1.08,           # 8%
}

# Default margin for unlisted modules
DEFAULT_SAFETY_MARGIN = 1.35


def get_safety_margin(module):
    """Get safety margin for a module."""
    return SAFETY_MARGINS.get(module, DEFAULT_SAFETY_MARGIN)


# =============================================================================
# PLACEMENT STRATEGY
# =============================================================================

# Target utilization per clock region (0.0-1.0)
# Lower values spread pblocks across more regions for better routing
# Recommended: 0.60-0.70 for tight pblocks with good routing
TARGET_REGION_UTILIZATION = 0.70  # 70% target per region

# =============================================================================
# FPGA SPECIFICATIONS (Xilinx XCKU040-FBVA676-1-C)
# =============================================================================

FPGA_SPECS = {
    'device': 'XCKU040-FBVA676-1-C',
    'family': 'Kintex UltraScale',
    
    # Clock region grid
    'clock_regions': {
        'columns': 2,         # X0-X1
        'rows': 5,            # Y0-Y4
        'total': 10,          # 2 × 5 grid
    },
    
    # Resources per clock region (approximate)
    'per_region': {
        'luts': 12000,        # Slice LUTs per region
        'ffs': 24000,         # Flip-flops per region
        'slices': 2400,       # Configurable Logic Blocks
        'brams': 60,          # Block RAMs
        'dsps': 120,          # DSP48E2 slices
    },
    
    # Total device resources
    'total': {
        'luts': 242400,
        'ffs': 484800,
        'slices': 48500,
        'brams': 600,
        'dsps': 1920,
    },
    
    # Slice geometry
    'slice_geometry': {
        'luts_per_slice': 8,      # Each slice has 8 LUTs
        'ffs_per_slice': 16,      # Each slice has 16 FFs
        'slices_per_clb': 1,      # 1 slice per CLB in UltraScale
    }
}


def get_clock_region_capacity():
    """Get the LUT capacity of one clock region."""
    return FPGA_SPECS['per_region']['luts']


def get_total_regions():
    """Get total number of clock regions."""
    return FPGA_SPECS['clock_regions']['total']


def luts_to_slices(lut_count):
    """
    Convert LUT count to approximate slice count.
    
    Args:
        lut_count (int): Number of LUTs
    
    Returns:
        int: Approximate number of slices needed
    
    Notes:
        - Each slice contains 8 LUTs
        - Add 10% overhead for packing inefficiency
    """
    slices = int(lut_count / 8.0 * 1.10) + 1
    return slices


# =============================================================================
# CONDITIONAL MODULE RULES
# =============================================================================
# Rules for determining which modules should be targeted based on configuration

CONDITIONAL_MODULES = {
    'PREFETCH_BUFFER': lambda cfg: cfg.get('FATORI_ICACHE', 0) == 0,
    'ICACHE': lambda cfg: cfg.get('FATORI_ICACHE', 0) == 1,
    'BRANCH_PREDICT': lambda cfg: cfg.get('FATORI_BRANCH_PRED', 0) == 1,
    'MULTDIV': lambda cfg: cfg.get('FATORI_RV32M', 'None') != 'None',
    'WB_STAGE': lambda cfg: cfg.get('FATORI_WSTAGE', 0) == 1,  # Currently disabled
}

# Modules that are always present (unconditional)
ALWAYS_PRESENT_MODULES = ['ALU', 'LSU', 'IF_STAGE', 'ID_STAGE', 'EX_BLOCK']


# =============================================================================
# MODULE HIERARCHY
# =============================================================================
# Parent-child relationships for nested pblocks

MODULE_HIERARCHY = {
    'IF_STAGE': ['PREFETCH_BUFFER', 'ICACHE'],
    'ID_STAGE': ['CONTROLLER', 'DECODER'],
    'EX_BLOCK': ['ALU', 'MULTDIV'],
}


def get_parent_module(module):
    """Get parent module name, or None if module is top-level."""
    for parent, children in MODULE_HIERARCHY.items():
        if module in children:
            return parent
    return None


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Valid configuration values
VALID_RV32B_VALUES = ['None', 'Balanced', 'Full']
VALID_RV32M_VALUES = ['None', 'Slow', 'Fast']
VALID_MON_N_RANGE = (1, 5)  # MON_N can be 1 to 5

# Maximum allowed MON_N per module (for safety)
MAX_RECOMMENDED_MON_N = {
    'ALU': 5,          # Tested up to 5
    'LSU': 3,          # Untested beyond 3
    'CONTROLLER': 3,   # Untested
    'DECODER': 3,      # Anomaly at 3, recommend caution
    'IF_STAGE': 3,     # Bugs at 5, recommend max 3
    'MULTDIV': 3,      # Untested
}

DEFAULT_MAX_MON_N = 3