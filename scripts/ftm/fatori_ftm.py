# =============================================================================
# FATORI-V • FTM Generation • FTM Header
# File: fatori_ftm.py
# -----------------------------------------------------------------------------
# Generates fatori_ftm.svh with fault tolerance mechanism enable macros.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import FATORI_FTM_SVH
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_ftm_state
from scripts.common.svh_writer.svh_writer import write_svh_file


def generate_ftm_header(config, output_dir):
    """
    Generate fatori_ftm.svh header file with FTM enable macros.
    
    Uses `__FATORI_MACRO_DEF for all FTM enables.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where the file should be written
    
    Returns:
        Path to the generated file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = FATORI_FTM_SVH
    output_path = output_dir / file_name
    
    lines = []
    
    # List of FTMs to check (excluding M-of-N which have separate files)
    ftm_map = {
        KEY_FTM_RF_ECC: 'FATORI_RF_ECC',
        KEY_FTM_RF_WE_GLITCH: 'FATORI_RF_WE_GLITCH',
        KEY_FTM_RF_RADDR_GLITCH: 'FATORI_RF_RADDR_GLITCH',
        KEY_FTM_HARDENED_PC: 'FATORI_HARDENED_PC',
    }
    
    # Track if any FTM is defined
    any_ftm_defined = False
    
    for ftm_key, macro_name in ftm_map.items():
        ftm_enabled = get_ftm_state(config, ftm_key)
        
        if ftm_enabled:
            lines.append(f"`__FATORI_MACRO_DEF({macro_name}, 1)")
            any_ftm_defined = True
    
    # If no FTMs defined, add a comment
    if not any_ftm_defined:
        lines.append("// No FTMs enabled in this configuration")
    
   # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Fault tolerance mechanism enable macros",
        content=lines,
        area="FTM",
        includes=["fatori_macro_functions.svh"]
    )