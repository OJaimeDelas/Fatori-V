# =============================================================================
# FATORI-V • FI Report Parsing - Utilization
# File: parsers/parse_utilization.py
# -----------------------------------------------------------------------------
# Parses Vivado utilization report for overall resource usage
# =============================================================================

import common


def parse(filepath):
    """
    Parse utilization report
    
    Args:
        filepath: Path to *_utilization.rpt file
    
    Returns:
        Tuple of (data_list, common_info)
        - data_list: List of (metric_id, value) tuples
        - common_info: Dictionary of common report metadata
    
    Extracts:
        - LUTs (total, as logic, as memory, as distributed RAM, as shift reg)
        - Flip-Flops (total, as FF, as latch)
        - CARRY8 primitives
        - CLBs
        - Block RAM (tiles, RAMB36, RAMB18)
        - DSPs
        - I/O pins
        - Clock resources (buffers, PLLs)
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info (design, device, etc.)
    common_info = common.extract_common_info(lines)
    
    # Parse "1. CLB Logic" section
    # Typical location: lines 29-47 in standard reports
    clb_line = common.find_line_with_text(lines, "1. CLB Logic")
    if clb_line >= 0:
        # Find table start
        table_start = common.find_line_with_text(lines, "| CLB LUTs", clb_line)
        if table_start >= 0:
            # Parse key metrics from table (next ~15 lines)
            for i in range(table_start, min(table_start + 15, len(lines))):
                line = lines[i]
                
                # Total LUTs
                if "| CLB LUTs" in line and "LUT as" not in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("LUTs - Total Used", cells[1]))
                        data.append(("LUTs - Total Available", cells[3]))
                        data.append(("LUTs - Utilization %", cells[4]))
                
                # LUTs as Logic
                elif "| LUT as Logic" in line and "LUT as Memory" not in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("LUTs - As Logic", cells[1]))
                
                # LUTs as Memory
                elif "| LUT as Memory" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("LUTs - As Memory", cells[1]))
                
                # Distributed RAM
                elif "| LUT as Distributed RAM" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 3:
                        data.append(("LUTs - As Distributed RAM", cells[1]))
                
                # Shift Registers
                elif "| LUT as Shift Register" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 3:
                        data.append(("LUTs - As Shift Register", cells[1]))
                
                # Flip-Flops
                elif "| CLB Registers" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("Flip-Flops - Total Used", cells[1]))
                        data.append(("Flip-Flops - Total Available", cells[3]))
                        data.append(("Flip-Flops - Utilization %", cells[4]))
                
                # CARRY8 primitives
                elif "| CARRY8" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("CARRY8 - Used", cells[1]))
                        data.append(("CARRY8 - Available", cells[3]))
    
    # Parse "2. CLB Logic Distribution" section
    clb_dist_line = common.find_line_with_text(lines, "2. CLB Logic Distribution")
    if clb_dist_line >= 0:
        table_start = common.find_line_with_text(lines, "| CLB ", clb_dist_line)
        if table_start >= 0:
            for i in range(table_start, min(table_start + 10, len(lines))):
                line = lines[i]
                # Look for main CLB line (not CLBL/CLBM sublines)
                if "| CLB" in line and "CLBL" not in line and "CLBM" not in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("CLB - Used", cells[1]))
                        data.append(("CLB - Available", cells[3]))
                        data.append(("CLB - Utilization %", cells[4]))
                    break
    
    # Parse "3. BLOCKRAM" section
    bram_line = common.find_line_with_text(lines, "3. BLOCKRAM")
    if bram_line >= 0:
        table_start = common.find_line_with_text(lines, "| Block RAM Tile", bram_line)
        if table_start >= 0:
            for i in range(table_start, min(table_start + 10, len(lines))):
                line = lines[i]
                
                # Total BRAM tiles
                if "| Block RAM Tile" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("BRAM - Tiles Used", cells[1]))
                        data.append(("BRAM - Tiles Available", cells[3]))
                        data.append(("BRAM - Utilization %", cells[4]))
                
                # RAMB36 count
                elif "| RAMB36/FIFO" in line or "| RAMB36E2 only" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 2:
                        data.append(("BRAM - RAMB36 Used", cells[1]))
                
                # RAMB18 count
                elif "| RAMB18" in line and "RAMB18E2 only" not in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("BRAM - RAMB18 Used", cells[1]))
    
    # Parse "4. ARITHMETIC" section (DSPs)
    dsp_line = common.find_line_with_text(lines, "4. ARITHMETIC")
    if dsp_line >= 0:
        table_start = common.find_line_with_text(lines, "| DSPs", dsp_line)
        if table_start >= 0:
            line = lines[table_start]
            cells = common.parse_table_row(line)
            if len(cells) >= 5:
                data.append(("DSP - Used", cells[1]))
                data.append(("DSP - Available", cells[3]))
                data.append(("DSP - Utilization %", cells[4]))
    
    # Parse "5. I/O" section
    io_line = common.find_line_with_text(lines, "5. I/O")
    if io_line >= 0:
        table_start = common.find_line_with_text(lines, "| Bonded IOB", io_line)
        if table_start >= 0:
            line = lines[table_start]
            cells = common.parse_table_row(line)
            if len(cells) >= 5:
                data.append(("IO - Bonded IOB Used", cells[1]))
                data.append(("IO - Bonded IOB Available", cells[3]))
                data.append(("IO - Utilization %", cells[4]))
    
    # Parse "6. CLOCK" section
    clock_line = common.find_line_with_text(lines, "6. CLOCK")
    if clock_line >= 0:
        table_start = common.find_line_with_text(lines, "| GLOBAL CLOCK BUFFERs", 
                                                  clock_line)
        if table_start >= 0:
            for i in range(table_start, min(table_start + 10, len(lines))):
                line = lines[i]
                
                # Global clock buffers
                if "| GLOBAL CLOCK BUFFERs" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("Clock - Global Buffers Used", cells[1]))
                        data.append(("Clock - Global Buffers Available", cells[3]))
                
                # BUFGCE count
                elif "| BUFGCE" in line and "BUFGCE_DIV" not in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("Clock - BUFGCE Used", cells[1]))
                
                # PLL count
                elif "| PLLE3_ADV" in line or "| MMCME3_ADV" in line:
                    cells = common.parse_table_row(line)
                    if len(cells) >= 5:
                        data.append(("Clock - PLL Used", cells[1]))
                        data.append(("Clock - PLL Available", cells[3]))
    
    return data, common_info