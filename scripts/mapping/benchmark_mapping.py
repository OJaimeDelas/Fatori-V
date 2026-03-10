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
    "coremark": "ITERATIONS",
    "dhrystone": "ITERATIONS",
}

# FATORI stress test target macros
# Maps target names to their enable macros in bench_config.h
FATORI_STRESS_TARGET_MACROS = {
    "alu": "FATORI_TARGET_ALU",
    "multiplier": "FATORI_TARGET_MULTIPLIER",
    "decoder": "FATORI_TARGET_DECODER",
    "controller": "FATORI_TARGET_CONTROLLER",
    "lsu": "FATORI_TARGET_LSU",
    "branch_pred": "FATORI_TARGET_BRANCH_PREDICT",
    "compressed": "FATORI_TARGET_COMPRESSED",
}

# Embench-IoT sub-benchmark macros
# Maps sub-benchmark names to their enable macros in bench_config.h
EMBENCH_IOT_MACROS = {
    "aha-mont64": "EMBENCH_AHA_MONT64",
    "crc32": "EMBENCH_CRC32",
    "cubic": "EMBENCH_CUBIC",
    "edn": "EMBENCH_EDN",
    "huffbench": "EMBENCH_HUFFBENCH",
    "matmult-int": "EMBENCH_MATMULT_INT",
    "md5sum": "EMBENCH_MD5SUM",
    "minver": "EMBENCH_MINVER",
    "nbody": "EMBENCH_NBODY",
    "nettle-aes": "EMBENCH_NETTLE_AES",
    "nettle-sha256": "EMBENCH_NETTLE_SHA256",
    "nsichneu": "EMBENCH_NSICHNEU",
    "picojpeg": "EMBENCH_PICOJPEG",
    "primecount": "EMBENCH_PRIMECOUNT",
    "qrduino": "EMBENCH_QRDUINO",
    "sglib-combined": "EMBENCH_SGLIB_COMBINED",
    "slre": "EMBENCH_SLRE",
    "st": "EMBENCH_ST",
    "statemate": "EMBENCH_STATEMATE",
    "ud": "EMBENCH_UD",
    "wikisort": "EMBENCH_WIKISORT",
}

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
    Get mapping of FATORI stress test targets to their enable macros.
    
    Each stress test has a corresponding macro that enables it.
    
    Returns:
        Dictionary mapping stress test name to macro name
    """
    return FATORI_STRESS_TARGET_MACROS


def get_embench_subbench_macros():
    """
    Get mapping of Embench-IoT sub-benchmarks to their enable macros.
    
    Each sub-benchmark has a corresponding enable macro.
    
    Returns:
        Dictionary mapping benchmark name to macro name
    """
    return EMBENCH_IOT_MACROS


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
    return benchmark_lower in [t.lower() for t in FATORI_STRESS_TARGET_MACROS.keys()]


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
    return list(FATORI_STRESS_TARGET_MACROS.keys())


def get_all_embench_benchmarks():
    """
    Get list of all Embench-IoT sub-benchmark names.
    
    Returns:
        List of Embench-IoT benchmark strings
    """
    return EMBENCH_IOT_BENCHMARKS.copy()