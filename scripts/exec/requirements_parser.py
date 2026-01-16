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
    Parse requirements.yaml for a benchmark to extract build dependencies.
    
    Each benchmark can have a requirements.yaml file that specifies:
    - libraries: List of library flags (e.g., ["-lm", "-lgcc"])
    
    Args:
        benchmark_name: Name of the benchmark (e.g., "coremark")
    
    Returns:
        Dictionary with requirements:
        {
            'llib': String for LLIB make parameter (e.g., "-lm -lgcc"),
                   or None if no libraries required
        }
    """
    # Construct path to requirements file
    requirements_path = cfg.BENCHMARKS_DIR / benchmark_name / "requirements.yaml"
    
    if not requirements_path.exists():
        log_event('BENCHMARK_NO_REQUIREMENTS', benchmark_name=benchmark_name)
        return {'llib': None}
    
    try:
        with requirements_path.open('r') as f:
            requirements = yaml.safe_load(f)
        
        if not requirements or not isinstance(requirements, dict):
            log_event('BENCHMARK_REQUIREMENTS_INVALID', benchmark_name=benchmark_name)
            return {'llib': None}
        
        # Extract libraries list
        libraries = requirements.get('libraries', [])
        
        if not libraries or not isinstance(libraries, list):
            return {'llib': None}
        
        # Convert library list to LLIB string
        # Example: ["-lm", "-lgcc"] -> "-lm -lgcc"
        llib_string = " ".join(libraries)
        
        log_event('BENCHMARK_REQUIREMENTS_LOADED', 
                  benchmark_name=benchmark_name,
                  llib=llib_string)
        
        return {'llib': llib_string}
    
    except Exception as e:
        log_event('BENCHMARK_REQUIREMENTS_ERROR',
                  benchmark_name=benchmark_name,
                  error_message=str(e))
        return {'llib': None}


def get_benchmark_libraries(benchmark_name):
    """
    Get library requirements for a benchmark as a make LLIB parameter.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        String for LLIB parameter, or None if no libraries required
    """
    requirements = parse_benchmark_requirements(benchmark_name)
    return requirements.get('llib')


def get_all_benchmark_requirements(config):
    """
    Get requirements for all enabled benchmarks.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary mapping benchmark names to their requirements
    """
    from scripts.common.yaml_io.yaml_helpers import get_benchmarks, is_benchmark_enabled
    
    benchmarks = get_benchmarks(config)
    all_requirements = {}
    
    for benchmark_name in benchmarks:
        if is_benchmark_enabled(config, benchmark_name):
            requirements = parse_benchmark_requirements(benchmark_name)
            all_requirements[benchmark_name] = requirements
    
    return all_requirements