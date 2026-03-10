# =============================================================================
# FATORI-V • Pblock Algorithm
# File: constants.py
# -----------------------------------------------------------------------------
# Baseline module sizes, scaling factors, and FPGA specifications from
# empirical characterization (Chapter 7, Table 7.3)
# =============================================================================

# =============================================================================
# BASELINE MODULE SIZES (C01 - Absolute Baseline)
# =============================================================================
# Measured with all features disabled:
# - ICACHE=0, RV32B=None, RV32M=None, BRANCH_PRED=0, BRANCH_TALU=0, WSTAGE=0
# - All MON_N=1, All FTMs=0, METRIC_LAYER=0

BASELINE_SIZES = {
    'ALU': 238,                # Arithmetic Logic Unit
    'CONTROLLER': 129,         # Control FSM
    'DECODER': 93,             # Instruction decoder
    'LSU': 154,                # Load/Store Unit
    'IF_STAGE': 431,           # Instruction Fetch stage (with prefetch)
    'ID_STAGE': 365,           # Instruction Decode stage (includes CTRL+DEC)
    'EX_BLOCK': 238,           # Execution block (ALU only, no multiplier)
    'WB_STAGE': 33,            # Writeback stage (merged mode)
    'PREFETCH_BUFFER': 168,    # Prefetch buffer (mutually exclusive with ICACHE)
    'BRANCH_PREDICT': 38,      # Branch predictor module
    'MULTDIV': 466,            # Multiplier/Divider (Fast variant baseline)
    'ICACHE': 4,               # I-cache wrapper (actual cache in BRAM)
    'FAULT_MGR': 1,            # Fault manager baseline
}

# Name aliases for user-friendly config names
NAME_ALIASES = {
    'BRANCH_PREDICTOR': 'BRANCH_PREDICT',
    'MULTIPLIER': 'MULTDIV',
    'MULT': 'MULTDIV',
    'FAULT_MANAGER': 'FAULT_MGR',
}

# =============================================================================
# MULTIPLICATIVE FEATURE FACTORS
# =============================================================================

# RV32B Bitmanip Extension impact on ALU (C02-C04)
RV32B_FACTORS = {
    'None': 1.0,       # No bitmanip (baseline)
    'Balanced': 4.2,   # Balanced: ALU=1000, factor=4.20
    'OTEarlGrey': 7.5, # OTEarlGrey: ALU=1772, factor=7.45 (rounded to 7.5)
    'Full': 8.9,       # Full: ALU=2118, factor=8.90
}

# ICACHE impact on IF_STAGE (C08)
ICACHE_FACTOR = 3.2  # IF_STAGE: 431 → 1382 (3.21×)

# =============================================================================
# ADDITIVE FEATURE COMPONENTS (LUTs)
# =============================================================================

# RV32B additive impact on DECODER (C02-C04)
S_RV32B_DECODER = {
    'None': 0,
    'Balanced': 55,      # DECODER +55 (C02)
    'OTEarlGrey': 59,    # DECODER +59 (C03)
    'Full': 56,          # DECODER +56 (C04)
}

# MULTDIV integration overhead (C05-C07)
S_MULTDIV_ALU = 18       # ALU +18 when RV32M enabled
S_MULTDIV_ID = 72        # ID_STAGE +72 when RV32M enabled

# Branch predictor integration overhead (C09)
S_BP_IF = 200            # IF_STAGE +200 when BRANCH_PRED enabled

# Branch Target ALU overhead (C10)
S_BTALU_ID = 38          # ID_STAGE +38 when BRANCH_TALU enabled

# Writeback stage overhead (C11)
S_WSTAGE_WB = 4          # WB_STAGE +4 when WSTAGE enabled
S_WSTAGE_CTRL = 11       # CONTROLLER +11 when WSTAGE enabled
S_WSTAGE_DEC = 11        # DECODER +11 when WSTAGE enabled

# MON logic wrapper overhead (C12-C24)
# Fixed overhead independent of N for N≥2
S_MON = 120              # All modules: +120 LUTs when MON enabled

