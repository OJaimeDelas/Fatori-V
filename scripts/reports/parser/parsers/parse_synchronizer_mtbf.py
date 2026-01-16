# =============================================================================
# FATORI-V • FI Report Parsing - Synchronizer MTBF
# File: parsers/parse_synchronizer_mtbf.py
# -----------------------------------------------------------------------------
# Parses metastability reliability metrics for fault-tolerant systems
# =============================================================================

import common
import re


def parse(filepath):
    """
    Parse synchronizer MTBF report
    
    Args:
        filepath: Path to *_synchronizer_mtbf.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Total synchronizers
        - Worst-case MTBF (Mean Time Between Failures)
        - Top 5 synchronizers with worst MTBF
        - Synchronizer stages
        - Clock frequencies
        - Violations and warnings
    
    Use Cases:
        - Quantify metastability risk
        - Identify weak CDC points
        - Calculate system-level reliability
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Look for summary statistics
    summary_line = common.find_line_with_text(lines, "Summary")
    if summary_line >= 0:
        for i in range(summary_line, min(summary_line + 30, len(lines))):
            line = lines[i]
            
            if "Total Synchronizers" in line or "Number of Synchronizers" in line:
                count = common.extract_value_from_line(line, r":\s*(\d+)")
                if count:
                    data.append(("Total Synchronizers", count))
            
            elif "Worst MTBF" in line or "Minimum MTBF" in line:
                mtbf = common.extract_value_from_line(line, r":\s*([\d.e+\-]+)")
                if mtbf:
                    data.append(("Worst Case MTBF", mtbf))
    
    # Parse synchronizer table
    table_line = common.find_line_with_text(lines, "Synchronizer")
    if table_line >= 0:
        synchronizers = []
        
        # Look for MTBF values (scientific notation: e+XX or e-XX)
        current_line = table_line
        while current_line < len(lines) and len(synchronizers) < 20:
            line = lines[current_line]
            
            # Look for scientific notation MTBF values
            if 'e+' in line or 'e-' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    # Match scientific notation pattern
                    if re.match(r'[\d.]+e[+\-]\d+', part):
                        mtbf_value = part
                        # Get sync name (usually before MTBF)
                        sync_name = ""
                        if i > 0:
                            sync_name = parts[i-1]
                        
                        synchronizers.append({
                            'name': sync_name,
                            'mtbf': mtbf_value
                        })
                        break
            
            current_line += 1
        
        if synchronizers:
            data.append(("Number of Synchronizers Analyzed", str(len(synchronizers))))
            
            # Sort by MTBF (lowest first = worst)
            try:
                sorted_syncs = sorted(synchronizers, 
                                    key=lambda x: float(x['mtbf']))
                
                # Add top 5 worst MTBF synchronizers
                for i, sync in enumerate(sorted_syncs[:5]):
                    idx = i + 1
                    data.append((f"Sync {idx} (Worst MTBF) - Name", sync['name']))
                    data.append((f"Sync {idx} (Worst MTBF) - MTBF", sync['mtbf']))
            except:
                pass
    
    # Look for synchronizer stage information
    stages_line = common.find_line_with_text(lines, "stages")
    if stages_line >= 0:
        for i in range(max(0, stages_line - 5), min(stages_line + 10, len(lines))):
            line = lines[i]
            
            # Look for stage count patterns
            stage_match = re.search(r'(\d+)\s+stage', line, re.IGNORECASE)
            if stage_match:
                data.append(("Typical Synchronizer Stages", stage_match.group(1)))
                break
    
    # Look for clock frequency
    freq_line = common.find_line_with_text(lines, "Clock Frequency")
    if freq_line >= 0:
        for i in range(freq_line, min(freq_line + 10, len(lines))):
            line = lines[i]
            freq = common.extract_value_from_line(line, r"([\d.]+)\s*MHz")
            if freq:
                data.append(("Synchronizer Clock Frequency (MHz)", freq))
                break
    
    # Look for data rate
    rate_line = common.find_line_with_text(lines, "Data Rate")
    if rate_line >= 0:
        for i in range(rate_line, min(rate_line + 10, len(lines))):
            line = lines[i]
            rate = common.extract_value_from_line(line, r"([\d.]+)")
            if rate:
                data.append(("Synchronizer Data Rate", rate))
                break
    
    # Check for violations
    violation_line = common.find_line_with_text(lines, "violation")
    if violation_line >= 0:
        data.append(("Synchronizer Violations Present", "YES"))
    
    # Check for warnings
    warning_line = common.find_line_with_text(lines, "below acceptable")
    if warning_line >= 0:
        data.append(("Synchronizers Below Acceptable MTBF", "YES"))
    
    return data, common_info