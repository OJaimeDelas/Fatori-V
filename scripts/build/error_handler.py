# =============================================================================
# FATORI-V • Build System • Error Handler
# File: error_handler.py
# -----------------------------------------------------------------------------
# Parses and categorizes build errors with suggested fixes.
# =============================================================================

import re
from pathlib import Path
from scripts.logging.logger import log_event


def parse_vivado_error(log_content):
    """
    Extract ERROR and CRITICAL WARNING messages from Vivado log.
    
    Vivado errors typically have format:
    ERROR: [<category>-<number>] <message>
    CRITICAL WARNING: [<category>-<number>] <message>
    
    Args:
        log_content: String containing log file content
    
    Returns:
        List of error message strings
    """
    errors = []
    
    # Split into lines
    lines = log_content.split('\n')
    
    # Patterns to match
    error_pattern = re.compile(r'ERROR:\s*\[([\w\-]+)\]\s*(.+)')
    critical_pattern = re.compile(r'CRITICAL WARNING:\s*\[([\w\-]+)\]\s*(.+)')
    
    for line in lines:
        # Check for ERROR
        match = error_pattern.search(line)
        if match:
            category = match.group(1)
            message = match.group(2)
            errors.append(f"ERROR [{category}]: {message}")
            continue
        
        # Check for CRITICAL WARNING
        match = critical_pattern.search(line)
        if match:
            category = match.group(1)
            message = match.group(2)
            errors.append(f"CRITICAL [{category}]: {message}")
    
    return errors


def parse_vivado_log_file(log_file_path):
    """
    Parse a Vivado log file and extract errors.
    
    Args:
        log_file_path: Path to Vivado log file
    
    Returns:
        List of error messages
    """
    log_file_path = Path(log_file_path)
    
    if not log_file_path.exists():
        log_event('BUILD_LOG_NOT_FOUND', log_file=str(log_file_path))
        return []
    
    try:
        with log_file_path.open('r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        errors = parse_vivado_error(content)
        return errors
    
    except Exception as e:
        log_event('BUILD_LOG_READ_ERROR',
                  log_file=str(log_file_path),
                  error_message=str(e))
        return []


def categorize_error(error_message):
    """
    Categorize an error message into a type.
    
    Categories:
    - timing: Timing constraint violations
    - synthesis: Synthesis errors
    - implementation: Place & route errors
    - resources: Resource utilization errors
    - other: Uncategorized errors
    
    Args:
        error_message: Error message string
    
    Returns:
        String indicating error category
    """
    error_lower = error_message.lower()
    
    # Timing-related errors
    timing_keywords = [
        'timing',
        'setup',
        'hold',
        'clock',
        'constraint',
        'frequency',
        'slack'
    ]
    
    if any(keyword in error_lower for keyword in timing_keywords):
        return 'timing'
    
    # Synthesis errors
    synthesis_keywords = [
        'synthesis',
        'synth',
        'elaborate',
        'parse',
        'syntax'
    ]
    
    if any(keyword in error_lower for keyword in synthesis_keywords):
        return 'synthesis'
    
    # Implementation errors
    implementation_keywords = [
        'place',
        'route',
        'implementation',
        'drc',
        'unroutable'
    ]
    
    if any(keyword in error_lower for keyword in implementation_keywords):
        return 'implementation'
    
    # Resource errors
    resource_keywords = [
        'resource',
        'utilization',
        'lut',
        'bram',
        'dsp',
        'insufficient'
    ]
    
    if any(keyword in error_lower for keyword in resource_keywords):
        return 'resources'
    
    # Default category
    return 'other'


def suggest_fix(error_category, error_message=None):
    """
    Provide suggested fixes based on error category.
    
    Args:
        error_category: Category of the error
        error_message: Optional full error message for context
    
    Returns:
        String with suggested fix
    """
    suggestions = {
        'timing': (
            "Timing constraint violations suggest:\n"
            "  • Review clock frequency settings in config\n"
            "  • Check if pblock placement is too tight\n"
            "  • Consider reducing target clock frequency\n"
            "  • Review critical paths in timing report"
        ),
        'synthesis': (
            "Synthesis errors suggest:\n"
            "  • Check SystemVerilog syntax in generated headers\n"
            "  • Verify all required files are present\n"
            "  • Review macro definitions in fatori_*.svh files\n"
            "  • Check for undefined signals or modules"
        ),
        'implementation': (
            "Implementation errors suggest:\n"
            "  • Pblock constraints may be too restrictive\n"
            "  • Check clock region utilization\n"
            "  • Review placement constraints in TCL files\n"
            "  • Consider relaxing pblock boundaries"
        ),
        'resources': (
            "Resource utilization errors suggest:\n"
            "  • Design exceeds FPGA capacity\n"
            "  • Reduce M-of-N redundancy levels\n"
            "  • Disable optional features (icache, etc.)\n"
            "  • Use simpler ISA configuration"
        ),
        'other': (
            "General troubleshooting steps:\n"
            "  • Review complete build log for details\n"
            "  • Check Vivado version compatibility\n"
            "  • Verify all input files are present\n"
            "  • Try clean rebuild: make clean setup"
        )
    }
    
    suggestion = suggestions.get(error_category, suggestions['other'])
    
    return suggestion


def analyze_build_failure(log_file_path):
    """
    Analyze a build log file and provide comprehensive error report.
    
    Args:
        log_file_path: Path to build log file
    
    Returns:
        Dictionary with analysis results:
        {
            'errors': [list of errors],
            'categories': {category: count},
            'suggestions': {category: suggestion}
        }
    """
    # Parse errors from log
    errors = parse_vivado_log_file(log_file_path)
    
    if not errors:
        log_event('BUILD_ERROR_ANALYSIS_NO_ERRORS')
        return {
            'errors': [],
            'categories': {},
            'suggestions': {}
        }
    
    # Categorize errors
    category_counts = {}
    for error in errors:
        category = categorize_error(error)
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Generate suggestions for each category
    suggestions = {}
    for category in category_counts:
        suggestions[category] = suggest_fix(category)
    
    log_event('BUILD_ERROR_ANALYSIS_COMPLETE',
              error_count=len(errors),
              category_count=len(category_counts))
    
    return {
        'errors': errors,
        'categories': category_counts,
        'suggestions': suggestions
    }