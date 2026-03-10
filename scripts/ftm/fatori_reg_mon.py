# =============================================================================
# FATORI-V • FTM Generation • Register M-of-N Header
# File: fatori_reg_mon.py
# -----------------------------------------------------------------------------
# Generates fatori_reg_mon.svh with percentage-based register selection.
# =============================================================================

from pathlib import Path
import yaml
import random
import fatori_settings as cfg
from config.constants import FATORI_REG_MON_SVH
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_ftm_state
from scripts.common.svh_writer.svh_writer import write_svh_file
from scripts.logging.logger import log_event


def get_target_name_from_module(module_filename):
    """
    Convert module filename to target name.
    
    Maps fatori_registers.yaml module names (e.g., "ibex_controller.sv")
    to target names in config (e.g., "controller").
    
    Args:
        module_filename: Module filename from fatori_registers.yaml
    
    Returns:
        Target name for config lookup
    """
    # Remove .sv extension
    name = module_filename.replace('.sv', '')
    
    # Map known patterns
    if name.startswith('fatori_'):
        # fatori_fault_mgr.sv -> fault_mgr
        return name.replace('fatori_', '')
    elif name.startswith('ibex_'):
        # ibex_controller.sv -> controller
        return name.replace('ibex_', '')
    
    # Otherwise return as-is
    return name


def select_active_registers(modules_data, target_config, percentage, seed_value):
    """
    Select which registers should be active based on targets and percentage.
    
    For each enabled target module, randomly select approximately the specified
    percentage of registers from that module.
    
    Args:
        modules_data: List of module entries from fatori_registers.yaml
        target_config: Dictionary of target enable states from config
        percentage: Percentage of registers to enable (0-100)
        seed_value: Random seed for selection
    
    Returns:
        Set of active register names
    """
    active_registers = set()
    
    # Initialize random number generator with seed
    rng = random.Random(seed_value)
    
    for module_entry in modules_data:
        if not isinstance(module_entry, dict):
            continue
        
        module_filename = module_entry.get('module', '')
        target_name = get_target_name_from_module(module_filename)
        
        # Check if this target is enabled
        target_enabled = target_config.get(target_name, False)
        
        # Normalize to boolean
        if isinstance(target_enabled, str):
            target_enabled = target_enabled.lower() == 'on'
        
        if not target_enabled:
            # Target disabled, skip all registers in this module
            continue
        
        # Target enabled, apply percentage selection
        regs = module_entry.get('regs', [])
        
        if not regs or percentage <= 0:
            continue
        
        # Calculate number of registers to activate
        num_to_activate = max(1, round(len(regs) * percentage / 100.0))
        
        # Randomly select registers
        selected_regs = rng.sample(regs, min(num_to_activate, len(regs)))
        
        for reg in selected_regs:
            if isinstance(reg, dict):
                reg_name = reg.get('name')
                if reg_name:
                    active_registers.add(reg_name)
    
    return active_registers


