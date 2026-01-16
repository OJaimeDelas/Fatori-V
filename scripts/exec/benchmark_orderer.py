# =============================================================================
# FATORI-V • Execution • Benchmark Orderer
# File: benchmark_orderer.py
# -----------------------------------------------------------------------------
# Orders benchmarks for execution based on configuration and dependencies.
# =============================================================================

from typing import List
from scripts.exec.benchmark_discovery import BenchmarkInfo
from scripts.logging.logger import log_event


def order_by_yaml_sequence(benchmark_infos):
    """
    Keep benchmarks in the order they appear in YAML.
    
    This is the default ordering - benchmarks execute in the
    same order as they appear in the configuration file.
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
    
    Returns:
        List of BenchmarkInfo objects (same order as input)
    """
    # No reordering - return as-is
    return benchmark_infos


def order_by_category(benchmark_infos):
    """
    Order benchmarks by category.
    
    This groups benchmarks by type, which can be useful for
    organizing results or targeting specific benchmark suites.
    
    Order: coremark, dhrystone, fatori_stress, embench_iot, unknown
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
    
    Returns:
        List of BenchmarkInfo objects (ordered by category)
    """
    # Define category priority
    category_order = {
        'coremark': 0,
        'dhrystone': 1,
        'fatori_stress': 2,
        'embench_iot': 3,
        'unknown': 4
    }
    
    # Sort by category priority
    sorted_benchmarks = sorted(
        benchmark_infos,
        key=lambda b: (category_order.get(b.category, 999), b.name)
    )
    
    return sorted_benchmarks


def order_by_fi_status(benchmark_infos):
    """
    Order benchmarks with FI-disabled first, FI-enabled last.
    
    This is useful when you want to run non-FI benchmarks first
    to verify basic functionality before running FI campaigns.
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
    
    Returns:
        List of BenchmarkInfo objects (non-FI first, FI last)
    """
    # Sort by injection status (False before True)
    sorted_benchmarks = sorted(
        benchmark_infos,
        key=lambda b: (b.injection, b.name)
    )
    
    return sorted_benchmarks


def order_by_timeout(benchmark_infos, ascending=True):
    """
    Order benchmarks by timeout duration.
    
    This can be useful to run quick benchmarks first (ascending)
    or long benchmarks first (descending).
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
        ascending: If True, shortest timeout first; if False, longest first
    
    Returns:
        List of BenchmarkInfo objects (ordered by timeout)
    """
    sorted_benchmarks = sorted(
        benchmark_infos,
        key=lambda b: b.timeout_s,
        reverse=not ascending
    )
    
    return sorted_benchmarks


def order_benchmarks(benchmark_infos, strategy='yaml_sequence'):
    """
    Order benchmarks for execution based on specified strategy.
    
    Available strategies:
    - 'yaml_sequence': Keep order from YAML (default)
    - 'category': Group by benchmark category
    - 'fi_status': Non-FI first, then FI-enabled
    - 'timeout_asc': Shortest timeout first
    - 'timeout_desc': Longest timeout first
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
        strategy: Ordering strategy name
    
    Returns:
        List of BenchmarkInfo objects (in execution order)
    """
    log_event('BENCHMARKS_ORDERING', strategy=strategy)
    
    if strategy == 'yaml_sequence':
        ordered = order_by_yaml_sequence(benchmark_infos)
    elif strategy == 'category':
        ordered = order_by_category(benchmark_infos)
    elif strategy == 'fi_status':
        ordered = order_by_fi_status(benchmark_infos)
    elif strategy == 'timeout_asc':
        ordered = order_by_timeout(benchmark_infos, ascending=True)
    elif strategy == 'timeout_desc':
        ordered = order_by_timeout(benchmark_infos, ascending=False)
    else:
        log_event('BENCHMARKS_ORDERING_UNKNOWN', strategy=strategy)
        ordered = order_by_yaml_sequence(benchmark_infos)
    
    # Log the order
    for i, bench in enumerate(ordered, 1):
        log_event('BENCHMARK_ORDER', position=i, benchmark_name=bench.name)
    
    return ordered