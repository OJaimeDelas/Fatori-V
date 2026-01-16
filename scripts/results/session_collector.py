# =============================================================================
# FATORI-V • Results • Session Metrics Collector
# File: session_collector.py
# -----------------------------------------------------------------------------
# Collects metrics from individual benchmark execution sessions.
# =============================================================================

import json
from pathlib import Path
from typing import Dict, Optional
from scripts.exec.console_manager import extract_console_summary
from scripts.exec.fi_collector import collect_fi_output
from scripts.logging import logger


def load_session_info(session):
    """
    Load session_info.json file from session directory.
    
    Args:
        session: Session object
    
    Returns:
        Dictionary with session info, or empty dict if not found
    """
    if not session.session_dir:
        return {}
    
    info_path = session.session_dir / "session_info.json"
    
    if not info_path.exists():
        logger.log_event('DEBUG', debug_message=f"No session_info.json in {session.session_dir}")
        return {}
    
    try:
        with info_path.open('r') as f:
            info = json.load(f)
        return info
    except Exception as e:
        logger.log_event('WARNING', warning_message=f"Error loading session info: {e}")
        return {}


def extract_benchmark_metrics(session):
    """
    Extract benchmark performance metrics from console output.
    
    This parses the console log to find benchmark-specific metrics like
    iterations completed, scores, execution time, etc.
    
    Args:
        session: Session object
    
    Returns:
        Dictionary with benchmark metrics
    """
    if not session.console_output_path or not session.console_output_path.exists():
        logger.log_event('DEBUG', debug_message=f"No console output for session {session.session_id}")
        return {}
    
    # Use console manager to extract metrics
    metrics = extract_console_summary(session.console_output_path)
    
    return metrics


def extract_fi_metrics(session):
    """
    Extract fault injection metrics from FI logs.
    
    Args:
        session: Session object
    
    Returns:
        Dictionary with FI metrics
    """
    if not session.injection_enabled:
        return {}
    
    if not session.session_dir:
        return {}
    
    # Collect FI output
    fi_data = collect_fi_output(session.session_dir)
    
    if not fi_data or not fi_data.get('log_exists'):
        logger.log_event('DEBUG', debug_message=f"No FI output for session {session.session_id}")
        return {}
    
    # Extract key FI metrics
    parsed = fi_data.get('parsed', {})
    
    fi_metrics = {
        'injection_count': parsed.get('injection_count', 0),
        'location_count': parsed.get('location_count', 0),
        'has_errors': parsed.get('has_errors', False),
        'timing': parsed.get('timing', {}),
    }
    
    # Add error counts if available
    errors = parsed.get('errors', {})
    if errors:
        fi_metrics['errors'] = errors
    
    return fi_metrics


def load_metrics_file(session):
    """
    Load metrics.json file if present.
    
    Some benchmarks may write their own metrics file with
    performance counters, resource usage, etc.
    
    Args:
        session: Session object
    
    Returns:
        Dictionary with metrics, or empty dict
    """
    if not session.metrics_path or not session.metrics_path.exists():
        return {}
    
    try:
        with session.metrics_path.open('r') as f:
            metrics = json.load(f)
        return metrics if isinstance(metrics, dict) else {}
    except Exception as e:
        logger.log_event('WARNING', warning_message=f"Error loading metrics file: {e}")
        return {}


def compute_session_success_rate(session, session_info):
    """
    Determine if session was successful.
    
    Args:
        session: Session object
        session_info: Loaded session info dict
    
    Returns:
        Boolean indicating success
    """
    # Check session status
    if session.status != "success":
        return False
    
    # If FI was enabled, check FI success
    if session.injection_enabled:
        fi_success = session_info.get('fi_success', False)
        if not fi_success:
            return False
    
    return True


def collect_session_metrics(session):
    """
    Collect comprehensive metrics from a session.
    
    This is the main entry point for session metrics collection.
    It gathers metrics from:
    - Session object (duration, status, etc.)
    - Console output (benchmark performance)
    - FI logs (injection data)
    - metrics.json file (if present)
    - session_info.json (metadata)
    
    Args:
        session: Session object
    
    Returns:
        Dictionary with SessionMetrics:
        {
            'session_id': int,
            'benchmark_name': str,
            'duration_s': float,
            'status': str,
            'success': bool,
            'timeout_occurred': bool,
            'benchmark_metrics': dict,
            'fi_metrics': dict,
            'error_message': str or None
        }
    """
    logger.log_event('DEBUG', debug_message=f"Collecting metrics for session {session.session_id}")
    
    # Load session info file
    session_info = load_session_info(session)
    
    # Extract benchmark performance metrics
    benchmark_metrics = extract_benchmark_metrics(session)
    
    # Extract FI metrics if enabled
    fi_metrics = extract_fi_metrics(session)
    
    # Load additional metrics file if present
    additional_metrics = load_metrics_file(session)
    
    # Determine success
    success = compute_session_success_rate(session, session_info)
    
    # Build comprehensive metrics dictionary
    metrics = {
        'session_id': session.session_id,
        'benchmark_name': session.benchmark_name,
        'duration_s': session.get_duration(),
        'status': session.status,
        'success': success,
        'timeout_occurred': session.status == "timeout",
        'injection_enabled': session.injection_enabled,
        'benchmark_metrics': benchmark_metrics,
        'fi_metrics': fi_metrics,
        'additional_metrics': additional_metrics,
        'error_message': None
    }
    
    # Extract error message if failed
    if not success:
        exec_result = session_info.get('execution_result', {})
        metrics['error_message'] = exec_result.get('error_message')
    
    # Extract specific performance indicators
    if benchmark_metrics:
        # Look for common performance metrics
        if 'execution_time' in benchmark_metrics:
            metrics['benchmark_execution_time'] = benchmark_metrics['execution_time']
        
        if 'iterations' in benchmark_metrics:
            metrics['benchmark_iterations'] = benchmark_metrics['iterations']
        
        if 'performance' in benchmark_metrics:
            metrics['benchmark_score'] = benchmark_metrics['performance']
    
    # Extract FI-specific indicators
    if fi_metrics:
        metrics['fi_injection_count'] = fi_metrics.get('injection_count', 0)
        
        # Error detection indicators
        if 'errors' in fi_metrics:
            errors = fi_metrics['errors']
            metrics['fi_detected_errors'] = errors.get('injection_errors', 0)
        
        # FI timing
        if 'timing' in fi_metrics and fi_metrics['timing']:
            metrics['fi_duration'] = fi_metrics['timing'].get('duration', 0)
    
    logger.log_event('DEBUG', debug_message=f"Session {session.session_id} metrics: {metrics.keys()}")
    
    return metrics


def collect_all_session_metrics(sessions):
    """
    Collect metrics from a list of sessions.
    
    Args:
        sessions: List of Session objects
    
    Returns:
        List of session metrics dictionaries
    """
    all_metrics = []
    
    for session in sessions:
        try:
            metrics = collect_session_metrics(session)
            all_metrics.append(metrics)
        except Exception as e:
            logger.log_event('ERROR', error_message=f"Error collecting metrics for session {session.session_id}: {e}")
            # Add minimal metrics entry
            all_metrics.append({
                'session_id': session.session_id,
                'benchmark_name': session.benchmark_name,
                'status': 'error',
                'success': False,
                'error_message': str(e)
            })
    
    logger.log_event('DEBUG', debug_message=f"Collected metrics from {len(all_metrics)} sessions")
    
    return all_metrics