# =============================================================================
# FATORI-V • Common Script Settings
# File: common_settings.py
# -----------------------------------------------------------------------------
# Settings shared across all script modules.
# =============================================================================

# YAML top-level section keys
KEY_RUN = "run"
KEY_GENERAL = "general"
KEY_SPECIFICS = "specifics"

# Run section keys
KEY_RUN_IDENTIFICATION = "identification"
KEY_RUN_HARDWARE = "hardware"
KEY_RUN_HW = "hardware"  # Alias for KEY_RUN_HARDWARE
KEY_RUN_EXECUTION = "execution"

# Keys under identification
KEY_IDENT_NAME = "name"
KEY_IDENT_SEED = "seed"
KEY_IDENT_DESCRIPTION = "description"

# Keys under hardware
KEY_HW_BOARD = "board"
KEY_HW_GRAB_TIMEOUT = "grab_timeout"

# Keys under general section

# Keys under general section
KEY_GEN_FEATURES = "features"
KEY_GEN_BENCHMARKS = "benchmarks"
KEY_GEN_RESULTS = "results"

# Keys under features
KEY_FEAT_FAULT_MANAGER = "fault_manager"
KEY_FEAT_FTMS = "fault_tolerance_mechanisms"
KEY_FEAT_PERF_MECH = "performance_mechanisms"
KEY_FEAT_ISA = "isa_extensions"

# Performance mechanism sub-keys
KEY_PERF_ICACHE = "icache"
KEY_PERF_WSTAGE = "wstage"
KEY_PERF_BRANCH_PRED = "branch_pred"
KEY_PERF_BRANCH_TALU = "branch_target_alu"

# ISA extension keys
KEY_ISA_RV32E = "RV32E"
KEY_ISA_RV32M = "RV32M"
KEY_ISA_RV32B = "RV32B"
KEY_ISA_RV32C = "RV32C"

# FTM keys under fault_tolerance_mechanisms
KEY_FTM_REG_MON = "register_m_of_n"
KEY_FTM_LOGIC_MON = "logic_m_of_n"
KEY_FTM_SELFTEST = "self_testing"
KEY_FTM_RF_ECC = "regfile_ecc"
KEY_FTM_RF_WE_GLITCH = "regfile_we_glitch"
KEY_FTM_RF_RADDR_GLITCH = "regfile_raddr_glitch"
KEY_FTM_HARDENED_PC = "hardened_pc"

# Keys under specifics section
KEY_SPEC_IBEX = "ibex"
KEY_SPEC_FT = "fault_tolerance"
KEY_SPEC_FI = "fault_injection"
KEY_SPEC_METRICS = "metrics"

# Keys under ibex specifics
KEY_IBEX_REGFILE = "regfile"
KEY_IBEX_MULTIPLIER = "multiplier"
KEY_IBEX_BIT_MANIP = "bit_manipulation"
KEY_IBEX_ICACHE = "icache"

# Keys under fault_tolerance specifics
KEY_FT_FAULT_MGR = "fault_manager"
KEY_FT_REG_MON = "reg_m_of_n"
KEY_FT_LOGIC_MON = "logic_m_of_n"

# Keys under fault_manager specifics
KEY_FM_RST_ON_MAJOR = "rst_on_major"
KEY_FM_WAIT_SLEEP = "wait_sleep_before_rst"

# Keys under metrics specifics
KEY_METRICS_LEVEL = "metrics_level"
KEY_METRICS_HPMC_NUM = "ibex_hpmc_num"
KEY_METRICS_HPMC_WIDTH = "ibex_hpmc_width"

# Keys under benchmarks
KEY_BENCH_ENABLE = "enable"
KEY_BENCH_TIMEOUT = "timeout_s"
KEY_BENCH_INJECTION = "injection"
KEY_BENCH_CONFIG = "config"

# Keys under results
KEY_RESULTS_VERIFIED_YAML = "verified_yaml"
KEY_RESULTS_FI_LOG_LEVEL = "fi_log_level"

# Keys under fault_injection
KEY_FI_AREA = "area"
KEY_FI_TIME = "time"

# Valid value sets for on/off boolean-like fields
VALID_ON_VALUES = {"on", "true", "yes", "1", "enabled"}
VALID_OFF_VALUES = {"off", "false", "no", "0", "disabled"}

# Valid values for specific fields
VALID_REGFILE = ["ff", "fpga", "file_latch"]
VALID_MULTIPLIER = ["none", "slow", "fast", "single_cycle"]
VALID_BIT_MANIP = ["none", "balanced", "ot_earlgrey", "full"]

# Valid FI profile types
VALID_AREA_PROFILES = ["device", "modules", "address_list", "target_list"]
VALID_TIME_PROFILES = ["uniform", "poisson", "microburst", "mmpp2", "ramp", "trace"]


def is_on(value):
    """
    Check if a value represents an 'on' state.
    
    Returns True if value is in the set of valid 'on' representations.
    Returns False if value is None or not recognized as 'on'.
    """
    if value is None:
        return False
    return str(value).lower() in VALID_ON_VALUES


def is_off(value):
    """
    Check if a value represents an 'off' state.
    
    Returns True if value is None or in the set of valid 'off' representations.
    """
    if value is None:
        return True
    return str(value).lower() in VALID_OFF_VALUES


def get_nested(data, *keys, default=None):
    """
    Safely retrieve a nested dictionary value.
    
    Args:
        data: The dictionary to traverse
        *keys: Sequence of keys to follow
        default: Value to return if any key is not found
    
    Returns:
        The value at the nested location, or default if not found.
    
    Example:
        get_nested(cfg, "general", "features", "fault_manager", default=False)
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current