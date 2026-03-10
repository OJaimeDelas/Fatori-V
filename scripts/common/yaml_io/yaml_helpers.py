# =============================================================================
# FATORI-V • YAML I/O • YAML Helpers
# File: yaml_helpers.py
# -----------------------------------------------------------------------------
# Helper functions to extract configuration values from run YAML.
# =============================================================================

from scripts.common.common_settings import *
import fatori_settings as cfg


def get_board_name(config):
    """
    Extract the board name from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Board name string, or default board if not specified
    """
    board = get_nested(config, KEY_RUN, KEY_RUN_HARDWARE, KEY_HW_BOARD)
    return board if board else cfg.DEFAULT_BOARD


def get_run_name(config):
    """
    Extract the run name from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Run name string, or None if not specified
    """
    return get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, KEY_IDENT_NAME)


def get_global_seed(config):
    """
    Extract the global seed from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Integer seed value, or default seed if not specified
    """
    seed = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, KEY_IDENT_SEED)
    return seed if seed is not None else cfg.DEFAULT_GLOBAL_SEED


def get_feature_state(config, feature_name):
    """
    Get the enabled/disabled state of a feature.
    
    Args:
        config: The loaded YAML configuration dictionary
        feature_name: Name of the feature (e.g., KEY_FEAT_FAULT_MANAGER)
    
    Returns:
        Boolean indicating if feature is enabled
    """
    value = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, feature_name)
    
    # Handle boolean directly
    if isinstance(value, bool):
        return value
    
    # Handle string representations
    if value is None:
        return False
    
    return is_on(value)


def get_isa_extension_state(config, isa_ext):
    """
    Get the enabled/disabled state of an ISA extension.
    
    Args:
        config: The loaded YAML configuration dictionary
        isa_ext: ISA extension key (e.g., KEY_ISA_RV32M)
    
    Returns:
        Boolean indicating if extension is enabled
    """
    value = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, isa_ext)
    
    # Handle boolean directly
    if isinstance(value, bool):
        return value
    
    # Handle string representations
    if value is None:
        return False
    
    return is_on(value)


def get_ftm_state(config, ftm_name):
    """
    Get the enabled/disabled state of a fault tolerance mechanism.
    
    Args:
        config: The loaded YAML configuration dictionary
        ftm_name: FTM key (e.g., KEY_FTM_REG_MON)
    
    Returns:
        Boolean indicating if FTM is enabled
    """
    value = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, ftm_name)
    
    # Handle boolean directly
    if isinstance(value, bool):
        return value
    
    # Handle string representations
    if value is None:
        return False
    
    return is_on(value)


def get_benchmarks(config):
    """
    Extract the benchmarks section from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary of benchmark configurations, or empty dict if not present
    """
    benchmarks = get_nested(config, KEY_GENERAL, KEY_GEN_BENCHMARKS)
    return benchmarks if isinstance(benchmarks, dict) else {}


def is_benchmark_enabled(config, benchmark_name):
    """
    Check if a specific benchmark is enabled.
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of the benchmark
    
    Returns:
        Boolean indicating if benchmark is enabled
    """
    benchmarks = get_benchmarks(config)
    
    # Check if benchmark exists in config
    if benchmark_name not in benchmarks:
        return False
    
    bench_config = benchmarks[benchmark_name]
    
    # Handle boolean directly
    if isinstance(bench_config, bool):
        return bench_config
    
    # Handle dictionary with 'enable' key
    if isinstance(bench_config, dict):
        enable_value = bench_config.get(KEY_BENCH_ENABLE)
        
        if isinstance(enable_value, bool):
            return enable_value
        
        if enable_value is None:
            # If no explicit enable key, default to enabled
            return True
        
        return is_on(enable_value)
    
    # Default to disabled for unexpected formats
    return False


def is_fi_enabled_for_benchmark(config, benchmark_name):
    """
    Check if fault injection is enabled globally (applies to all benchmarks).
    
    Note: FI is now controlled globally via general.fault_injection.enable,
    not per-benchmark. This function maintains compatibility with existing code.
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of the benchmark (unused, kept for compatibility)
    
    Returns:
        Boolean indicating if FI is enabled globally
    """
    return any_benchmark_has_fi(config)


def any_benchmark_has_fi(config):
    """
    Check if fault injection is enabled globally for all benchmarks.
    
    FI is controlled by general.fault_injection.enable (on/off).
    When enabled, ALL active benchmarks will have FI enabled.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Boolean indicating if FI is enabled globally
    """
    fi_config = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    fi_enable = fi_config.get("enable", False)
    
    # Normalize to boolean
    if isinstance(fi_enable, str):
        return is_on(fi_enable)
    
    return bool(fi_enable)

def is_enabled(value):
    """
    Check if a configuration value indicates enabled state.
    
    Handles multiple representations:
    - Boolean: True = enabled, False = disabled
    - String: "on"/"yes"/"true"/"1" = enabled, "off"/"no"/"false"/"0" = disabled
    - None: disabled
    
    Args:
        value: Configuration value to check
    
    Returns:
        Boolean indicating if value represents enabled state
    """
    if value is None:
        return False
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('on', 'yes', 'true', '1')
    
    # Numeric non-zero is enabled
    return bool(value)