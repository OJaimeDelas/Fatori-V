# =============================================================================
# FATORI-V • Results • Metrics Computer
# File: metrics_computer.py
# -----------------------------------------------------------------------------
# Computes derived metrics from collected data.
# =============================================================================

from typing import Dict, List, Optional
from scripts.logging.logger import log_event


def compute_error_detection_rate(session_metrics_list):
    """
    Compute fault injection error detection rate.
    
    This calculates the percentage of injections that resulted
    in detected errors vs. undetected errors (silent data corruption).
    
    Args:
        session_metrics_list: List of session metrics dictionaries
    
    Returns:
        Dictionary with detection rate metrics
    """
    total_injections = 0
    detected_errors = 0
    undetected_errors = 0
    
    for metrics in session_metrics_list:
        if not metrics.get('injection_enabled'):
            continue
        
        fi_metrics = metrics.get('fi_metrics', {})
        
        injection_count = metrics.get('fi_injection_count', 0)
        total_injections += injection_count
        
        # Count detected errors
        detected = metrics.get('fi_detected_errors', 0)
        detected_errors += detected
        
        # Undetected errors would be injections that didn't cause detection
        # This is approximate - assumes success means no detection
        if metrics.get('success'):
            undetected = injection_count - detected
            if undetected > 0:
                undetected_errors += undetected
    
    # Compute rate
    if total_injections == 0:
        detection_rate = 0.0
    else:
        detection_rate = (detected_errors / total_injections) * 100.0
    
    return {
        'total_injections': total_injections,
        'detected_errors': detected_errors,
        'undetected_errors': undetected_errors,
        'detection_rate_percent': detection_rate
    }


def compute_fi_coverage(session_metrics_list):
    """
    Compute fault injection coverage.
    
    This measures how much of the design was exercised with FI.
    
    Args:
        session_metrics_list: List of session metrics dictionaries
    
    Returns:
        Dictionary with coverage metrics
    """
    total_injections = 0
    unique_locations = set()
    sessions_with_fi = 0
    
    for metrics in session_metrics_list:
        if not metrics.get('injection_enabled'):
            continue
        
        sessions_with_fi += 1
        
        injection_count = metrics.get('fi_injection_count', 0)
        total_injections += injection_count
        
        # Track unique injection locations if available
        fi_metrics = metrics.get('fi_metrics', {})
        if 'location_count' in fi_metrics:
            unique_locations.add(metrics['session_id'])  # Placeholder
    
    return {
        'total_injections': total_injections,
        'sessions_with_fi': sessions_with_fi,
        'unique_location_estimate': len(unique_locations)
    }


def compute_benchmark_speedup(current_metrics, baseline_metrics):
    """
    Compute benchmark speedup compared to baseline.
    
    Args:
        current_metrics: Session metrics for current configuration
        baseline_metrics: Session metrics for baseline configuration
    
    Returns:
        Speedup factor (1.0 = same speed, >1.0 = faster, <1.0 = slower)
    """
    # Extract execution times
    current_time = current_metrics.get('benchmark_execution_time')
    baseline_time = baseline_metrics.get('benchmark_execution_time')
    
    if not current_time or not baseline_time:
        return None
    
    # Speedup = baseline_time / current_time
    speedup = baseline_time / current_time
    
    return speedup


def compute_overhead(with_ftm_metrics, without_ftm_metrics):
    """
    Compute overhead of fault tolerance mechanisms.
    
    Args:
        with_ftm_metrics: Session metrics with FTM enabled
        without_ftm_metrics: Session metrics without FTM
    
    Returns:
        Dictionary with overhead metrics
    """
    overhead = {}
    
    # Execution time overhead
    ftm_time = with_ftm_metrics.get('duration_s')
    base_time = without_ftm_metrics.get('duration_s')
    
    if ftm_time and base_time:
        time_overhead = ((ftm_time - base_time) / base_time) * 100.0
        overhead['execution_time_overhead_percent'] = time_overhead
    
    # Performance overhead (if scores available)
    ftm_score = with_ftm_metrics.get('benchmark_score')
    base_score = without_ftm_metrics.get('benchmark_score')
    
    if ftm_score and base_score:
        score_overhead = ((base_score - ftm_score) / base_score) * 100.0
        overhead['performance_overhead_percent'] = score_overhead
    
    return overhead


def compute_success_rate(session_metrics_list):
    """
    Compute overall session success rate.
    
    Args:
        session_metrics_list: List of session metrics dictionaries
    
    Returns:
        Dictionary with success rate metrics
    """
    total_sessions = len(session_metrics_list)
    successful_sessions = sum(1 for m in session_metrics_list if m.get('success'))
    failed_sessions = total_sessions - successful_sessions
    timeout_sessions = sum(1 for m in session_metrics_list if m.get('timeout_occurred'))
    
    success_rate = (successful_sessions / total_sessions * 100.0) if total_sessions > 0 else 0.0
    
    return {
        'total_sessions': total_sessions,
        'successful': successful_sessions,
        'failed': failed_sessions,
        'timeouts': timeout_sessions,
        'success_rate_percent': success_rate
    }


def compute_average_duration(session_metrics_list):
    """
    Compute average session duration.
    
    Args:
        session_metrics_list: List of session metrics dictionaries
    
    Returns:
        Average duration in seconds, or None
    """
    durations = [m['duration_s'] for m in session_metrics_list if m.get('duration_s')]
    
    if not durations:
        return None
    
    return sum(durations) / len(durations)