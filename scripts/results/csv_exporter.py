# =============================================================================
# FATORI-V • Results • CSV Exporter
# File: csv_exporter.py
# -----------------------------------------------------------------------------
# Exports metrics to CSV files for programmatic access.
# =============================================================================

import csv
from pathlib import Path
from typing import Dict, List
from scripts.logging.logger import log_event


def export_summary_csv(aggregates, output_path):
    """
    Export aggregate metrics to CSV file.
    
    Creates a simple key-value CSV with summary statistics.
    
    Args:
        aggregates: Aggregated metrics dictionary
        output_path: Path where CSV should be written
    
    Returns:
        Boolean indicating success
    """
    output_path = Path(output_path)
    
    try:
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Metric', 'Value'])
            
            # Session statistics
            writer.writerow(['Total Sessions', aggregates.get('session_count', 0)])
            
            success = aggregates.get('success', {})
            writer.writerow(['Successful Sessions', success.get('successful', 0)])
            writer.writerow(['Failed Sessions', success.get('failed', 0)])
            writer.writerow(['Timeout Sessions', success.get('timeouts', 0)])
            writer.writerow(['Success Rate (%)', f"{success.get('success_rate_percent', 0):.2f}"])
            
            # Duration statistics
            avg_duration = aggregates.get('average_duration_s')
            if avg_duration is not None:
                writer.writerow(['Average Duration (s)', f"{avg_duration:.2f}"])
            
            total_duration = aggregates.get('total_duration_s')
            if total_duration is not None:
                writer.writerow(['Total Duration (s)', f"{total_duration:.2f}"])
            
            # FI statistics
            fi_count = aggregates.get('fi_enabled_count', 0)
            writer.writerow(['FI Enabled Sessions', fi_count])
            
            if fi_count > 0:
                fi_detection = aggregates.get('fi_detection', {})
                writer.writerow(['Total Injections', fi_detection.get('total_injections', 0)])
                writer.writerow(['Detected Errors', fi_detection.get('detected_errors', 0)])
                writer.writerow(['Undetected Errors', fi_detection.get('undetected_errors', 0)])
                writer.writerow(['Detection Rate (%)', f"{fi_detection.get('detection_rate_percent', 0):.2f}"])
        
        log_event('CSV_SUMMARY_EXPORTED', output_path=str(output_path))
        return True
    
    except Exception as e:
        log_event('CSV_SUMMARY_EXPORT_ERROR', error_message=str(e))
        return False


def export_sessions_csv(session_metrics, output_path):
    """
    Export per-session metrics to CSV file.
    
    Creates a CSV with one row per session.
    
    Args:
        session_metrics: List of session metrics dictionaries
        output_path: Path where CSV should be written
    
    Returns:
        Boolean indicating success
    """
    output_path = Path(output_path)
    
    if not session_metrics:
        log_event('CSV_SESSIONS_NO_DATA')
        return False
    
    try:
        with output_path.open('w', newline='', encoding='utf-8') as f:
            # Determine all keys across all sessions
            all_keys = set()
            for metrics in session_metrics:
                all_keys.update(metrics.keys())
            
            # Define column order (important ones first)
            priority_keys = [
                'session_id',
                'benchmark_name',
                'duration_s',
                'status',
                'success',
                'timeout_occurred',
                'injection_enabled',
                'fi_injection_count',
                'benchmark_score',
                'error_message'
            ]
            
            # Build ordered fieldnames
            fieldnames = []
            for key in priority_keys:
                if key in all_keys:
                    fieldnames.append(key)
                    all_keys.remove(key)
            
            # Add remaining keys
            fieldnames.extend(sorted(all_keys))
            
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            
            # Write header
            writer.writeheader()
            
            # Write sessions
            for metrics in session_metrics:
                # Convert nested dicts to strings for CSV
                row = {}
                for key, value in metrics.items():
                    if isinstance(value, (dict, list)):
                        row[key] = str(value)
                    else:
                        row[key] = value
                
                writer.writerow(row)
        
        log_event('CSV_SESSIONS_EXPORTED',
                  session_count=len(session_metrics),
                  output_path=str(output_path))
        return True
    
    except Exception as e:
        log_event('CSV_SESSIONS_EXPORT_ERROR', error_message=str(e))
        return False


def export_build_metrics_csv(build_metrics, output_path):
    """
    Export build metrics to CSV file.
    
    Args:
        build_metrics: Build metrics dictionary
        output_path: Path where CSV should be written
    
    Returns:
        Boolean indicating success
    """
    output_path = Path(output_path)
    
    if not build_metrics:
        log_event('CSV_BUILD_METRICS_NO_DATA')
        return False
    
    try:
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Metric', 'Value'])
            
            # Timing metrics
            timing = build_metrics.get('timing', {})
            if timing:
                writer.writerow(['Timing', ''])
                writer.writerow(['  WNS (ns)', timing.get('wns', 'N/A')])
                writer.writerow(['  TNS (ns)', timing.get('tns', 'N/A')])
                writer.writerow(['  Timing Met', timing.get('timing_met', False)])
            
            # Utilization metrics
            util = build_metrics.get('utilization', {})
            if util:
                writer.writerow(['Utilization', ''])
                writer.writerow(['  LUTs', util.get('lut_count', 'N/A')])
                writer.writerow(['  FFs', util.get('ff_count', 'N/A')])
                writer.writerow(['  BRAMs', util.get('bram_count', 'N/A')])
                writer.writerow(['  DSPs', util.get('dsp_count', 'N/A')])
            
            # Build duration
            duration = build_metrics.get('build_duration_s')
            if duration:
                writer.writerow(['Build Duration (s)', f"{duration:.2f}"])
        
        log_event('CSV_BUILD_METRICS_EXPORTED', output_path=str(output_path))
        return True
    
    except Exception as e:
        log_event('CSV_BUILD_METRICS_EXPORT_ERROR', error_message=str(e))
        return False


def export_all_csvs(metrics_aggregator, output_dir):
    """
    Export all metrics to CSV files.
    
    Creates:
    - metrics_summary.csv
    - sessions.csv
    - build_metrics.csv
    
    Args:
        metrics_aggregator: MetricsAggregator instance
        output_dir: Directory where CSVs should be written
    
    Returns:
        Dictionary with paths to created files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('CSV_EXPORT_ALL_START', output_dir=str(output_dir))
    
    results = {}
    
    # Export summary
    summary_path = output_dir / "metrics_summary.csv"
    aggregates = metrics_aggregator.compute_aggregates()
    if export_summary_csv(aggregates, summary_path):
        results['summary'] = summary_path
    
    # Export sessions
    sessions_path = output_dir / "sessions.csv"
    if export_sessions_csv(metrics_aggregator.session_metrics, sessions_path):
        results['sessions'] = sessions_path
    
    # Export build metrics
    build_path = output_dir / "build_metrics.csv"
    if export_build_metrics_csv(metrics_aggregator.build_metrics, build_path):
        results['build'] = build_path
    
    log_event('CSV_EXPORT_ALL_COMPLETE', file_count=len(results))
    
    return results