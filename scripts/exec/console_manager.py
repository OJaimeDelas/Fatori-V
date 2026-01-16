# =============================================================================
# FATORI-V • Execution • Console Output Manager
# File: console_manager.py
# -----------------------------------------------------------------------------
# Manages console output capture and parsing for benchmark execution.
# =============================================================================

import re
import logging  # Used for FileHandler utility class
from pathlib import Path
from typing import Dict, Optional
from scripts.logging.logger import log_event


def create_console_logger(output_path):
    """
    Create a file logger for console output.
    
    This creates a file handler that logs all output to the specified path.
    
    Args:
        output_path: Path where console output should be logged
    
    Returns:
        Logging handler object
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create file handler
    file_handler = logging.FileHandler(output_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Simple format for console output (just the message)
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    
    return file_handler


def stream_output(process, output_path):
    """
    Stream process output to console and log file.
    
    This reads stdout/stderr from a process and writes to both
    console (via logger) and a log file.
    
    Args:
        process: subprocess.Popen object
        output_path: Path to output log file
    
    Returns:
        List of output lines
    """
    output_lines = []
    
    # Open output file
    with open(output_path, 'w', encoding='utf-8') as f:
        # Read output line by line
        if process.stdout:
            for line in iter(process.stdout.readline, b''):
                if not line:
                    break
                
                decoded = line.decode('utf-8', errors='replace').rstrip()
                output_lines.append(decoded)
                
                # Write to file
                f.write(decoded + '\n')
                f.flush()
                
                # Log at debug level to avoid spam
                log_event('CONSOLE_OUTPUT_LINE', line=decoded)
        
        # Also read stderr if available
        if process.stderr:
            for line in iter(process.stderr.readline, b''):
                if not line:
                    break
                
                decoded = line.decode('utf-8', errors='replace').rstrip()
                output_lines.append(decoded)
                
                # Write to file with marker
                f.write('[STDERR] ' + decoded + '\n')
                f.flush()
                
                # Log as warning
                log_event('CONSOLE_STDERR_LINE', line=decoded)
    
    return output_lines


def parse_benchmark_output(output):
    """
    Parse benchmark console output to extract key metrics.
    
    This looks for common patterns in benchmark output to extract:
    - Execution time
    - Iterations completed
    - Performance metrics
    - Error messages
    
    Args:
        output: String or list of output lines
    
    Returns:
        Dictionary with extracted metrics
    """
    metrics = {}
    
    # Convert to list if string
    if isinstance(output, str):
        lines = output.split('\n')
    else:
        lines = output
    
    # Patterns to search for
    patterns = {
        'execution_time': [
            r'time[:\s]+(\d+\.?\d*)\s*s',  # "time: 1.23 s"
            r'elapsed[:\s]+(\d+\.?\d*)',   # "elapsed: 1.23"
        ],
        'iterations': [
            r'iterations[:\s]+(\d+)',      # "iterations: 1000"
            r'completed[:\s]+(\d+)',       # "completed: 1000"
        ],
        'performance': [
            r'(\d+\.?\d*)\s*mips',         # "12.5 MIPS"
            r'score[:\s]+(\d+\.?\d*)',     # "score: 123.45"
        ],
    }
    
    # Search for patterns in output
    for metric_name, pattern_list in patterns.items():
        for pattern in pattern_list:
            regex = re.compile(pattern, re.IGNORECASE)
            
            for line in lines:
                match = regex.search(line)
                if match:
                    try:
                        value = float(match.group(1))
                        metrics[metric_name] = value
                        break
                    except (ValueError, IndexError):
                        continue
            
            if metric_name in metrics:
                break
    
    # Look for error indicators
    error_patterns = [
        r'error[:\s]',
        r'failed[:\s]',
        r'exception[:\s]',
        r'abort',
    ]
    
    has_error = False
    error_lines = []
    
    for line in lines:
        for pattern in error_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                has_error = True
                error_lines.append(line)
                break
    
    if has_error:
        metrics['has_error'] = True
        metrics['error_count'] = len(error_lines)
        metrics['error_sample'] = error_lines[0] if error_lines else None
    
    return metrics


def extract_console_summary(output_path):
    """
    Extract summary information from console output file.
    
    Args:
        output_path: Path to console output log
    
    Returns:
        Dictionary with summary metrics
    """
    output_path = Path(output_path)
    
    if not output_path.exists():
        log_event('CONSOLE_OUTPUT_NOT_FOUND', output_path=str(output_path))
        return {}
    
    try:
        with output_path.open('r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        metrics = parse_benchmark_output(content)
        return metrics
    except Exception as e:
        log_event('CONSOLE_SUMMARY_ERROR', error_message=str(e))
        return {}