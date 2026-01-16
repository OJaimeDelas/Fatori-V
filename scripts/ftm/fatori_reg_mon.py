# =============================================================================
# FATORI-V • FTM Generation • Register M-of-N Header
# File: fatori_reg_mon.py
# -----------------------------------------------------------------------------
# Generates fatori_reg_mon.svh by reading fatori_registers.yaml.
# =============================================================================

from pathlib import Path
import yaml
import fatori_settings as cfg
from config.constants import FATORI_REG_MON_SVH
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_ftm_state
from scripts.common.svh_writer.svh_writer import write_svh_file
from scripts.logging.logger import log_event


def generate_reg_mon_header(config, output_dir):
    """
    Generate fatori_reg_mon.svh header file with register M-of-N configuration.
    
    This reads from the static fatori_registers.yaml file (NOT generated from config).
    The fatori_registers.yaml file contains pre-defined register monitoring configuration.
    
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
    
    if not reg_mon_enabled:
        # Just guards, no content
        lines.append("// Register M-of-N is not enabled")
    else:
        # Load fatori_registers.yaml
        # Add import at top of file after other imports
        from scripts.common.paths import get_fatori_registers_yaml

        # Then in the code, replace:
        registers_path = get_fatori_registers_yaml()
        
        if registers_path.exists():
            try:
                with registers_path.open('r') as f:
                    registers_data = yaml.safe_load(f)
                
                if registers_data and isinstance(registers_data, dict):
                    # Add register monitoring definitions from YAML
                    # The format in fatori_registers.yaml defines which registers to monitor
                    lines.append("// Register monitoring configuration from fatori_registers.yaml")
                    
                    # Process register definitions
                    for reg_name, reg_config in registers_data.items():
                        if isinstance(reg_config, dict):
                            mon_n = reg_config.get('mon_n', cfg.DEFAULT_MON_N)
                            mon_m = reg_config.get('mon_m', cfg.DEFAULT_MON_M)
                            
                            lines.append(f"`define {reg_name}_MON_N {mon_n}")
                            lines.append(f"`define {reg_name}_MON_M {mon_m}")
                else:
                    lines.append("// fatori_registers.yaml is empty")
            
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