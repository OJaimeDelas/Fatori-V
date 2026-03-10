# =============================================================================
# FATORI-V • Pblock Generation • Pblock System Caller
# File: pblock_caller.py
# -----------------------------------------------------------------------------
# Calls pblock placement generation system by importing functions directly.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from scripts.logging.logger import log_event
from config.constants import FATORI_PBLOCKS_TCL, PBLOCK_DICT_YAML


def call_pblock_system(config_path, output_dir):
    """
    Call the pblock placement generation system.
    
    Directly imports and calls pblock generation functions to generate:
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
        Returns None if generation fails
    """
    config_path = Path(config_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Expected output paths
    pblock_dict_path = output_dir / PBLOCK_DICT_YAML
    pblock_tcl_path = output_dir / FATORI_PBLOCKS_TCL
    pblock_summary_path = output_dir / "pblock_summary.txt"
    
    try:
        # Import pblock functions here to avoid import errors at module load time
        from scripts.pblocks.system.generate_pblocks import load_configuration, run_pipeline
        
        log_event('DEBUG', debug_message=f"Loading pblock configuration: {config_path}")
        
        # Load configuration
        config = load_configuration(str(config_path))
        log_event('DEBUG', debug_message="Running pblock generation pipeline...")
        
        # Run pipeline with auto-approve to avoid interactive prompts
        run_pipeline(
            config, 
            str(pblock_dict_path), 
            verbose=False,  # Disable verbose to avoid excessive output
            auto_approve=True  # Auto-approve warnings for automated execution
        )
        
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
    
    except Exception as e:
        log_event('PBLOCK_SYSTEM_ERROR', error_message=str(e))
        return None