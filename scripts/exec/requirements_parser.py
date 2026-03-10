# =============================================================================
# FATORI-V • Execution • Requirements Parser
# File: requirements_parser.py
# -----------------------------------------------------------------------------
# Parses benchmark requirements.yaml files for build dependencies.
# =============================================================================

from pathlib import Path
import yaml
import fatori_settings as cfg
from scripts.logging.logger import log_event


def parse_benchmark_requirements(benchmark_name):
    """
    Parse requirements.yaml for a benchmark to extract build flags.
    
    Each benchmark can have a requirements.yaml file that specifies:
    - flags: Dictionary of make flags (e.g., {LLIB: "-lm -lgcc", targets: "1 2 3"})
    
    Args:
        benchmark_name: Name of the benchmark (e.g., "coremark")
    
    Returns:
        Dictionary mapping flag names to their values:
        {
            'LLIB': '-lm -lgcc',
            'targets': '1 2 3',
            ...
        }
        Returns empty dict {} if no requirements file or no flags
    """
    # Construct path to requirements file
    requirements_path = cfg.BENCHMARKS_DIR / benchmark_name / "requirements.yaml"
    
    if not requirements_path.exists():
        log_event('BENCHMARK_NO_REQUIREMENTS', benchmark_name=benchmark_name)
        return {}
    
    try:
        with requirements_path.open('r') as f:
            requirements = yaml.safe_load(f)
        
        if not requirements or not isinstance(requirements, dict):
            log_event('BENCHMARK_REQUIREMENTS_INVALID', benchmark_name=benchmark_name)
            return {}
        
        # Extract flags dictionary
        flags = requirements.get('flags', {})
        
        if not flags or not isinstance(flags, dict):
            return {}
        
        # Process all flags - strip quotes from string values
        processed_flags = {}
        for flag_name, flag_value in flags.items():
            if isinstance(flag_value, str):
                # Strip surrounding quotes if present
                processed_flags[flag_name] = flag_value.strip('"').strip("'")
            else:
                # Convert non-string values to string
                processed_flags[flag_name] = str(flag_value)
        
        log_event('BENCHMARK_REQUIREMENTS_LOADED', 
                  benchmark_name=benchmark_name,
                  flags=processed_flags)
        
        return processed_flags
    
    except Exception as e:
        log_event('BENCHMARK_REQUIREMENTS_ERROR',
                  benchmark_name=benchmark_name,
                  error_message=str(e))
        return {}


def get_benchmark_flags(benchmark_name):
    """
    Get all make flags for a benchmark from requirements.yaml.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        Dictionary mapping flag names to values (e.g., {'LLIB': '-lm', 'targets': '1 2 3'})
        Returns empty dict {} if no requirements
    """
    return parse_benchmark_requirements(benchmark_name)


def get_all_benchmark_requirements(config):
    """
    Get requirements for all enabled benchmarks.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary mapping benchmark names to their flag dictionaries
    """
    from scripts.common.yaml_io.yaml_helpers import get_benchmarks, is_benchmark_enabled
    
    benchmarks = get_benchmarks(config)
    all_requirements = {}
    
    for benchmark_name in benchmarks:
        if is_benchmark_enabled(config, benchmark_name):
            flags = parse_benchmark_requirements(benchmark_name)
            all_requirements[benchmark_name] = flags
    
    return all_requirements
