# =============================================================================
# FATORI-V • Results • Bench Metrics Table
# File: bench_metrics_table.py
# -----------------------------------------------------------------------------
# Generates benchmark metrics table from metrics.txt files with system config.
# =============================================================================

import csv
from pathlib import Path
from typing import Dict, List, Tuple
from scripts.logging.logger import log_event
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_nested, is_enabled
from config.metrics_definitions import (
    get_metrics_for_benchmark,
    get_all_direct_metrics,
    get_all_indirect_metrics,
    compute_indirect_metric,
    METRIC_DEFINITIONS
)


def parse_metrics_txt(metrics_file: Path) -> Dict[str, Dict]:
    """
    Parse a metrics.txt file and extract [pre], [post], and [benchmark] metrics.
    
    Handles both numeric and non-numeric values. Numeric values are converted
    from hex/dec to integers. Non-numeric values are kept as strings.
    
    Args:
        metrics_file: Path to metrics.txt file
    
    Returns:
        Dictionary with 'pre', 'post', and 'benchmark' keys containing metric dicts
    """
    metrics = {
        'pre': {},
        'post': {},
        'benchmark': {}
    }
    
    def parse_value(value_str):
        """Parse a metric value, handling hex, decimal, and non-numeric strings."""
        value_str = value_str.strip()
        
        # Try hex conversion
        if value_str.startswith('0x'):
            try:
                return int(value_str, 16)
            except ValueError:
                return value_str
        
        # Try decimal conversion
        try:
            return int(value_str)
        except ValueError:
            # Keep as string (e.g., "STATIC", "HEAP", etc.)
            return value_str
    
    try:
        with metrics_file.open('r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse line: [stage] metric_name,value
                if line.startswith('[pre]'):
                    parts = line.replace('[pre]', '').strip().split(',', 1)
                    if len(parts) == 2:
                        metric_name = parts[0].strip()
                        value = parse_value(parts[1])
                        metrics['pre'][metric_name] = value
                
                elif line.startswith('[post]'):
                    parts = line.replace('[post]', '').strip().split(',', 1)
                    if len(parts) == 2:
                        metric_name = parts[0].strip()
                        value = parse_value(parts[1])
                        metrics['post'][metric_name] = value
                
                elif line.startswith('[benchmark]'):
                    parts = line.replace('[benchmark]', '').strip().split(',', 1)
                    if len(parts) == 2:
                        metric_name = parts[0].strip()
                        value = parse_value(parts[1])
                        metrics['benchmark'][metric_name] = value
    
    except Exception as e:
        log_event('ERROR', error_message=f"Error parsing {metrics_file}: {e}")
    
    return metrics


def compute_metrics_for_benchmark(benchmark_name, parsed_metrics):
    """
    Compute all applicable metrics for a benchmark using centralized definitions.
    
    Processing order:
    1. Compute all DIRECT metrics first (populates result dict)
    2. Compute all INDIRECT metrics second (can reference direct metrics)
    
    This ensures indirect metrics have access to all direct metrics they depend on.
    
    Args:
        benchmark_name: Name of the benchmark
        parsed_metrics: Dict with 'pre', 'post', 'benchmark' from metrics.txt
    
    Returns:
        Dictionary with all computed metrics for this benchmark
    """
    result = {}
    
    # Get applicable metrics for this benchmark
    applicable_metrics = get_metrics_for_benchmark(benchmark_name)
    
    # PHASE 1: Compute all DIRECT metrics first
    # This populates result dict with base metrics that indirect metrics depend on
    for metric_def in applicable_metrics:
        if metric_def['type'] != 'direct':
            continue
            
        metric_id = metric_def['id']
        compute_type = metric_def.get('compute', 'copy')
        
        if compute_type == 'diff':
            # Differential: post - pre
            pre_val = parsed_metrics['pre'].get(metric_id, 0)
            post_val = parsed_metrics['post'].get(metric_id, 0)
            
            # Handle wraparound for counters (assume 64-bit)
            if isinstance(pre_val, int) and isinstance(post_val, int):
                if post_val < pre_val:
                    diff = (2**64) - pre_val + post_val
                else:
                    diff = post_val - pre_val
                result[metric_id] = diff
                
        elif compute_type == 'copy':
            # Copy: use benchmark value as-is
            value = parsed_metrics['benchmark'].get(metric_id)
            if value is not None:
                result[metric_id] = value
    
    # PHASE 2: Compute all INDIRECT metrics second
    # Now result dict contains all direct metrics needed for formulas
    for metric_def in applicable_metrics:
        if metric_def['type'] != 'indirect':
            continue
            
        metric_id = metric_def['id']
        value = compute_indirect_metric(metric_def, result)
        if value is not None:
            result[metric_id] = value
    
    return result

def extract_system_config(config: dict) -> List[Tuple[str, str]]:
    """
    Extract ALL system configuration features from config.
    
    Includes:
    - run.identification (name, description, seed, run)
    - general.metrics_level
    - general.features.fault_manager
    - general.features.fault_tolerance_mechanisms (all FTMs)
    - general.features.performance_mechanisms (all perf boosters)
    - general.features.isa_extensions (all ISA extensions)
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        List of (name, value) tuples
    """
    system_config = []
    
    # ===== Identification Section =====
    ident = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, default={})
    
    system_config.append(("Run Name", str(ident.get("name", "N/A"))))
    system_config.append(("Description", str(ident.get("description", "N/A"))))
    system_config.append(("Global Seed", str(ident.get("seed", "N/A"))))
    system_config.append(("Run Mode", str(ident.get("run", "N/A"))))
    
    # ===== Metrics Level =====
    metrics_level = get_nested(config, KEY_GENERAL, "metrics_level", default=0)
    system_config.append(("Metrics Level", str(metrics_level)))
    
    # ===== Features Section =====
    features = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, default={})
    
    # Fault Manager
    fault_mgr = features.get("fault_manager", False)
    system_config.append(("Fault Manager", "on" if is_enabled(fault_mgr) else "off"))
    
    # ===== Fault Tolerance Mechanisms =====
    ftms = features.get(KEY_FEAT_FTMS, {})
    
    system_config.append(("Data Indep Timing", "on" if is_enabled(ftms.get("data_indep_timing", False)) else "off"))
    system_config.append(("Dummy Instructions", "on" if is_enabled(ftms.get("dummy_instr", False)) else "off"))
    system_config.append(("Hardened PC", "on" if is_enabled(ftms.get("hard_pc", False)) else "off"))
    system_config.append(("ICache ECC", "on" if is_enabled(ftms.get("icache_ecc", False)) else "off"))
    system_config.append(("Lockstep", "on" if is_enabled(ftms.get("lockstep", False)) else "off"))
    system_config.append(("Logic M-of-N", "on" if is_enabled(ftms.get(KEY_FTM_LOGIC_MON, False)) else "off"))
    system_config.append(("Mem ECC", "on" if is_enabled(ftms.get("mem_ecc", False)) else "off"))
    system_config.append(("PMP", "on" if is_enabled(ftms.get("pmp", False)) else "off"))
    system_config.append(("Register M-of-N", "on" if is_enabled(ftms.get(KEY_FTM_REG_MON, False)) else "off"))
    system_config.append(("RegFile ECC", "on" if is_enabled(ftms.get(KEY_FTM_RF_ECC, False)) else "off"))
    system_config.append(("RegFile Raddr Glitch", "on" if is_enabled(ftms.get(KEY_FTM_RF_RADDR_GLITCH, False)) else "off"))
    system_config.append(("RegFile WE Glitch", "on" if is_enabled(ftms.get(KEY_FTM_RF_WE_GLITCH, False)) else "off"))
    system_config.append(("Secure Guards", "on" if is_enabled(ftms.get("secure_guards", False)) else "off"))
    system_config.append(("Self Testing", "on" if is_enabled(ftms.get(KEY_FTM_SELFTEST, False)) else "off"))
    system_config.append(("Shadow CSRs", "on" if is_enabled(ftms.get("shadow_csrs", False)) else "off"))
    
    # ===== Performance Mechanisms =====
    perf = features.get(KEY_FEAT_PERF_MECH, {})
    
    system_config.append(("ICache", "on" if is_enabled(perf.get(KEY_PERF_ICACHE, False)) else "off"))
    system_config.append(("Branch Predictor", "on" if is_enabled(perf.get(KEY_PERF_BRANCH_PRED, False)) else "off"))
    system_config.append(("Branch Target ALU", "on" if is_enabled(perf.get(KEY_PERF_BRANCH_TALU, False)) else "off"))
    system_config.append(("Writeback Stage", "on" if is_enabled(perf.get(KEY_PERF_WSTAGE, False)) else "off"))
    
    # ===== ISA Extensions =====
    isa = features.get("isa_extensions", {})
    
    system_config.append(("RV32E", "on" if is_enabled(isa.get("RV32E", False)) else "off"))
    system_config.append(("RV32M", "on" if is_enabled(isa.get("RV32M", False)) else "off"))
    system_config.append(("RV32B", "on" if is_enabled(isa.get("RV32B", False)) else "off"))
    system_config.append(("RV32C", "on" if is_enabled(isa.get("RV32C", False)) else "off"))
    
    return system_config


