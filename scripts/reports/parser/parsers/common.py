# =============================================================================
# FATORI-V • FI Report Parsing Utilities
# File: parsers/common.py
# -----------------------------------------------------------------------------
# Shared utilities for parsing Vivado text reports
# =============================================================================

import re


def read_file(filepath):
    """
    Read entire file and return as list of lines
    
    Args:
        filepath: Path to file
    
    Returns:
        List of strings (one per line)
    
    Note: Reads entire file into memory - suitable for report files (<1GB)
    """
    with open(filepath, 'r') as f:
        return f.readlines()


def find_line_with_text(lines, search_text, start_line=0):
    """
    Find first line containing search text
    
    Args:
        lines: List of lines to search
        search_text: Text to find
        start_line: Line index to start from (0-based)
    
    Returns:
        Line index (0-based) or -1 if not found
    
    Example:
        line_num = find_line_with_text(lines, "CLB Logic")
        if line_num >= 0:
            # Process section starting at line_num
    """
    for i in range(start_line, len(lines)):
        if search_text in lines[i]:
            return i
    return -1


def extract_value_from_line(line, pattern):
    """
    Extract value using regex pattern
    
    Args:
        line: Line to search
        pattern: Regex with one capture group
    
    Returns:
        Captured value (stripped) or None
    
    Example:
        value = extract_value_from_line(line, r"Used:\s+(\d+)")
    """
    match = re.search(pattern, line)
    if match:
        return match.group(1).strip()
    return None


def parse_table_row(line):
    """
    Parse Vivado table row with | separators
    
    Args:
        line: Table row like "| Cell | Value | Available |"
    
    Returns:
        List of cell values (whitespace stripped)
    
    Example:
        cells = parse_table_row("| LUTs | 9492 | 242400 | 3.92 |")
        # Returns: ['LUTs', '9492', '242400', '3.92']
    """
    cells = line.split('|')
    # Remove empty cells, strip whitespace
    return [cell.strip() for cell in cells if cell.strip()]


def extract_number(text):
    """
    Extract first number from text (integer or float)
    
    Args:
        text: String potentially containing number
    
    Returns:
        Number as string, or original text if no number found
    
    Example:
        extract_number("Used: 123") -> "123"
        extract_number("3.14 MHz") -> "3.14"
    """
    match = re.search(r'[\d.]+', text)
    if match:
        return match.group()
    return text


def extract_common_info(lines):
    """
    Extract metadata present in all Vivado reports
    
    Args:
        lines: List of lines from report file
    
    Returns:
        Dictionary with common parameters:
        - Vivado Version
        - Date
        - Design
        - Device  
        - Design State
    
    Note: Typically found in first 15 lines of report
    """
    common_info = {}
    
    # Extract Tool Version (e.g., "Vivado v.2020.2")
    tool_line = find_line_with_text(lines, "Tool Version")
    if tool_line >= 0:
        version = extract_value_from_line(lines[tool_line], r"Vivado\s+(v\.\S+)")
        if version:
            common_info['Vivado Version'] = version
    
    # Extract Date
    date_line = find_line_with_text(lines, "Date")
    if date_line >= 0:
        date = extract_value_from_line(lines[date_line], r"Date\s+:\s+(.+)")
        if date:
            common_info['Date'] = date
    
    # Extract Design name
    design_line = find_line_with_text(lines, "Design")
    if design_line >= 0:
        design = extract_value_from_line(lines[design_line], r"Design\s+:\s+(\S+)")
        if design:
            common_info['Design'] = design
    
    # Extract Device (FPGA part number)
    device_line = find_line_with_text(lines, "Device")
    if device_line >= 0:
        device = extract_value_from_line(lines[device_line], r"Device\s+:\s+(\S+)")
        if device:
            common_info['Device'] = device
    
    # Extract Design State (e.g., "Routed")
    state_line = find_line_with_text(lines, "Design State")
    if state_line >= 0:
        state = extract_value_from_line(lines[state_line], r"Design State\s+:\s+(.+)")
        if state:
            common_info['Design State'] = state
    
    return common_info