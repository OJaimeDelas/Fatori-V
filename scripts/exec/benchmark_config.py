# =============================================================================
# FATORI-V • Execution • Benchmark Config Extractor
# File: benchmark_config.py
# -----------------------------------------------------------------------------
# Extracts benchmark-specific configuration parameters from YAML.
# =============================================================================

from typing import Dict, List, Optional
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_benchmarks, get_nested
from scripts.mapping.benchmark_mapping import (
    get_benchmark_category,
    get_fatori_stress_target_macros,
    get_all_embench_benchmarks
)
from scripts.logging.logger import log_event


def get_coremark_config(bench_config):
    """
    Extract CoreMark-specific configuration.
    
    CoreMark configuration includes:
    - iterations: Number of iterations to run
    
    Args:
        bench_config: Benchmark configuration dictionary
    
    Returns:
        Dictionary with CoreMark configuration
    """
    config = {}
    
    # Default iterations for CoreMark
    default_iterations = 1000
    
    if isinstance(bench_config, dict):
        # Get iterations from config
        iterations = bench_config.get('iterations', default_iterations)
        config['iterations'] = int(iterations)
    else:
        config['iterations'] = default_iterations
    
    return config


def get_dhrystone_config(bench_config):
    """
    Extract Dhrystone-specific configuration.
    
    Dhrystone configuration includes:
    - iterations: Number of iterations to run
    
    Args:
        bench_config: Benchmark configuration dictionary
    
    Returns:
        Dictionary with Dhrystone configuration
    """
    config = {}
    
    # Default iterations for Dhrystone
    default_iterations = 1000
    
    if isinstance(bench_config, dict):
        # Get iterations from config
        iterations = bench_config.get('iterations', default_iterations)
        config['iterations'] = int(iterations)
    else:
        config['iterations'] = default_iterations
    
    return config


def get_fatori_stress_config(bench_config):
    """
    Extract FATORI stress test configuration.
    
    FATORI stress tests can target specific modules and run
    configurable iterations.
    
    Configuration includes:
    - iterations: Number of test iterations
    - targets: List of modules to stress (alu, ctrl, load, branch, mult)
    
    Args:
        bench_config: Benchmark configuration dictionary
    
    Returns:
        Dictionary with stress test configuration
    """
    config = {}
    
    # Default iterations
    default_iterations = 100
    
    if isinstance(bench_config, dict):
        # Get iterations
        iterations = bench_config.get('iterations', default_iterations)
        config['iterations'] = int(iterations)
        
        # Get targets list
        targets = bench_config.get('targets', [])
        if isinstance(targets, list):
            config['targets'] = targets
        else:
            # If no targets specified, enable all
            config['targets'] = list(get_fatori_stress_target_macros().keys())
    else:
        config['iterations'] = default_iterations
        config['targets'] = list(get_fatori_stress_target_macros().keys())
    
    return config


def get_embench_config(bench_config):
    """
    Extract Embench-IoT configuration.
    
    Embench-IoT is a suite of sub-benchmarks that can be
    individually enabled.
    
    Configuration includes:
    - iterations: Number of iterations per sub-benchmark
    - sub_benchmarks: List of specific sub-benchmarks to run
    
    Args:
        bench_config: Benchmark configuration dictionary
    
    Returns:
        Dictionary with Embench configuration
    """
    config = {}
    
    # Default iterations
    default_iterations = 1
    
    if isinstance(bench_config, dict):
        # Get iterations
        iterations = bench_config.get('iterations', default_iterations)
        config['iterations'] = int(iterations)
        
        # Get sub-benchmarks list
        sub_benchmarks = bench_config.get('sub_benchmarks', [])
        if isinstance(sub_benchmarks, list) and sub_benchmarks:
            config['sub_benchmarks'] = sub_benchmarks
        else:
            # If no sub-benchmarks specified, enable all
            config['sub_benchmarks'] = get_all_embench_benchmarks()
    else:
        config['iterations'] = default_iterations
        config['sub_benchmarks'] = get_all_embench_benchmarks()
    
    return config


def extract_benchmark_configs(config):
    """
    Extract all benchmark configurations from YAML.
    
    This processes each benchmark in the configuration and extracts
    category-specific parameters.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary mapping benchmark names to their extracted configurations:
        {
            'coremark': {'iterations': 1000},
            'fatori_stress': {'iterations': 100, 'targets': ['alu', 'ctrl']},
            ...
        }
    """
    log_event('BENCHMARK_CONFIG_EXTRACTION_START')
    
    benchmarks_dict = get_benchmarks(config)
    
    if not benchmarks_dict:
        log_event('BENCHMARK_CONFIG_EXTRACTION_NONE')
        return {}
    
    extracted = {}
    
    for benchmark_name, bench_config in benchmarks_dict.items():
        # Determine benchmark category
        category = get_benchmark_category(benchmark_name)
        
        # Extract category-specific configuration
        if category == "coremark":
            extracted[benchmark_name] = get_coremark_config(bench_config)
        elif category == "dhrystone":
            extracted[benchmark_name] = get_dhrystone_config(bench_config)
        elif category == "fatori_stress":
            extracted[benchmark_name] = get_fatori_stress_config(bench_config)
        elif category == "embench_iot":
            extracted[benchmark_name] = get_embench_config(bench_config)
        else:
            # Unknown category - extract generic config
            if isinstance(bench_config, dict):
                extracted[benchmark_name] = bench_config.copy()
            else:
                extracted[benchmark_name] = {}
        
        log_event('BENCHMARK_CONFIG_EXTRACTED',
                  benchmark_name=benchmark_name,
                  config=extracted[benchmark_name])
    
    return extracted


def validate_benchmark_config(benchmark_name, bench_config, category):
    """
    Validate that benchmark configuration is reasonable.
    
    This checks for common configuration errors like negative iterations,
    invalid targets, etc.
    
    Args:
        benchmark_name: Name of the benchmark
        bench_config: Extracted configuration dictionary
        category: Benchmark category
    
    Returns:
        Tuple of (is_valid: bool, errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []
    
    # Check iterations if present
    if 'iterations' in bench_config:
        iterations = bench_config['iterations']
        
        if iterations <= 0:
            errors.append(f"{benchmark_name}: iterations must be positive (got {iterations})")
        elif iterations > 100000:
            warnings.append(f"{benchmark_name}: very high iterations ({iterations}), may take long time")
    
    # Category-specific validation
    if category == "fatori_stress":
        targets = bench_config.get('targets', [])
        valid_targets = set(get_fatori_stress_target_macros().keys())
        
        for target in targets:
            if target.lower() not in valid_targets:
                warnings.append(f"{benchmark_name}: unknown stress target '{target}'")
    
    elif category == "embench_iot":
        sub_benchmarks = bench_config.get('sub_benchmarks', [])
        valid_subs = set(b.lower() for b in get_all_embench_benchmarks())
        
        for sub in sub_benchmarks:
            if sub.lower() not in valid_subs:
                warnings.append(f"{benchmark_name}: unknown sub-benchmark '{sub}'")
    
    is_valid = len(errors) == 0
    
    return is_valid, errors, warnings