def extract_fi_system_config(config: dict) -> List[Tuple[str, str]]:
    """
    Extract ALL FI system configuration from config.
    
    Includes:
    - general.fault_injection (corrector, area_profile, time_profile)
    - specifics.fault_tolerance.fault_injection.time.seed
    - specifics.fault_tolerance.fault_injection.time.<chosen_time_profile>
    - specifics.fault_tolerance.fault_injection.area (common fields)
    - specifics.fault_tolerance.fault_injection.area.<chosen_area_profile>
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        List of (name, value) tuples
    """
    fi_config = []
    
    # ===== General Fault Injection Settings =====
    fi_general = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    
    fi_config.append(("FI Corrector", str(fi_general.get("corrector", "N/A"))))
    
    area_profile = fi_general.get("area_profile", "N/A")
    fi_config.append(("Area Profile", str(area_profile)))
    
    time_profile = fi_general.get("time_profile", "N/A")
    fi_config.append(("Time Profile", str(time_profile)))
    
    # ===== Specifics - Time Configuration =====
    time_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "time", default={})
    
    time_seed = time_config.get("seed", "null")
    if time_seed is None or str(time_seed).lower() == "null":
        time_seed = "uses global"
    fi_config.append(("Time Seed", str(time_seed)))
    
    # Add time profile specific parameters
    if time_profile and time_profile != "N/A":
        profile_params = time_config.get(time_profile, {})
        
        if time_profile == "uniform":
            fi_config.append(("Uniform: Rate Hz", str(profile_params.get("rate_hz", "N/A"))))
            fi_config.append(("Uniform: Period s", str(profile_params.get("period_s", "N/A"))))
            fi_config.append(("Uniform: Duration s", str(profile_params.get("duration_s", "N/A"))))
        
        elif time_profile == "ramp":
            fi_config.append(("Ramp: Start Rate Hz", str(profile_params.get("start_rate_hz", "N/A"))))
            fi_config.append(("Ramp: End Rate Hz", str(profile_params.get("end_rate_hz", "N/A"))))
            fi_config.append(("Ramp: Duration s", str(profile_params.get("duration_s", "N/A"))))
        
        elif time_profile == "poisson":
            fi_config.append(("Poisson: Rate Hz", str(profile_params.get("rate_hz", "N/A"))))
            fi_config.append(("Poisson: Duration s", str(profile_params.get("duration_s", "N/A"))))
        
        elif time_profile == "mmpp2":
            fi_config.append(("MMPP2: Low Hz", str(profile_params.get("low_hz", "N/A"))))
            fi_config.append(("MMPP2: High Hz", str(profile_params.get("high_hz", "N/A"))))
            fi_config.append(("MMPP2: P Low to High", str(profile_params.get("p_low_to_high", "N/A"))))
            fi_config.append(("MMPP2: P High to Low", str(profile_params.get("p_high_to_low", "N/A"))))
            fi_config.append(("MMPP2: Start State", str(profile_params.get("start_state", "N/A"))))
            fi_config.append(("MMPP2: Duration s", str(profile_params.get("duration_s", "N/A"))))
        
        elif time_profile == "trace":
            fi_config.append(("Trace: File", str(profile_params.get("file", "N/A"))))
            fi_config.append(("Trace: Mode", str(profile_params.get("mode", "N/A"))))
            fi_config.append(("Trace: Repeat", str(profile_params.get("repeat", "N/A"))))
            fi_config.append(("Trace: Duration s", str(profile_params.get("duration_s", "N/A"))))
        
        elif time_profile == "microburst":
            fi_config.append(("Microburst: Burst Rate Hz", str(profile_params.get("burst_rate_hz", "N/A"))))
            fi_config.append(("Microburst: Idle Rate Hz", str(profile_params.get("idle_rate_hz", "N/A"))))
            fi_config.append(("Microburst: Burst Duration s", str(profile_params.get("burst_duration_s", "N/A"))))
            fi_config.append(("Microburst: Idle Duration s", str(profile_params.get("idle_duration_s", "N/A"))))
            fi_config.append(("Microburst: Bursts", str(profile_params.get("bursts", "N/A"))))
            fi_config.append(("Microburst: Duration s", str(profile_params.get("duration_s", "N/A"))))
        
        elif time_profile == "input":
            fi_config.append(("Input: Profile Path", str(profile_params.get("profile_path", "N/A"))))
    
    # ===== Specifics - Area Configuration =====
    area_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", default={})
    
    # Common area parameters
    repeat = area_config.get("repeat", False)
    fi_config.append(("Area: Repeat Targets", "on" if is_enabled(repeat) else "off"))
    
    fi_config.append(("Area: Target Pool Size", str(area_config.get("target_pool_size", "N/A"))))
    fi_config.append(("Area: Ratio", str(area_config.get("ratio", "N/A"))))
    
    strict = area_config.get("strict", False)
    fi_config.append(("Area: Strict", "on" if is_enabled(strict) else "off"))
    
    area_seed = area_config.get("seed", "null")
    if area_seed is None or str(area_seed).lower() == "null":
        area_seed = "uses global"
    fi_config.append(("Area: Seed", str(area_seed)))
    
    # Add area profile specific parameters
    if area_profile and area_profile != "N/A":
        profile_params = area_config.get(area_profile, {})
        
        if area_profile == "device":
            fi_config.append(("Device: Mode", str(profile_params.get("mode", "N/A"))))
        
        elif area_profile == "modules":
            fi_config.append(("Modules: Module Mode", str(profile_params.get("module_mode", "N/A"))))
            fi_config.append(("Modules: Target Mode", str(profile_params.get("target_mode", "N/A"))))
            fi_config.append(("Modules: Weights", str(profile_params.get("weights", "N/A"))))
            
            # Add enabled targets
            targets = profile_params.get("targets", {})
            enabled_targets = [name for name, val in targets.items() if is_enabled(val)]
            fi_config.append(("Modules: Enabled Targets", ", ".join(enabled_targets) if enabled_targets else "none"))
        
        elif area_profile == "target_list":
            fi_config.append(("Target List: File", str(profile_params.get("file", "N/A"))))
        
        elif area_profile == "input":
            fi_config.append(("Input: Profile Path", str(profile_params.get("profile_path", "N/A"))))
    
    return fi_config


