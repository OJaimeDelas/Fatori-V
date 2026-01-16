# =============================================================================
# FATORI-V • Execution • Benchmark Config Generator
# File: bench_config_generator.py
# -----------------------------------------------------------------------------
# Generates bench_config.h with benchmark configuration macros.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import MACRO_PREFIX, HEADER_WIDTH, BENCH_CONFIG_H
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import (
    get_benchmarks,
    is_benchmark_enabled,
)
from scripts.mapping.benchmark_mapping import (
    get_iterations_macro,
    get_fatori_stress_target_macros,
    get_embench_subbench_macros,
    is_embench_iot,
    is_fatori_stress,
    get_benchmark_category,
)
from scripts.logging import logger


def generate_header_guard(file_name):
    """
    Generate C header guard name from filename.
    
    Args:
        file_name: Name of the header file (e.g., "bench_config.h")
    
    Returns:
        Guard name (e.g., "BENCH_CONFIG_H")
    """
    return file_name.upper().replace(".", "_")


def generate_c_header_comment(file_name, description):
    """
    Generate C-style header comment block.
    
    Args:
        file_name: Name of the file
        description: Description of the file's purpose
    
    Returns:
        String with formatted header comment
    """
    lines = []
    
    # Top separator
    lines.append("//" + "=" * (HEADER_WIDTH - 1))
    
    # Title
    lines.append("// FATORI-V • Benchmark Configuration")
    
    # File name
    lines.append(f"// File: {file_name}")
    
    # Sub-separator
    lines.append("//" + "-" * (HEADER_WIDTH - 2))
    
    # Description
    lines.append(f"// {description}")
    
    # Bottom separator
    lines.append("//" + "=" * (HEADER_WIDTH - 1))
    
    return "\n".join(lines)


def generate_section_comment(section_name):
    """
    Generate C-style section divider comment.
    
    Args:
        section_name: Name of the section
    
    Returns:
        String with formatted section comment
    """
    lines = []
    
    # Section separator
    lines.append("// " + "-" * (HEADER_WIDTH - 3))
    
    # Section name
    lines.append(f"// {section_name}")
    
    # Section separator
    lines.append("// " + "-" * (HEADER_WIDTH - 3))
    
    return "\n".join(lines)


def generate_coremark_config(bench_config):
    """
    Generate configuration macros for CoreMark benchmark.
    
    Args:
        bench_config: Configuration dictionary for CoreMark
    
    Returns:
        List of C macro definition lines
    """
    lines = []
    
    # Get iterations value (default to 1000 if not specified)
    iterations = bench_config.get("iterations", 1000) if isinstance(bench_config, dict) else 1000
    
    # Define iterations macro
    macro_name = get_iterations_macro("coremark")
    lines.append(f"#define {macro_name} {iterations}")
    
    return lines


def generate_dhrystone_config(bench_config):
    """
    Generate configuration macros for Dhrystone benchmark.
    
    Args:
        bench_config: Configuration dictionary for Dhrystone
    
    Returns:
        List of C macro definition lines
    """
    lines = []
    
    # Get iterations value (default to 1000 if not specified)
    iterations = bench_config.get("iterations", 1000) if isinstance(bench_config, dict) else 1000
    
    # Define iterations macro
    macro_name = get_iterations_macro("dhrystone")
    lines.append(f"#define {macro_name} {iterations}")
    
    return lines


def generate_fatori_stress_config(bench_config):
    """
    Generate configuration macros for FATORI stress tests.
    
    Args:
        bench_config: Configuration dictionary for FATORI stress
    
    Returns:
        List of C macro definition lines
    """
    lines = []
    
    # Get iterations value (default to 100 if not specified)
    iterations = bench_config.get("iterations", 100) if isinstance(bench_config, dict) else 100
    
    # Define iterations macro
    lines.append(f"#define {MACRO_PREFIX}FATORI_ITERATIONS {iterations}")
    lines.append("")
    
    # Get enabled targets
    stress_macros = get_fatori_stress_target_macros()
    
    if isinstance(bench_config, dict):
        targets = bench_config.get("targets", [])
        
        # If targets is a list, enable those specific targets
        if isinstance(targets, list) and targets:
            lines.append("// Enabled stress test targets:")
            for target in targets:
                if target.lower() in stress_macros:
                    macro_name = stress_macros[target.lower()]
                    lines.append(f"#define {macro_name} 1")
        else:
            # Enable all targets by default
            lines.append("// All stress test targets enabled:")
            for target, macro_name in stress_macros.items():
                lines.append(f"#define {macro_name} 1")
    else:
        # Enable all targets by default
        lines.append("// All stress test targets enabled:")
        for target, macro_name in stress_macros.items():
            lines.append(f"#define {macro_name} 1")
    
    return lines


