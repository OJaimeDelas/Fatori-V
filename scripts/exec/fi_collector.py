# =============================================================================
# FATORI-V • Execution • FI Output Collector
# File: fi_collector.py
# -----------------------------------------------------------------------------
# Collects and parses fault injection output logs and metrics.
# =============================================================================

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from scripts.logging import logger


def find_injection_log(session_dir):
    """
    Find injection log file in session directory.
    
    Searches for injection_log.txt or fi.log in the session directory.
    
    Args:
        session_dir: Path to session directory
    
    Returns:
        Path to injection log, or None if not found
    """
    session_dir = Path(session_dir)
    
    # Common names for injection logs
    log_names = ['injection_log.txt', 'fi.log', 'fi_output.log']
    
    for log_name in log_names:
        log_path = session_dir / log_name
        if log_path.exists():
            logger.log_event('DEBUG', debug_message=f"Found injection log: {log_path}")
            return log_path
    
    logger.log_event('WARNING', warning_message=f"No injection log found in {session_dir}")
    return None


def parse_injection_count(log_content):
    """
    Extract total injection count from log.
    
    Args:
        log_content: String containing log file content
    
    Returns:
        Integer with injection count, or 0 if not found
    """
    # Look for patterns like "Total injections: 1234"
    patterns = [
        r'Total\s+injections[:\s]+(\d+)',
        r'Injection\s+count[:\s]+(\d+)',
        r'(\d+)\s+injections\s+performed',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, log_content, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0


def parse_injection_locations(log_content):
    """
    Extract injection locations from log.
    
    Args:
        log_content: String containing log file content
    
    Returns:
        List of injection location dictionaries
    """
    locations = []
    
    # Look for patterns like "Injection at address 0x12345678"
    pattern = r'Injection\s+at\s+(?:address\s+)?(0x[0-9a-fA-F]+|[\d]+)'
    
    for match in re.finditer(pattern, log_content, re.IGNORECASE):
        addr_str = match.group(1)
        
        # Convert to integer
        if addr_str.startswith('0x'):
            addr = int(addr_str, 16)
        else:
            addr = int(addr_str)
        
        locations.append({'address': addr})
    
    return locations


def parse_timing_information(log_content):
    """
    Extract timing information from log.
    
    Args:
        log_content: String containing log file content
    
    Returns:
        Dictionary with timing metrics
    """
    timing = {}
    
    # Look for start/end times
    patterns = {
        'start_time': r'Start\s+time[:\s]+([\d.]+)',
        'end_time': r'End\s+time[:\s]+([\d.]+)',
        'duration': r'Duration[:\s]+([\d.]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, log_content, re.IGNORECASE)
        if match:
            timing[key] = float(match.group(1))
    
    # Calculate duration if start and end present but duration not
    if 'start_time' in timing and 'end_time' in timing and 'duration' not in timing:
        timing['duration'] = timing['end_time'] - timing['start_time']
    
    return timing


def parse_error_rates(log_content):
    """
    Extract error rates and statistics from log.
    
    Args:
        log_content: String containing log file content
    
    Returns:
        Dictionary with error statistics
    """
    errors = {}
    
    # Look for error-related patterns
    patterns = {
        'injection_errors': r'Injection\s+errors[:\s]+(\d+)',
        'communication_errors': r'Communication\s+errors[:\s]+(\d+)',
        'timeout_errors': r'Timeout\s+errors[:\s]+(\d+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, log_content, re.IGNORECASE)
        if match:
            errors[key] = int(match.group(1))
    
    return errors


def parse_injection_log(log_path):
    """
    Parse injection log file and extract all metrics.
    
    This reads the FI console output log and extracts:
    - Injection count
    - Injection locations
    - Timing information
    - Error statistics
    
    Args:
        log_path: Path to injection log file
    
    Returns:
        Dictionary with parsed metrics
    """
    log_path = Path(log_path)
    
    if not log_path.exists():
        logger.log_event('WARNING', warning_message=f"Injection log not found: {log_path}")
        return {}
    
    try:
        # Read log file
        with log_path.open('r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Parse different sections
        metrics = {
            'injection_count': parse_injection_count(content),
            'locations': parse_injection_locations(content),
            'timing': parse_timing_information(content),
            'errors': parse_error_rates(content),
            'log_size_bytes': log_path.stat().st_size,
        }
        
        # Add summary stats
        metrics['location_count'] = len(metrics['locations'])
        metrics['has_errors'] = sum(metrics['errors'].values()) > 0 if metrics['errors'] else False
        
        logger.log_event('DEBUG', debug_message=f"Parsed injection log: {metrics['injection_count']} injections")
        
        return metrics
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error parsing injection log: {e}")
        return {}


def extract_fi_metrics(log_content):
    """
    Extract FI console metrics from log content.
    
    This looks for structured metrics output by the FI console,
    typically in JSON or key=value format.
    
    Args:
        log_content: String containing log content
    
    Returns:
        Dictionary with FI metrics
    """
    metrics = {}
    
    # Try to find JSON metrics block
    json_match = re.search(r'\{[^{}]*"injections"[^{}]*\}', log_content, re.DOTALL)
    if json_match:
        try:
            metrics = json.loads(json_match.group(0))
            logger.log_event('DEBUG', debug_message="Extracted JSON metrics from FI log")
            return metrics
        except json.JSONDecodeError:
            pass
    
    # Fall back to key=value parsing
    kv_patterns = {
        'injections': r'injections[:\s=]+(\d+)',
        'successful': r'successful[:\s=]+(\d+)',
        'failed': r'failed[:\s=]+(\d+)',
        'rate': r'rate[:\s=]+([\d.]+)',
    }
    
    for key, pattern in kv_patterns.items():
        match = re.search(pattern, log_content, re.IGNORECASE)
        if match:
            try:
                # Try float first, fall back to int
                metrics[key] = float(match.group(1))
                if metrics[key].is_integer():
                    metrics[key] = int(metrics[key])
            except ValueError:
                pass
    
    return metrics


def collect_fi_output(session_dir):
    """
    Collect all FI output from a session directory.
    
    This is the main entry point for FI output collection.
    It finds the injection log, parses it, and returns all metrics.
    
    Args:
        session_dir: Path to session directory
    
    Returns:
        Dictionary with FI output data:
        {
            'log_path': Path or None,
            'log_exists': bool,
            'metrics': dict,
            'parsed': dict (from parse_injection_log)
        }
    """
    session_dir = Path(session_dir)
    
    # Find injection log
    log_path = find_injection_log(session_dir)
    
    if not log_path:
        logger.log_event('WARNING', warning_message=f"No FI output found in {session_dir}")
        return {
            'log_path': None,
            'log_exists': False,
            'metrics': {},
            'parsed': {}
        }
    
    # Parse injection log
    parsed = parse_injection_log(log_path)
    
    # Extract metrics from log content
    with log_path.open('r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    metrics = extract_fi_metrics(content)
    
    return {
        'log_path': log_path,
        'log_exists': True,
        'metrics': metrics,
        'parsed': parsed
    }