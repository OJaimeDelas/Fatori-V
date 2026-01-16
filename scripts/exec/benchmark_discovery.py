# =============================================================================
# FATORI-V • Execution • Benchmark Discovery
# File: benchmark_discovery.py
# -----------------------------------------------------------------------------
# Discovers and creates BenchmarkInfo objects from configuration and filesystem.
# =============================================================================

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import fatori_settings as cfg
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import (
    get_benchmarks,
    is_benchmark_enabled,
    is_fi_enabled_for_benchmark,
    get_nested
)
from scripts.mapping.benchmark_mapping import get_benchmark_category
from scripts.exec.requirements_parser import parse_benchmark_requirements
from scripts.logging import logger


@dataclass
class BenchmarkInfo:
    """
    Container for all information about a benchmark.
    
    This dataclass holds everything needed to execute a benchmark:
    configuration, requirements, paths, and execution settings.
    """
    name: str                          # Benchmark name (e.g., "coremark")
    path: Path                         # Path to benchmark directory
    category: str                      # Category: coremark, dhrystone, embench_iot, fatori_stress
    enabled: bool                      # Whether benchmark is enabled
    timeout_s: int                     # Execution timeout in seconds
    injection: bool                    # Whether fault injection is enabled
    requirements: Dict                 # Requirements from requirements.yaml (libraries, etc.)
    config: Dict                       # Benchmark-specific configuration from YAML
    
    def __str__(self):
        """String representation for logging."""
        status = "enabled" if self.enabled else "disabled"
        fi = "FI" if self.injection else "no FI"
        return f"{self.name} ({self.category}, {status}, {fi}, timeout={self.timeout_s}s)"


def get_benchmark_path(benchmark_name):
    """
    Get path to a benchmark directory.
    
    Benchmarks are located in benchmarks/<name>/ directory.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        Path object to benchmark directory
    """
    return cfg.BENCHMARKS_DIR / benchmark_name


def check_benchmark_exists(benchmark_name):
    """
    Check if a benchmark directory exists.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        Boolean indicating if directory exists
    """
    bench_path = get_benchmark_path(benchmark_name)
    exists = bench_path.exists() and bench_path.is_dir()
    
    if not exists:
        logger.log_event('WARNING', warning_message=f"Benchmark directory not found: {bench_path}")
    
    return exists


def extract_benchmark_timeout(config, benchmark_name, bench_config):
    """
    Extract timeout setting for a benchmark.
    
    Timeout can be specified per-benchmark or use default.
    
    Args:
        config: Full configuration dictionary
        benchmark_name: Name of the benchmark
        bench_config: Benchmark-specific configuration
    
    Returns:
        Timeout in seconds (integer)
    """
    # Try to get timeout from benchmark config
    if isinstance(bench_config, dict):
        timeout = bench_config.get(KEY_BENCH_TIMEOUT)
        if timeout is not None:
            return int(timeout)
    
    # Fall back to default
    default_timeout = cfg.DEFAULT_BENCHMARK_TIMEOUT
    
    # Use category-specific defaults if available
    category = get_benchmark_category(benchmark_name)
    if category == "coremark":
        default_timeout = 300  # CoreMark typically takes 2-5 minutes
    elif category == "dhrystone":
        default_timeout = 60   # Dhrystone is faster
    elif category == "embench_iot":
        default_timeout = 120  # Embench varies
    elif category == "fatori_stress":
        default_timeout = 180  # Stress tests vary
    
    return default_timeout


def extract_benchmark_config(bench_config):
    """
    Extract benchmark-specific configuration dictionary.
    
    This extracts any custom configuration parameters for the benchmark
    (iterations, targets, sub-benchmarks, etc.)
    
    Args:
        bench_config: Benchmark configuration from YAML
    
    Returns:
        Dictionary with benchmark-specific config, or empty dict
    """
    if not isinstance(bench_config, dict):
        return {}
    
    # Get the 'config' sub-dictionary if present
    config_dict = bench_config.get(KEY_BENCH_CONFIG, {})
    
    # Also extract top-level config keys (iterations, targets, etc.)
    # that aren't standard keys (enable, timeout_s, injection)
    standard_keys = {KEY_BENCH_ENABLE, KEY_BENCH_TIMEOUT, KEY_BENCH_INJECTION, KEY_BENCH_CONFIG}
    
    extra_config = {
        k: v for k, v in bench_config.items()
        if k not in standard_keys
    }
    
    # Merge config dict and extra config (extra config takes precedence)
    merged_config = {**config_dict, **extra_config}
    
    return merged_config


