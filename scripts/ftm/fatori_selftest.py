# =============================================================================
# FATORI-V • FTM Generation • Self-Test Header
# File: fatori_selftest.py
# -----------------------------------------------------------------------------
# Generates fatori_selftest.svh stub file for self-testing mechanisms.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import FATORI_SELFTEST_SVH
from scripts.common.common_settings import *
from scripts.common.svh_writer.svh_writer import write_svh_file


def generate_selftest_header(config, output_dir):
    """
    Generate fatori_selftest.svh header file (stub).
    
    This file is always generated but currently contains no configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where the file should be written
    
    Returns:
        Path to the generated file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = FATORI_SELFTEST_SVH
    output_path = output_dir / file_name
    
    lines = []
    
    # Empty - just guards
    lines.append("// Self-testing configuration placeholder")
    
    # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Self-testing configuration placeholder",
        content=lines,
        area="FTM"
    )