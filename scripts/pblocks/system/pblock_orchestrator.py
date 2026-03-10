# =============================================================================
# FATORI-V • Pblock Generation • Pblock Orchestrator
# File: pblock_orchestrator.py
# -----------------------------------------------------------------------------
# Orchestrates complete pblock generation workflow including external system.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import PBLOCK_CONFIG_YAML, FATORI_PBLOCKS_SVH
from scripts.common.common_settings import KEY_GENERAL
from scripts.common.yaml_io.yaml_helpers import any_benchmark_has_fi, get_nested
from scripts.pblocks.generation.fatori_pblocks import generate_pblocks_svh
from scripts.pblocks.system.config_builder import build_pblock_config
from scripts.pblocks.system.pblock_caller import call_pblock_system
from scripts.pblocks.generation.tcl_controller import generate_all_tcl_files
from scripts.features.override_handler import apply_override
from scripts.logging import logger
from config.constants import HEADER_WIDTH


def orchestrate_pblock_generation(config):
    """
    Orchestrate complete pblock and TCL generation workflow.
    
    This is the main entry point for pblock system integration.
    
    Workflow:
    1. Generate pblock_config.yaml for external system
    2. If FI enabled: Call external pblock placement system
       - Generates fatori_pblocks.tcl
       - Generates pblock_dict.yaml
    3. Generate fatori_pblocks.svh with KEEP macros
    4. Generate all Vivado TCL hook scripts
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary with paths to all generated files:
        {
            'pblock_config': Path,
            'pblock_svh': Path,
            'pblock_tcl': Path or None,
            'pblock_dict': Path or None,
            'tcl_scripts': {
                'pre_synthesis': Path,
                'post_opt': Path,
                ...
            }
        }
    """
    logger.log_event('PBLOCK_GENERATION_START')
    
    generated_files = {
        'pblock_config': None,
        'pblock_svh': None,
        'pblock_tcl': None,
        'pblock_dict': None,
        'tcl_scripts': {}
    }
    
    # Check if FI is enabled and get area profile
    fi_enabled = any_benchmark_has_fi(config)
    fi_general_config = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    area_profile = fi_general_config.get("area_profile", "device")
    
    # Step 1: Generate pblock_config.yaml
    logger.log_event('DEBUG', debug_message="Step 1: Generating pblock configuration...")
    config_path = cfg.TMP_GENERATED_DIR / PBLOCK_CONFIG_YAML
    pblock_config_path = build_pblock_config(config, config_path)
    generated_files['pblock_config'] = pblock_config_path
    logger.log_event('DEBUG', debug_message=f"  → {pblock_config_path}")
    
    # Step 2: Call external pblock system (only if FI enabled AND area_profile is "modules")
    # For "device" area profile, no pblocks needed
    if fi_enabled and area_profile == "modules":
        logger.log_event('DEBUG', debug_message="Step 2: Calling external pblock placement system...")
        pblock_outputs = call_pblock_system(pblock_config_path, cfg.TMP_GENERATED_DIR)
        
        if pblock_outputs:
            if pblock_outputs.get('pblock_tcl'):
                generated_files['pblock_tcl'] = pblock_outputs['pblock_tcl']
                logger.log_event('DEBUG', debug_message=f"  → {pblock_outputs['pblock_tcl']}")
            
            if pblock_outputs.get('pblock_dict'):
                generated_files['pblock_dict'] = pblock_outputs['pblock_dict']
                logger.log_event('DEBUG', debug_message=f"  → {pblock_outputs['pblock_dict']}")
        else:
            logger.log_event('WARNING', warning_message="External pblock system not available or failed")
            logger.log_event('WARNING', warning_message="Continuing without external pblock constraints")
    elif fi_enabled and area_profile != "modules":
        logger.log_event('DEBUG', debug_message=f"Step 2: Area profile is '{area_profile}' - no targeted placement blocks needed")
    else:
        logger.log_event('DEBUG', debug_message="Step 2: Skipping external pblock system (FI not enabled)")
    
    # Step 3: Generate fatori_pblocks.svh (or use override)
    logger.log_event('DEBUG', debug_message="Step 3: Generating pblocks SVH header...")
    override_path = apply_override(config, FATORI_PBLOCKS_SVH, cfg.TMP_GENERATED_DIR)
    if override_path:
        pblock_svh_path = override_path
        logger.log_event('DEBUG', debug_message=f"  → {pblock_svh_path} (from override)")
    else:
        pblock_svh_path = generate_pblocks_svh(config, cfg.TMP_GENERATED_DIR)
        logger.log_event('DEBUG', debug_message=f"  → {pblock_svh_path}")
    generated_files['pblock_svh'] = pblock_svh_path
    
    # Step 4: Generate all TCL scripts
    logger.log_event('DEBUG', debug_message="Step 4: Generating Vivado TCL scripts...")
    tcl_files = generate_all_tcl_files(config, cfg.TMP_TCL_DIR)
    generated_files['tcl_scripts'] = tcl_files
    
    for script_name, script_path in tcl_files.items():
        logger.log_event('DEBUG', debug_message=f"  → {script_name}: {script_path.name}")
    
    # Summary - count total generated files
    file_count = sum(1 for v in [generated_files.get('pblock_config'), 
                                   generated_files.get('pblock_svh'),
                                   generated_files.get('pblock_tcl'),
                                   generated_files.get('pblock_dict')] if v) + len(tcl_files)
    
    logger.log_event('PBLOCK_GENERATION_END', file_count=file_count)
    
    return generated_files


def get_generated_file_list(generated_files):
    """
    Create a flat list of all successfully generated file paths.
    
    Args:
        generated_files: Dictionary returned by orchestrate_pblock_generation
    
    Returns:
        List of Path objects for successfully generated files
    """
    file_list = []
    
    # Add single files
    for key in ['pblock_config', 'pblock_svh', 'pblock_tcl', 'pblock_dict']:
        if generated_files.get(key):
            file_list.append(generated_files[key])
    
    # Add TCL scripts
    if generated_files.get('tcl_scripts'):
        for script_path in generated_files['tcl_scripts'].values():
            if script_path:
                file_list.append(script_path)
    
    return file_list