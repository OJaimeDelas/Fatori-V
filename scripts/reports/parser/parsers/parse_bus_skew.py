# =============================================================================
# FATORI-V • FI Report Parsing - Bus Skew
# File: parsers/parse_bus_skew.py
# -----------------------------------------------------------------------------
# Parses bus timing skew metrics
# =============================================================================

import common


def parse(filepath):
    """
    Parse bus skew report
    
    Args:
        filepath: Path to *_bus_skew.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Total buses analyzed
        - Maximum bus skew
        - Top 5 worst skew buses
        - Skew violations
        - Skew margin
    
    Use Cases:
        - Identify bus timing issues
        - Debug intermittent data corruption
        - Verify parallel bus integrity
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Parse summary section
    summary_line = common.find_line_with_text(lines, "Summary")
    if summary_line >= 0:
        for i in range(summary_line, min(summary_line + 20, len(lines))):
            line = lines[i]
            
            if "Total Buses" in line or "Number of Buses" in line:
                count = common.extract_value_from_line(line, r":\s*(\d+)")
                if count:
                    data.append(("Total Buses Analyzed", count))
            
            elif "Maximum Skew" in line or "Worst Skew" in line:
                skew = common.extract_value_from_line(line, r":\s*([-\d.]+)")
                if skew:
                    data.append(("Maximum Bus Skew (ns)", skew))
    
    # Parse bus skew table
    table_line = common.find_line_with_text(lines, "Bus")
    if table_line >= 0:
        buses = []
        
        for i in range(table_line, min(table_line + 100, len(lines))):
            line = lines[i]
            
            # Look for table rows with bus names and skew values
            if '|' in line and 'Bus' in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 3:
                    bus_name = cells[0]
                    # Skew value is typically last column
                    skew_val = cells[-1] if cells[-1].replace('.', '').replace('-', '').isdigit() else cells[-2]
                    
                    try:
                        skew_float = float(skew_val)
                        buses.append({
                            'name': bus_name,
                            'skew': skew_float
                        })
                    except ValueError:
                        pass
            
            if len(buses) >= 10:
                break
        
        if buses:
            # Sort by absolute skew (worst first)
            buses.sort(key=lambda x: abs(x['skew']), reverse=True)
            
            data.append(("Buses With Skew Data", str(len(buses))))
            
            # Report top 5 worst skew buses
            for i, bus in enumerate(buses[:5]):
                idx = i + 1
                data.append((f"Bus {idx} (Worst Skew) - Name", bus['name'][:50]))
                data.append((f"Bus {idx} (Worst Skew) - Skew (ns)", str(bus['skew'])))
    
    # Look for violations
    violation_line = common.find_line_with_text(lines, "violation")
    if violation_line >= 0:
        violation_count = 0
        for i in range(violation_line, min(violation_line + 20, len(lines))):
            if "violation" in lines[i].lower():
                count = common.extract_value_from_line(lines[i], r"(\d+)")
                if count:
                    violation_count = int(count)
                    break
        
        data.append(("Bus Skew Violations", str(violation_count)))
    
    # Look for margin
    margin_line = common.find_line_with_text(lines, "margin")
    if margin_line >= 0:
        for i in range(margin_line, min(margin_line + 10, len(lines))):
            margin = common.extract_value_from_line(lines[i], r"([-\d.]+)")
            if margin:
                data.append(("Bus Skew Margin (ns)", margin))
                break
    
    return data, common_info