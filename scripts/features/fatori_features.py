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
    
    # Get performance mechanisms from general configuration
    perf_mech_config = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, default={})
    
    # FATORI_ICACHE - from performance_mechanisms.icache
    icache_enable = perf_mech_config.get(KEY_PERF_ICACHE, False)
    icache_val = 1 if icache_enable else 0
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_ICACHE, {icache_val})")
    
    # FATORI_WSTAGE - from performance_mechanisms.wstage
    wstage_enable = perf_mech_config.get(KEY_PERF_WSTAGE, False)
    wstage_val = 1 if wstage_enable else 0
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_WSTAGE, {wstage_val})")
    
    # FATORI_BRANCH_TALU - from performance_mechanisms.branch_target_alu
    branch_talu_enable = perf_mech_config.get(KEY_PERF_BRANCH_TALU, False)
    branch_talu_val = 1 if branch_talu_enable else 0
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_BRANCH_TALU, {branch_talu_val})")
    
    # FATORI_BRANCH_PRED - from performance_mechanisms.branch_pred
    branch_pred_enable = perf_mech_config.get(KEY_PERF_BRANCH_PRED, False)
    branch_pred_val = 1 if branch_pred_enable else 0
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_BRANCH_PRED, {branch_pred_val})")
    
    # Get Ibex configuration for regfile, multiplier, bit manipulation
    ibex_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, default={})
    regfile_type = ibex_config.get(KEY_IBEX_REGFILE, "ff")
    multiplier_type = ibex_config.get(KEY_IBEX_MULTIPLIER, "none")
    bit_manip_type = ibex_config.get(KEY_IBEX_BIT_MANIP, "none")
    
    # FATORI_REGFILE
    regfile_enum = get_regfile_enum(regfile_type)
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_REGFILE, {regfile_enum})")
    
    # Get ISA extensions
    isa_config = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, default={})
    rv32b_enabled = get_isa_extension_state(config, KEY_ISA_RV32B)
    rv32m_enabled = get_isa_extension_state(config, KEY_ISA_RV32M)
    rv32e_enabled = get_isa_extension_state(config, KEY_ISA_RV32E)
    
    # FATORI_RV32B - always define
    # If extension disabled: use "none", if enabled: use specifics.ibex.bit_manipulation
    if rv32b_enabled:
        bit_manip_enum = get_bit_manip_enum(bit_manip_type)
    else:
        bit_manip_enum = get_bit_manip_enum("none")
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_RV32B, {bit_manip_enum})")
    
    # FATORI_RV32M - always define
    # If extension disabled: use "none", if enabled: use specifics.ibex.multiplier
    if rv32m_enabled:
        multiplier_enum = get_multiplier_enum(multiplier_type)
    else:
        multiplier_enum = get_multiplier_enum("none")
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_RV32M, {multiplier_enum})")
    
    # FATORI_RV32E
    rv32e_val = 1 if rv32e_enabled else 0
    lines.append(f"`__FATORI_MACRO_DEF(FATORI_RV32E, {rv32e_val})")
    
    # Get metrics_level from general (not specifics)
    metrics_level = get_nested(config, KEY_GENERAL, KEY_METRICS_LEVEL, default=0)
    
    # Get override from specifics if present
    metrics_config = get_nested(config, KEY_SPECIFICS, KEY_SPEC_METRICS, default={})
    custom_layer_override = metrics_config.get('custom_fi_layer_override')
    
    # HPMC counters configuration
    if metrics_level == 0:
        hpmc_num = 0
        hpmc_width = 32
    else:
        # Get overrides from specifics.metrics or use defaults based on metrics_level
        hpmc_num = metrics_config.get('ibex_hpmc_num')
        if hpmc_num is None:
            hpmc_num = 10  # Default for metrics_level > 0
        
        hpmc_width = metrics_config.get('ibex_hpmc_width')
        if hpmc_width is None:
            hpmc_width = 32  # Default width
    
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
    
    # FT layers based on metrics_level (or custom override)
    if custom_layer_override is not None:
        effective_layer = custom_layer_override
    else:
        effective_layer = metrics_level
    
    # Add comment explaining metrics layers
    lines.append("")
    lines.append("// METRIC_LAYER Selection")
    lines.append("// 0 = Baseline (mcycle, minstret only)")
    lines.append("// 1 = + HPM counters (mhpmcounter3-12)")
    lines.append("// 2 = + Error counting (minor_cnt, major_cnt) + injection counting")
    lines.append("// 3 = + Correction tracking (corrected_cnt) + per-class major breakdown (major_internal_cnt, major_bus_cnt, double_fault_cnt)")
    lines.append("// 4 = + Timing metrics (cycles_to_first_min/maj, detect_latency)")
    lines.append("// 5 = + Latency statistics (latency_sum, latency_cnt)")

    
    if effective_layer >= 2:
        lines.append("`define FATORI_FT_LAYER_1")
    if effective_layer >= 3:
        lines.append("`define FATORI_FT_LAYER_2")
    if effective_layer >= 4:
        lines.append("`define FATORI_FT_LAYER_3")
    if effective_layer >= 5:
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