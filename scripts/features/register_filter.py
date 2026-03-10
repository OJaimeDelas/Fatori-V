# =============================================================================
# FATORI-V • Feature Generation • Register Filter
# File: register_filter.py
# -----------------------------------------------------------------------------
# Filters fatori_registers.yaml to create fatori_registers_active.yaml.
# Excludes registers gated behind disabled ifdef macros (RVFI, INC_ASSERT, etc).
# =============================================================================

from pathlib import Path
import yaml
from scripts.logging import logger
from config.constants import FATORI_REGISTERS_ACTIVE_NAME


# Hardcoded mapping: register ID → gating macro
# Registers without a gating macro are always active
REGISTER_GATING_MAP = {
    # RVFI-gated registers (RISC-V Formal Interface - trace/verification only)
    21: 'RVFI',  # rvfi_instr_new_wb_q
    27: 'RVFI',  # rvfi_irq_valid
    28: 'RVFI',  # rvfi_ext_stage_irq_id (appears twice in generate loops)
    29: 'RVFI',  # rvfi_ext_stage_irq_ipack
    30: 'RVFI',  # rvfi_ext_stage_irq_ilpack
    31: 'RVFI',  # rvfi_ext_stage_irq_valid_latched
    32: 'RVFI',  # rvfi_ext_stage_irq_valid
    33: 'RVFI',  # rvfi_stage_halt
    34: 'RVFI',  # rvfi_stage_trap
    35: 'RVFI',  # rvfi_stage_intr
    36: 'RVFI',  # rvfi_stage_order
    37: 'RVFI',  # rvfi_stage_insn
    38: 'RVFI',  # rvfi_stage_mode
    39: 'RVFI',  # rvfi_stage_ixl
    40: 'RVFI',  # rvfi_stage_rs1_addr
    41: 'RVFI',  # rvfi_stage_rs2_addr
    42: 'RVFI',  # rvfi_stage_rs3_addr
    43: 'RVFI',  # rvfi_stage_pc_rdata
    44: 'RVFI',  # rvfi_stage_pc_wdata
    45: 'RVFI',  # rvfi_stage_mem_rmask
    46: 'RVFI',  # rvfi_stage_mem_wmask
    47: 'RVFI',  # rvfi_stage_rs1_rdata
    48: 'RVFI',  # rvfi_stage_rs2_rdata
    49: 'RVFI',  # rvfi_stage_rs3_rdata
    50: 'RVFI',  # rvfi_stage_mem_wdata
    51: 'RVFI',  # rvfi_stage_mem_addr
    52: 'RVFI',  # rvfi_stage_rd_addr
    53: 'RVFI',  # rvfi_stage_rd_wdata
    54: 'RVFI',  # rvfi_stage_mem_rdata
    55: 'RVFI',  # rvfi_ext_stage_debug_mode
    56: 'RVFI',  # rvfi_ext_stage_mcycle
    57: 'RVFI',  # rvfi_ext_stage_icache_inval
    58: 'RVFI',  # rvfi_ext_stage_mhpmcounters[0]
    59: 'RVFI',  # rvfi_ext_stage_mhpmcounters[1]
    60: 'RVFI',  # rvfi_stage_valid
    61: 'RVFI',  # rvfi_ext_stage_irq_id_next
    62: 'RVFI',  # rvfi_ext_stage_irq_ipack_next
    63: 'RVFI',  # rvfi_ext_stage_irq_ilpack_next
    64: 'RVFI',  # rvfi_ext_stage_irq_valid_latched_next
    65: 'RVFI',  # rvfi_ext_stage_irq_valid_next
    66: 'RVFI',  # rvfi_mem_addr_q
    67: 'RVFI',  # rvfi_mem_rdata_q
    68: 'RVFI',  # rvfi_mem_wdata_q
    69: 'RVFI',  # rvfi_rs1_data_q
    70: 'RVFI',  # rvfi_rs1_addr_q
    71: 'RVFI',  # rvfi_rs2_data_q
    72: 'RVFI',  # rvfi_rs2_addr_q
    73: 'RVFI',  # rvfi_rd_addr_q
    74: 'RVFI',  # rvfi_rd_wdata_q
    75: 'RVFI',  # rvfi_set_trap_pc_q
    76: 'RVFI',  # rvfi_intr_q
    169: 'RVFI', # rvfi_ext_stage_mhpmcounters[2]
    170: 'RVFI', # rvfi_ext_stage_mhpmcounters[3]
    171: 'RVFI', # rvfi_ext_stage_mhpmcounters[4]
    172: 'RVFI', # rvfi_ext_stage_mhpmcounters[5]
    173: 'RVFI', # rvfi_ext_stage_mhpmcounters[6]
    174: 'RVFI', # rvfi_ext_stage_mhpmcounters[7]
    175: 'RVFI', # rvfi_ext_stage_mhpmcounters[8]
    176: 'RVFI', # rvfi_ext_stage_mhpmcounters[9]
    177: 'RVFI', # rvfi_ext_stage_mhpmcounters[10]
    178: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[0]
    179: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[1]
    180: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[2]
    181: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[3]
    182: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[4]
    183: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[5]
    184: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[6]
    185: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[7]
    186: 'RVFI', # rvfi_ext_stage_mhpmcounters_h[8]
    
    # INC_ASSERT-gated registers (assertion/debug infrastructure)
    19: 'INC_ASSERT',   # last_fetch_enable
    20: 'INC_ASSERT',   # pc_at_fetch_disable
    157: 'INC_ASSERT',  # ibex_top assertion register
    158: 'INC_ASSERT',  # ibex_top assertion register
    159: 'INC_ASSERT',  # ibex_top assertion register
    
    # DV_FCOV_DISABLE-gated registers (coverage collection)
    # These are wrapped in `ifndef DV_FCOV_DISABLE, so they're DISABLED when macro is defined
    138: 'DV_FCOV_DISABLE',  # LSU coverage counter
    139: 'DV_FCOV_DISABLE',  # LSU coverage counter
    
    # FATORI_FI-gated registers (fault injection infrastructure - ENABLED in your config)
    193: 'FATORI_FI',  # last_injection_cycle_q
    194: 'FATORI_FI',  # last_detection_latency_q
    
    # === PARAMETER-GATED REGISTERS ===
    # These are inside generate blocks gated by module parameters that default to 0
    
    # MemECC = 0 (Memory ECC disabled by default)
    7: 'MemECC',    # mem_resp_intg_err_irq_pending_q (ibex_controller)
    8: 'MemECC',    # mem_resp_intg_err_addr_q (ibex_controller)
    
    # DataIndTiming = 0 (Data-independent timing disabled by default)
    97: 'DataIndTiming',  # branch_taken_q (ibex_id_stage)
    
    # ResetAll = 0 (Selective reset mode - many registers disabled)
    84: 'ResetAll',   # ibex_fetch_fifo
    85: 'ResetAll',   # ibex_fetch_fifo
    102: 'ResetAll',  # ibex_if_stage
    103: 'ResetAll',  # ibex_if_stage
    104: 'ResetAll',  # ibex_if_stage
    105: 'ResetAll',  # ibex_if_stage
    106: 'ResetAll',  # ibex_if_stage
    107: 'ResetAll',  # ibex_if_stage
    108: 'ResetAll',  # ibex_if_stage
    109: 'ResetAll',  # ibex_if_stage
    110: 'ResetAll',  # ibex_if_stage
    111: 'ResetAll',  # ibex_if_stage
    112: 'ResetAll',  # ibex_if_stage
    113: 'ResetAll',  # ibex_if_stage
    114: 'ResetAll',  # ibex_if_stage
    115: 'ResetAll',  # ibex_if_stage
    116: 'ResetAll',  # ibex_if_stage
    117: 'ResetAll',  # ibex_if_stage
    119: 'ResetAll',  # ibex_if_stage
    120: 'ResetAll',  # ibex_if_stage
    121: 'ResetAll',  # ibex_if_stage
    122: 'ResetAll',  # ibex_if_stage
    123: 'ResetAll',  # ibex_if_stage
    124: 'ResetAll',  # ibex_if_stage
    125: 'ResetAll',  # ibex_if_stage
    126: 'ResetAll',  # ibex_if_stage
    127: 'ResetAll',  # ibex_if_stage
    147: 'ResetAll',  # ibex_prefetch_buffer
    
    # PCIncrCheck = 0 (PC increment checking disabled)
    118: 'PCIncrCheck',  # ibex_if_stage
    
    # WritebackStage = 0 (Optional writeback stage disabled)
    160: 'WritebackStage',  # ibex_wb_stage
    161: 'WritebackStage',  # ibex_wb_stage
    162: 'WritebackStage',  # ibex_wb_stage
    163: 'WritebackStage',  # ibex_wb_stage
    164: 'WritebackStage',  # ibex_wb_stage
    165: 'WritebackStage',  # ibex_wb_stage
    166: 'WritebackStage',  # ibex_wb_stage
    167: 'WritebackStage',  # ibex_wb_stage
    
    # DummyInstructions = 0 (Dummy instruction insertion disabled)
    168: 'DummyInstructions',  # ibex_wb_stage
    
    # === ALWAYS-ENABLED REGISTERS (DESIGN LIMITATION) ===
    # These registers have enable='1, meaning they are written EVERY clock cycle.
    # FI logic requires en_i=0 to apply injections: do_flip = flip_required && !en_i
    # Since en_i is always HIGH, injections NEVER get applied to register storage.
    # Excluding these prevents wasted injection attempts.
    
    # ibex_controller.sv - all controller registers have enable='1
    9: 'ALWAYS_ENABLED',    # debug_cause_q
    10: 'ALWAYS_ENABLED',   # ctrl_fsm_cs
    11: 'ALWAYS_ENABLED',   # nmi_mode_q
    12: 'ALWAYS_ENABLED',   # do_single_step_q
    13: 'ALWAYS_ENABLED',   # debug_mode_q
    14: 'ALWAYS_ENABLED',   # enter_debug_mode_prio_q
    15: 'ALWAYS_ENABLED',   # load_err_q
    16: 'ALWAYS_ENABLED',   # store_err_q
    17: 'ALWAYS_ENABLED',   # exc_req_q
    18: 'ALWAYS_ENABLED',   # illegal_insn_q
    
    # ibex_cs_registers.sv - CSR registers with enable='1
    77: 'ALWAYS_ENABLED',   # mcountinhibit_q
    78: 'ALWAYS_ENABLED',   # priv_lvl_q
    
    # ibex_decoder.sv - decoder register with enable='1
    81: 'ALWAYS_ENABLED',   # use_rs3_q
    
    # ibex_fetch_fifo.sv - FIFO valid flag with enable='1
    86: 'ALWAYS_ENABLED',   # valid_q
    
    # ibex_id_stage.sv - always-enabled branch tracking registers
    95: 'ALWAYS_ENABLED',   # branch_set_raw_q
    96: 'ALWAYS_ENABLED',   # branch_jump_set_done_q
    
    # ibex_if_stage.sv - instruction valid tracking with enable='1
    100: 'ALWAYS_ENABLED',  # instr_valid_id_q
    101: 'ALWAYS_ENABLED',  # instr_new_id_q
    121: 'ALWAYS_ENABLED',  # instr_skid_valid_q
    
    # ibex_load_store_unit.sv - always-enabled FSM and error registers
    134: 'ALWAYS_ENABLED',  # ls_fsm_cs (LSU state machine)
    135: 'ALWAYS_ENABLED',  # handle_misaligned_q
    136: 'ALWAYS_ENABLED',  # pmp_err_q
    137: 'ALWAYS_ENABLED',  # lsu_err_q
}


