# =============================================================================
# FATORI-V • Run Validator
# File: run_validator.py
# -----------------------------------------------------------------------------
# Main validation orchestrator for run configurations.
# =============================================================================

from scripts.common.common_settings import *
from scripts.validation.validation_settings import *
from scripts.validation.schema_validator import *
from scripts.validation.isa_validator import *
from scripts.validation.ftm_validator import *
from scripts.logging.logger import log_event


def validate_run_config(config, strict=STRICT_MODE_DEFAULT):
    """
    Perform complete validation of a run configuration.
    
    This orchestrates all validation checks and aggregates results.
    
    Args:
        config: The loaded YAML configuration dictionary
        strict: If True, treat warnings as errors
    
    Returns:
        Tuple of (is_valid, validation_result)
        - is_valid: Boolean indicating if configuration passed validation
        - validation_result: Dictionary with detailed validation information
    """
    # Create combined result
    combined = create_validation_result()
    
    # Run all validation checks
    validators = [
        ("Schema", validate_schema),
        ("Field Types", validate_field_types),
        ("Value Ranges", validate_value_ranges),
        ("ISA Extensions", validate_isa_extensions),
        ("Multiplier Config", validate_multiplier_config),
        ("Bit Manipulation Config", validate_bit_manip_config),
        ("Regfile Config", validate_regfile_config),
        ("FTM Consistency", validate_ftm_consistency),
        ("M-of-N Parameters", validate_mon_parameters),
        ("FTM Specific Configs", validate_ftm_specific_configs),
    ]
    
    for validator_name, validator_func in validators:
        result = validator_func(config)
        
        # Merge errors
        combined[KEY_ERRORS].extend(result[KEY_ERRORS])
        
        # Merge warnings
        combined[KEY_WARNINGS].extend(result[KEY_WARNINGS])
        
        # Merge corrections
        combined[KEY_CORRECTIONS].extend(result[KEY_CORRECTIONS])
        
        # Update validity
        if not result[KEY_VALID]:
            combined[KEY_VALID] = False
    
    # In strict mode, warnings also invalidate the configuration
    if strict and combined[KEY_WARNINGS]:
        combined[KEY_VALID] = False
    
    return combined[KEY_VALID], combined


def print_validation_results(validation_result):
    """
    Log validation results using centralized logging system.
    
    Args:
        validation_result: Dictionary from validate_run_config
    """
    errors = validation_result[KEY_ERRORS]
    warnings = validation_result[KEY_WARNINGS]
    corrections = validation_result[KEY_CORRECTIONS]
    
    # Log errors
    if errors:
        for error in errors:
            log_event('VALIDATION_ERROR', error_message=error)
    
    # Log warnings
    if warnings:
        for warning in warnings:
            log_event('VALIDATION_WARNING', warning_message=warning)
    
    # Log corrections
    if corrections:
        for correction in corrections:
            log_event('VALIDATION_AUTO_CORRECTION', correction_description=correction)
    
    # Log final status if no issues
    if not errors and not warnings:
        log_event('VALIDATION_COMPLETE_NO_ISSUES')