# METRIC_LAYER overhead on FAULT_MGR (C25-C30)
# Only minimal overhead - bulk goes to cs_registers (not a pblock target)
S_ML_MAX = 5             # FAULT_MGR: 1→5 LUTs (max across all ML levels)

# Register MON overhead (C38-C45)
# Empirically shows optimization effects at 100% coverage
R_MODULE = 0             # No overhead (Vivado optimization dominates)

# Voter LUT coefficient per module for register_m_of_n overhead.
# Unit: LUTs per replication step, i.e. voter_luts = FF_BASELINE[module] × (N - 1).
# Calibrated from placed-design measurements with anchored cell patterns:
#   coefficient = (actual_module_luts_with_reg_mon − baseline_luts) / (N − 1)
# Coefficient derived from IF_STAGE observation (medium_ft, N=3):
#   (2270 − 431) / (3 − 1) = 919.5 → 920.  Applied uniformly: ≈3.3 LUTs/FF/step.
FF_BASELINE_SIZES = {
    'ALU':              66,   # 20 FFs × 3.3 LUTs/FF/step
    'CONTROLLER':      130,   # Kept from prior calibration; not observed to overflow
    'DECODER':          82,   # 25 FFs × 3.3 LUTs/FF/step
    'LSU':             280,   # Kept from prior calibration; not observed to overflow
    'IF_STAGE':        920,   # Calibrated: (2270 − 431) / (3 − 1) = 919.5 → 920
    'ID_STAGE':        680,   # Kept from prior calibration; not observed to overflow
    'EX_BLOCK':         30,   # Small pipeline register
    'WB_STAGE':         50,   # Write-back pipeline register
    'PREFETCH_BUFFER': 130,   # Prefetch FIFO state
    'BRANCH_PREDICT':   40,   # Branch history state
    'MULTDIV':          80,   # Multiplier state registers
    'ICACHE':           30,   # Cache control state
    'FAULT_MGR':        20,   # Fault counters/state
}

# =============================================================================
# MULTIPLIER VARIANTS (C05-C07)
# =============================================================================

MULTIPLIER_SIZES = {
    'None': 0,
    'Slow': 621,            # CONFIG 05: Multi-cycle, 0 DSP
    'Fast': 466,            # CONFIG 06: Fast, 1 DSP
    'Single_cycle': 434,    # CONFIG 07: Single-cycle, 4 DSP (corrected from 500)
}

# DSP resource consumption per MULTDIV variant
MULTIPLIER_DSP = {
    'None': 0,
    'Slow': 0,
    'Fast': 1,
    'Single_cycle': 4,
}

# =============================================================================
# SAFETY MARGINS (C32-C37 validation)
# =============================================================================
# Uniform 15% margin prevents placement failures across all feature combinations

SAFETY_MARGIN = 1.25     # Universal margin (M=1.15 from Chapter 7)

def get_safety_margin(module):
    """Get safety margin for any module (uniform)."""
    return SAFETY_MARGIN

# =============================================================================
# FATORI_FI MODE EFFECTS
# =============================================================================
# When FATORI_FI is enabled, CONTROLLER and DECODER are heavily optimized/merged

FATORI_FI_MERGED_MODULES = {
    'CONTROLLER': 18,  # 129L → 18L (86% reduction, merged into parent)
    'DECODER': 27,     # 93L → 27L (71% reduction, merged into parent)
}

# When FI mode is active, these modules should NOT be targeted independently
FI_MODE_INVALID_TARGETS = ['CONTROLLER', 'DECODER']

# =============================================================================
# CONDITIONAL MODULE RULES
# =============================================================================

CONDITIONAL_MODULES = {
    'PREFETCH_BUFFER': lambda cfg: cfg.get('FATORI_ICACHE', 0) == 0,
    'ICACHE': lambda cfg: cfg.get('FATORI_ICACHE', 0) == 1,
    'BRANCH_PREDICT': lambda cfg: cfg.get('FATORI_BRANCH_PRED', 0) == 1,
    'MULTDIV': lambda cfg: cfg.get('FATORI_RV32M', 'None') != 'None',
    'WB_STAGE': lambda cfg: cfg.get('FATORI_WSTAGE', 0) == 1,
    'FAULT_MGR': lambda cfg: cfg.get('FATORI_FAULT_MGR', 0) == 1,
}