def generate_reg_mon_header(config, output_dir):
    """
    Generate fatori_reg_mon.svh header file with register M-of-N configuration.
    
    Process:
    1. Check if register M-of-N FTM is enabled
    2. If enabled, determine active registers:
       - Load target configuration (which modules are enabled)
       - For each enabled target, randomly select percentage of registers
       - Use seed for reproducible randomization
    3. Generate 3 macros for EVERY register:
       - Active registers: use N, M, HOLD from config
       - Inactive registers: N=1, M=0, HOLD=0
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where the file should be written
    
    Returns:
        Path to the generated file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = FATORI_REG_MON_SVH
    output_path = output_dir / file_name
    
    lines = []
    
    # Check if register M-of-N is enabled
    reg_mon_enabled = get_ftm_state(config, KEY_FTM_REG_MON)
    
    # Determine active registers
    active_registers = set()
    
    if reg_mon_enabled:
        # Get register M-of-N configuration
        reg_mon_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_REG_MON, default={})
        
        # Get target configuration
        target_config = reg_mon_config.get("target", {})
        
        # Get percentage
        percentage = reg_mon_config.get("m_of_n_percentage", 0)
        
        # Get seed (use global seed if not specified)
        seed_value = reg_mon_config.get("m_of_n_seed")
        if seed_value is None:
            seed_value = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, KEY_IDENT_SEED, default=0)
        
        # Load fatori_registers.yaml
        from scripts.common.paths import get_fatori_registers_yaml
        registers_path = get_fatori_registers_yaml()
        
        if registers_path.exists():
            try:
                with registers_path.open('r') as f:
                    registers_data = yaml.safe_load(f)
                
                if registers_data and 'modules' in registers_data:
                    modules_data = registers_data['modules']
                    
                    # Select active registers based on targets and percentage
                    active_registers = select_active_registers(
                        modules_data, 
                        target_config, 
                        percentage, 
                        seed_value
                    )
                    
                    log_event('DEBUG', debug_message=f"Register M-of-N: {len(active_registers)} active registers selected from {percentage}% of enabled targets")
            
            except Exception as e:
                log_event('REG_MON_YAML_READ_ERROR', error_message=str(e))
    
    # Get M-of-N values for active registers
    if reg_mon_enabled and active_registers:
        reg_mon_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_REG_MON, default={})
        
        # Get N (default 3 if null)
        active_mon_n = reg_mon_config.get("m_of_n_N")
        if active_mon_n is None:
            active_mon_n = 3
        
        # Get M (calculate majority if null)
        active_mon_m = reg_mon_config.get("m_of_n_M")
        if active_mon_m is None:
            active_mon_m = (active_mon_n // 2) + 1
        
        # Get hold_on_major (0 if off/null, 1 if on)
        hold_on_major = reg_mon_config.get("hold_on_major", False)
        active_hold = 1 if hold_on_major else 0
    else:
        # Disabled or no active registers
        active_mon_n = 1
        active_mon_m = 0
        active_hold = 0
    
    # Inactive register defaults
    inactive_mon_n = 1
    inactive_mon_m = 0
    inactive_hold = 0
    
    # Load fatori_registers.yaml and generate macros
    from scripts.common.paths import get_fatori_registers_yaml
    registers_path = get_fatori_registers_yaml()
    
    if registers_path.exists():
        try:
            with registers_path.open('r') as f:
                registers_data = yaml.safe_load(f)
            
            if registers_data and 'modules' in registers_data:
                modules = registers_data['modules']
                
                # Process each module
                for module_entry in modules:
                    if not isinstance(module_entry, dict):
                        continue
                    
                    module_name = module_entry.get('module', 'unknown')
                    regs = module_entry.get('regs', [])
                    
                    if regs:
                        lines.append("")
                        lines.append(f"// {module_name}")
                    
                    # Process each register in the module
                    for reg in regs:
                        if not isinstance(reg, dict):
                            continue
                        
                        reg_name = reg.get('name')
                        if not reg_name:
                            continue
                        
                        # Check if this register is active
                        is_active = reg_name in active_registers
                        
                        if is_active:
                            # Active register: use config values
                            lines.append(f"`define {reg_name}_MON_N {active_mon_n}")
                            lines.append(f"`define {reg_name}_MON_M {active_mon_m}")
                            lines.append(f"`define {reg_name}_HOLD_LAST_GOOD {active_hold}")
                        else:
                            # Inactive register: use defaults
                            lines.append(f"`define {reg_name}_MON_N {inactive_mon_n}")
                            lines.append(f"`define {reg_name}_MON_M {inactive_mon_m}")
                            lines.append(f"`define {reg_name}_HOLD_LAST_GOOD {inactive_hold}")
                        
                        lines.append("")
            else:
                lines.append("// fatori_registers.yaml is empty or invalid format")
        
        except Exception as e:
            log_event('REG_MON_YAML_READ_ERROR', error_message=str(e))
            lines.append(f"// Error reading fatori_registers.yaml: {e}")
    else:
        log_event('REG_MON_YAML_NOT_FOUND', registers_path=str(registers_path))
        lines.append("// fatori_registers.yaml not found")
    
    # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Register M-of-N redundancy configuration",
        content=lines,
        area="FTM"
    )