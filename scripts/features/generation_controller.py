# =============================================================================
# FATORI-V • Feature Generation • Generation Controller
# File: generation_controller.py
# -----------------------------------------------------------------------------
# Orchestrates generation of all SystemVerilog header files.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_ftm_state
from scripts.features.fatori_features import generate_features_header
from scripts.ftm.fatori_ftm import generate_ftm_header
from scripts.ftm.fatori_reg_mon import generate_reg_mon_header
from scripts.ftm.fatori_logic_mon import generate_logic_mon_header
from scripts.ftm.fatori_selftest import generate_selftest_header
from scripts.logging.logger import log_event


def generate_all_svh_headers(config, output_dir=None):
    """
    Generate all SystemVerilog header files for a run configuration.
    
    This orchestrates the generation of:
    - fatori_features.svh: ISA extensions and Ibex configuration
    - fatori_ftm.svh: FTM enable macros
    - fatori_reg_mon.svh: Register M-of-N configuration (if enabled)
    - fatori_logic_mon.svh: Logic M-of-N configuration (if enabled)
    - fatori_selftest.svh: Self-test stub (if enabled or always)
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where files should be written.
                   Defaults to tmp/generated/
    
    Returns:
        Dictionary mapping file names to their generated paths
        {
            'features': Path,
            'ftm': Path,
            'reg_mon': Path or None,
            'logic_mon': Path or None,
            'selftest': Path or None,
        }
    """
    # Use default output directory if not specified
    if output_dir is None:
        output_dir = cfg.TMP_GENERATED_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('SVH_GENERATION_START', output_dir=str(output_dir))
    
    generated_files = {}
    
    # Generate features header (always required)
    log_event('SVH_GENERATING', file_type='features')
    features_path = generate_features_header(config, output_dir)
    generated_files['features'] = features_path
    log_event('SVH_GENERATED', file_name=features_path.name)
    
    # Generate FTM header (always generated, may be empty)
    log_event('SVH_GENERATING', file_type='ftm')
    ftm_path = generate_ftm_header(config, output_dir)
    generated_files['ftm'] = ftm_path
    log_event('SVH_GENERATED', file_name=ftm_path.name)
    
    # Generate register M-of-N header (if enabled)
    reg_mon_enabled = get_ftm_state(config, KEY_FTM_REG_MON)
    if reg_mon_enabled:
        log_event('SVH_GENERATING', file_type='reg_mon')
        reg_mon_path = generate_reg_mon_header(config, output_dir)
        if reg_mon_path:
            generated_files['reg_mon'] = reg_mon_path
            log_event('SVH_GENERATED', file_name=reg_mon_path.name)
        else:
            log_event('SVH_SKIPPED', file_type='reg_mon', reason='override_enabled')
            generated_files['reg_mon'] = None
    else:
        # Still generate stub file
        log_event('SVH_GENERATING', file_type='reg_mon_stub')
        reg_mon_path = generate_reg_mon_header(config, output_dir)
        generated_files['reg_mon'] = reg_mon_path
        log_event('SVH_GENERATED', file_name=reg_mon_path.name, status='disabled')
    
    # Generate logic M-of-N header (if enabled)
    logic_mon_enabled = get_ftm_state(config, KEY_FTM_LOGIC_MON)
    if logic_mon_enabled:
        log_event('SVH_GENERATING', file_type='logic_mon')
        logic_mon_path = generate_logic_mon_header(config, output_dir)
        if logic_mon_path:
            generated_files['logic_mon'] = logic_mon_path
            log_event('SVH_GENERATED', file_name=logic_mon_path.name)
        else:
            log_event('SVH_SKIPPED', file_type='logic_mon', reason='override_enabled')
            generated_files['logic_mon'] = None
    else:
        # Still generate stub file
        log_event('SVH_GENERATING', file_type='logic_mon_stub')
        logic_mon_path = generate_logic_mon_header(config, output_dir)
        generated_files['logic_mon'] = logic_mon_path
        log_event('SVH_GENERATED', file_name=logic_mon_path.name, status='disabled')
    
    # Generate self-test header (always generate stub)
    log_event('SVH_GENERATING', file_type='selftest')
    selftest_path = generate_selftest_header(config, output_dir)
    generated_files['selftest'] = selftest_path
    log_event('SVH_GENERATED', file_name=selftest_path.name)
    
    file_count = len([p for p in generated_files.values() if p])
    log_event('SVH_GENERATION_COMPLETE', file_count=file_count)
    
    return generated_files


def list_generated_files(generated_files):
    """
    Create a list of all successfully generated file paths.
    
    Args:
        generated_files: Dictionary returned by generate_all_svh_headers
    
    Returns:
        List of Path objects for successfully generated files
    """
    return [path for path in generated_files.values() if path is not None]