# =============================================================================
# FATORI-V • FI Report Parsing - Timing Detail
# File: parsers/parse_timing_detail.py
# -----------------------------------------------------------------------------
# Parses detailed single critical path timing report
# =============================================================================

import common


def parse(filepath):
    """
    Parse timing detail report (single critical path)
    
    Args:
        filepath: Path to *_timing.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Critical path slack and status
        - Source and destination cells
        - Path group and type
        - Data path delay (logic vs route breakdown)
        - Logic levels by primitive type
        - Clock path skew components (DCD, SCD, CPR)
        - Clock uncertainty breakdown (TSJ, DJ, PE)
        - Clock net delays
    
    Note: This is the most detailed timing report for a single path
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Parse main timing information
    # Look for "Timing Report" section header
    timing_line = common.find_line_with_text(lines, "Timing Report")
    
    if timing_line >= 0:
        # Parse next ~30 lines for key metrics
        for i in range(timing_line, min(timing_line + 35, len(lines))):
            line = lines[i]
            
            # Slack
            if "Slack" in line and ":" in line:
                slack = common.extract_value_from_line(line, r"Slack.*:\s*([-\d.]+)ns")
                if slack:
                    data.append(("Critical Path - Slack (ns)", slack))
                # Check if timing met
                if "MET" in line:
                    data.append(("Critical Path - Status", "MET"))
                elif "VIOLATED" in line:
                    data.append(("Critical Path - Status", "VIOLATED"))
            
            # Source cell
            elif "Source:" in line:
                # Next line usually has the source
                if i + 1 < len(lines):
                    source = lines[i + 1].strip()
                    # Remove trailing parenthesis content
                    source = source.split("(")[0].strip()
                    data.append(("Critical Path - Source", source[:80]))
            
            # Destination cell
            elif "Destination:" in line:
                # Next line usually has the destination
                if i + 1 < len(lines):
                    dest = lines[i + 1].strip()
                    dest = dest.split("(")[0].strip()
                    data.append(("Critical Path - Destination", dest[:80]))
            
            # Path Group
            elif "Path Group:" in line:
                group = common.extract_value_from_line(line, r"Path Group:\s+(\S+)")
                if group:
                    data.append(("Critical Path - Path Group", group))
            
            # Path Type
            elif "Path Type:" in line:
                path_type = line.split("Path Type:")[1].strip()
                # Remove trailing info in parentheses
                path_type = path_type.split("(")[0].strip()
                data.append(("Critical Path - Path Type", path_type))
            
            # Requirement (period)
            elif "Requirement:" in line:
                req = common.extract_value_from_line(line, r"Requirement:\s+([-\d.]+)ns")
                if req:
                    data.append(("Critical Path - Requirement (ns)", req))
            
            # Data Path Delay
            elif "Data Path Delay:" in line:
                # Extract total delay
                total = common.extract_value_from_line(line, r"Data Path Delay:\s+([-\d.]+)ns")
                if total:
                    data.append(("Critical Path - Data Path Delay (ns)", total))
                
                # Extract logic delay
                logic = common.extract_value_from_line(line, r"logic\s+([-\d.]+)ns")
                if logic:
                    data.append(("Critical Path - Logic Delay (ns)", logic))
                
                # Extract route delay
                route = common.extract_value_from_line(line, r"route\s+([-\d.]+)ns")
                if route:
                    data.append(("Critical Path - Route Delay (ns)", route))
                
                # Extract logic percentage
                logic_pct = common.extract_value_from_line(line, r"\(([-\d.]+)%\)")
                if logic_pct:
                    data.append(("Critical Path - Logic Delay %", logic_pct))
            
            # Logic Levels
            elif "Logic Levels:" in line:
                levels = common.extract_value_from_line(line, r"Logic Levels:\s+(\d+)")
                if levels:
                    data.append(("Critical Path - Total Logic Levels", levels))
                
                # Extract primitive breakdown (CARRY8=6 LUT2=2 etc.)
                import re
                primitives = re.findall(r'([A-Z0-9_]+)=(\d+)', line)
                for prim_name, prim_count in primitives:
                    data.append((f"Critical Path - {prim_name} Count", prim_count))
            
            # Clock Path Skew
            elif "Clock Path Skew:" in line:
                skew = common.extract_value_from_line(line, r"Clock Path Skew:\s+([-\d.]+)ns")
                if skew:
                    data.append(("Critical Path - Clock Path Skew (ns)", skew))
            
            # Destination Clock Delay (DCD)
            elif "Destination Clock Delay (DCD):" in line:
                dcd = common.extract_value_from_line(line, r"Destination Clock Delay \(DCD\):\s+([-\d.]+)ns")
                if dcd:
                    data.append(("Critical Path - DCD (ns)", dcd))
            
            # Source Clock Delay (SCD)
            elif "Source Clock Delay      (SCD):" in line or "Source Clock Delay (SCD):" in line:
                scd = common.extract_value_from_line(line, r"Source Clock Delay.*:\s+([-\d.]+)ns")
                if scd:
                    data.append(("Critical Path - SCD (ns)", scd))
            
            # Clock Pessimism Removal (CPR)
            elif "Clock Pessimism Removal (CPR):" in line:
                cpr = common.extract_value_from_line(line, r"Clock Pessimism Removal \(CPR\):\s+([-\d.]+)ns")
                if cpr:
                    data.append(("Critical Path - CPR (ns)", cpr))
            
            # Clock Uncertainty
            elif "Clock Uncertainty:" in line and "Total System Jitter" not in line:
                uncertainty = common.extract_value_from_line(line, r"Clock Uncertainty:\s+([-\d.]+)ns")
                if uncertainty:
                    data.append(("Critical Path - Clock Uncertainty (ns)", uncertainty))
            
            # Total System Jitter (TSJ)
            elif "Total System Jitter" in line and "TSJ" in line:
                tsj = common.extract_value_from_line(line, r"Total System Jitter.*:\s+([-\d.]+)ns")
                if tsj:
                    data.append(("Critical Path - TSJ (ns)", tsj))
            
            # Discrete Jitter (DJ)
            elif "Discrete Jitter" in line and "DJ" in line:
                dj = common.extract_value_from_line(line, r"Discrete Jitter.*:\s+([-\d.]+)ns")
                if dj:
                    data.append(("Critical Path - DJ (ns)", dj))
            
            # Phase Error (PE)
            elif "Phase Error" in line and "PE" in line:
                pe = common.extract_value_from_line(line, r"Phase Error.*:\s+([-\d.]+)ns")
                if pe:
                    data.append(("Critical Path - PE (ns)", pe))
            
            # Clock Net Delay - Source
            elif "Clock Net Delay (Source):" in line:
                src_delay = common.extract_value_from_line(line, r"Clock Net Delay \(Source\):\s+([-\d.]+)ns")
                if src_delay:
                    data.append(("Critical Path - Clock Net Delay Source (ns)", src_delay))
                
                # Extract routing and distribution
                routing = common.extract_value_from_line(line, r"routing\s+([-\d.]+)ns")
                if routing:
                    data.append(("Critical Path - Clock Routing Source (ns)", routing))
                
                distribution = common.extract_value_from_line(line, r"distribution\s+([-\d.]+)ns")
                if distribution:
                    data.append(("Critical Path - Clock Distribution Source (ns)", distribution))
            
            # Clock Net Delay - Destination
            elif "Clock Net Delay (Destination):" in line:
                dst_delay = common.extract_value_from_line(line, r"Clock Net Delay \(Destination\):\s+([-\d.]+)ns")
                if dst_delay:
                    data.append(("Critical Path - Clock Net Delay Dest (ns)", dst_delay))
                
                # Extract routing and distribution
                routing = common.extract_value_from_line(line, r"routing\s+([-\d.]+)ns")
                if routing:
                    data.append(("Critical Path - Clock Routing Dest (ns)", routing))
                
                distribution = common.extract_value_from_line(line, r"distribution\s+([-\d.]+)ns")
                if distribution:
                    data.append(("Critical Path - Clock Distribution Dest (ns)", distribution))
    
    return data, common_info