def check_macro_enabled(macro_name, config):
    """
    Check if a macro is enabled in the configuration.
    
    Args:
        macro_name: Name of the macro (e.g., 'RVFI', 'INC_ASSERT', 'MemECC')
        config: Configuration dictionary from YAML
    
    Returns:
        True if macro is enabled, False otherwise
    """
    # Special case: DV_FCOV_DISABLE is inverted (registers active when NOT defined)
    if macro_name == 'DV_FCOV_DISABLE':
        # Check if coverage is enabled - if it is, DV_FCOV_DISABLE is NOT defined
        # For now, assume coverage is disabled (DV_FCOV_DISABLE is defined)
        return False
    
    # FATORI_FI is always enabled in FI builds
    if macro_name == 'FATORI_FI':
        return True
    
    # Parameter-based macros (Ibex module parameters that default to 0)
    # These require explicit configuration to enable
    parameter_macros = {
        'MemECC': 'mem_ecc',              # Memory ECC protection
        'DataIndTiming': 'data_indep_timing',  # Data-independent timing
        'ResetAll': 'lockstep',           # Full vs selective reset (ResetAll = Lockstep in ibex_top.sv)
        'PCIncrCheck': 'pc_incr_check',   # PC increment checking
        'WritebackStage': 'wstage',       # Optional writeback pipeline stage
        'DummyInstructions': 'dummy_instr'  # Dummy instruction insertion
    }
    
    if macro_name in parameter_macros:
        # Map parameter name to configuration key name
        config_key = parameter_macros[macro_name]
        
        # Check in fault_tolerance_mechanisms section
        features = config.get('features', {})
        ftm = features.get('fault_tolerance_mechanisms', {})
        if ftm.get(config_key) == 'on':
            return True
        
        # Check in performance_mechanisms section (for wstage)
        perf = features.get('performance_mechanisms', {})
        if perf.get(config_key) == 'on':
            return True
        
        # Default: all Ibex parameters default to 0, so disabled
        return False
    
    # Always-enabled registers (enable='1) - design limitation
    # FI logic cannot apply injections when en_i is always HIGH
    if macro_name == 'ALWAYS_ENABLED':
        return False
    
    # Check config for macro enablement (RVFI, INC_ASSERT, etc.)
    macro_config_map = {
        'RVFI': 'RVFI',
        'INC_ASSERT': 'INC_ASSERT',
    }
    
    config_key = macro_config_map.get(macro_name)
    if config_key:
        # Check both top-level and features section
        if config.get(config_key):
            return True
        features = config.get('features', {})
        if features.get(config_key):
            return True
    
    # Default: macro not enabled
    return False


