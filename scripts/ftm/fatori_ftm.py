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
    
    # Complete list of FTMs (excluding M-of-N and self-test which have separate files)
    ftm_map = {
        'data_indep_timing': 'FATORI_DATA_INDEP_TIMING',
        'dummy_instr': 'FATORI_DUMMY_INSTR',
        'hard_pc': 'FATORI_HARDENED_PC',
        'icache_ecc': 'FATORI_ICACHE_ECC',
        'lockstep': 'FATORI_LOCKSTEP',
        'mem_ecc': 'FATORI_MEM_ECC',
        'pmp': 'FATORI_PMP',
        'regfile_ecc': 'FATORI_RF_ECC',
        'regfile_raddr_glitch': 'FATORI_RF_RADDR_GLITCH',
        'regfile_we_glitch': 'FATORI_RF_WE_GLITCH',
        'secure_guards': 'FATORI_SECURE_GUARDS',
        'shadow_csrs': 'FATORI_SHADOW_CSRS',
    }
    
    # Generate macros for ALL FTMs (1 if enabled, 0 if disabled)
    for ftm_key, macro_name in sorted(ftm_map.items()):
        ftm_enabled = get_ftm_state(config, ftm_key)
        value = 1 if ftm_enabled else 0
        lines.append(f"`__FATORI_MACRO_DEF({macro_name}, {value})")
    
   # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Fault tolerance mechanism enable macros",
        content=lines,
        area="FTM",
        includes=["fatori_macro_functions.svh"]
    )