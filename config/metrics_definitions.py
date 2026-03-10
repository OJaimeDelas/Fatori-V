# =============================================================================
# FATORI-V • Configuration • Metrics Definitions
# File: metrics_definitions.py
# -----------------------------------------------------------------------------
# Central definition of all direct and indirect metrics for benchmark tables.
# =============================================================================

# Metric definitions list
# Each metric has:
# - id: Unique metric identifier
# - type: 'direct' (from metrics.txt) or 'indirect' (computed)
# - benchmarks: 'GENERAL' for all benchmarks, or list like ['coremark']
# - For direct metrics:
#   - compute: 'diff' (post-pre) or 'copy' (use as-is)
#   - value_type: 'hex', 'dec', or 'str'
# - For indirect metrics:
#   - formula: Lambda function taking metrics dict, returns computed value

METRIC_DEFINITIONS = [

    # ===== Indirect Metrics (GENERAL) - Performance =====
    {
        'id': 'instructions_per_cycle',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round(m.get('minstret', 0) / m.get('mcycle', 1), 2) if m.get('mcycle', 0) > 0 else 0
    },
    {
        'id': 'branch_prediction_rate',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round((m.get('hpm_branches_taken', 0) / m.get('hpm_branches', 1)) * 100, 2) if m.get('hpm_branches', 0) > 0 else 0
    },
    {
        'id': 'compressed_instruction_rate',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round((m.get('hpm_compressed', 0) / m.get('minstret', 1)) * 100, 2) if m.get('minstret', 0) > 0 else 0
    },
    
    # ===== Indirect Metrics (GENERAL) - Fault Injection =====
    {
        'id': 'total_injections',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: m.get('fatori_reg_inj_cnt', 0) + m.get('fatori_logic_inj_cnt', 0)
    },
    {
        'id': 'avg_detection_latency',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round(m.get('fatori_latency_sum', 0) / m.get('fatori_latency_cnt', 1), 2) if m.get('fatori_latency_cnt', 0) > 0 else 0
    },
    {
        'id': 'minor_error_rate',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round((m.get('fatori_minor_cnt', 0) / m.get('mcycle', 1)) * 1000000, 2) if m.get('mcycle', 0) > 0 else 0
    },
    {
        'id': 'major_error_rate',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round((m.get('fatori_major_cnt', 0) / m.get('mcycle', 1)) * 1000000, 2) if m.get('mcycle', 0) > 0 else 0
    },
    {
        'id': 'correction_rate',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round((m.get('fatori_corrected_cnt', 0) / (m.get('fatori_minor_cnt', 0) + m.get('fatori_major_cnt', 0) + 1)) * 100, 2) if (m.get('fatori_minor_cnt', 0) + m.get('fatori_major_cnt', 0)) > 0 else 0
    },
    {
        'id': 'fault_coverage',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round(((m.get('fatori_minor_cnt', 0) + m.get('fatori_major_cnt', 0)) / (m.get('fatori_reg_inj_cnt', 0) + m.get('fatori_logic_inj_cnt', 0) + 1)) * 100, 2) if (m.get('fatori_reg_inj_cnt', 0) + m.get('fatori_logic_inj_cnt', 0)) > 0 else 0
    },
    {
        'id': 'double_fault_rate',
        'type': 'indirect',
        'benchmarks': 'GENERAL',
        'formula': lambda m: round((m.get('fatori_double_fault_cnt', 0) / (m.get('fatori_major_cnt', 0) + 1)) * 100, 2) if m.get('fatori_major_cnt', 0) > 0 else 0
    },

    # ===== Differential Metrics (GENERAL) =====
    {'id': 'mcycle', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'minstret', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_lsu_busy', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_ifetch_stall', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_loads', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_stores', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_jumps', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_branches', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_branches_taken', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_compressed', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_multiply_stalls', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    {'id': 'hpm_divide_stalls', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'hex'},
    
    # ===== FATORI Measured Metrics (from CSRs 0xBC1-0xBCD) =====
    # Error counters
    {'id': 'fatori_err_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_minor_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_major_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_major_internal_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_major_bus_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_double_fault_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_corrected_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    
    # Injection counters
    {'id': 'fatori_reg_inj_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_logic_inj_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    
    # Timing metrics
    {'id': 'fatori_cycles_min', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_cycles_maj', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_detect_latency', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_latency_sum', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    {'id': 'fatori_latency_cnt', 'type': 'direct', 'benchmarks': 'GENERAL', 'compute': 'diff', 'value_type': 'dec'},
    
    # ===== CoreMark Benchmark Metrics =====
    {'id': 'coremark_size', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'total_ticks', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'total_time_secs', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'iterations_per_sec', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'iterations', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'memory_location', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'str'},
    {'id': 'seedcrc', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'hex'},
    {'id': 'crclist', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'hex'},
    {'id': 'crcmatrix', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'hex'},
    {'id': 'crcstate', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'hex'},
    {'id': 'crcfinal', 'type': 'direct', 'benchmarks': ['coremark'], 'compute': 'copy', 'value_type': 'hex'},
    
   # ===== Embench-IoT Benchmark Metrics =====
    # Summary metrics (always present)
    {'id': 'total_benchmarks', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'total_passed', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'embench_score', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    
    # Per-benchmark metrics (3 metrics per benchmark: cycles, pass, ratio)
    {'id': 'aha-mont64_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'aha-mont64_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'aha-mont64_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'crc32_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'crc32_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'crc32_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'cubic_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'cubic_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'cubic_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'edn_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'edn_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'edn_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'huffbench_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'huffbench_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'huffbench_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'matmult-int_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'matmult-int_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'matmult-int_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'md5sum_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'md5sum_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'md5sum_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'minver_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'minver_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'minver_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nbody_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nbody_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nbody_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nettle-aes_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nettle-aes_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nettle-aes_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nettle-sha256_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nettle-sha256_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nettle-sha256_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nsichneu_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nsichneu_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'nsichneu_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'picojpeg_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'picojpeg_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'picojpeg_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'primecount_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'primecount_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'primecount_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'qrduino_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'qrduino_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'qrduino_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'sglib-combined_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'sglib-combined_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'sglib-combined_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'slre_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'slre_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'slre_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'st_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'st_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'st_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'statemate_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'statemate_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'statemate_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'ud_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'ud_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'ud_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'wikisort_cycles', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'wikisort_pass', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'wikisort_ratio', 'type': 'direct', 'benchmarks': ['embench-iot'], 'compute': 'copy', 'value_type': 'dec'},
    
    # ===== FATORI Stress Benchmark Metrics =====
    {'id': 'enabled_targets', 'type': 'direct', 'benchmarks': ['fatori_stress'], 'compute': 'copy', 'value_type': 'str'},
    {'id': 'iterations', 'type': 'direct', 'benchmarks': ['fatori_stress'], 'compute': 'copy', 'value_type': 'dec'},
    {'id': 'initial_checksum', 'type': 'direct', 'benchmarks': ['fatori_stress'], 'compute': 'copy', 'value_type': 'hex'},
    {'id': 'forward_checksum', 'type': 'direct', 'benchmarks': ['fatori_stress'], 'compute': 'copy', 'value_type': 'hex'},
    {'id': 'backward_checksum', 'type': 'direct', 'benchmarks': ['fatori_stress'], 'compute': 'copy', 'value_type': 'hex'},
    {'id': 'validation', 'type': 'direct', 'benchmarks': ['fatori_stress'], 'compute': 'copy', 'value_type': 'str'},
    {'id': 'first_mismatch', 'type': 'direct', 'benchmarks': ['fatori_stress'], 'compute': 'copy', 'value_type': 'str'},
    
    # ===== Hello World Benchmark Metrics =====
    # Minimal benchmark, only has general metrics
]


def get_metrics_for_benchmark(benchmark_name):
    """
    Get all metrics that apply to a specific benchmark.
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        List of metric definitions applicable to this benchmark
    """
    applicable_metrics = []
    
    for metric in METRIC_DEFINITIONS:
        benchmarks = metric.get('benchmarks', [])
        
        if benchmarks == 'GENERAL':
            # Applies to all benchmarks
            applicable_metrics.append(metric)
        elif isinstance(benchmarks, list) and benchmark_name in benchmarks:
            # Applies to specific benchmarks
            applicable_metrics.append(metric)
    
    return applicable_metrics


def get_all_direct_metrics():
    """Get all direct metrics that need to be read from metrics.txt."""
    return [m for m in METRIC_DEFINITIONS if m['type'] == 'direct']


def get_all_indirect_metrics():
    """Get all indirect metrics that need to be computed."""
    return [m for m in METRIC_DEFINITIONS if m['type'] == 'indirect']


def compute_indirect_metric(metric_def, metrics_dict):
    """
    Compute an indirect metric using its formula.
    
    Args:
        metric_def: Metric definition dict with formula
        metrics_dict: Dictionary of available metrics
    
    Returns:
        Computed value, or None if computation fails
    """
    try:
        formula = metric_def.get('formula')
        if formula and callable(formula):
            return formula(metrics_dict)
        return None
    except Exception:
        # Silently return None if computation fails (missing dependencies)
        return None