def get_benchmark_fi_status(config: dict, benchmark_name: str) -> str:
    """
    Check if FI is enabled for benchmarks.
    
    FI is globally enabled/disabled via general.fault_injection.enable.
    When enabled, ALL active benchmarks have FI enabled.
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of the benchmark (unused, kept for API compatibility)
    
    Returns:
        "on" or "off"
    """
    from scripts.common.yaml_io.yaml_helpers import any_benchmark_has_fi
    
    fi_enabled = any_benchmark_has_fi(config)
    return "on" if fi_enabled else "off"


def generate_session_metrics_table(
    session_dir: Path,
    benchmark_name: str,
    computed_metrics: dict,
    system_config: list,
    fi_config: list,
    config: dict,
) -> bool:
    """
    Write metrics_table.csv for a single session.

    Contains System Features + FI Parameters columns on the left and the
    metrics for this one benchmark/session on the right. Mirrors the
    structure of bench_metrics.csv but scoped to one session so it can
    be read stand-alone.

    Args:
        session_dir: Path to the session directory (output goes here)
        benchmark_name: Name of the benchmark / session
        computed_metrics: Dict of {metric_id: value} already computed
        system_config: List of (name, value) tuples from extract_system_config
        fi_config: List of (name, value) tuples from extract_fi_system_config
        config: Full config dict (used for FI status)

    Returns:
        Boolean indicating success
    """
    output_path = session_dir / 'metrics_table.csv'

    # Ordered metric names that actually have values for this session
    ordered_metric_names = [
        m['id'] for m in METRIC_DEFINITIONS if m['id'] in computed_metrics
    ]

    num_metric_rows = len(ordered_metric_names)
    num_system_rows = len(system_config)
    num_fi_rows = len(fi_config)
    num_data_rows = max(num_metric_rows, num_system_rows, num_fi_rows, 1)

    try:
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header row
            writer.writerow(['System Features', '', 'FI Parameters', '', benchmark_name, ''])

            # FI status row
            fi_status = get_benchmark_fi_status(config, benchmark_name)
            writer.writerow(['', '', '', '', 'FI Status', fi_status])

            # Data rows
            for row_idx in range(num_data_rows):
                row = []

                # System section
                row.extend(system_config[row_idx] if row_idx < num_system_rows else ['', ''])

                # FI section
                row.extend(fi_config[row_idx] if row_idx < num_fi_rows else ['', ''])

                # Metrics section
                if row_idx < num_metric_rows:
                    metric_name = ordered_metric_names[row_idx]
                    row.extend([metric_name, computed_metrics[metric_name]])
                else:
                    row.extend(['', ''])

                writer.writerow(row)

        log_event('BENCH_METRICS_SESSION_TABLE_SUCCESS',
                  output=str(output_path),
                  benchmark=benchmark_name,
                  metric_count=num_metric_rows)
        return True

    except Exception as e:
        log_event('ERROR', error_message=f"Error writing metrics_table.csv for {benchmark_name}: {e}")
        return False


