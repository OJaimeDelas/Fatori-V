# =============================================================================
# FATORI-V • Feature Generation • Features Header
# File: fatori_features.py
# -----------------------------------------------------------------------------
# Generates fatori_features.svh with ISA extensions and Ibex configuration.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import FATORI_FEATURES_SVH
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import (
    get_isa_extension_state,
    get_feature_state,
    any_benchmark_has_fi,
)
from scripts.mapping.isa_mapping import (
    get_multiplier_enum,
    get_bit_manip_enum,
    get_regfile_enum,
)
from scripts.common.svh_writer.svh_writer import (
    write_svh_file,
)


def generate_features_header(config, output_dir):
    """
    Generate fatori_features.svh header file with ISA extensions and Ibex configuration.
    
    Uses `__FATORI_MACRO_DEF macro for all definitions and includes fatori_macro_functions.svh.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where the file should be written
    
    Returns:
        Path to the generated file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = FATORI_FEATURES_SVH
    output_path = output_dir / file_name
    
    lines = []
    
    lines.append("")
    
    # FATORI_FI - simple define if any benchmark has FI
    if any_benchmark_has_fi(config):
        lines.append("`define FATORI_FI")
        lines.append("")
    
    # Get Ibex configuration
    ibex_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, default={})
    icache_enable = ibex_config.get(KEY_IBEX_ICACHE, False)
    regfile_type = ibex_config.get(KEY_IBEX_REGFILE, "ff")
    multiplier_type = ibex_config.get(KEY_IBEX_MULTIPLIER, "none")
    bit_manip_type = ibex_config.get(KEY_IBEX_BIT_MANIP, "none")
    
    # FATORI_ICACHE
    icache_val = 1 if icache_enable else 0
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_ICACHE, {icache_val})")
    
    # FATORI_WSTAGE (always 1 for our configuration)
    lines.append("`__FATORI_MACRO_DEF(FATORI_WSTAGE, 1)")
    
    # FATORI_BRANCH_TALU (always 1)
    lines.append("`__FATORI_MACRO_DEF(FATORI_BRANCH_TALU, 1)")
    
    # FATORI_BRANCH_PRED (always 1)
    lines.append("`__FATORI_MACRO_DEF(FATORI_BRANCH_PRED, 1)")
    
    # FATORI_REGFILE
    regfile_enum = get_regfile_enum(regfile_type)
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_REGFILE, {regfile_enum})")
    
    # Get ISA extensions
    isa_config = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, default={})
    rv32b_enabled = get_isa_extension_state(config, KEY_ISA_RV32B)
    rv32m_enabled = get_isa_extension_state(config, KEY_ISA_RV32M)
    rv32e_enabled = get_isa_extension_state(config, KEY_ISA_RV32E)
    
    # FATORI_RV32B - only define if enabled
    if rv32b_enabled:
        bit_manip_enum = get_bit_manip_enum(bit_manip_type)
        lines.append(f"`__FATORI_MACRO_DEF(FATORI_RV32B, {bit_manip_enum})")
    
    # FATORI_RV32M - only define if enabled
    if rv32m_enabled:
        multiplier_enum = get_multiplier_enum(multiplier_type)
        lines.append(f"`__FATORI_MACRO_DEF(FATORI_RV32M, {multiplier_enum})")
    
    # FATORI_RV32E
    rv32e_val = 1 if rv32e_enabled else 0
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_RV32E, {rv32e_val})")
    
    # Get metrics configuration
    metrics_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_METRICS, default={})
    metrics_level = metrics_config.get(KEY_METRICS_LEVEL, 0)
    
    # HPMC counters
    if metrics_level == 0:
        hpmc_num = cfg.DEFAULT_HPMC_NUM_LEVEL_0
    else:
        hpmc_num = metrics_config.get(KEY_METRICS_HPMC_NUM, cfg.DEFAULT_HPMC_NUM_LEVEL_PLUS)
    
    hpmc_width = metrics_config.get(KEY_METRICS_HPMC_WIDTH, cfg.DEFAULT_HPMC_WIDTH)
    
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_MHPMCOUNTER_NUM, {hpmc_num})")
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_MHPMCOUNTER_W, {hpmc_width})")
    
    # Get fault manager configuration
    fault_mgr_enabled = get_feature_state(config, KEY_FEAT_FAULT_MANAGER)
    
    if fault_mgr_enabled:
        fm_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_FT_FAULT_MGR, default={})
        rst_on_major = fm_config.get(KEY_FM_RST_ON_MAJOR, False)
        wait_sleep = fm_config.get(KEY_FM_WAIT_SLEEP, False)
        
        rst_val = 1 if rst_on_major else 0
        wait_val = 1 if wait_sleep else 0
        
        lines.append(f"`__FATORI_MACRO_DEF(FATORI_RESET_ON_MAJOR, {rst_val})")
        lines.append(f"`__FATORI_MACRO_DEF(FATORI_WAIT_SLEEP_BEFORE_RESET, {wait_val})")
        lines.append("`__FATORI_MACRO_DEF(FATORI_FAULT_MGR, 1)")
    else:
        lines.append("`__FATORI_MACRO_DEF(FATORI_RESET_ON_MAJOR, 0)")
        lines.append("`__FATORI_MACRO_DEF(FATORI_WAIT_SLEEP_BEFORE_RESET, 0)")
        lines.append("`__FATORI_MACRO_DEF(FATORI_FAULT_MGR, 0)")
    
    lines.append("")
    
    # FT layers based on metrics_level
    if metrics_level >= 1:
        lines.append("`define FATORI_FT_LAYER_1")
    if metrics_level >= 2:
        lines.append("`define FATORI_FT_LAYER_2")
    if metrics_level >= 3:
        lines.append("`define FATORI_FT_LAYER_3")
    if metrics_level >= 4:
        lines.append("`define FATORI_FT_LAYER_4")
    
    # Write the complete file with proper header
    return write_svh_file(
        output_path=output_dir,
        file_name=file_name,
        description="Fault tolerance mechanism enable macros",
        content=lines,
        area="FTM",
        includes=["fatori_macro_functions.svh"]
    )