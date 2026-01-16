# =============================================================================
# FATORI-V • Execution • Benchmark Validator
# File: benchmark_validator.py
# -----------------------------------------------------------------------------
# Validates benchmark directories and configurations.
# =============================================================================

from pathlib import Path
from typing import List, Tuple
import fatori_settings as cfg
from scripts.exec.benchmark_discovery import BenchmarkInfo
from scripts.logging.logger import log_event


def validate_benchmark_directory(benchmark_info):
    """
    Validate that a benchmark directory exists and has required files.
    
    Each benchmark should have:
    - Directory exists
    - Makefile present (for building firmware)
    
    Args:
        benchmark_info: BenchmarkInfo object
    
    Returns:
        Tuple of (is_valid: bool, errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []
    
    bench_name = benchmark_info.name
    bench_path = benchmark_info.path
    
    # Check directory exists
    if not bench_path.exists():
        errors.append(f"{bench_name}: directory does not exist: {bench_path}")
        return False, errors, warnings
    
    if not bench_path.is_dir():
        errors.append(f"{bench_name}: path is not a directory: {bench_path}")
        return False, errors, warnings
    
    # Check for Makefile
    makefile = bench_path / "Makefile"
    if not makefile.exists():
        warnings.append(f"{bench_name}: no Makefile found (may use alternative build)")
    
    # Check for requirements.yaml (optional, so just warn)
    requirements = bench_path / "requirements.yaml"
    if not requirements.exists():
        log_event('BENCHMARK_NO_REQUIREMENTS_FILE', benchmark_name=bench_name)
    
    # Directory validation passed
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def validate_timeout_value(benchmark_info):
    """
    Validate timeout value is reasonable.
    
    Args:
        benchmark_info: BenchmarkInfo object
    
    Returns:
        Tuple of (is_valid: bool, errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []
    
    timeout = benchmark_info.timeout_s
    bench_name = benchmark_info.name
    
    # Check for invalid timeout values
    # Note: -1 is a special value meaning "no timeout" (infinite wait)
    if timeout == -1:
        # Valid: -1 means no timeout, benchmark runs until completion
        pass
    elif timeout <= 0:
        # Invalid: other negative values or zero are not allowed
        errors.append(f"{bench_name}: timeout must be positive or -1 for infinite (got {timeout}s)")
    # Warn about very short timeouts
    elif timeout < 10:
        warnings.append(f"{bench_name}: very short timeout ({timeout}s), benchmark may not complete")
    # Warn about very long timeouts
    elif timeout > 3600:
        warnings.append(f"{bench_name}: very long timeout ({timeout}s = {timeout/60:.1f}min)")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def validate_config_parameters(benchmark_info):
    """
    Validate benchmark configuration parameters.
    
    Args:
        benchmark_info: BenchmarkInfo object
    
    Returns:
        Tuple of (is_valid: bool, errors: List[str], warnings: List[str])
    """
    from scripts.exec.benchmark_config import validate_benchmark_config
    
    # Use the validator from benchmark_config
    is_valid, errors, warnings = validate_benchmark_config(
        benchmark_info.name,
        benchmark_info.config,
        benchmark_info.category
    )
    
    return is_valid, errors, warnings


def validate_single_benchmark(benchmark_info):
    """
    Perform all validation checks on a single benchmark.
    
    Args:
        benchmark_info: BenchmarkInfo object
    
    Returns:
        Tuple of (is_valid: bool, errors: List[str], warnings: List[str])
    """
    all_errors = []
    all_warnings = []
    
    # Validate directory
    valid, errors, warnings = validate_benchmark_directory(benchmark_info)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Validate timeout
    valid, errors, warnings = validate_timeout_value(benchmark_info)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Validate config parameters
    valid, errors, warnings = validate_config_parameters(benchmark_info)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    is_valid = len(all_errors) == 0
    
    return is_valid, all_errors, all_warnings


def validate_benchmarks(config):
    """
    Validate all benchmarks in configuration.
    
    This performs comprehensive validation including:
    - Directory existence
    - Required files present
    - Timeout values reasonable
    - Configuration parameters valid
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Tuple of (errors: List[str], warnings: List[str])
    """
    from scripts.exec.benchmark_discovery import discover_benchmarks, filter_enabled_benchmarks
    
    log_event('BENCHMARKS_VALIDATION_START')
    
    # Discover all benchmarks
    all_benchmarks = discover_benchmarks(config)
    
    # Validate only enabled benchmarks (others don't matter for execution)
    enabled_benchmarks = filter_enabled_benchmarks(all_benchmarks)
    
    if not enabled_benchmarks:
        log_event('BENCHMARKS_VALIDATION_NONE_ENABLED')
        return [], ["No enabled benchmarks"]
    
    # Validate each benchmark
    all_errors = []
    all_warnings = []
    
    for benchmark_info in enabled_benchmarks:
        log_event('BENCHMARK_VALIDATING', benchmark_name=benchmark_info.name)
        
        is_valid, errors, warnings = validate_single_benchmark(benchmark_info)
        
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        
        if is_valid:
            log_event('BENCHMARK_VALID', benchmark_name=benchmark_info.name)
        else:
            log_event('BENCHMARK_INVALID', 
                      benchmark_name=benchmark_info.name,
                      error_count=len(errors))
    
    # Summary
    log_event('BENCHMARKS_VALIDATION_COMPLETE',
              error_count=len(all_errors),
              warning_count=len(all_warnings))
    
    return all_errors, all_warnings