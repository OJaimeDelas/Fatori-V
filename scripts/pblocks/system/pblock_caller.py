# =============================================================================
# FATORI-V • Pblock Generation • Pblock System Caller
# File: pblock_caller.py
# -----------------------------------------------------------------------------
# Calls external pblock placement generation system.
# =============================================================================

import subprocess
from pathlib import Path
import fatori_settings as cfg
from scripts.logging.logger import log_event
from config.constants import FATORI_PBLOCKS_TCL, PBLOCK_DICT_YAML
from config.constants import HEADER_WIDTH


def call_pblock_system(config_path, output_dir):
    """
    Call the external pblock placement generation system.
    
    The external system (generate_pblocks.py) takes a config file and
    generates:
    - fatori_pblocks.tcl: Vivado placement constraints
    - pblock_dict.yaml: Module size and placement information
    - pblock_summary.txt: Human-readable summary
    
    Args:
        config_path: Path to pblock_config.yaml
        output_dir: Directory where outputs should be written
    
    Returns:
        Dictionary with paths: {
            'pblock_tcl': Path to fatori_pblocks.tcl,
            'pblock_dict': Path to pblock_dict.yaml,
            'pblock_summary': Path to pblock_summary.txt
        }
        Returns None if the external system is not available or fails
    """
    config_path = Path(config_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to external pblock generation script (now in same directory)
    pblock_script = Path(__file__).parent / "generate_pblocks.py"
    
    if not pblock_script.exists():
        log_event('PBLOCK_SCRIPT_NOT_FOUND', script_path=str(pblock_script))
        return None
    
    # Expected output paths
    pblock_dict_path = output_dir / PBLOCK_DICT_YAML
    pblock_tcl_path = output_dir / FATORI_PBLOCKS_TCL
    pblock_summary_path = output_dir / "pblock_summary.txt"
    
    try:
        # Build command - external system uses --input and --output
        # The external system writes multiple files (pblock_dict.yaml, fatori_pblocks.tcl, pblock_summary.txt)
        # and derives their names from the output path's basename
        cmd = [
            "python3",
            str(pblock_script),
            "--input", str(config_path),
            "--output", str(pblock_dict_path),
            "--verbose"  # Add verbose for debugging
        ]
        
        log_event('PBLOCK_SYSTEM_CALLING', command=' '.join(cmd))
        
        # Call the external system
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode != 0:
            log_event('PBLOCK_SYSTEM_FAILED',
                      return_code=result.returncode,
                      stdout=result.stdout,
                      stderr=result.stderr)
            return None
        
        log_event('PBLOCK_SYSTEM_SUCCESS')
        
        # Verify outputs were created
        if not pblock_tcl_path.exists():
            log_event('PBLOCK_OUTPUT_MISSING', expected_file=str(pblock_tcl_path))
            return None
        
        if not pblock_dict_path.exists():
            log_event('PBLOCK_DICT_MISSING', expected_file=str(pblock_dict_path))
            # Continue anyway - dict is optional for some configurations
        
        if not pblock_summary_path.exists():
            log_event('PBLOCK_SUMMARY_MISSING', expected_file=str(pblock_summary_path))
        
        return {
            'pblock_tcl': pblock_tcl_path if pblock_tcl_path.exists() else None,
            'pblock_dict': pblock_dict_path if pblock_dict_path.exists() else None,
            'pblock_summary': pblock_summary_path if pblock_summary_path.exists() else None
        }
    
    except subprocess.TimeoutExpired:
        log_event('PBLOCK_SYSTEM_TIMEOUT')
        return None
    
    except Exception as e:
        log_event('PBLOCK_SYSTEM_ERROR', error_message=str(e))
        return None