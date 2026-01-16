# =============================================================================
# FATORI-V • Schema Validator
# File: schema_validator.py
# -----------------------------------------------------------------------------
# Validates YAML structure and required fields.
# =============================================================================

from scripts.common.common_settings import *
from scripts.validation.validation_settings import *


def validate_schema(config):
    """
    Validate that the configuration has the expected structure and required fields.
    
    Checks:
    - Top-level sections exist (run, general)
    - Required fields under run.identification
    - Proper nesting structure
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    # Check top-level sections
    if KEY_RUN not in config:
        add_error(result, f"Missing required section: '{KEY_RUN}'")
    
    if KEY_GENERAL not in config:
        add_error(result, f"Missing required section: '{KEY_GENERAL}'")
    
    # Validate run section structure
    if KEY_RUN in config:
        run_section = config[KEY_RUN]
        
        if not isinstance(run_section, dict):
            add_error(result, f"Section '{KEY_RUN}' must be a dictionary")
        else:
            # Check for identification subsection
            if KEY_RUN_IDENTIFICATION not in run_section:
                add_error(result, f"Missing required subsection: '{KEY_RUN}.{KEY_RUN_IDENTIFICATION}'")
            else:
                ident = run_section[KEY_RUN_IDENTIFICATION]
                if not isinstance(ident, dict):
                    add_error(result, f"'{KEY_RUN}.{KEY_RUN_IDENTIFICATION}' must be a dictionary")
                else:
                    # Name is required
                    if KEY_IDENT_NAME not in ident or not ident[KEY_IDENT_NAME]:
                        add_error(result, f"Missing required field: '{KEY_RUN}.{KEY_RUN_IDENTIFICATION}.{KEY_IDENT_NAME}'")
    
    # Validate general section structure
    if KEY_GENERAL in config:
        general = config[KEY_GENERAL]
        
        if not isinstance(general, dict):
            add_error(result, f"Section '{KEY_GENERAL}' must be a dictionary")
        else:
            # Check for features subsection
            if KEY_GEN_FEATURES not in general:
                add_warning(result, f"Missing optional subsection: '{KEY_GENERAL}.{KEY_GEN_FEATURES}'")
    
    return result


def validate_field_types(config):
    """
    Validate that fields have the correct data types.
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    # Validate seed is an integer if present
    seed = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, KEY_IDENT_SEED)
    if seed is not None and not isinstance(seed, int):
        add_error(result, f"Field '{KEY_RUN}.{KEY_RUN_IDENTIFICATION}.{KEY_IDENT_SEED}' must be an integer")
    
    # Validate boolean fields under features
    features = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES)
    if features:
        # Check ISA extensions are boolean
        isa = features.get(KEY_FEAT_ISA, {})
        for isa_key in [KEY_ISA_RV32E, KEY_ISA_RV32M, KEY_ISA_RV32B, KEY_ISA_RV32C]:
            value = isa.get(isa_key)
            if value is not None and not isinstance(value, bool):
                add_error(result, f"ISA extension '{isa_key}' must be a boolean")
        
        # Check FTMs are boolean
        ftms = features.get(KEY_FEAT_FTMS, {})
        for ftm_key in [KEY_FTM_REG_MON, KEY_FTM_LOGIC_MON, KEY_FTM_SELFTEST,
                        KEY_FTM_RF_ECC, KEY_FTM_RF_WE_GLITCH, KEY_FTM_RF_RADDR_GLITCH,
                        KEY_FTM_HARDENED_PC]:
            value = ftms.get(ftm_key)
            if value is not None and not isinstance(value, bool):
                add_error(result, f"FTM '{ftm_key}' must be a boolean")
    
    return result


def validate_value_ranges(config):
    """
    Validate that numeric fields are within acceptable ranges.
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Validation result dictionary
    """
    result = create_validation_result()
    
    # Validate metrics level
    metrics_level = get_nested(config, KEY_SPECIFICS, KEY_SPEC_METRICS, KEY_METRICS_LEVEL)
    if metrics_level is not None:
        if not isinstance(metrics_level, int):
            add_error(result, f"'{KEY_SPEC_METRICS}.{KEY_METRICS_LEVEL}' must be an integer")
        elif metrics_level < METRICS_LEVEL_MIN or metrics_level > METRICS_LEVEL_MAX:
            add_error(result, f"'{KEY_SPEC_METRICS}.{KEY_METRICS_LEVEL}' must be between {METRICS_LEVEL_MIN} and {METRICS_LEVEL_MAX}")
    
    # Validate HPMC num
    hpmc_num = get_nested(config, KEY_SPECIFICS, KEY_SPEC_METRICS, KEY_METRICS_HPMC_NUM)
    if hpmc_num is not None:
        if not isinstance(hpmc_num, int):
            add_error(result, f"'{KEY_SPEC_METRICS}.{KEY_METRICS_HPMC_NUM}' must be an integer")
        elif hpmc_num < HPMC_NUM_MIN or hpmc_num > HPMC_NUM_MAX:
            add_error(result, f"'{KEY_SPEC_METRICS}.{KEY_METRICS_HPMC_NUM}' must be between {HPMC_NUM_MIN} and {HPMC_NUM_MAX}")
    
    # Validate HPMC width
    hpmc_width = get_nested(config, KEY_SPECIFICS, KEY_SPEC_METRICS, KEY_METRICS_HPMC_WIDTH)
    if hpmc_width is not None:
        if not isinstance(hpmc_width, int):
            add_error(result, f"'{KEY_SPEC_METRICS}.{KEY_METRICS_HPMC_WIDTH}' must be an integer")
        elif hpmc_width < HPMC_WIDTH_MIN or hpmc_width > HPMC_WIDTH_MAX:
            add_error(result, f"'{KEY_SPEC_METRICS}.{KEY_METRICS_HPMC_WIDTH}' must be between {HPMC_WIDTH_MIN} and {HPMC_WIDTH_MAX}")
    
    return result