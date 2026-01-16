# =============================================================================
# FATORI-V • Override Validator
# File: override_validator.py
# -----------------------------------------------------------------------------
# Validates configuration overrides for correctness and safety.
# =============================================================================

from typing import Dict, Any, List, Tuple
from scripts.common.common_settings import *
from scripts.logging.logger import log_event


def validate_required_fields(config: Dict) -> List[str]:
    """
    Validate that required configuration fields are present.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        List of error messages
    """
    errors = []
    
    # Required top-level sections
    required_sections = [KEY_RUN, KEY_GENERAL]
    
    for section in required_sections:
        if section not in config:
            errors.append(f"Required section missing: {section}")
    
    # Required run fields
    if KEY_RUN in config:
        run = config[KEY_RUN]
        
        if KEY_RUN_HARDWARE not in run:
            errors.append(f"Required field missing: run.hardware")
        elif KEY_HW_BOARD not in run[KEY_RUN_HARDWARE]:
            errors.append(f"Required field missing: run.hardware.board")
    
    return errors


def validate_type_consistency(original: Dict, overridden: Dict, path: str = "") -> List[str]:
    """
    Validate that override values maintain type consistency.
    
    Args:
        original: Original configuration
        overridden: Configuration with overrides applied
        path: Current path (for recursion)
    
    Returns:
        List of warning messages
    """
    warnings = []
    
    for key, orig_value in original.items():
        current_path = f"{path}.{key}" if path else key
        
        if key not in overridden:
            continue
        
        overr_value = overridden[key]
        
        # Check type consistency
        if type(orig_value) != type(overr_value):
            warnings.append(
                f"Type change at {current_path}: "
                f"{type(orig_value).__name__} -> {type(overr_value).__name__}"
            )
        
        # Recurse for dictionaries
        if isinstance(orig_value, dict) and isinstance(overr_value, dict):
            warnings.extend(validate_type_consistency(orig_value, overr_value, current_path))
    
    return warnings


def validate_dependency_constraints(config: Dict) -> List[str]:
    """
    Validate configuration dependencies are satisfied.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        List of error messages
    """
    errors = []
    
    # Check ISA extension dependencies
    from scripts.common.yaml_io.yaml_helpers import get_nested
    
    features = get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, default={})
    isa = features.get(KEY_FEAT_ISA, {})
    
    # RV32M depends on having M extension enabled
    if isa.get(KEY_ISA_RV32M, False):
        # Check if multiplier is configured
        multiplier = get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_MULTIPLIER)
        if multiplier == "off":
            errors.append(
                "Inconsistent configuration: RV32M enabled but multiplier is 'off'"
            )
    
    # Check FTM dependencies
    ftms = features.get(KEY_FEAT_FTMS, {})
    
    # Register M-of-N depends on fault manager
    if ftms.get(KEY_FTM_REG_MON, False):
        fault_mgr = features.get(KEY_FEAT_FAULT_MANAGER)
        if fault_mgr == "off":
            errors.append(
                "Inconsistent configuration: register_m_of_n enabled but fault_manager is 'off'"
            )
    
    return errors


def validate_value_ranges(config: Dict) -> List[str]:
    """
    Validate configuration values are within acceptable ranges.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        List of warning messages
    """
    warnings = []
    
    from scripts.common.yaml_io.yaml_helpers import get_nested
    
    # Check timeout values
    results = get_nested(config, KEY_GENERAL, KEY_GEN_RESULTS, default={})
    grab_timeout = results.get('grab_timeout', 0)
    
    if grab_timeout > 0 and grab_timeout < 100:
        warnings.append(f"Very low grab_timeout: {grab_timeout}s (may cause issues)")
    
    if grab_timeout > 10000:
        warnings.append(f"Very high grab_timeout: {grab_timeout}s (may be excessive)")
    
    return warnings


def validate_overrides(original: Dict, overridden: Dict) -> Tuple[List[str], List[str]]:
    """
    Comprehensive validation of overridden configuration.
    
    Checks:
    - Required fields still present
    - Type consistency maintained
    - Dependencies satisfied
    - Values within acceptable ranges
    
    Args:
        original: Original configuration dictionary
        overridden: Configuration with overrides applied
    
    Returns:
        Tuple of (errors, warnings)
    """
    log_event('OVERRIDE_VALIDATION_START')
    
    errors = []
    warnings = []
    
    # Validate required fields
    errors.extend(validate_required_fields(overridden))
    
    # Validate type consistency
    warnings.extend(validate_type_consistency(original, overridden))
    
    # Validate dependencies
    errors.extend(validate_dependency_constraints(overridden))
    
    # Validate value ranges
    warnings.extend(validate_value_ranges(overridden))
    
    # Log results
    if errors:
        log_event('OVERRIDE_VALIDATION_ERRORS', error_count=len(errors), errors=errors)
    
    if warnings:
        log_event('OVERRIDE_VALIDATION_WARNINGS', warning_count=len(warnings))
    
    if not errors and not warnings:
        log_event('OVERRIDE_VALIDATION_PASSED')
    
    return errors, warnings