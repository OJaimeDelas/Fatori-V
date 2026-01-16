# =============================================================================
# FATORI-V • FI Report Parsing - DRC
# File: parsers/parse_drc.py
# -----------------------------------------------------------------------------
# Parses design rule check violations
# =============================================================================

import common


def parse(filepath):
    """
    Parse DRC report
    
    Args:
        filepath: Path to *_drc.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Total DRC violations
        - Per-rule violation counts
        - Severity breakdown (WARNING, CRITICAL, ADVISORY)
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Parse "REPORT SUMMARY" section
    summary_line = common.find_line_with_text(lines, "REPORT SUMMARY")
    if summary_line >= 0:
        # Look for total violations
        violations_line = common.find_line_with_text(lines, "Violations found:", summary_line)
        if violations_line >= 0:
            violations = common.extract_value_from_line(lines[violations_line], 
                                                       r"Violations found:\s+(\d+)")
            if violations:
                data.append(("Total DRC Violations", violations))
        
        # Parse violation table
        severity_count = {}
        for i in range(summary_line, min(summary_line + 30, len(lines))):
            line = lines[i]
            
            # Skip header and separator lines
            if '| Rule' in line or '| Severity' in line or '+---' in line:
                continue
            
            # Parse table rows
            if '|' in line:
                cells = common.parse_table_row(line)
                # Typical columns: Rule | Severity | Description | Violations
                if len(cells) >= 4:
                    rule = cells[0]
                    severity = cells[1]
                    description = cells[2]
                    count = cells[3]
                    
                    if rule and count and count.isdigit():
                        data.append((f"DRC {rule} - Severity", severity))
                        data.append((f"DRC {rule} - Description", description[:60]))
                        data.append((f"DRC {rule} - Count", count))
                        
                        # Track by severity
                        if severity in severity_count:
                            severity_count[severity] += int(count)
                        else:
                            severity_count[severity] = int(count)
        
        # Add severity totals
        for severity, count in severity_count.items():
            data.append((f"Total DRC {severity}", str(count)))
    
    return data, common_info