def filter_registers(fatori_registers_data, config):
    """
    Filter fatori_registers.yaml to remove registers gated behind disabled macros.
    
    Preserves original register IDs - creates gaps for disabled registers.
    
    Args:
        fatori_registers_data: Loaded fatori_registers.yaml content
        config: Configuration dictionary
    
    Returns:
        Filtered register data with same structure as input
    """
    filtered_data = {
        'modules': []
    }
    
    # Track statistics
    total_regs = 0
    filtered_regs = 0
    excluded_by_macro = {}
    
    modules = fatori_registers_data.get('modules', [])
    
    for module_entry in modules:
        module_name = module_entry.get('module', '')
        regs = module_entry.get('regs', [])
        
        if not module_name or not regs:
            continue
        
        # Filter registers in this module
        filtered_regs_list = []
        
        for reg in regs:
            reg_id = reg.get('id')
            reg_name = reg.get('name')
            
            if reg_id is None or not reg_name:
                continue
            
            total_regs += 1
            
            # Check if this register is gated
            gating_macro = REGISTER_GATING_MAP.get(reg_id)
            
            if gating_macro:
                # Check if the gating macro is enabled
                if check_macro_enabled(gating_macro, config):
                    # Macro is enabled - keep the register
                    filtered_regs_list.append(reg)
                else:
                    # Macro is disabled - exclude this register
                    filtered_regs += 1
                    excluded_by_macro[gating_macro] = excluded_by_macro.get(gating_macro, 0) + 1
                    logger.log_event('DEBUG', debug_message=f"  Excluding reg ID {reg_id} ({reg_name}) - gated by disabled macro {gating_macro}")
            else:
                # No gating - always active
                filtered_regs_list.append(reg)
        
        # Only include module if it has registers left
        if filtered_regs_list:
            filtered_data['modules'].append({
                'module': module_name,
                'regs': filtered_regs_list
            })
    
    # Log summary
    logger.log_event('INFO', info_message=f"Register filtering: {total_regs} total, {filtered_regs} excluded, {total_regs - filtered_regs} active")
    
    if excluded_by_macro:
        for macro, count in sorted(excluded_by_macro.items()):
            logger.log_event('INFO', info_message=f"  Excluded {count} registers gated by '{macro}'")
    
    return filtered_data


