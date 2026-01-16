# =============================================================================
# FATORI-V • Results • Summary Generator
# File: summary_generator.py
# -----------------------------------------------------------------------------
# Generates human-readable summary reports of execution runs.
# =============================================================================

from datetime import datetime
from typing import Dict
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.common.common_settings import *
from scripts.logging import logger


def format_duration(seconds):
    """
    Format duration in seconds as human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    if seconds is None:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def generate_header(config):
    """
    Generate summary report header.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with header content
    """
    header = []
    header.append("=" * 80)
    header.append("FATORI-V RUN SUMMARY")
    header.append("=" * 80)
    header.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    header.append("")
    
    # Run identification
    run_ident = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, default={})
    if run_ident:
        header.append("Run Identification:")
        name = run_ident.get(KEY_IDENT_NAME)
        if name:
            header.append(f"  Name: {name}")
        
        description = run_ident.get(KEY_IDENT_DESCRIPTION)
        if description:
            header.append(f"  Description: {description}")
        
        header.append("")
    
    return "\n".join(header)


def generate_config_summary(config):
    """
    Generate configuration summary section.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with configuration summary
    """
    lines = []
    lines.append("Configuration Summary:")
    lines.append("-" * 80)
    
    # Hardware
    board = get_nested(config, KEY_RUN, KEY_RUN_HW, KEY_HW_BOARD, default="unknown")
    lines.append(f"  Board: {board}")
    
    # ISA extensions
    features = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, default={})
    isa = features.get(KEY_FEAT_ISA, {})
    
    enabled_isa = [name for name, enabled in isa.items() if enabled]
    if enabled_isa:
        lines.append(f"  ISA Extensions: {', '.join(enabled_isa)}")
    
    # Fault tolerance
    ftms = features.get(KEY_FEAT_FTMS, {})
    enabled_ftms = [name for name, enabled in ftms.items() if enabled]
    if enabled_ftms:
        lines.append(f"  FTMs Enabled: {', '.join(enabled_ftms)}")
    
    # Benchmarks
    benchmarks = get_nested(config, KEY_GENERAL, KEY_GEN_BENCHMARKS, default={})
    enabled_benchmarks = [name for name, cfg in benchmarks.items() 
                          if isinstance(cfg, dict) and cfg.get(KEY_BENCH_ENABLE, True)]
    lines.append(f"  Benchmarks: {len(enabled_benchmarks)}")
    
    lines.append("")
    
    return "\n".join(lines)


def generate_build_summary(build_metrics):
    """
    Generate build metrics summary section.
    
    Args:
        build_metrics: Dictionary with build metrics
    
    Returns:
        String with build summary
    """
    lines = []
    lines.append("Build Metrics:")
    lines.append("-" * 80)
    
    if not build_metrics or not build_metrics.get('reports_available'):
        lines.append("  No build metrics available")
        lines.append("")
        return "\n".join(lines)
    
    # Timing
    timing = build_metrics.get('timing', {})
    if timing:
        wns = timing.get('wns')
        tns = timing.get('tns')
        timing_met = timing.get('timing_met', False)
        
        lines.append(f"  Timing:")
        if wns is not None:
            lines.append(f"    WNS: {wns:.3f} ns")
        if tns is not None:
            lines.append(f"    TNS: {tns:.3f} ns")
        lines.append(f"    Status: {'MET' if timing_met else 'FAILED'}")
    
    # Utilization
    util = build_metrics.get('utilization', {})
    if util:
        lines.append(f"  Resource Utilization:")
        if 'lut_count' in util:
            lines.append(f"    LUTs: {util['lut_count']}")
        if 'ff_count' in util:
            lines.append(f"    FFs: {util['ff_count']}")
        if 'bram_count' in util:
            lines.append(f"    BRAMs: {util['bram_count']}")
        if 'dsp_count' in util:
            lines.append(f"    DSPs: {util['dsp_count']}")
    
    # Build duration
    duration = build_metrics.get('build_duration_s')
    if duration:
        lines.append(f"  Build Duration: {format_duration(duration)}")
    
    lines.append("")
    
    return "\n".join(lines)


def generate_session_summary(aggregates):
    """
    Generate session execution summary section.
    
    Args:
        aggregates: Aggregated metrics dictionary
    
    Returns:
        String with session summary
    """
    lines = []
    lines.append("Execution Summary:")
    lines.append("-" * 80)
    
    # Overall stats
    lines.append(f"  Total Sessions: {aggregates.get('session_count', 0)}")
    
    success = aggregates.get('success', {})
    lines.append(f"  Successful: {success.get('successful', 0)}")
    lines.append(f"  Failed: {success.get('failed', 0)}")
    lines.append(f"  Timeouts: {success.get('timeouts', 0)}")
    lines.append(f"  Success Rate: {success.get('success_rate_percent', 0):.1f}%")
    
    # Duration
    avg_duration = aggregates.get('average_duration_s')
    total_duration = aggregates.get('total_duration_s')
    
    if avg_duration:
        lines.append(f"  Average Duration: {format_duration(avg_duration)}")
    if total_duration:
        lines.append(f"  Total Duration: {format_duration(total_duration)}")
    
    lines.append("")
    
    return "\n".join(lines)


def generate_benchmark_details(aggregates):
    """
    Generate per-benchmark details section.
    
    Args:
        aggregates: Aggregated metrics dictionary
    
    Returns:
        String with benchmark details
    """
    lines = []
    lines.append("Per-Benchmark Results:")
    lines.append("-" * 80)
    
    per_benchmark = aggregates.get('per_benchmark', {})
    
    if not per_benchmark:
        lines.append("  No benchmark data available")
        lines.append("")
        return "\n".join(lines)
    
    for bench_name, stats in sorted(per_benchmark.items()):
        lines.append(f"  {bench_name}:")
        lines.append(f"    Sessions: {stats.get('session_count', 0)}")
        lines.append(f"    Successful: {stats.get('success_count', 0)}")
        
        avg_duration = stats.get('average_duration')
        if avg_duration:
            lines.append(f"    Avg Duration: {format_duration(avg_duration)}")
        
        avg_score = stats.get('average_score')
        if avg_score:
            lines.append(f"    Avg Score: {avg_score:.2f}")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_fi_summary(aggregates):
    """
    Generate fault injection summary section.
    
    Args:
        aggregates: Aggregated metrics dictionary
    
    Returns:
        String with FI summary
    """
    lines = []
    
    fi_count = aggregates.get('fi_enabled_count', 0)
    
    if fi_count == 0:
        lines.append("Fault Injection: Not enabled")
        lines.append("")
        return "\n".join(lines)
    
    lines.append("Fault Injection Summary:")
    lines.append("-" * 80)
    lines.append(f"  Sessions with FI: {fi_count}")
    
    # Detection metrics
    fi_detection = aggregates.get('fi_detection', {})
    if fi_detection:
        lines.append(f"  Total Injections: {fi_detection.get('total_injections', 0)}")
        lines.append(f"  Detected Errors: {fi_detection.get('detected_errors', 0)}")
        lines.append(f"  Undetected Errors: {fi_detection.get('undetected_errors', 0)}")
        lines.append(f"  Detection Rate: {fi_detection.get('detection_rate_percent', 0):.1f}%")
    
    # Coverage metrics
    fi_coverage = aggregates.get('fi_coverage', {})
    if fi_coverage:
        lines.append(f"  Coverage:")
        lines.append(f"    Total Injections: {fi_coverage.get('total_injections', 0)}")
        lines.append(f"    Unique Locations: {fi_coverage.get('unique_location_estimate', 0)}")
    
    lines.append("")
    
    return "\n".join(lines)


def generate_run_summary(config, metrics_aggregator):
    """
    Generate complete run summary report.
    
    This creates a human-readable text report with:
    - Run identification and timestamp
    - Configuration summary
    - Build metrics
    - Execution statistics
    - Per-benchmark results
    - FI statistics (if enabled)
    
    Args:
        config: The loaded YAML configuration dictionary
        metrics_aggregator: MetricsAggregator instance with collected metrics
    
    Returns:
        String with complete summary report
    """
    logger.log_event('DEBUG', debug_message="Generating run summary...")
    
    # Compute aggregates
    aggregates = metrics_aggregator.compute_aggregates()
    build_metrics = metrics_aggregator.build_metrics
    
    # Generate sections
    sections = []
    
    sections.append(generate_header(config))
    sections.append(generate_config_summary(config))
    sections.append(generate_build_summary(build_metrics))
    sections.append(generate_session_summary(aggregates))
    sections.append(generate_benchmark_details(aggregates))
    sections.append(generate_fi_summary(aggregates))
    
    # Footer
    sections.append("=" * 80)
    sections.append("END OF SUMMARY")
    sections.append("=" * 80)
    
    summary = "\n".join(sections)
    
    logger.log_event('DEBUG', debug_message="Run summary generated")
    
    return summary