# =============================================================================
# FATORI-V • FI Report Parsing - Clocks
# File: parsers/parse_clocks.py
# -----------------------------------------------------------------------------
# Parses clock domain information
# =============================================================================

import common


def parse(filepath):
    """
    Parse clocks report
    
    Args:
        filepath: Path to *_clocks.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - All clock domains (name, period, frequency)
        - Generated clocks and their masters
        - Clock types (primary vs generated)
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Find main clock table
    clock_report_line = common.find_line_with_text(lines, "Clock Report")
    if clock_report_line >= 0:
        clock_count = 0
        
        # Look for clock entries
        for i in range(clock_report_line + 5, min(clock_report_line + 30, len(lines))):
            line = lines[i]
            
            # Stop at empty lines or section markers
            if line.strip() == '' or '====' in line:
                break
            
            # Skip header lines
            if 'Clock' in line and 'Period' in line:
                continue
            
            # Parse clock lines (have period and waveform)
            if not line.strip().startswith('Clock') and line.strip():
                parts = line.split()
                
                if len(parts) >= 3:
                    clock_name = parts[0]
                    period = parts[1]
                    
                    # Calculate frequency from period
                    try:
                        period_val = float(period)
                        frequency = 1000.0 / period_val  # Convert to MHz
                        
                        clock_count += 1
                        data.append((f"Clock {clock_count} - Name", clock_name))
                        data.append((f"Clock {clock_count} - Period (ns)", period))
                        data.append((f"Clock {clock_count} - Frequency (MHz)", 
                                   f"{frequency:.3f}"))
                        
                        # Check if generated clock
                        if 'G' in line or 'Generated' in line:
                            data.append((f"Clock {clock_count} - Type", "Generated"))
                        else:
                            data.append((f"Clock {clock_count} - Type", "Primary"))
                    except ValueError:
                        pass
        
        data.append(("Total Number of Clocks", str(clock_count)))
    
    # Parse "Generated Clocks" section
    gen_clocks_line = common.find_line_with_text(lines, "Generated Clocks")
    if gen_clocks_line >= 0:
        gen_clock_count = 0
        
        for i in range(gen_clocks_line, min(gen_clocks_line + 20, len(lines))):
            line = lines[i]
            
            if "Generated Clock" in line and ":" in line:
                gen_clock_count += 1
                clock_name = line.split(':')[1].strip()
                data.append((f"Generated Clock {gen_clock_count} - Name", clock_name))
            
            elif "Master Clock" in line and ":" in line:
                master = line.split(':')[1].strip()
                data.append((f"Generated Clock {gen_clock_count} - Master", master))
        
        if gen_clock_count > 0:
            data.append(("Total Generated Clocks", str(gen_clock_count)))
    
    return data, common_info