def create_active_registers_yaml(config, output_path):
    """
    Create fatori_registers_active.yaml by filtering fatori_registers.yaml.
    
    Removes registers that are gated behind disabled ifdef macros while
    preserving original register IDs (creates gaps for excluded registers).
    
    Args:
        config: Configuration dictionary from YAML
        output_path: Path where fatori_registers_active.yaml should be written
    
    Returns:
        Path to the generated active registers file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.log_event('DEBUG', debug_message="Filtering registers based on enabled macros...")
    
    # Load fatori_registers.yaml
    from scripts.common.paths import get_fatori_registers_yaml
    fatori_registers_path = get_fatori_registers_yaml()
    
    if not fatori_registers_path.exists():
        logger.log_event('ERROR', error_message=f"fatori_registers.yaml not found at {fatori_registers_path}")
        return None
    
    try:
        with fatori_registers_path.open('r') as f:
            fatori_registers_data = yaml.safe_load(f)
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error loading fatori_registers.yaml: {e}")
        return None
    
    if not fatori_registers_data:
        logger.log_event('ERROR', error_message="fatori_registers.yaml is empty")
        return None
    
    # Filter the registers
    filtered_data = filter_registers(fatori_registers_data, config)
    
    # Write filtered data to fatori_registers_active.yaml
    try:
        with output_path.open('w') as f:
            # Add header comment
            f.write("# ----------------------------------------------------------------------\n")
            f.write("# FATORI-V Active Register Index\n")
            f.write("# Filtered from fatori_registers.yaml - only includes enabled registers\n")
            f.write("# Register IDs preserved (gaps indicate disabled registers)\n")
            f.write("# ----------------------------------------------------------------------\n")
            
            # Write YAML data
            yaml.dump(filtered_data, f, default_flow_style=False, sort_keys=False)
        
        logger.log_event('FILE_GENERATED', filename=FATORI_REGISTERS_ACTIVE_NAME, output_path=str(output_path))
        return output_path
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error writing {FATORI_REGISTERS_ACTIVE_NAME}: {e}")
        return None