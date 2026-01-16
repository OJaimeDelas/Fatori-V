# =============================================================================
# FATORI-V • FI Report Parsing - Timing Paths
# File: parsers/parse_timing_paths.py
# -----------------------------------------------------------------------------
# Parses critical path details for performance bottleneck analysis
# =============================================================================

import common
import re


def parse(filepath):
    """
    Parse timing paths report
    
    Args:
        filepath: Path to *_timing_paths.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Top 3 critical paths (slack, start/end points, delays, logic levels)
        - Logic vs routing delay breakdown
        - Modules appearing most frequently in critical paths
    
    Use Cases:
        - Identify performance bottlenecks
        - Understand voter logic timing impact
        - Guide optimization efforts
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Find "Max Delay Paths" section
    max_delay_line = common.find_line_with_text(lines, "Max Delay Paths")
    
    if max_delay_line >= 0:
        path_count = 0
        
        # Parse up to 3 critical paths
        for i in range(max_delay_line, min(max_delay_line + 500, len(lines))):
            line = lines[i]
            
            # Each path starts with "Slack" line
            if "Slack" in line and ":" in line:
                path_count += 1
                
                if path_count <= 3:
                    # Extract slack value
                    slack = common.extract_value_from_line(line, r"Slack.*:\s*([-\d.]+)")
                    if slack:
                        data.append((f"Path {path_count} - Slack (ns)", slack))
                    
                    # Look ahead for path details (next ~50 lines)
                    for j in range(i, min(i + 50, len(lines))):
                        detail_line = lines[j]
                        
                        # Extract source
                        if "Source:" in detail_line:
                            source = detail_line.split("Source:")[1].strip()
                            # Remove parentheses content
                            source = source.split("(")[0].strip()
                            data.append((f"Path {path_count} - Start Point", source[:50]))
                        
                        # Extract destination
                        elif "Destination:" in detail_line:
                            dest = detail_line.split("Destination:")[1].strip()
                            dest = dest.split("(")[0].strip()
                            data.append((f"Path {path_count} - End Point", dest[:50]))
                        
                        # Extract data path delay
                        elif "Data Path Delay:" in detail_line:
                            delay = common.extract_value_from_line(detail_line, r"([\d.]+)ns")
                            if delay:
                                data.append((f"Path {path_count} - Total Delay (ns)", delay))
                            
                            # Extract logic delay
                            logic = common.extract_value_from_line(detail_line, r"logic\s+([\d.]+)ns")
                            if logic:
                                data.append((f"Path {path_count} - Logic Delay (ns)", logic))
                            
                            # Extract route delay
                            route = common.extract_value_from_line(detail_line, r"route\s+([\d.]+)ns")
                            if route:
                                data.append((f"Path {path_count} - Route Delay (ns)", route))
                        
                        # Extract logic levels
                        elif "Logic Levels:" in detail_line:
                            levels = common.extract_value_from_line(detail_line, r":\s*(\d+)")
                            if levels:
                                data.append((f"Path {path_count} - Logic Levels", levels))
                        
                        # Extract clock uncertainty
                        elif "clock uncertainty" in detail_line:
                            uncertainty = common.extract_value_from_line(detail_line, r"([\d.]+)")
                            if uncertainty:
                                data.append((f"Path {path_count} - Clock Uncertainty (ns)", 
                                          uncertainty))
                            break
    
    # Track which modules appear most in critical paths
    module_counts = {}
    
    if max_delay_line >= 0:
        for i in range(max_delay_line, min(max_delay_line + 1000, len(lines))):
            line = lines[i]
            
            # Look for hierarchy paths (have / separators)
            if '/' in line and ('SLICE' in line or 'RAMB' in line or 'DSP' in line):
                # Extract module hierarchy (before leaf cell)
                parts = line.split('/')
                if len(parts) > 2:
                    # Get second-to-last element as module name
                    module = parts[-2]
                    module_counts[module] = module_counts.get(module, 0) + 1
    
    # Report top 5 modules appearing in critical paths
    if module_counts:
        sorted_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (module, count) in enumerate(sorted_modules[:5]):
            data.append((f"Frequent in Paths {i+1} - Module", module[:50]))
            data.append((f"Frequent in Paths {i+1} - Count", str(count)))
    
    return data, common_info