def create_benchmark_info(config, benchmark_name, bench_config):
    """
    Create a BenchmarkInfo object from configuration.
    
    This combines information from multiple sources:
    - YAML configuration (enable, timeout, injection, config)
    - Filesystem (benchmark directory path)
    - Requirements file (libraries, dependencies)
    - Category detection (coremark, dhrystone, etc.)
    
    Args:
        config: Full configuration dictionary
        benchmark_name: Name of the benchmark
        bench_config: Benchmark-specific configuration from YAML
    
    Returns:
        BenchmarkInfo object
    """
    # Get basic information
    bench_path = get_benchmark_path(benchmark_name)
    category = get_benchmark_category(benchmark_name)
    enabled = is_benchmark_enabled(config, benchmark_name)
    injection = is_fi_enabled_for_benchmark(config, benchmark_name)
    timeout = extract_benchmark_timeout(config, benchmark_name, bench_config)
    bench_specific_config = extract_benchmark_config(bench_config)
    
    # Parse requirements.yaml if present
    requirements = parse_benchmark_requirements(benchmark_name)
    
    # Create BenchmarkInfo object
    info = BenchmarkInfo(
        name=benchmark_name,
        path=bench_path,
        category=category,
        enabled=enabled,
        timeout_s=timeout,
        injection=injection,
        requirements=requirements,
        config=bench_specific_config
    )
    
    return info


def discover_benchmarks(config):
    """
    Discover all benchmarks from configuration.
    
    This reads the benchmarks section of the configuration and creates
    BenchmarkInfo objects for each benchmark, including checking filesystem
    existence and parsing requirements.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        List of BenchmarkInfo objects (includes both enabled and disabled)
    """
    logger.log_event('DEBUG', debug_message="Discovering benchmarks...")
    
    # Get benchmarks section from config
    benchmarks_dict = get_benchmarks(config)
    
    if not benchmarks_dict:
        logger.log_event('WARNING', warning_message="No benchmarks configured")
        return []
    
    # Create BenchmarkInfo for each benchmark
    benchmark_infos = []
    
    for benchmark_name, bench_config in benchmarks_dict.items():
        logger.log_event('DEBUG', debug_message=f"Processing benchmark: {benchmark_name}")
        
        # Create BenchmarkInfo object
        info = create_benchmark_info(config, benchmark_name, bench_config)
        benchmark_infos.append(info)
        
        # Log discovery
        status = "enabled" if info.enabled else "disabled"
        exists = "found" if info.path.exists() else "missing"
        logger.log_event('DEBUG', debug_message=f"  {status} {info.name} [{info.category}] (dir: {exists})")
    
    logger.log_event('DEBUG', debug_message=f"Discovered {len(benchmark_infos)} benchmarks")
    
    # Count enabled
    enabled_count = sum(1 for b in benchmark_infos if b.enabled)
    logger.log_event('DEBUG', debug_message=f"  Enabled: {enabled_count}")
    logger.log_event('DEBUG', debug_message=f"  Disabled: {len(benchmark_infos) - enabled_count}")
    
    return benchmark_infos


def filter_enabled_benchmarks(benchmark_infos):
    """
    Filter list to only enabled benchmarks.
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
    
    Returns:
        List of BenchmarkInfo objects (only enabled ones)
    """
    enabled = [b for b in benchmark_infos if b.enabled]
    logger.log_event('DEBUG', debug_message=f"Filtered to {len(enabled)} enabled benchmarks")
    return enabled


def filter_by_category(benchmark_infos, category):
    """
    Filter benchmarks by category.
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
        category: Category string (e.g., "coremark", "fatori_stress")
    
    Returns:
        List of BenchmarkInfo objects matching category
    """
    filtered = [b for b in benchmark_infos if b.category == category]
    return filtered


def has_fi_benchmarks(benchmark_infos):
    """
    Check if any benchmarks have fault injection enabled.
    
    Args:
        benchmark_infos: List of BenchmarkInfo objects
    
    Returns:
        Boolean indicating if any benchmark has FI enabled
    """
    return any(b.injection and b.enabled for b in benchmark_infos)