def generate_embench_config(bench_config):
    """
    Generate configuration macros for Embench-IoT benchmark suite.
    
    Args:
        bench_config: Configuration dictionary for Embench-IoT
    
    Returns:
        List of C macro definition lines
    """
    lines = []
    
    # Get iterations value (default to 1 if not specified)
    iterations = bench_config.get("iterations", 1) if isinstance(bench_config, dict) else 1
    
    # Define iterations macro
    macro_name = get_iterations_macro("embench_iot")
    lines.append(f"#define {macro_name} {iterations}")
    lines.append("")
    
    # Get sub-benchmark enable macros
    embench_macros = get_embench_subbench_macros()
    
    if isinstance(bench_config, dict):
        sub_benchmarks = bench_config.get("sub_benchmarks", [])
        
        # If sub_benchmarks is specified, enable only those
        if isinstance(sub_benchmarks, list) and sub_benchmarks:
            lines.append("// Enabled Embench-IoT sub-benchmarks:")
            for subbench in sub_benchmarks:
                if subbench.lower() in [k.lower() for k in embench_macros.keys()]:
                    # Find the correct macro name (case-insensitive)
                    for bench_name, macro_name in embench_macros.items():
                        if bench_name.lower() == subbench.lower():
                            lines.append(f"#define {macro_name} 1")
                            break
        else:
            # Enable all sub-benchmarks by default
            lines.append("// All Embench-IoT sub-benchmarks enabled:")
            for bench_name, macro_name in embench_macros.items():
                lines.append(f"#define {macro_name} 1")
    else:
        # Enable all sub-benchmarks by default
        lines.append("// All Embench-IoT sub-benchmarks enabled:")
        for bench_name, macro_name in embench_macros.items():
            lines.append(f"#define {macro_name} 1")
    
    return lines


def generate_single_bench_config_h(config, benchmark_name, output_dir):
    """
    Generate bench_config.h for a single benchmark.
    
    Creates a header file named bench_config_<benchmark>.h with configuration
    specific to that benchmark only.
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of the benchmark (e.g., 'coremark', 'fatori_stress')
        output_dir: Directory where file should be written
    
    Returns:
        Path to the generated file, or None if benchmark disabled/invalid
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if benchmark is enabled
    if not is_benchmark_enabled(config, benchmark_name):
        logger.log_event('DEBUG', debug_message=f"Skipping disabled benchmark: {benchmark_name}")
        return None
    
    # Get benchmark config
    benchmarks = get_benchmarks(config)
    bench_config = benchmarks.get(benchmark_name, {})
    
    # Determine output filename: bench_config_<benchmark>.h
    output_filename = f"bench_config_{benchmark_name}.h"
    output_path = output_dir / output_filename
    
    # Determine benchmark category
    category = get_benchmark_category(benchmark_name)
    
    logger.log_event('DEBUG', debug_message=f"Generating {output_filename} for {benchmark_name}")
    
    lines = []
    
    # Header comment
    lines.append(generate_c_header_comment(
        BENCH_CONFIG_H,
        f"Configuration for {benchmark_name} benchmark"
    ))
    lines.append("")
    
    # Header guard (always BENCH_CONFIG_H)
    guard_name = generate_header_guard(BENCH_CONFIG_H)
    lines.append(f"#ifndef {guard_name}")
    lines.append(f"#define {guard_name}")
    lines.append("")
    
    # Generate appropriate configuration based on category
    if category == "coremark":
        lines.extend(generate_coremark_config(bench_config))
    elif category == "dhrystone":
        lines.extend(generate_dhrystone_config(bench_config))
    elif category == "fatori_stress":
        lines.extend(generate_fatori_stress_config(bench_config))
    elif category == "embench_iot":
        lines.extend(generate_embench_config(bench_config))
    elif category == "hello_world":
        # Hello world has no config, just empty file
        lines.append("// No configuration needed for hello_world")
    else:
        # Unknown benchmark type
        lines.append(f"// Unknown benchmark type: {benchmark_name}")
    
    lines.append("")
    
    # Header guard end
    lines.append(f"#endif // {guard_name}")
    
    # Write file
    try:
        with output_path.open('w') as f:
            f.write("\n".join(lines))
            f.write("\n")  # Ensure file ends with newline
        
        logger.log_event('FILE_GENERATED', filename=output_filename, output_path=str(output_path))
        return output_path
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error writing {output_filename}: {e}")
        raise


def generate_all_bench_configs(config, output_dir):
    """
    Generate bench_config.h files for all enabled benchmarks.
    
    Creates separate bench_config_<benchmark>.h files in tmp/generated/
    that will later be copied to benchmarks/<benchmark>/bench_config.h
    by the file allocator.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where files should be written (tmp/generated/)
    
    Returns:
        List of Paths to generated files
    """
    output_dir = Path(output_dir)
    
    logger.log_event('GENERATION_BENCH_CONFIG_START')
    
    # Get all benchmarks
    benchmarks = get_benchmarks(config)
    
    if not benchmarks:
        logger.log_event('WARNING', warning_message="No benchmarks configured")
        return []
    
    # Generate config for each enabled benchmark
    generated_files = []
    for benchmark_name in benchmarks.keys():
        result = generate_single_bench_config_h(config, benchmark_name, output_dir)
        if result:
            generated_files.append(result)
    
    logger.log_event('GENERATION_BENCH_CONFIG_COMPLETE', count=len(generated_files))
    return generated_files