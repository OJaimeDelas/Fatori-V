# =============================================================================
# FATORI-V • Mappings • Benchmark Mapping
# File: benchmark_mapping.py
# -----------------------------------------------------------------------------
# Maps benchmark names to configuration macros and categorizes benchmarks.
# =============================================================================

import fatori_settings as cfg
from config.constants import MACRO_PREFIX

# Benchmark iteration count macros
# These are used in bench_config.h to control how many times benchmarks run
BENCHMARK_CONFIG_MACROS = {
    "coremark": f"{MACRO_PREFIX}COREMARK_ITERATIONS",
    "dhrystone": f"{MACRO_PREFIX}DHRYSTONE_ITERATIONS",
    "embench_iot": f"{MACRO_PREFIX}EMBENCH_ITERATIONS",
}

# FATORI stress test target macros
# Each stress test targets specific fault detection capabilities
FATORI_STRESS_TARGETS = [
    "ctrl",      # Control flow stress test
    "alu",       # ALU stress test
    "load",      # Load/store stress test
    "branch",    # Branch prediction stress test
    "mult",      # Multiplier stress test (if RV32M enabled)
]

# Embench-IoT sub-benchmarks
# These are individual benchmarks within the Embench-IoT suite
EMBENCH_IOT_BENCHMARKS = [
    "aha-mont64",
    "crc32",
    "cubic",
    "edn",
    "huffbench",
    "matmult-int",
    "minver",
    "nbody",
    "nettle-aes",
    "nettle-sha256",
    "nsichneu",
    "picojpeg",
    "qrduino",
    "sglib-combined",
    "slre",
    "st",
    "statemate",
    "ud",
    "wikisort",
]


def get_iterations_macro(benchmark_name):
    """
    Get the iterations macro name for a benchmark.
    
    This macro is defined in bench_config.h to control how many
    times the benchmark executes.
    
    Args:
        benchmark_name: Name of the benchmark (e.g., "coremark")
    
    Returns:
        String containing the macro name, or None if benchmark doesn't use iterations
    """
    benchmark_lower = benchmark_name.lower()
    return BENCHMARK_CONFIG_MACROS.get(benchmark_lower)


def get_fatori_stress_target_macros():
    """
    Get list of macro names for FATORI stress test targets.
    
    Each stress test has a corresponding macro that enables it.
    
    Returns:
        Dictionary mapping stress test name to macro name
    """
    macros = {}
    for target in FATORI_STRESS_TARGETS:
        macro_name = f"{MACRO_PREFIX}STRESS_{target.upper()}"
        macros[target] = macro_name
    
    return macros


def get_embench_subbench_macros():
    """
    Get list of macro names for Embench-IoT sub-benchmarks.
    
    Returns:
        Dictionary mapping sub-benchmark name to macro name
    """
    macros = {}
    for subbench in EMBENCH_IOT_BENCHMARKS:
        # Convert benchmark name to valid macro name (replace hyphens with underscores)
        macro_suffix = subbench.upper().replace("-", "_")
        macro_name = f"{MACRO_PREFIX}EMBENCH_{macro_suffix}"
        macros[subbench] = macro_name
    
    return macros


def is_embench_iot(benchmark_name):
    """
    Check if a benchmark is part of Embench-IoT suite.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        Boolean indicating if benchmark is in Embench-IoT suite
    """
    benchmark_lower = benchmark_name.lower()
    
    # Check main benchmark name
    if benchmark_lower == "embench_iot" or benchmark_lower == "embench-iot":
        return True
    
    # Check if it's a specific sub-benchmark
    return benchmark_lower in [b.lower() for b in EMBENCH_IOT_BENCHMARKS]


def is_fatori_stress(benchmark_name):
    """
    Check if a benchmark is a FATORI stress test.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        Boolean indicating if benchmark is a FATORI stress test
    """
    benchmark_lower = benchmark_name.lower()
    
    # Check for general stress test
    if "stress" in benchmark_lower or "fatori" in benchmark_lower:
        return True
    
    # Check if it matches a specific stress target
    return benchmark_lower in [t.lower() for t in FATORI_STRESS_TARGETS]


def get_benchmark_category(benchmark_name):
    """
    Categorize a benchmark into its type.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        String indicating category: "embench_iot", "fatori_stress", "coremark",
        "dhrystone", or "unknown"
    """
    benchmark_lower = benchmark_name.lower()
    
    if is_embench_iot(benchmark_lower):
        return "embench_iot"
    elif is_fatori_stress(benchmark_lower):
        return "fatori_stress"
    elif "coremark" in benchmark_lower:
        return "coremark"
    elif "dhrystone" in benchmark_lower:
        return "dhrystone"
    else:
        return "unknown"


def get_all_fatori_stress_targets():
    """
    Get list of all FATORI stress test target names.
    
    Returns:
        List of stress test target strings
    """
    return FATORI_STRESS_TARGETS.copy()


def get_all_embench_benchmarks():
    """
    Get list of all Embench-IoT sub-benchmark names.
    
    Returns:
        List of Embench-IoT benchmark strings
    """
    return EMBENCH_IOT_BENCHMARKS.copy()