def generate_bench_metrics_csv(results_dir: Path, config: dict = None) -> bool:
    """
    Generate bench_metrics.csv from all sessions' metrics.txt files.
    
    Table structure:
    - Header: System Features (2 cols) | FI Parameters (2 cols) | Benchmark1 (2 cols) | Benchmark2 (2 cols) ...
    - Row 1: FI Status for each benchmark
    - Remaining rows: System config | FI config | Benchmark metrics
    
    Args:
        results_dir: Path to results directory
        config: Optional config dict for system info (loads from verified_yaml if not provided)
    
    Returns:
        Boolean indicating success
    """
    log_event('BENCH_METRICS_TABLE_START')
    
    sessions_dir = results_dir / 'sessions'
    if not sessions_dir.exists():
        log_event('ERROR', error_message=f"Sessions directory not found: {sessions_dir}")
        return False
    
    # Load config if not provided
    if config is None:
        import yaml
        verified_yaml = results_dir / 'verified_yaml.yaml'
        if verified_yaml.exists():
            with verified_yaml.open('r') as f:
                config = yaml.safe_load(f)
        else:
            log_event('WARNING', warning_message="No config provided and verified_yaml.yaml not found")
            config = {}
    
    # Collect metrics from all sessions
    session_metrics = {}
    
    for session_dir in sorted(sessions_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        
        benchmark_name = session_dir.name
        metrics_file = session_dir / 'metrics.txt'
        
        if not metrics_file.exists():
            log_event('DEBUG', debug_message=f"No metrics.txt for {benchmark_name}, will show as empty in table")
            # Still add benchmark to session_metrics with empty dict so it appears in table
            session_metrics[benchmark_name] = {}
            continue
        
        # Parse metrics file
        parsed = parse_metrics_txt(metrics_file)
        
        # Compute all applicable metrics using centralized definitions
        computed = compute_metrics_for_benchmark(benchmark_name, parsed)
        
        session_metrics[benchmark_name] = computed
    
    if not session_metrics:
        log_event('WARNING', warning_message="No metrics found in any session")
        return False
    
    # Get ordered metric list from METRIC_DEFINITIONS
    # Preserve definition order and only include metrics that exist in at least one benchmark
    from config.metrics_definitions import METRIC_DEFINITIONS
    
    # Collect which metrics actually have values in any benchmark
    metrics_with_values = set()
    for metrics in session_metrics.values():
        metrics_with_values.update(metrics.keys())
    
    # Build ordered list using METRIC_DEFINITIONS order
    ordered_metric_names = []
    for metric_def in METRIC_DEFINITIONS:
        metric_id = metric_def['id']
        if metric_id in metrics_with_values:
            ordered_metric_names.append(metric_id)
    
    sorted_benchmark_names = sorted(session_metrics.keys())
    
    # Extract system and FI configuration
    system_config = extract_system_config(config)
    fi_config = extract_fi_system_config(config)
    
    # Determine number of rows needed (1 for FI status + max of system, FI, or metrics)
    num_metric_rows = len(ordered_metric_names)
    num_system_rows = len(system_config)
    num_fi_rows = len(fi_config)
    num_data_rows = max(num_metric_rows, num_system_rows, num_fi_rows)
    
    # Write CSV file
    output_path = sessions_dir / 'bench_metrics.csv'
    
    try:
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Build header row with merged columns
            header = ['System Features', '', 'FI Parameters', '']
            
            # Add benchmark names (2 columns each, merged header)
            for bench_name in sorted_benchmark_names:
                header.extend([bench_name, ''])
            
            writer.writerow(header)
            
            # First data row: FI Status for each benchmark
            fi_status_row = ['', '', '', '']  # Empty system and FI columns
            for bench_name in sorted_benchmark_names:
                fi_status = get_benchmark_fi_status(config, bench_name)
                fi_status_row.extend(['FI Status', fi_status])
            writer.writerow(fi_status_row)
            
            # Remaining data rows
            for row_idx in range(num_data_rows):
                row = []
                
                # System section (2 columns)
                if row_idx < num_system_rows:
                    row.extend(system_config[row_idx])
                else:
                    row.extend(['', ''])
                
                # FI System section (2 columns)
                if row_idx < num_fi_rows:
                    row.extend(fi_config[row_idx])
                else:
                    row.extend(['', ''])
                
                # Benchmark metrics (2 columns per benchmark)
                for bench_name in sorted_benchmark_names:
                    if row_idx < num_metric_rows:
                        metric_name = ordered_metric_names[row_idx]
                        # Only display metric if it exists for this benchmark
                        if metric_name in session_metrics[bench_name]:
                            value = session_metrics[bench_name][metric_name]
                            row.extend([metric_name, value])
                        else:
                            # Metric doesn't apply to this benchmark - leave empty
                            row.extend(['', ''])
                    else:
                        row.extend(['', ''])
                
                writer.writerow(row)
        
        log_event('BENCH_METRICS_TABLE_SUCCESS', 
                  output=str(output_path),
                  benchmark_count=len(sorted_benchmark_names),
                  metric_count=len(ordered_metric_names),
                  system_params=len(system_config),
                  fi_params=len(fi_config))

        # Write per-session metrics_table.csv for each benchmark that has metrics
        for bench_name in sorted_benchmark_names:
            if session_metrics[bench_name]:
                generate_session_metrics_table(
                    session_dir=sessions_dir / bench_name,
                    benchmark_name=bench_name,
                    computed_metrics=session_metrics[bench_name],
                    system_config=system_config,
                    fi_config=fi_config,
                    config=config,
                )

        return True

    except Exception as e:
        log_event('ERROR', error_message=f"Error writing bench_metrics.csv: {e}")
        import traceback
        log_event('DEBUG', debug_message=traceback.format_exc())
        return False