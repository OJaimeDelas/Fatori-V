# =============================================================================
# FATORI-V • FI Report Parsing - Hierarchical Utilization
# File: parsers/parse_hierarchical_utilization.py
# -----------------------------------------------------------------------------
# ENHANCED VERSION: Finds more modules (ALU, LSU, pipeline stages, etc.)
# =============================================================================

import common


def parse(filepath):
    """
    Parse hierarchical utilization report - ENHANCED VERSION
    
    Returns:
        Tuple of (data_list, common_info)
    
    Enhancements:
        - Finds ALU, LSU, and other CPU pipeline stages
        - More comprehensive keyword search
        - Top 15 modules instead of 10
        - More module categories
        - Flexible partial matching
    """
    
    lines = common.read_file(filepath)
    data = []
    
    # Extract common info
    common_info = common.extract_common_info(lines)
    
    # Find the hierarchical utilization table
    table_line = common.find_line_with_text(lines, "1. Utilization by Hierarchy")
    
    if table_line < 0:
        return data, common_info
    
    # Find table header - flexible search
    header_line = -1
    for i in range(table_line, min(table_line + 20, len(lines))):
        if "Instance" in lines[i] and "Module" in lines[i] and "|" in lines[i]:
            header_line = i
            break
    
    if header_line < 0:
        return data, common_info
    
    # Parse header row to get column indices
    header_cells = common.parse_table_row(lines[header_line])
    
    # Build column index map
    col_map = {}
    for idx, cell in enumerate(header_cells):
        col_map[cell] = idx
    
    # Get column indices with fallbacks
    instance_idx = col_map.get("Instance", -1)
    module_idx = col_map.get("Module", -1)
    luts_idx = col_map.get("Total LUTs", col_map.get("CLB LUTs", -1))
    ffs_idx = col_map.get("FFs", col_map.get("CLB Registers", -1))
    ramb36_idx = col_map.get("RAMB36", -1)
    ramb18_idx = col_map.get("RAMB18", -1)
    dsps_idx = col_map.get("DSP Blocks", col_map.get("DSPs", -1))
    
    # Check required columns
    if instance_idx < 0 or module_idx < 0:
        return data, common_info
    
    # Collect all modules
    modules = []
    
    # Start parsing after separator line
    current_line = header_line + 2
    
    while current_line < len(lines):
        line = lines[current_line]
        
        # Stop at table end
        if '+---' in line or line.strip() == '':
            break
        
        # Parse data row
        if '|' in line:
            cells = common.parse_table_row(line)
            
            if len(cells) < 3:
                current_line += 1
                continue
            
            # Extract values
            instance = cells[instance_idx] if instance_idx < len(cells) else ""
            module = cells[module_idx] if module_idx < len(cells) else ""
            
            # Skip (top) entries
            if "(top)" in instance.lower():
                current_line += 1
                continue
            
            # Extract resources with error handling
            try:
                luts = int(cells[luts_idx]) if luts_idx >= 0 and luts_idx < len(cells) else 0
                ffs = int(cells[ffs_idx]) if ffs_idx >= 0 and ffs_idx < len(cells) else 0
                ramb36 = int(cells[ramb36_idx]) if ramb36_idx >= 0 and ramb36_idx < len(cells) else 0
                ramb18 = int(cells[ramb18_idx]) if ramb18_idx >= 0 and ramb18_idx < len(cells) else 0
                dsps = int(cells[dsps_idx]) if dsps_idx >= 0 and dsps_idx < len(cells) else 0
                
                # Only store non-zero modules
                if luts > 0 or ffs > 0 or ramb36 > 0 or ramb18 > 0 or dsps > 0:
                    modules.append({
                        'instance': instance,
                        'module': module,
                        'luts': luts,
                        'ffs': ffs,
                        'bram36': ramb36,
                        'bram18': ramb18,
                        'dsps': dsps
                    })
            except (ValueError, IndexError):
                pass
        
        current_line += 1
    
    if not modules:
        return data, common_info
    
    # Sort by LUTs (largest first)
    modules.sort(key=lambda x: x['luts'], reverse=True)
    
    # Report total modules
    data.append(("Hierarchical - Total Modules Analyzed", str(len(modules))))
    
    # Top 15 modules (increased from 10)
    top_n = min(15, len(modules))
    for i, mod in enumerate(modules[:top_n]):
        idx = i + 1
        data.append((f"Top {idx} Module - Instance", mod['instance'][:80]))
        data.append((f"Top {idx} Module - Type", mod['module'][:60]))
        data.append((f"Top {idx} Module - LUTs", str(mod['luts'])))
        data.append((f"Top {idx} Module - FFs", str(mod['ffs'])))
        data.append((f"Top {idx} Module - BRAM36", str(mod['bram36'])))
        data.append((f"Top {idx} Module - BRAM18", str(mod['bram18'])))
        data.append((f"Top {idx} Module - DSPs", str(mod['dsps'])))
    
    # ENHANCED: Key modules with comprehensive search terms
    # Organized by functional category for easy analysis
    keywords = {
        # CPU Core
        'cpu': ['cpu', 'ibex', 'core', 'processor', 'u_top'],
        
        # Memory System
        'memory': ['ext_mem', 'ram', 'cache', 'sram'],
        'bootrom': ['bootrom', 'boot_rom', 'rom'],
        'register_file': ['register_file', 'regfile', 'gen_regfile'],
        
        # CPU Pipeline Stages
        'alu': ['alu_i', 'alu', 'arithmetic'],
        'lsu': ['load_store_unit', 'lsu', 'load_store'],
        'if_stage': ['if_stage', 'fetch', 'prefetch'],
        'id_stage': ['id_stage', 'decode'],
        'ex_stage': ['ex_block', 'execute', 'ex_stage'],
        'wb_stage': ['wb_stage', 'writeback'],
        
        # Control & Decode
        'controller': ['controller_i', 'controller', 'ctrl'],
        'decoder': ['decoder_i', 'decoder', 'dec'],
        
        # CSR & Registers
        'csr_registers': ['cs_registers', 'csr', 'mcause', 'mepc', 'mstatus'],
        
        # Peripherals
        'timer': ['timer', 'TIMER'],
        'uart': ['uart', 'UART'],
        
        # Clock & Reset
        'clock': ['clk_', 'clock_wizard', 'mmcm', 'pll'],
        
        # Fault Tolerance
        'sem': ['sem_ultra', 'sem_', 'fault'],
        'voter': ['voter', 'tmr', 'nmr'],
        'aes': ['aes', 'crypto', 'cipher']
    }
    
    # Search for key modules
    for category, search_terms in keywords.items():
        found = False
        
        for mod in modules:
            instance_lower = mod['instance'].lower()
            module_lower = mod['module'].lower()
            
            # Flexible matching: any search term in either instance or module
            for term in search_terms:
                term_lower = term.lower()
                if term_lower in instance_lower or term_lower in module_lower:
                    data.append((f"Key Module [{category}] - Instance", mod['instance'][:80]))
                    data.append((f"Key Module [{category}] - Module Type", mod['module'][:60]))
                    data.append((f"Key Module [{category}] - LUTs", str(mod['luts'])))
                    data.append((f"Key Module [{category}] - FFs", str(mod['ffs'])))
                    data.append((f"Key Module [{category}] - BRAM36", str(mod['bram36'])))
                    data.append((f"Key Module [{category}] - BRAM18", str(mod['bram18'])))
                    data.append((f"Key Module [{category}] - DSPs", str(mod['dsps'])))
                    found = True
                    break
            
            if found:
                break
    
    # Calculate totals
    total_luts = sum(m['luts'] for m in modules)
    total_ffs = sum(m['ffs'] for m in modules)
    total_bram36 = sum(m['bram36'] for m in modules)
    total_bram18 = sum(m['bram18'] for m in modules)
    total_dsps = sum(m['dsps'] for m in modules)
    
    if total_luts > 0:
        data.append(("Hierarchical - Total LUTs Sum", str(total_luts)))
        if modules:
            top_pct = (modules[0]['luts'] / total_luts) * 100
            data.append(("Top Module - LUT Percentage", f"{top_pct:.1f}"))
    
    if total_ffs > 0:
        data.append(("Hierarchical - Total FFs Sum", str(total_ffs)))
    
    if total_bram36 > 0:
        data.append(("Hierarchical - Total BRAM36 Sum", str(total_bram36)))
    
    if total_bram18 > 0:
        data.append(("Hierarchical - Total BRAM18 Sum", str(total_bram18)))
    
    if total_dsps > 0:
        data.append(("Hierarchical - Total DSPs Sum", str(total_dsps)))
    
    return data, common_info