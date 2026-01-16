# =============================================================================
# FATORI-V • FI Report Parsing - Timing Summary
# File: parsers/parse_timing.py
# -----------------------------------------------------------------------------
# Parses timing summary for WNS, WHS, and constraint status
# =============================================================================

import common


def parse(filepath):
    """
    Parse timing summary report
    
    Args:
        filepath: Path to *_timing_summary.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - WNS (Worst Negative Slack)
        - WHS (Worst Hold Slack)
        - TNS, THS (Total Negative/Hold Slack)
        - Failing endpoints count
        - Total endpoints count
        - Constraint status (met/not met)
        - Clock domain timing details
        - Maximum achievable frequency
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Find "Design Timing Summary" section
    timing_summary_line = common.find_line_with_text(lines, "Design Timing Summary")
    if timing_summary_line >= 0:
        # Look for data line (space-separated values)
        # Typical format: WNS TNS TNS_Fail TNS_Total WHS THS THS_Fail THS_Total ...
        for i in range(timing_summary_line, min(timing_summary_line + 15, len(lines))):
            line = lines[i]
            # Skip header and separator lines
            if 'WNS(ns)' in line or '---' in line or line.strip() == '':
                continue
            
            # Parse data line (has numbers)
            values = line.split()
            if len(values) >= 12:
                try:
                    # Validate first value is a number
                    float(values[0])
                    
                    # Extract timing metrics
                    data.append(("WNS (Worst Negative Slack)", values[0]))
                    data.append(("TNS (Total Negative Slack)", values[1]))
                    data.append(("TNS Failing Endpoints", values[2]))
                    data.append(("TNS Total Endpoints", values[3]))
                    data.append(("WHS (Worst Hold Slack)", values[4]))
                    data.append(("THS (Total Hold Slack)", values[5]))
                    data.append(("THS Failing Endpoints", values[6]))
                    data.append(("THS Total Endpoints", values[7]))
                    data.append(("WPWS (Worst Pulse Width Slack)", values[8]))
                    data.append(("TPWS (Total Pulse Width Slack)", values[9]))
                    data.append(("TPWS Failing Endpoints", values[10]))
                    data.append(("TPWS Total Endpoints", values[11]))
                    break
                except ValueError:
                    continue
    
    # Check constraint status
    constraints_line = common.find_line_with_text(lines, 
                        "All user specified timing constraints are met")
    if constraints_line >= 0:
        data.append(("All Timing Constraints Met", "YES"))
    else:
        violations_line = common.find_line_with_text(lines, 
                        "timing constraints are NOT met")
        if violations_line >= 0:
            data.append(("All Timing Constraints Met", "NO"))
    
    # Parse "Clock Summary" section
    clock_summary_line = common.find_line_with_text(lines, "Clock Summary")
    if clock_summary_line >= 0:
        clock_count = 0
        # Look for clock entries (have waveform brackets and period)
        for i in range(clock_summary_line + 5, min(clock_summary_line + 20, len(lines))):
            line = lines[i]
            
            # Stop at empty line or next section
            if line.strip() == '' or '---' in line:
                break
            
            # Clock lines have waveform notation: {0.000 2.000}
            if '{' in line and '}' in line:
                parts = line.split()
                if len(parts) >= 3:
                    clock_name = parts[0]
                    # Find period and frequency
                    period = None
                    freq = None
                    for j, part in enumerate(parts):
                        # Period is a number (ns)
                        if part.replace('.', '').isdigit() and j < len(parts) - 1:
                            period = part
                            if j + 1 < len(parts):
                                freq = parts[j + 1]
                                break
                    
                    if period and freq:
                        clock_count += 1
                        data.append((f"Clock {clock_count} - Name", clock_name))
                        data.append((f"Clock {clock_count} - Period (ns)", period))
                        data.append((f"Clock {clock_count} - Frequency (MHz)", freq))
        
        data.append(("Total Clock Domains", str(clock_count)))
    
    # Parse "Intra Clock Table" for per-clock timing
    intra_clock_line = common.find_line_with_text(lines, "Intra Clock Table")
    if intra_clock_line >= 0:
        # Find main design clock (usually has most endpoints)
        for i in range(intra_clock_line + 5, min(intra_clock_line + 25, len(lines))):
            line = lines[i]
            
            # Look for clock with significant endpoint count
            if "clk" in line.lower():
                values = line.split()
                if len(values) >= 12:
                    clock_name = values[0]
                    # Store main clock details
                    data.append(("Main Clock - Name", clock_name))
                    data.append(("Main Clock - WNS", values[1]))
                    data.append(("Main Clock - Total Endpoints", values[4]))
                    data.append(("Main Clock - WHS", values[5]))
                    break
    
    # Look for clock uncertainty
    uncertainty_line = common.find_line_with_text(lines, "clock uncertainty")
    if uncertainty_line >= 0:
        line = lines[uncertainty_line]
        uncertainty = common.extract_value_from_line(line, r"-([\d.]+)")
        if uncertainty:
            data.append(("Clock Uncertainty (ns)", uncertainty))
    
    return data, common_info