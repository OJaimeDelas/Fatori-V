# =============================================================================
# FATORI-V • Master File Generator
# File: generate_all.py
# -----------------------------------------------------------------------------
# Master orchestrator for all file generation phases.
# =============================================================================

from pathlib import Path
from typing import Dict
from scripts.validation.run_validator import validate_run_config, print_validation_results
from scripts.features.generation_controller import generate_all_svh_headers
from scripts.pblocks.system.pblock_orchestrator import orchestrate_pblock_generation
from scripts.features.system_dict_merger import merge_system_dicts
from scripts.exec.bench_config_generator import generate_all_bench_configs
from scripts.exec.metrics_config_generator import generate_metrics_config_h
from scripts.cli.override_applicator import apply_cli_overrides
from scripts.common.yaml_io.load_run_yaml import load_run_yaml
from scripts.logging.logger import log_event
import fatori_settings as cfg
from config.constants import METRICS_CONFIG_H, SYSTEM_DICT_MERGED_NAME


def generate_all_files(config):
    """
    Master orchestrator for complete file generation workflow.
    
    This is the main entry point for generating all files required for a
    FATORI-V run. It orchestrates validation and all generation phases.
    
    Workflow:
    1. Validate configuration (Phase 2 validators)
    2. Generate SystemVerilog headers (Phase 5)
       - fatori_features.svh
       - fatori_ftm.svh
       - fatori_reg_mon.svh
       - fatori_logic_mon.svh
       - fatori_selftest.svh
    3. Generate pblock files (Phase 6)
       - fatori_pblocks.svh
       - pblock_config.yaml
       - Call external pblock system (if FI enabled)
       - Generate all TCL scripts
    4. Generate system integration files (Phase 7)
       - system_dict_merged.yaml
       - bench_config.h
    
    All generated files are placed in:
    - tmp/generated/ for .svh headers and YAML files
    - tmp/tcl/ for TCL scripts
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary with paths to all generated files:
        {
            'valid': bool,
            'validation_result': dict,
            'svh_headers': {
                'features': Path,
                'ftm': Path,
                'reg_mon': Path,
                'logic_mon': Path,
                'selftest': Path
            },
            'pblock_files': {
                'pblock_config': Path,
                'pblock_svh': Path,
                'pblock_tcl': Path or None,
                'pblock_dict': Path or None
            },
            'tcl_scripts': {
                'pre_synthesis': Path,
                'post_opt': Path,
                'post_route': Path,
                'pre_bitstream': Path,
                'post_bitstream': Path
            },
            'system_files': {
                'system_dict_merged': Path,
                'bench_config_h': Path
            }
        }
    
    Raises:
        ValueError: If configuration validation fails
    """
    log_event('GENERATION_MASTER_START')
    
    generated_files = {
        'valid': False,
        'validation_result': None,
        'svh_headers': {},
        'pblock_files': {},
        'tcl_scripts': {},
        'system_files': {}
    }
    
    # Step 1: Validate Configuration
    log_event('GENERATION_STEP1_START')
    
    is_valid, validation_result = validate_run_config(config, strict=cfg.VALIDATION_STRICT_DEFAULT)
    generated_files['valid'] = is_valid
    generated_files['validation_result'] = validation_result
    
    # Print validation results
    print_validation_results(validation_result)
    
    if not is_valid:
        log_event('ERROR_GENERATION_VALIDATION_FAILED')
        raise ValueError("Configuration validation failed. Cannot proceed with generation.")
    
    log_event('GENERATION_VALIDATION_SUCCESS')
    
    # Step 2: Generate SystemVerilog Headers
    log_event('GENERATION_STEP2_START')
    
    svh_headers = generate_all_svh_headers(config, cfg.TMP_GENERATED_DIR)
    generated_files['svh_headers'] = svh_headers
    
    log_event('GENERATION_SVH_COMPLETE', file_count=len([p for p in svh_headers.values() if p]))
    
    # Step 3: Generate Pblock Files and TCL Scripts
    log_event('GENERATION_STEP3_START')
    
    pblock_files = orchestrate_pblock_generation(config)
    generated_files['pblock_files'] = {
        'pblock_config': pblock_files['pblock_config'],
        'pblock_svh': pblock_files['pblock_svh'],
        'pblock_tcl': pblock_files['pblock_tcl'],
        'pblock_dict': pblock_files['pblock_dict']
    }
    generated_files['tcl_scripts'] = pblock_files['tcl_scripts']
    
    log_event('GENERATION_PBLOCK_TCL_COMPLETE')
    
    # Step 4: Generate System Integration Files
    log_event('GENERATION_STEP4_START')
    
    # Generate system_dict_merged.yaml
    log_event('GENERATION_SYSTEM_DICT_START')
    system_dict_path = cfg.TMP_GENERATED_DIR / SYSTEM_DICT_MERGED_NAME
    system_dict_merged = merge_system_dicts(config, system_dict_path)
    generated_files['system_files']['system_dict_merged'] = system_dict_merged
    
    # Generate bench_config.h files (per-benchmark)
    bench_config_files = generate_all_bench_configs(config, cfg.TMP_GENERATED_DIR)
    generated_files['system_files']['bench_config_files'] = bench_config_files
    
    # Generate metrics_config.h
    log_event('GENERATION_METRICS_CONFIG_START')
    metrics_config_path = cfg.TMP_GENERATED_DIR / METRICS_CONFIG_H
    metrics_config_h = generate_metrics_config_h(config, metrics_config_path)
    generated_files['system_files']['metrics_config_h'] = metrics_config_h
    
    log_event('GENERATION_SYSTEM_INTEGRATION_COMPLETE')
    
    # Final Summary
    # Count total files generated
    total_files = 0
    total_files += len([p for p in generated_files['svh_headers'].values() if p])
    total_files += len([p for p in generated_files['pblock_files'].values() if p])
    total_files += len([p for p in generated_files['tcl_scripts'].values() if p])
    total_files += len([p for p in generated_files['system_files'].values() if p])
    
    svh_count = len([p for p in generated_files['svh_headers'].values() if p])
    pblock_count = len([p for p in generated_files['pblock_files'].values() if p])
    tcl_count = len([p for p in generated_files['tcl_scripts'].values() if p])
    system_count = len([p for p in generated_files['system_files'].values() if p])
    
    log_event('GENERATION_COMPLETE', 
              total_files=total_files,
              svh_headers=svh_count,
              pblock_files=pblock_count,
              tcl_scripts=tcl_count,
              system_files=system_count)
    
    return generated_files


def get_all_generated_file_paths(generated_files):
    """
    Extract a flat list of all successfully generated file paths.
    
    Args:
        generated_files: Dictionary returned by generate_all_files
    
    Returns:
        List of Path objects for all successfully generated files
    """
    file_list = []
    
    # Add SVH headers
    for path in generated_files['svh_headers'].values():
        if path:
            file_list.append(path)
    
    # Add pblock files
    for path in generated_files['pblock_files'].values():
        if path:
            file_list.append(path)
    
    # Add TCL scripts
    for path in generated_files['tcl_scripts'].values():
        if path:
            file_list.append(path)
    
    # Add system files
    for path in generated_files['system_files'].values():
        if path:
            file_list.append(path)
    
    return file_list