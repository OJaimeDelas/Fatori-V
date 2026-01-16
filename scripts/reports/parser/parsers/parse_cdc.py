# =============================================================================
# FATORI-V • FI Report Parsing - CDC
# File: parsers/parse_cdc.py
# -----------------------------------------------------------------------------
# Parses clock domain crossing safety metrics
# =============================================================================

import common


def parse(filepath):
    """
    Parse CDC report
    
    Args:
        filepath: Path to *_cdc.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Total CDC paths
        - CDC violations
        - Missing synchronizers
        - Unsafe paths
        - Clock pairs with CDC
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Parse summary section
    summary_line = common.find_line_with_text(lines, "Summary")
    if summary_line >= 0:
        for i in range(summary_line, min(summary_line + 30, len(lines))):
            line = lines[i]
            
            if "Total CDC paths" in line or "Total Paths" in line:
                count = common.extract_value_from_line(line, r":\s*(\d+)")
                if count:
                    data.append(("Total CDC Paths", count))
            
            elif "Violations" in line:
                violations = common.extract_value_from_line(line, r":\s*(\d+)")
                if violations:
                    data.append(("CDC Violations", violations))
            
            elif "Safe" in line and "paths" in line.lower():
                safe = common.extract_value_from_line(line, r":\s*(\d+)")
                if safe:
                    data.append(("CDC Safe Paths", safe))
    
    # Look for specific violation types
    violation_types = [
        ("Missing Synchronizer", "CDC - Missing Synchronizers"),
        ("No Constraint", "CDC - Paths Without Constraints"),
        ("Unsafe", "CDC - Unsafe Paths"),
        ("Reconvergence", "CDC - Reconvergent Paths"),
        ("Multi-bit", "CDC - Multi-bit CDC Issues")
    ]
    
    for search_term, metric_name in violation_types:
        term_line = common.find_line_with_text(lines, search_term)
        if term_line >= 0:
            for i in range(max(0, term_line - 2), min(term_line + 5, len(lines))):
                count = common.extract_value_from_line(lines[i], r":\s*(\d+)")
                if count:
                    data.append((metric_name, count))
                    break
    
    # Look for clock pairs
    pairs_line = common.find_line_with_text(lines, "Clock Pairs")
    if pairs_line >= 0:
        clock_pairs = []
        
        for i in range(pairs_line, min(pairs_line + 50, len(lines))):
            line = lines[i]
            
            if '->' in line or 'to' in line:
                parts = line.split()
                if len(parts) >= 3:
                    clock_pairs.append(line.strip()[:60])
            
            if len(clock_pairs) >= 5:
                break
        
        if clock_pairs:
            data.append(("CDC Clock Pairs Count", str(len(clock_pairs))))
            for i, pair in enumerate(clock_pairs[:5]):
                data.append((f"CDC Pair {i+1}", pair))
    
    # Check for asynchronous groups
    async_line = common.find_line_with_text(lines, "Asynchronous")
    if async_line >= 0:
        data.append(("Has Asynchronous Clock Groups", "YES"))
    
    # Look for false path constraints
    false_path_line = common.find_line_with_text(lines, "false_path")
    if false_path_line >= 0:
        count = 0
        for i in range(false_path_line, min(false_path_line + 20, len(lines))):
            if "false_path" in lines[i]:
                count += 1
        
        if count > 0:
            data.append(("False Path Constraints", str(count)))
    
    return data, common_info