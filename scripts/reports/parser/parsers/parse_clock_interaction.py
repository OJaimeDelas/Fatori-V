# =============================================================================
# FATORI-V • FI Report Parsing - Clock Interaction
# File: parsers/parse_clock_interaction.py
# -----------------------------------------------------------------------------
# Parses timing relationships between clock domains
# =============================================================================

import common


def parse(filepath):
    """
    Parse clock interaction report
    
    Args:
        filepath: Path to *_clock_interaction.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - Clock domain interactions count
        - Inter-clock timing constraints
        - Timing violations between clocks
        - Asynchronous clock pairs
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Find clock interaction section
    interaction_line = common.find_line_with_text(lines, "Clock Interaction")
    if interaction_line < 0:
        interaction_line = common.find_line_with_text(lines, "Inter-Clock")
    
    if interaction_line >= 0:
        interactions = []
        
        # Parse interaction entries
        for i in range(interaction_line, min(interaction_line + 100, len(lines))):
            line = lines[i]
            
            # Look for lines with clock relationships
            if '->' in line or 'WNS' in line:
                parts = line.split()
                if len(parts) >= 3:
                    interactions.append(line.strip()[:80])
            
            if len(interactions) >= 10:
                break
        
        if interactions:
            data.append(("Clock Interactions Count", str(len(interactions))))
            
            # Add first 5 interactions
            for i, interaction in enumerate(interactions[:5]):
                data.append((f"Clock Interaction {i+1}", interaction))
    
    # Look for max delay constraints
    constraint_line = common.find_line_with_text(lines, "Constraint")
    if constraint_line >= 0:
        for i in range(constraint_line, min(constraint_line + 20, len(lines))):
            line = lines[i]
            
            if "Max Delay" in line:
                delay = common.extract_value_from_line(line, r"([\d.]+)")
                if delay:
                    data.append(("Max Delay Between Clocks (ns)", delay))
                    break
    
    # Look for setup timing between domains
    setup_line = common.find_line_with_text(lines, "Setup")
    if setup_line >= 0:
        for i in range(setup_line, min(setup_line + 10, len(lines))):
            line = lines[i]
            
            if "Worst" in line or "WNS" in line:
                wns = common.extract_value_from_line(line, r"([-\d.]+)")
                if wns:
                    data.append(("Inter-Clock Setup WNS (ns)", wns))
                    break
    
    # Check for violations
    violation_line = common.find_line_with_text(lines, "violation")
    if violation_line >= 0:
        data.append(("Inter-Clock Timing Violations", "YES"))
    else:
        data.append(("Inter-Clock Timing Violations", "NO"))
    
    # Look for asynchronous pairs
    async_line = common.find_line_with_text(lines, "Asynchronous")
    if async_line >= 0:
        async_count = 0
        for i in range(async_line, min(async_line + 30, len(lines))):
            if "Asynchronous" in lines[i]:
                async_count += 1
        
        if async_count > 0:
            data.append(("Asynchronous Clock Pairs", str(async_count)))
    
    # Look for clock groups
    group_line = common.find_line_with_text(lines, "Clock Groups")
    if group_line >= 0:
        group_count = 0
        for i in range(group_line, min(group_line + 20, len(lines))):
            line = lines[i]
            
            if "Group" in line and ":" in line:
                group_count += 1
        
        if group_count > 0:
            data.append(("Clock Groups Defined", str(group_count)))
    
    return data, common_info