ALWAYS_PRESENT_MODULES = ['ALU', 'LSU', 'IF_STAGE', 'ID_STAGE', 'EX_BLOCK']

# =============================================================================
# MODULE HIERARCHY
# =============================================================================

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
# FPGA SPECIFICATIONS (Xilinx XCKU040-FBVA676-1-C)
# =============================================================================

FPGA_SPECS = {
    'device': 'XCKU040-FBVA676-1-C',
    'family': 'Kintex UltraScale',
    
    'clock_regions': {
        'columns': 4,  # X0, X1, X2, X3
        'rows': 5,     # Y0, Y1, Y2, Y3, Y4
        'total': 20,   # 4×5 grid
    },
    
    'per_region': {
        'luts': 12000,
        'ffs': 24000,
        'slices': 2400,
        'brams': 60,
        'dsps': 120,  # Average - actual varies by column
    },
    
    'total': {
        'luts': 242400,
        'ffs': 484800,
        'slices': 48500,
        'brams': 600,
        'dsps': 1920,
    },
    
    'slice_geometry': {
        'luts_per_slice': 8,
        'ffs_per_slice': 16,
        'slices_per_clb': 1,
    },
    
    # Physical coordinate limits (4×5 grid, verified from Vivado)
    'slice_limits': {
        'x_max': 100,  # SLICE_X0 to SLICE_X100 (empirically verified)
        'y_max': 299,  # 5 rows × 60 slices - 1
    },
    
    # Clock region dimensions in slices (per-column, empirically verified)
    # X0Y*: X0-X23   (24 wide)
    # X1Y*: X24-X48  (25 wide)
    # X2Y*: X49-X75  (27 wide)
    # X3Y*: X76-X100 (25 wide)
    'region_dims': {
        'height': 60,  # All regions are 60 slices tall
        'col_widths': [24, 25, 27, 25],  # Width per column (X0, X1, X2, X3)
        'col_x_bases': [0, 24, 49, 76],  # Starting X coordinate per column
    },
    
    # DSP48 tile distribution (empirically verified from Vivado query)
    # All clock regions have DSP tiles on FBVA676 package (previous assumption was wrong)
    # DSP Y coordinates: 24 DSPs per region (Y0-Y23, Y24-Y47, ..., Y96-Y119)
    # DSP X columns per clock region column:
    #   X0Y*: DSP X0-X3   (4 DSP columns, 96 DSPs/region)
    #   X1Y*: DSP X4-X7   (4 DSP columns, 96 DSPs/region)
    #   X2Y*: DSP X8-X13  (6 DSP columns, 144 DSPs/region)
    #   X3Y*: DSP X14-X15 (2 DSP columns, 48 DSPs/region)
    'dsp_regions': {
        'dsps_per_region_row': 24,  # 24 DSPs tall per region (Y dimension)
        'dsp_x_primary': [0, 4, 8, 14],  # Primary DSP X column per clock region column
    },
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
    """
    slices = int(lut_count / 8.0 * 1.10) + 1
    return slices

# =============================================================================
# PLACEMENT STRATEGY
# =============================================================================

TARGET_REGION_UTILIZATION = 0.70  # 70% target per region

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

VALID_RV32B_VALUES = ['None', 'Balanced', 'OTEarlGrey', 'Full']
VALID_RV32M_VALUES = ['None', 'Slow', 'Fast', 'Single_cycle']
VALID_MON_N_RANGE = (1, 5)

# Maximum recommended MON_N (empirically N≥2 gives identical overhead)
MAX_RECOMMENDED_MON_N = {
    'ALU': 5,
    'LSU': 5,
    'CONTROLLER': 5,
    'DECODER': 5,
    'IF_STAGE': 5,
    'MULTDIV': 5,
}

DEFAULT_MAX_MON_N = 5