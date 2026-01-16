# =============================================================================
# FATORI-V • FI Report Parsing - Power
# File: parsers/parse_power.py
# -----------------------------------------------------------------------------
# Parses power consumption breakdown
# =============================================================================

import common


def parse(filepath):
    """
    Parse power report
    
    Args:
        filepath: Path to *_power.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Total on-chip power
        - Dynamic vs static power breakdown
        - Power by component (clocks, logic, signals, BRAM, DSP, I/O)
        - Junction temperature
        - Confidence level
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Parse "1. Summary" section
    summary_line = common.find_line_with_text(lines, "1. Summary")
    if summary_line >= 0:
        for i in range(summary_line, min(summary_line + 20, len(lines))):
            line = lines[i]
            
            if "Total On-Chip Power (W)" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Total On-Chip Power (W)", cells[1]))
            
            elif "Dynamic (W)" in line and "Dynamic (A)" not in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Dynamic Power (W)", cells[1]))
            
            elif "Device Static (W)" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Static Power (W)", cells[1]))
            
            elif "Junction Temperature (C)" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Junction Temperature (C)", cells[1]))
            
            elif "Max Ambient (C)" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Max Ambient (C)", cells[1]))
            
            elif "Confidence Level" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power Confidence Level", cells[1]))
    
    # Parse "1.1 On-Chip Components" section
    components_line = common.find_line_with_text(lines, "1.1 On-Chip Components")
    if components_line >= 0:
        for i in range(components_line, min(components_line + 30, len(lines))):
            line = lines[i]
            
            if "| Clocks" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - Clocks (W)", cells[1]))
            
            elif "| CLB Logic" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - CLB Logic (W)", cells[1]))
            
            elif "| LUT as Logic" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - LUT as Logic (W)", cells[1]))
            
            elif "| Register" in line and "LUT" not in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - Registers (W)", cells[1]))
            
            elif "| Signals" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - Signals (W)", cells[1]))
            
            elif "| Block RAM" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - Block RAM (W)", cells[1]))
            
            elif "| PLL" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - PLL (W)", cells[1]))
            
            elif "| DSPs" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - DSPs (W)", cells[1]))
            
            elif "| I/O" in line:
                cells = common.parse_table_row(line)
                if len(cells) >= 2:
                    data.append(("Power - I/O (W)", cells[1]))
    
    # Calculate dynamic/static percentages
    try:
        dynamic_val = None
        static_val = None
        for item in data:
            if item[0] == "Dynamic Power (W)":
                dynamic_val = float(item[1])
            elif item[0] == "Static Power (W)":
                static_val = float(item[1])
        
        if dynamic_val is not None and static_val is not None:
            total = dynamic_val + static_val
            if total > 0:
                dynamic_pct = (dynamic_val / total) * 100
                static_pct = (static_val / total) * 100
                data.append(("Dynamic Power %", f"{dynamic_pct:.1f}"))
                data.append(("Static Power %", f"{static_pct:.1f}"))
    except:
        pass
    
    return data, common_info